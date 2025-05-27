from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.db import SessionLocal, Document

doc_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
