# uvicorn main:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import login_router

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

app.include_router(login_router)
