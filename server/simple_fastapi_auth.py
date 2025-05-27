from __future__ import annotations

"""
PNU Scholarship Parser API  (공지 1개 – 첨부 N개 구조)
---------------------------------------------------
실행 예시
$ uvicorn scholarship_parser:app --reload
"""

# ────────────────────────── 표준 라이브러리 ──────────────────────────
import logging
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from urllib.parse import urljoin

# ────────────────────────── 외부 라이브러리 ──────────────────────────
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_upstage import UpstageEmbeddings
from langchain_community.vectorstores import FAISS
from requests.adapters import HTTPAdapter               # ★
from requests.exceptions import HTTPError, ReadTimeout  # ★
from urllib3.util import Retry                          # ★

# ────────────────────────── 환경설정 ──────────────────────────
load_dotenv()
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
if not UPSTAGE_API_KEY:
    raise RuntimeError("환경변수 UPSTAGE_API_KEY 가 설정되지 않았습니다.")

# ────────────────────────── 로깅 설정 ──────────────────────────
logger = logging.getLogger(__name__)     # ★ 모듈 로거 사용
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
logger.addHandler(handler)

# ────────────────────────── FastAPI ──────────────────────────
app = FastAPI(title="PNU Scholarship Parser API")

# ────────────────────────── 상수 ────────────────────────────
BASE_URL = "https://cse.pusan.ac.kr"
LIST_URL = f"{BASE_URL}/bbs/cse/2605/artclList.do"
SUPPORTED_EXTENSIONS = (
    ".pdf",
    ".hwp",
    ".hwpx",
    ".docx",
    ".ppt",
    ".pptx",
)
KEYWORD = "장학"
CATEGORY_SEQ = "4229"
MAX_PAGES = 1
MAX_NOTICES = 1

# ────────────────────────── 인메모리 데이터 구조 ─────────────
@dataclass
class AttachmentDoc:
    id: int
    file_name: str
    content_html: str
    content_text: str

parsed_notices: Dict[int, Dict] = {}
next_notice_id: int = 1
next_attach_id: int = 1

# ────────────────────────── Embedding & FAISS ───────────────
embeddings = UpstageEmbeddings(
    model="solar-embedding-1-large",
    upstage_api_key=UPSTAGE_API_KEY,
)
vector_store: FAISS | None = None
VECTOR_DIR = Path("./faiss_index")

# ────────────────────────── Session & Retry 설정 ────────────
retry_policy = Retry(                              # ★
    total=2,
    backoff_factor=1.5,
    allowed_methods={"POST"},
    status_forcelist=[502, 503, 504],
)
session = requests.Session()                       # ★
session.mount("https://", HTTPAdapter(max_retries=retry_policy))

# ────────────────────────── 유틸 함수 ───────────────────────
def guess_mime(fname: str) -> str:
    mime, _ = mimetypes.guess_type(fname)
    if mime:
        return mime
    ext = Path(fname).suffix.lower()
    return {
        ".hwp": "application/x-hwp",
        ".hwpx": "application/x-hwp",
    }.get(ext, "application/octet-stream")


def call_upstage(file_name: str, file_bytes: bytes) -> dict:
    """Upstage Document-Parse 호출 후 JSON 반환 (ReadTimeout 처리)"""
    api_url = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
    files = {"document": (file_name, file_bytes, guess_mime(file_name))}
    data = {"model": "document-parse"}

    try:
        resp = session.post(
            api_url,
            headers=headers,
            files=files,
            data=data,
            timeout=(10, 180),       # ★ (connect 10s, read 180s)
        )
        resp.raise_for_status()
    except ReadTimeout as e:          # ★
        logger.warning(f"⏰ ReadTimeout ▶ {file_name} – {e}")
        raise
    except HTTPError as e:
        logger.error(f"HTTPError ▶ {file_name} – {e}")
        raise
    return resp.json()

