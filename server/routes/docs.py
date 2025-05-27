from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
from fastapi import HTTPException
from db.db import SessionLocal, Document
from sqlalchemy import or_, desc

from fastapi import HTTPException
from db.db import SessionLocal, Document
from sqlalchemy import or_, desc

from fastapi import HTTPException
from fastapi import Query

doc_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@doc_router.get("/documents")
def get_all_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()

    return [
        {
            "id": doc.id,
            "title": doc.title,
            "link": doc.link,
            # "content": doc.content,
            "gpa": doc.gpa,
            "start_date": doc.start_date,
            "end_date": doc.end_date,
            "status": doc.status,
            "grade": doc.grade,
        }
        for doc in docs
    ]

@doc_router.get("/documents/titles")
def get_document_titles(db: Session = Depends(get_db)):
    docs = db.query(
        Document.title,
        Document.link,
        Document.start_date,
        Document.end_date,
        Document.status,
        Document.grade,
        Document.gpa
    ).all()
    
    return [
        {
            "title": title,
            "link": link,
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "grade": grade,
            "gpa": gpa
        }
        for title, link, start_date, end_date, status, grade, gpa in docs
    ]


class DocumentCreate(BaseModel):
    title: str
    link: str
    content: str
    gpa: Optional[float] = None
    start_date: Optional[str] = None  # ISO date string
    end_date: Optional[str] = None
    status: Optional[str] = None
    grade: Optional[int] = None

