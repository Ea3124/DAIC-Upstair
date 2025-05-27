from fastapi import Query
from typing import Optional, List

@doc_router.get("/documents/filter")
def filter_documents(
    min_gpa: Optional[float] = Query(None),
    grade: Optional[int] = Query(None),
    status: Optional[str] = Query(None),  # "재학" 또는 "휴학"
    db: Session = Depends(get_db)
):
    query = db.query(Document)

    if min_gpa is not None:
        query = query.filter(Document.gpa >= min_gpa)
    if grade is not None:
        query = query.filter(Document.grade == grade)
    if status is not None:
        query = query.filter(Document.status == status)

    docs = query.all()
    return [{"title": d.title, "link": d.link} for d in docs]
