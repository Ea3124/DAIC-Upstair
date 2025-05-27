from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.db import SessionLocal, Document
from pydantic import BaseModel
from typing import Optional
from datetime import date

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