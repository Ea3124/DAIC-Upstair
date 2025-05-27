from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.db import SessionLocal, Document
from pydantic import BaseModel
from typing import Optional
from datetime import date
from utils.function_calling import  filter_documents_api, run_conversation
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
    return response