# ────────────────────────── 크롤러 ──────────────────────────
def crawl_and_parse(
    keyword: str = KEYWORD,
    max_pages: int = MAX_PAGES,
    max_notices: int = MAX_NOTICES,
) -> None:
    """장학 카테고리 + 제목 검색 크롤러"""
    global next_notice_id, next_attach_id

    headers = {"User-Agent": "Mozilla/5.0"}

    logger.info("[START] 크롤링 시작")
    page = 1
    while page <= max_pages and len(parsed_notices) < max_notices:
        payload = {
            "srchColumn": "sj",
            "srchWrd": keyword,
            "bbsClSeq": CATEGORY_SEQ,
            "page": str(page),
            "isViewMine": "false",
        }

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
            parsed_notices[notice_id] = {"title": notice_title, "attachments": []}
            next_notice_id += 1

            try:
                detail_resp = session.get(detail_url, headers=headers, timeout=15)
                detail_resp.raise_for_status()
                detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
            except Exception as e:
                logger.error(f"[ERROR] 상세 페이지 오류: {e}")
                continue

            attachments = detail_soup.select(
                'dl.artclForm dd.artclInsert li a[href*="/download.do"]'
            )
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

                # ── Upstage 변환 요청 ──
                logger.info(f"📤 Upstage 요청 시작 ▶ {file_name}")          # ★
                try:
                    result_json = call_upstage(file_name, file_resp.content)
                except ReadTimeout:
                    logger.error(f"[SKIP] 변환 지연 ▶ {file_name}")        # ★
                    continue
                except HTTPError as e:
                    logger.error(f"[ERROR] {file_name} 변환 실패: {e}")
                    continue

                html_segments = [
                    elem["content"]["html"]
                    for elem in result_json.get("elements", [])
                    if "content" in elem
                ]
                full_html = "\n".join(html_segments) or "<p>(빈 문서)</p>"

                text_segments = []

                for html in html_segments:
                    soup = BeautifulSoup(html, "html.parser")
                    plain_text = soup.get_text(" ", strip=True)
                    if plain_text:
                        text_segments.append(plain_text)

                full_text = "\n".join(text_segments) or "(빈 문서)"

                parsed_notices[notice_id]["attachments"].append(
                    AttachmentDoc(
                        id=next_attach_id,
                        file_name=file_name,
                        content_html=full_html,
                        content_text=full_text,
                    )
                )
                logger.info(
                    f"[✅ 저장] notice {notice_id}, attach {next_attach_id}: {file_name}"
                )
                next_attach_id += 1

        page += 1

# ────────────────────────── FAISS 인덱스 빌드 ──────────────
def build_faiss_index() -> None:
    global vector_store
    if not parsed_notices:
        logger.warning("빌드할 문서가 없습니다.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    texts: List[str] = []
    metadatas: List[dict] = []

    for notice in parsed_notices.values():
        for attach in notice["attachments"]:
            raw_text = attach.content_html
            for chunk in splitter.split_text(raw_text):
                texts.append(chunk)
                metadatas.append({
                    "notice_title": notice["title"],
                    "attachment_id": attach.id,
                    "file_name": attach.file_name,
                })

    if not texts:
        logger.warning("임베딩할 텍스트가 없습니다.")
        return

    vector_store = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
    vector_store.save_local(str(VECTOR_DIR))
    logger.info(f"[✅ FAISS] {len(texts)}개 청크 저장 완료")

# ────────────────────────── API 엔드포인트 ────────────────
@app.get("/notices")
def list_notices():
    return [
        {
            "notice_id": nid,
            "title": notice["title"],
            "attachments": [
                {"id": att.id, "file_name": att.file_name}
                for att in notice["attachments"]
            ],
        }
        for nid, notice in parsed_notices.items()
    ]


@app.get("/notices/{notice_id}/{attach_id}")
def get_attachment(notice_id: int, attach_id: int):
    notice = parsed_notices.get(notice_id)
    if not notice:
        raise HTTPException(404, "Notice not found")

    attach = next((a for a in notice["attachments"] if a.id == attach_id), None)
    if not attach:
        raise HTTPException(404, "Attachment not found")

    return {
        "notice_id": notice_id,
        "title": notice["title"],
        "attachment_id": attach_id,
        "file_name": attach.file_name,
        "content_html": attach.content_html,
        "content_text": attach.content_text,
    }


@app.post("/notices/refresh")
def refresh_notices(keyword: str = KEYWORD):
    parsed_notices.clear()
    global next_notice_id, next_attach_id
    next_notice_id = 1
    next_attach_id = 1
    try:
        crawl_and_parse(keyword)
        build_faiss_index()
        return {
            "status": "success",
            "notices": len(parsed_notices),
            "faiss": "built" if vector_store else "none",
        }
    except Exception as e:
        raise HTTPException(500, str(e))

# ────────────────────────── (옵션) 서버 기동 시 자동 수집 ───
# crawl_and_parse()
