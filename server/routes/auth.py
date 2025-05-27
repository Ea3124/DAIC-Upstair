# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel

# login_router = APIRouter()

# users = {"test@example.com": {"password": "1234", "name": "홍길동"}}

# class LoginRequest(BaseModel):
#     email: str
#     password: str

# @login_router.post("/login")
# def login(req: LoginRequest):
#     user = users.get(req.email)
#     if user and user["password"] == req.password:
#         return {"success": True, "name": user["name"]}
#     raise HTTPException(status_code=401, detail="Invalid credentials")


# routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.db import SessionLocal, User

login_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginRequest(BaseModel):
    email: str
    password: str

@login_router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if user and user.password == req.password:  # 해커톤용: 비밀번호 평문 비교
        return {"success": True, "name": user.nickname}
    raise HTTPException(status_code=401, detail="Invalid credentials")
