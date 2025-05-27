from __future__ import annotations
"""
PNU Scholarship Parser API – v1.1
--------------------------------
* 개선 사항
  1. **중복 파싱 방지** – 첨부파일을 SHA‑256 해시로 식별해 이미 처리된 문서는 건너뜀.
  2. **FAISS 인덱스 영속/증분** – 인덱스 디렉터리가 존재하면 로드 후 새 청크만 추가.
  3. **장학금 조건 키워드 매칭** – 간단한 룰 기반 스캐닝(알람용) + 로깅.
  4. **로깅 강화** – 단계별 진행 상황과 스킵 사유가 콘솔에 출력.

"""
from fastapi import APIRouter
# ───────── 표준 라이브러리 ─────────
import hashlib
import json
import logging
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from urllib.parse import urljoin

from db.db import SessionLocal, Document  # DB 세션 및 모델


# ───────── 외부 라이브러리 ─────────
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_upstage import UpstageEmbeddings
from langchain_community.vectorstores import FAISS
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, ReadTimeout
from urllib3.util import Retry
from openai import OpenAI

# ───────── 환경설정 ─────────
load_dotenv()
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
if not UPSTAGE_API_KEY:
    raise RuntimeError("환경변수 UPSTAGE_API_KEY 가 설정되지 않았습니다.")

# ───────── 로깅 ─────────
logger = logging.getLogger("pnu_parser")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
logger.addHandler(handler)

# ───────── FastAPI ─────────
scholarship_router = APIRouter()


# ───────── 상수 ─────────
BASE_URL = "https://cse.pusan.ac.kr"
LIST_URL = f"{BASE_URL}/bbs/cse/2605/artclList.do"
SUPPORTED_EXTENSIONS = (".pdf", ".hwp", ".hwpx", ".docx", ".ppt", ".pptx")
KEYWORD = "장학"
CATEGORY_SEQ = "4229"
MAX_PAGES = 1
MAX_NOTICES = 8  # 처리할 공지 개수 확대

# ───────── 장학금 룰 (예시) ─────────
SCHOLARSHIP_RULES = {
    "국가근로": ["국가근로", "근로장학"],
    "푸른등대": ["푸른등대"],
    "지역인재": ["지역인재", "특별"]
}

# ───────── 데이터 구조 ─────────
@dataclass
class AttachmentDoc:
    id: int
    file_name: str
    content_html: str
    content_text: str
    matched_rules: List[str]

parsed_notices: Dict[int, Dict] = {}
next_notice_id: int = 1
next_attach_id: int = 1

# ───────── Embedding & FAISS ─────────
embeddings = UpstageEmbeddings(
    model="solar-embedding-1-large",
    upstage_api_key=UPSTAGE_API_KEY,
)
vector_store: FAISS | None = None
VECTOR_DIR = Path("./faiss_index")

# ───────── 해시 저장소 ─────────
HASH_FILE = Path("known_hashes.json")
if HASH_FILE.exists():
    known_hashes = set(json.loads(HASH_FILE.read_text()))
else:
    known_hashes: set[str] = set()

def save_known_hashes():
    HASH_FILE.write_text(json.dumps(list(known_hashes), ensure_ascii=False, indent=2))

# ───────── Session & Retry ─────────
retry_policy = Retry(total=2, backoff_factor=1.5, allowed_methods={"POST"}, status_forcelist=[502, 503, 504])
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry_policy))

# ───────── 유틸 ─────────

def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def guess_mime(fname: str) -> str:
    mime, _ = mimetypes.guess_type(fname)
    if mime:
        return mime
    return {".hwp": "application/x-hwp", ".hwpx": "application/x-hwp"}.get(Path(fname).suffix.lower(), "application/octet-stream")


def call_upstage(file_name: str, file_bytes: bytes) -> dict:
    """Upstage Document-Parse 호출 후 JSON 반환"""
    api_url = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
    files = {"document": (file_name, file_bytes, guess_mime(file_name))}
    data = {"model": "document-parse"}

    try:
        resp = session.post(api_url, headers=headers, files=files, data=data, timeout=(10, 180))
        resp.raise_for_status()
        return resp.json()
    except ReadTimeout:
        logger.warning(f"⏰ ReadTimeout ▶ {file_name}")
        raise
    except HTTPError as e:
        logger.error(f"HTTPError ▶ {file_name} – {e}")
        raise

# ───────── 키워드 매칭 ─────────

def match_rules(text: str) -> List[str]:
    matched = []
    lower = text.lower()
    for rule_name, kws in SCHOLARSHIP_RULES.items():
        if all(kw.lower() in lower for kw in kws):
            matched.append(rule_name)
    return matched

# ───────── 크롤러 ─────────

