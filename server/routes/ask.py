from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.db import SessionLocal, Document
from pydantic import BaseModel
from typing import Optional
from datetime import date
from utils.function_calling import  filter_documents_api, run_conversation, ask_llm
from utils.chat import RAG_chat, make_vectorstore
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from openai import OpenAI
import os
from pathlib import Path
from simple_fastapi_auth import UPSTAGE_API_KEY, UpstageEmbeddings
import json
load_dotenv()
api_key = os.getenv("UPSTAGE_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.upstage.ai/v1")
VECTOR_DIR = Path("./faiss_index")
embeddings = UpstageEmbeddings(
    model="solar-embedding-1-large",
    upstage_api_key=UPSTAGE_API_KEY,
)
ask_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AskRequest(BaseModel):
    question: str

@ask_router.post("/ask/database")
def ask(req: AskRequest, db: Session = Depends(get_db)):
    response = run_conversation(req.question, top_k=3, db=db)
    if not response:
        vector_store = FAISS.load_local(str(VECTOR_DIR), embeddings, allow_dangerous_deserialization=True,)
        responses = ask_llm(req.question, vectorstore=vector_store, top_k=10)
        responses = [r.metadata for r in responses]
        print(responses)
        unique_titles = set()
        response = []
        for res in responses:
            if res["notice_title"] not in unique_titles:
                unique_titles.add(res["notice_title"])
                response.append({"notice_title": res["notice_title"], "file_name": res["file_name"], "url": res["url"]})
        return json.dumps(response, ensure_ascii=False)
    else:
        return response