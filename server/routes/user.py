# user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.db import SessionLocal, User

user_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserUpdateRequest(BaseModel):
    email: str  # 수정 대상 사용자
    gpa: float
    grade: int
    status: str  # "재학" 또는 "휴학"

@user_router.put("/user/update")
def update_user(req: UserUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.gpa = req.gpa
    user.grade = req.grade
    user.status = req.status
    db.commit()
    return {"success": True, "message": "User updated"}