def crawl_and_parse(keyword: str = KEYWORD, max_pages: int = MAX_PAGES, max_notices: int = MAX_NOTICES) -> None:
    """장학 카테고리 + 제목 검색 크롤러"""
    global next_notice_id, next_attach_id

    headers = {"User-Agent": "Mozilla/5.0"}
    logger.info("[START] 크롤링 시작")

    page = 1
    while page <= max_pages and len(parsed_notices) < max_notices:
        payload = {"srchColumn": "sj", "srchWrd": keyword, "bbsClSeq": CATEGORY_SEQ, "page": str(page), "isViewMine": "false"}
        resp = session.post(LIST_URL, headers=headers, data=payload, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        articles = soup.select("td._artclTdTitle a.artclLinkView")
        if not articles:
            break
        logger.info(f"[INFO] page {page} - 글 {len(articles)}개")

        for a in articles:
            if len(parsed_notices) >= max_notices:
                break

            row = a.find_parent("tr")
            if row and any(cls.startswith("headline") for cls in (row.get("class") or [])):
                logger.info(f"[SKIP] 고정공지: {a.get_text(strip=True)}")
                continue

            notice_title = a.get_text(strip=True)
            detail_url = urljoin(BASE_URL, a["href"])
            logger.info(f"[INFO] 처리 중(공지): {notice_title}")

            notice_id = next_notice_id
            parsed_notices[notice_id] = {"title": notice_title, "url": detail_url, "attachments": []}

            next_notice_id += 1

            try:
                detail_resp = session.get(detail_url, headers=headers, timeout=15)
                detail_resp.raise_for_status()
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
            except Exception as e:
                logger.error(f"[ERROR] 상세 페이지 오류: {e}")
                continue

            attachments = detail_soup.select('dl.artclForm dd.artclInsert li a[href*="/download.do"]')
            if not attachments:
                logger.info("[SKIP] 첨부 없음")
                continue

            for file_link in attachments:
                file_name = file_link.get_text(strip=True)
                if not file_name.lower().endswith(SUPPORTED_EXTENSIONS):
                    logger.warning(f"[SKIP] 미지원 포맷: {file_name}")
                    continue

                file_url = urljoin(detail_url, file_link["href"])
                try:
                    file_resp = session.get(file_url, headers=headers, timeout=30)
                    file_resp.raise_for_status()
                except Exception as e:
                    logger.error(f"[ERROR] 파일 다운로드 실패: {file_name} – {e}")
                    continue

                f_hash = sha256_bytes(file_resp.content)
                if f_hash in known_hashes:
                    logger.info(f"[SKIP] 중복 파일: {file_name}")
                    continue

                # ── Upstage 변환 요청 ──
                logger.info(f"📤 Upstage 요청 시작 ▶ {file_name}")
                try:
                    result_json = call_upstage(file_name, file_resp.content)
                except (ReadTimeout, HTTPError):
                    continue

                html_segments = [elem["content"]["html"] for elem in result_json.get("elements", []) if "content" in elem and "html" in elem["content"]]
                full_html = "\n".join(html_segments) or "<p>(빈 문서)</p>"

                text_segments = [BeautifulSoup(h, "html.parser").get_text(" ", strip=True) for h in html_segments]
                full_text = "\n".join(filter(None, text_segments)) or "(빈 문서)"

                # 파일에서 장학금 조건 추출
                client = OpenAI(
                    api_key=UPSTAGE_API_KEY,
                    base_url="https://api.upstage.ai/v1"
                )
                prompt = f"""Extract scholarship conditions from the following text:
                {full_text}
                Return the conditions in csv format including min_gpa,start_date,end_date,grade,status.
                min_gpa is a float number between 0 and 4.5 inclusive.
                min_gpa is the minimum GPA required for the scholarship.
                start_date and end_date are date strings in YYYY-MM-DD format.
                start_date is the start date of application period of the scholarship.
                end_date is the end date of application period of the scholarship.
                grade is an integer between 1 and 4.
                grade is the attending year of the student.
                status is a string that can be 재학 or 휴학.
                if min_gpa is not found, return an empty string.
                if start date is not found, return an empty string.
                if end date is not found, return an empty string.
                if grade is not found, return an empty string.
                if status is not found, return an empty string.
                the following is an example of the response:
                min_gpa: 2.5, start_date: 2024-03-01, end_date: 2024-08-31, grade: 1, status: 재학
                Do not include any other text in the response.
                """
                response = client.chat.completions.create(
                    model="solar-pro2-preview",
                    messages=[{"role": "user", "content": prompt}]
                )
                conditions = response.choices[0].message.content
     
                if conditions:
                    try:
                        import re

                        pattern_gpa = r"min_gpa:\s*([\d.]+)"
                        match = re.search(pattern_gpa, conditions)

                        try:
                            gpa = match.group(1)
                        except:
                            gpa = None

                        pattern_start_date = r"start_date:\s*([\d-]+)"
                        match = re.search(pattern_start_date, conditions)

                        try:
                            start_date = match.group(1)
                        except:
                            start_date = None

                        pattern_end_date = r"end_date:\s*([\d-]+)"
                        match = re.search(pattern_end_date, conditions)

                        try:
                            end_date = match.group(1)
                        except:
                            end_date = None

                        pattern_grade = r"grade:\s*(\d+)"
                        match = re.search(pattern_grade, conditions)

                        try:
                            grade = match.group(1)
                        except:
                            grade = None

                        pattern_status = r"status:\s*(\S+)"
                        match = re.search(pattern_status, conditions)

                        try:
                            status = match.group(1)
                        except:
                            status = None

                        
                    except Exception as e:
                        logger.error(f"❌ 조건 파싱 실패: {e}")
                        continue

                matched = match_rules(full_text)
                if matched:
                    logger.info(f"🔔 알림 매칭: {matched} – {file_name}")
                else:
                    logger.info(f"⚪ 조건 미일치: {file_name}")

                parsed_notices[notice_id]["attachments"].append(
                    AttachmentDoc(id=next_attach_id, file_name=file_name, content_html=full_html, content_text=full_text, matched_rules=matched)
                )
                # DB에 문서 저장
                try:
                    db = SessionLocal()
                    new_doc = Document(
                        title=notice_title,
                        link=detail_url,
                        content=full_text,
                        gpa=float(gpa) if gpa else None,
                        start_date=datetime.strptime(start_date, "%Y-%m-%d") if start_date else None,
                        end_date=datetime.strptime(end_date, "%Y-%m-%d") if end_date else None,
                        status=status if status else None,
                        grade=int(grade) if grade else None,
                    )
                    db.add(new_doc)
                    db.commit()
                    logger.info(f"✅ DB 저장 완료: {notice_title}")
                except Exception as e:
                    try:
                        db.rollback()
                        db = SessionLocal()
                        new_doc = Document(
                            title=notice_title,
                            link=detail_url,
                            content=full_text,
                            gpa=None,
                            start_date=None,
                            end_date=None,
                            status=None,
                            grade=None,
                        )
                        db.add(new_doc)
                        db.commit()
                        logger.info(f"✅ DB 저장 완료: {notice_title}")
                    except Exception as e:
                        logger.error(f"❌ DB 저장 실패: {e}")
                finally:
                    db.close()
                next_attach_id += 1
                known_hashes.add(f_hash)
        page += 1

    save_known_hashes()

# ───────── FAISS 인덱싱 ─────────

def build_faiss_index() -> None:
    """새 문서만 인덱스에 추가하거나, 인덱스가 없으면 새로 생성"""
    global vector_store

    if not parsed_notices:
        logger.warning("빌드할 문서가 없습니다.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=256)

    # 1️⃣ 새로 수집된 모든 텍스트 청크 수집
    new_texts: List[str] = []
    new_metas: List[dict] = []

    for notice in parsed_notices.values():
        for attach in notice["attachments"]:
            for chunk in splitter.split_text(attach.content_html):
                new_texts.append(chunk)
                new_metas.append({
                    "notice_title": notice["title"],
                    "attachment_id": attach.id,
                    "file_name": attach.file_name,
                    "url": notice.get("url"), 
                })  

    if not new_texts:
        logger.info("[FAISS] 추가할 청크 없음 – 저장 스킵")
        return

    # 2️⃣ 기존 인덱스 로드 or 새 인덱스 생성
    if VECTOR_DIR.exists():
        logger.info("[FAISS] 기존 인덱스 로드")
        vector_store = FAISS.load_local(str(VECTOR_DIR), embeddings, allow_dangerous_deserialization=True,)
        vector_store.add_texts(new_texts, metadatas=new_metas)
    else:
        logger.info("[FAISS] 새 인덱스 생성")
        vector_store = FAISS.from_texts(texts=new_texts, embedding=embeddings, metadatas=new_metas)

    # 3️⃣ 저장
    vector_store.save_local(str(VECTOR_DIR))
    logger.info(f"[✅ FAISS] {len(new_texts)}개 청크 저장 완료")

# ───────── API ───────── ─────────

@scholarship_router.post("/notices/refresh")
def refresh_notices(background_tasks: BackgroundTasks, keyword: str = KEYWORD):
    parsed_notices.clear()
    global next_notice_id, next_attach_id
    next_notice_id = 1
    next_attach_id = 1
    try:
        crawl_and_parse(keyword)
        # 인덱싱은 백그라운드 태스크로 실행해 응답 속도 향상
        background_tasks.add_task(build_faiss_index)
        return {"status": "success", "notices": len(parsed_notices)}
    except Exception as e:
        raise HTTPException(500, str(e))

# ───────── (옵션) 서버 기동 시 자동 수집 ─────────
# crawl_and_parse()