@doc_router.post("/documents")
def create_document(doc: DocumentCreate, db: Session = Depends(get_db)):
    new_doc = Document(
        title=doc.title,
        link=doc.link,
        content=doc.content,
        gpa=doc.gpa,
        start_date=doc.start_date,
        end_date=doc.end_date,
        status=doc.status,
        grade=doc.grade,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return {"success": True, "document_id": new_doc.id}


class DocumentUpdateRequest(BaseModel):
    gpa: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    grade: Optional[int] = None


@doc_router.put("/documents/{doc_id}")
def update_document(doc_id: int, update: DocumentUpdateRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if update.gpa is not None:
        doc.gpa = update.gpa
    if update.start_date is not None:
        doc.start_date = update.start_date
    if update.end_date is not None:
        doc.end_date = update.end_date
    if update.status is not None:
        doc.status = update.status
    if update.grade is not None:
        doc.grade = update.grade

    db.commit()
    db.refresh(doc)
    return {"success": True, "message": "Document updated", "document_id": doc.id}


@doc_router.post("/documents/sample")
def create_sample_documents(db: Session = Depends(get_db)):
    sample_docs = [
        {
            "title": "[장학] 2025.1학기 경제사정 곤란 대학생 국가장학금 지원 신청 안내(~6.5.)새글",
            "link": "https://cse.pusan.ac.kr/bbs/cse/2605/1728294/artclView.do",
            "content": "2025년 1학기 경제사정 곤란 대학생 국가장학금Ⅱ유형 지원 신청서\n신청자 인적 사항 대학 학과 학번 이름 학자금지원구간 (해당란에 체크) 기초～9구간 10구간 미산정 (국가장학금 미신청) 신청불가 신청 유형 (해당란에 체크) 부․모 실직/폐업 자립준비청년(舊 보호종료아동), 보호(연장)아동, 쉼터 입·퇴소 청소년인 대학생, 청소년 한부모인 대학생 본인 및 가족의 중대질병, 사고 등 그 외 기타 경제사정곤란 기존 수혜 여부* (○ 또는 ×) 비고(해당 시 모두 작성) 수혜 학기 사유\n* 동일 사유로 국가장학금Ⅱ유형(경제사정곤란 대학생 지원) 2회 이상 기 수혜자는 선발 제외\n본인은 상기와 같은 사유로 경제사정 곤란 대학생 장학금 지원을 신청합니다. ※ 붙임 증빙서류 각 1부.\n년 월 일 작성자 : (인)\n부산대학교총장 귀하\n※ 단, 한국장학재단의 국가장학금Ⅱ유형 선발 대상 심사 결과 지원이 불가하거나 제출 서류 등이 해당 장학금의 지원 계획과 상이한 경우 대상자에서 제외될 수 있습니다.\n- 1 -\n【첨부_추가제출서류 안내】\n- 실직 또는 폐업\n구분 증빙 서류 발급 방법 실직 ① 가족관계증명서(필수) 온라인발급(정부24 홈페이지 등) ② 아래 중 택일하여 제출(필수) - 퇴직증명서 - 건강보험자격득실확인서 - 고용보험 피보험자격 신고사실 통지서 온라인발급 (국민건강보험공단, 근로복지공단 등) ③ 아래 중 택일하여 제출(필수) - 실업급여 수급 상세 내역서 - 고용보험 수급자격 인정명세서 - 고용보험수급자격증 온라인발급(고용노동부 등) 폐업 ① 가족관계증명서(필수) ② 폐업사실증명서(필수) ③ 사실증명(사업자등록 사실여부)(필수) 온라인발급 (정부24 홈페이지, 국세청 홈택스 등)\n- 그 외 기타 경제적 사정 곤란\n구분 증빙서류 발급방법 자립준비청년 (舊 보호종료아동) - 보호종료확인서(필수) (′20. 9. 30.이전 보호종료) 아동복지시설, 가정위탁지원센터 (′20. 10. 1.이후 보호종료) 읍면동 행정복지센터 보호(연장) 아동 아동복지 시설 ① 입소사실 확인서(필수) ② 아동복지시설 신고증(사본)(필수) 아동복지시설 가정위탁 가정위탁보호 확인서(필수) 시·군·구청 및 읍면동 행정복지센터 쉼터 입·퇴소 청소년인 대학생 아래 중 택일하여 제출(필수) - 쉼터 입소 확인증 - 퇴소사실 증명서 청소년 쉼터 청소년 한부모인 대학생 - 한부모 가족 증명서(필수) 시·군·구청 및 읍면동 행정복지센터 본인 및 가족의 중대질병(장기투병 등) 및 사고 등 ① 진단서(필수) ② 의료비 영수증(필수) ③ 가족관계증명서(필수) 해당기관 발급 ④ 그 외 추가 서류(선택) - 경제적 곤란 사정을 확인할 수 있는 기타 증빙이 있을 경우 그 외 기타 경제사정 곤란 기타 공공기관에 의해 경제사정 곤란에 대한 사유 확인이 가능한 서류(필수) 해당기관 발급\n- 2 -",
            "gpa": 3.5,
            "start_date": "2025-05-23",
            "end_date": "2025-06-23",
            "status": '재학',
            "grade": 2
        },
        {
            "title": "[장학] 2025.2학기 국가근로장학금 1차 신청 안내(~6.23. 18시)새글",
            "link": "https://cse.pusan.ac.kr/bbs/cse/2605/1727555/artclView.do",
            "content": "푸른등대\n한국장학재단\n국가근로장학금\n2025년 2학기 1차 학생신청 방법(모바일 앱)\n근로장학생용\n※ 신청 전 주요 안내 사항\n2025년 2학기 1차 국가근로장학금 학생 신청기간 2025. 5. 23.(금) 09:00 ~ 2025. 6. 23.(월) 18:00까지\n서류제출 및 가구원 동의기간 2025. 5. 23.(금) 09:00 ~ 2025. 6. 30.(월) 18:00까지\n1.국가근로장학금은 근로장학생의 근로시간에 따라 지급됩니다.\n2. 2025년 동계방학 집중근로 프로그램에 참여하고자 하는 학생은 반드시 1차및 2차 통합신청 기간에 국가근로장학금을 신청하시기 바랍니다.\n3. 희망 근로기관 신청, 장학생 선발 등의 절차는 대학별 상이하므로, 소속대학의 공지사항을 확인한 후 담당자 문의 바랍니다.\n※ 국가근로장학금 신청 관련 문의: ☎1599-2290\n2025. 5.\n1) 모바일 앱 접속\n한국장학재단 모바일 앱 접속\n· 한국장학재단 모바일 앱 접속 · 왼쪽 상단 메뉴 클릭 1 ) · 로그인 ( 2 ) 후 장학금 신청 - 통합신청 클릭 3 )\n2) 통합신청 - 신청 화면\n모바일 앱 > 통합신청 > 통합신청하러 가기 > 학사 정보 등록\n· 통합신청 가이드 내용 확인 후 '통합신청하러 가기' ( 1 ) 클릭 · 학사 정보 등록 ( 2 ) 클릭\n2) 통합신청 - 개인(신용) 정보 수집 ·이용·제공 조회 동의\n모바일 앱 > 통합신청 > 개인(신용) 수집·이용·제공 및 조회 동의\n· 개인(신용)정보 수집·이용·제공 및 조회 동의 - 동의서 세부 내용 확인 및 '동의함 / 동의하지 않음' 선택 - 하단의 '약관에 동의함' 클릭( 1 ) - 공동인증서, 금융인증서, 민간인증서 중 선택하여 동의 진행\n2) 통합신청 - ① 학사 정보 등록\n모바일 앱 > 통합신청 > 학사 정보 등록\n· 신청자 본인의 학적 상태, 소속 대학 등 학사 정보 등록 후 확인 클릭( 1 )\n- 본인의 학적 상태, 소속 대학, 학번 등을 정확하게 입력 - 잘못된 정보를 기입할 경우, 장학금 심사 및 지급 시 불이익이 발생할 수 있으므로 정확한 정보 기입\n· '학교정보 불러오기' 여부 선택\n- '불러오기' 선택 시 직전학기 통합신청 시 입력한 학교 정보가 자동 입력됨 ※ 자동 입력된 학교 정보와 신청자 본인의 정보가 일치하는지 확인\n- '직접입력 선택 시 학교 정보 직접 입력\n2) 통합신청  ② 학자금 유형 선택\n모바일 앱 > 통합신청 > 학자금 유형 선택\n· 학자금 유형 선택 메뉴 클릭 ( 1 · '국가근로장학금'  2 ) 선택 후 확인 ( 3 ) 클릭\n2) 통합신청  ③ 약관 동의\n모바일 앱 > 통합신청 > 약관 동의\n· 약관 동의 메뉴 클릭( 1 · 약관 동의 세부 내용을 확인 후 하단의 확인 ( 2 ) 버튼 클릭\n2) 통합신청  ④ 신청정보 등록 - 1\n모바일 앱 > 통합신청 > 신청정보 등록(개인정보)\n· 신청정보 등록 ( 1 ) 클릭 · 개인정보(휴대전화번호, 이메일 등) 입력 ( 2 ) 후 다음 ( 3 ) 클릭\n2) 통합신청 - ④ 신청정보 등록 - 2\n모바일 앱 > 통합신청 > 신청정보 등록(가족 및 계좌정보)\n· 가족정보 입력 - 결혼 여부, 자녀 정보, 수급자 여부 등 입력 후 다음 ( 1 ) 클릭\n· 계좌정보 입력 - 기존에 등록된 계좌를 선택하거나 신규 계좌 등록 후 하단의 확인 ( 2 ) 클릭 - 반드시 본인 명의 계좌를 등록해야 하며, 타인 명의 계좌 입력 시 장학금 수혜 불가 - 반드시 선택한 은행에 맞는 계좌번호를 입력해야 하며, 계좌정보가 불일치할 경우 추후 대학에서 장학금 지급 불가할 수 있음\n※ 계좌정보 불일치 예시: A은행 선택 후 B은행의 계좌번호를 입력한 경우\n2) 통합신청  ⑤ 신청 내용 제출 및 신청 완료\n통합신청완료\n· 학사 정보 등록부터 신청정보 등록까지 완료하였다면 하단의 신청하기 ( 1 ) 버튼 클릭 후 인증서를 사용하여 전자서명 ※ 공동인증서, 금융인증서, 간편인증(민간인증서) 이용\n2025년 2학기 1차 국가근로장학금 신청 완료 2 )\n3) 신청 완료 및 현황 조회\n· 신청현황 보러가기( 1 ) 클릭 시 장학금 신청 정보 확인 가능 · 해당 화면에서 신청 상태 확인( 2 ) 및 신청 취소 가능\n(참고) 가구원 동의 절차\n개인정보제공 및 약관동의\nx\n모바일 앱 > 메뉴 > 학자금 지원구간 > 가구원 정보제공 동의하기\n· 개인정보제공 및 약관동의( 1 ) 클릭 · 개인정보제공 및 약관 내용 확인( 2 ) 및 약관에 동의함( 3 ) 클릭 · 개인정보를 제공하는 사람(신청자의 부·모 또는 배우자) 실명인증( 4 ) (공동인증서, 금융인증서, 민간인증서를 활용하여 인증) 후 다음 클릭\n(참고) 가구원 동의 절차\n모바일 앱 > 메뉴 > 학자금 지원구간 > 가구원 정보제공 동의하기\n· [학생신청정보 존재 시] 동의대상자 선택 > 개인정보 및 금융정보 제공동의 동의박스 체크( 1 ) > 동의완료( 3 ) (공동/금융/민간 인증서 활용)\n· [학생신청정보 미존재 시] 동의대상자 정보 직접등록( 2 ) 클릭 동의대상자 정보 직접 입력 후, 동의대상자(신청자) 선택 > 개인정보 및 금융 정보 제공동의 동의박스 체크( 1 ) > 동의완료( 3 ) (공동/금융/민간 인증서 활용)",
            "gpa": 3.0,
            "start_date": "2025-06-23",
            "end_date": "2025-06-29",
            "status": '재학',
            "grade": 3
        },
        {
            "title": "[장학] 미얀마 지진 피해 장학생 신청 안내(~5.9.)",
            "link": "https://cse.pusan.ac.kr/bbs/cse/2605/1725021/artclView.do",
            "content": "미얀마 지진 피해 장학생 선발 계획\n<2024. 4. 23. 국제협력실>\n□ 추진 배경\n◦ 최근 발생한 2025년 미얀마 지진 피해로 물질적‧정신적 어려움을 겪는 피해 가정 학생의 경제적 부담 경감을 위한 생활비 성격 장학금 지원\n□ 장학생 추천 및 선발 주요 내용\n◦ (선발 근거)\n- 「부산대학교 장학금규정」(이하 “규정”) 제9조(자격)제6호 - 「부산대학교 장학생 선발 지침」(이하 “지침”) 제12조(장학위원회 인정자 장학금) 및 제33조(학사과정 장학제도와 동일한 장학금)\n◦ (선발 방법) 국제처(국제협력실)에서 신청서를 접수하여 1차 취합‧ 검토 후 장학위원회 심의를 거쳐 최종 선발\n◦ (지원 자격) 2025년 미얀마 지진 피해 지역* 출신 학위 과정** 재학생(성적 무관)\n* 미얀마 및 지진 피해를 입은 국가 포함\n** 학부 및 대학원생(어학연수과정 등록 학생 장학 신청은 언어교육원에서 별도 진행)\n※ (장학 대상 제외) 수업연한 초과자, 휴학생 및 수료생\n◦ (장학금) 학업지원금(생활비) 50만원 지급(1회 한정)\n◦ (신청 절차)\n- 신청 방법: 국제처 국제협력실로 신청서 등 필요 서류 제출 - 신청 기간: ˊ25. 4. 28.(월) ~ 5. 9.(금) 18:00 - 제출 서류: 장학금 신청서 1부 ※ 증빙 자료(공공기관 발급 서류 혹은 피해 현장 사진 등)는 별첨 제출 - 제출처: 국제처 국제협력실(상남국제관 1층)\n- 유의사항\n· 피해 정도에 따라 장학생으로 선발되지 않을 수도 있음 · 최종 선발 이후 학생지원시스템에 등록된 계좌*로 장학금 지급 * (계좌등록) 학생지원시스템-학적-학적부-계좌번호 수정\n□ 추진 일정\n◦ 장학생 신청 접수 공고: ˊ25. 4. 24.(목) ※ 국제처 웹사이트 게시 및 학내 공문 발송 ◦ 장학 신청 접수: ˊ25. 4. 28.(월) ~ 5. 9.(금) ◦ 학생처 제출: ˊ25. 5월 2주 ◦ 장학위원회 개최: ˊ25년 5월 중 ◦ 장학금 지급: ˊ25년 6월 중\n[붙임1]\n재난지원장학금 신청서\nScholarship for Disaster Relief Support\n소속 단과대학 college 소속 학과(부) department (school) 학년 year 학번 student ID 성명 name 연락처 phone # 피해내용 description of the damage situation 부산대학교 총장 ※ (지진으로인한피해내용상세히작성하고,피해사진은별도첨부,작성후삭제) ※ (Please provide a detailed account of the damage caused by the earthquake. Photographs of the damage should be attached separately. E rase after fillingout.) 위와 같이 재난지원장학금을 신청합니다. In accordance with the above, I am submitting my application for the Disaster Relief Support Scholarship. 2025년 월 일 신청인 (학 생) (인) 귀하\nTo the President of Pusan National University",
            "gpa": 3.0,
            "start_date": "2025-04-28",
            "end_date": "2025-05-09",
            "status": '재학',
            "grade": 2
        },
        {
            "title": "[장학] 2025 푸른등대 삼성기부장학사업 신규 장학생 신청 안내(~4.21.)",
            "link": "https://cse.pusan.ac.kr/bbs/cse/2605/1719053/artclView.do",
            "content": "푸른등대\n한국장학재단\n국가근로장학금\n2025년 2학기 1차 학생신청 방법(모바일 앱)\n근로장학생용\n※ 신청 전 주요 안내 사항\n2025년 2학기 1차 국가근로장학금 학생 신청기간 2025. 5. 23.(금) 09:00 ~ 2025. 6. 23.(월) 18:00까지\n서류제출 및 가구원 동의기간 2025. 5. 23.(금) 09:00 ~ 2025. 6. 30.(월) 18:00까지\n1.국가근로장학금은 근로장학생의 근로시간에 따라 지급됩니다.\n2. 2025년 동계방학 집중근로 프로그램에 참여하고자 하는 학생은 반드시 1차및 2차 통합신청 기간에 국가근로장학금을 신청하시기 바랍니다.\n3. 희망 근로기관 신청, 장학생 선발 등의 절차는 대학별 상이하므로, 소속대학의 공지사항을 확인한 후 담당자 문의 바랍니다.\n※ 국가근로장학금 신청 관련 문의: ☎1599-2290\n2025. 5.\n1) 모바일 앱 접속\n한국장학재단 모바일 앱 접속\n· 한국장학재단 모바일 앱 접속 · 왼쪽 상단 메뉴 클릭 1 ) · 로그인 ( 2 ) 후 장학금 신청 - 통합신청 클릭 3 )\n2) 통합신청 - 신청 화면\n모바일 앱 > 통합신청 > 통합신청하러 가기 > 학사 정보 등록\n· 통합신청 가이드 내용 확인 후 '통합신청하러 가기' ( 1 ) 클릭 · 학사 정보 등록 ( 2 ) 클릭\n2) 통합신청 - 개인(신용) 정보 수집 ·이용·제공 조회 동의\n모바일 앱 > 통합신청 > 개인(신용) 수집·이용·제공 및 조회 동의\n· 개인(신용)정보 수집·이용·제공 및 조회 동의 - 동의서 세부 내용 확인 및 '동의함 / 동의하지 않음' 선택 - 하단의 '약관에 동의함' 클릭( 1 ) - 공동인증서, 금융인증서, 민간인증서 중 선택하여 동의 진행\n2) 통합신청 - ① 학사 정보 등록\n모바일 앱 > 통합신청 > 학사 정보 등록\n· 신청자 본인의 학적 상태, 소속 대학 등 학사 정보 등록 후 확인 클릭( 1 )\n- 본인의 학적 상태, 소속 대학, 학번 등을 정확하게 입력 - 잘못된 정보를 기입할 경우, 장학금 심사 및 지급 시 불이익이 발생할 수 있으므로 정확한 정보 기입\n· '학교정보 불러오기' 여부 선택\n- '불러오기' 선택 시 직전학기 통합신청 시 입력한 학교 정보가 자동 입력됨 ※ 자동 입력된 학교 정보와 신청자 본인의 정보가 일치하는지 확인\n- '직접입력 선택 시 학교 정보 직접 입력\n2) 통합신청  ② 학자금 유형 선택\n모바일 앱 > 통합신청 > 학자금 유형 선택\n· 학자금 유형 선택 메뉴 클릭 ( 1 · '국가근로장학금'  2 ) 선택 후 확인 ( 3 ) 클릭\n2) 통합신청  ③ 약관 동의\n모바일 앱 > 통합신청 > 약관 동의\n· 약관 동의 메뉴 클릭( 1 · 약관 동의 세부 내용을 확인 후 하단의 확인 ( 2 ) 버튼 클릭\n2) 통합신청  ④ 신청정보 등록 - 1\n모바일 앱 > 통합신청 > 신청정보 등록(개인정보)\n· 신청정보 등록 ( 1 ) 클릭 · 개인정보(휴대전화번호, 이메일 등) 입력 ( 2 ) 후 다음 ( 3 ) 클릭\n2) 통합신청 - ④ 신청정보 등록 - 2\n모바일 앱 > 통합신청 > 신청정보 등록(가족 및 계좌정보)\n· 가족정보 입력 - 결혼 여부, 자녀 정보, 수급자 여부 등 입력 후 다음 ( 1 ) 클릭\n· 계좌정보 입력 - 기존에 등록된 계좌를 선택하거나 신규 계좌 등록 후 하단의 확인 ( 2 ) 클릭 - 반드시 본인 명의 계좌를 등록해야 하며, 타인 명의 계좌 입력 시 장학금 수혜 불가 - 반드시 선택한 은행에 맞는 계좌번호를 입력해야 하며, 계좌정보가 불일치할 경우 추후 대학에서 장학금 지급 불가할 수 있음\n※ 계좌정보 불일치 예시: A은행 선택 후 B은행의 계좌번호를 입력한 경우\n2) 통합신청  ⑤ 신청 내용 제출 및 신청 완료\n통합신청완료\n· 학사 정보 등록부터 신청정보 등록까지 완료하였다면 하단의 신청하기 ( 1 ) 버튼 클릭 후 인증서를 사용하여 전자서명 ※ 공동인증서, 금융인증서, 간편인증(민간인증서) 이용\n2025년 2학기 1차 국가근로장학금 신청 완료 2 )\n3) 신청 완료 및 현황 조회\n· 신청현황 보러가기( 1 ) 클릭 시 장학금 신청 정보 확인 가능 · 해당 화면에서 신청 상태 확인( 2 ) 및 신청 취소 가능\n(참고) 가구원 동의 절차\n개인정보제공 및 약관동의\nx\n모바일 앱 > 메뉴 > 학자금 지원구간 > 가구원 정보제공 동의하기\n· 개인정보제공 및 약관동의( 1 ) 클릭 · 개인정보제공 및 약관 내용 확인( 2 ) 및 약관에 동의함( 3 ) 클릭 · 개인정보를 제공하는 사람(신청자의 부·모 또는 배우자) 실명인증( 4 ) (공동인증서, 금융인증서, 민간인증서를 활용하여 인증) 후 다음 클릭\n(참고) 가구원 동의 절차\n모바일 앱 > 메뉴 > 학자금 지원구간 > 가구원 정보제공 동의하기\n· [학생신청정보 존재 시] 동의대상자 선택 > 개인정보 및 금융정보 제공동의 동의박스 체크( 1 ) > 동의완료( 3 ) (공동/금융/민간 인증서 활용)\n· [학생신청정보 미존재 시] 동의대상자 정보 직접등록( 2 ) 클릭 동의대상자 정보 직접 입력 후, 동의대상자(신청자) 선택 > 개인정보 및 금융 정보 제공동의 동의박스 체크( 1 ) > 동의완료( 3 ) (공동/금융/민간 인증서 활용)",
            "gpa": 2.5,
            "start_date": "2025-04-08",
            "end_date": "2025-04-21",
            "status": "재학",
            "grade": 1
        },
    ]

    created_docs = []
    for doc in sample_docs:
        new_doc = Document(
            title=doc["title"],
            link=doc["link"],
            content=doc["content"],
            gpa=doc.get("gpa"),
            start_date=doc.get("start_date"),
            end_date=doc.get("end_date"),
            status=doc.get("status"),
            grade=doc.get("grade"),
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        created_docs.append(new_doc.id)

    return {"success": True, "created_document_ids": created_docs}


@doc_router.get("/documents/filter")
def filter_documents(
    min_gpa: Optional[float] = None,
    grade: Optional[int] = None,
    status: Optional[str] = None,  # "재학" 또는 "휴학"
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    conditions = []

    # 각 조건을 OR로 누적
    if min_gpa is not None:
        conditions.append(Document.gpa >= min_gpa)
    if grade is not None:
        conditions.append(Document.grade == grade)
    if status is not None:
        conditions.append(Document.status == status)
    
    # 날짜 조건도 OR로 추가
    conditions.append(Document.start_date <= date.today())
    conditions.append(Document.end_date >= date.today())

    # OR 조건 적용
    if conditions:
        query = query.filter(or_(*conditions))

    # 정렬 조건 추가 (GPA 높은 순, 학년 낮은 순)
    query = query.order_by(desc(Document.gpa), Document.grade)

    docs = query.all()
    return [{
        "title": d.title, 
        "link": d.link, 
        "gpa": d.gpa, 
        "grade": d.grade, 
        "status": d.status
    } for d in docs]


@doc_router.get("/documents/filter")
def filter_documents(
    min_gpa: Optional[float] = None,
    grade: Optional[int] = None,
    status: Optional[str] = None,  # "재학" 또는 "휴학"
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    conditions = []

    # 각 조건을 OR로 누적
    if min_gpa is not None:
        conditions.append(Document.gpa >= min_gpa)
    if grade is not None:
        conditions.append(Document.grade == grade)
    if status is not None:
        conditions.append(Document.status == status)
    
    # 날짜 조건도 OR로 추가
    conditions.append(Document.start_date <= date.today())
    conditions.append(Document.end_date >= date.today())

    # OR 조건 적용
    if conditions:
        query = query.filter(or_(*conditions))

    # 정렬 조건 추가 (GPA 높은 순, 학년 낮은 순)
    query = query.order_by(desc(Document.gpa), Document.grade)

    docs = query.all()
    return [{
        "title": d.title, 
        "link": d.link, 
        "gpa": d.gpa, 
        "grade": d.grade, 
        "status": d.status,
        "start_date": d.start_date,
        "end_date": d.end_date
    } for d in docs]
