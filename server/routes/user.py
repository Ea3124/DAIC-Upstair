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

@user_router.get("/user/{email}")
def get_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "email": user.email,
        "nickname": user.nickname,
        "gpa": user.gpa,
        "grade": user.grade,
        "status": user.status
    }


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

@user_router.post("/user/sample")
def create_sample_users(db: Session = Depends(get_db)):
    sample_users = [
        {
            "email": "test1@example.com",
            "password": "1234",
            "nickname": "이승재",
            "gpa": 4.1,
            "grade": 3,
            "status": "재학"
        },
        {
            "email": "test2@example.com",
            "password": "1234",
            "nickname": "박준혁",
            "gpa": 4.5,
            "grade": 2,
            "status": "재학"
        },
        {
            "email": "test3@example.com",
            "password": "1234",
            "nickname": "김정희",
            "gpa": 3.9,
            "grade": 1,
            "status": "휴학"
        },
        {
            "email": "test4@example.com",
            "password": "1234",
            "nickname": "금비",
            "gpa": 3.9,
            "grade": 4,
            "status": "재학"
        },
        {
            "email": "test5@example.com",
            "password": "1234",
            "nickname": "이병찬",
            "gpa": 3.9,
            "grade": 3,
            "status": "휴학"
        },
    ]

    added_count = 0
    for u in sample_users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            continue
        new_user = User(**u)
        db.add(new_user)
        added_count += 1

    db.commit()
    return {"success": True, "added_users": added_count}
