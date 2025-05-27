# uvicorn main:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import login_router
from routes.user import user_router
from routes.docs import doc_router
from simple_fastapi_auth import scholarship_router
from db.db import init_db

app = FastAPI()

# --- CORS 설정 -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 모든 도메인 허용. 필요하면 ["https://example.com"] 식으로 제한
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT … 전부 허용. 필요하면 ["GET", "POST"] 식으로 제한
    allow_headers=["*"],          # 모든 헤더 허용
)
# --------------------------------------------------------------------

init_db()  # 앱 시작 시 DB 테이블 생성

app.include_router(login_router)
app.include_router(user_router)
app.include_router(doc_router)
app.include_router(scholarship_router)