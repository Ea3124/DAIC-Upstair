from openai import OpenAI  # openai==1.52.2
import json
from dotenv import load_dotenv
import os
load_dotenv()
from utils.chat import RAG_chat, make_vectorstore
from langchain_community.vectorstores import FAISS
from db.db import SessionLocal, Document
api_key = os.getenv("UPSTAGE_API_KEY")
import requests
from typing import List, Dict, Optional
API_BASE_URL = "http://localhost:8000"

client = OpenAI(
    api_key=api_key,
    base_url="https://api.upstage.ai/v1"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ask_llm(question: str, vectorstore: FAISS, top_k: int):
    return RAG_chat(question, vectorstore, top_k=top_k)

def filter_documents_api(min_gpa: Optional[float] = None, 
                         grade: Optional[int] = None, 
                         status: Optional[str] = None,):
    params = {}
    if min_gpa is not None:
        params["min_gpa"] = min_gpa
    if grade is not None:
        params["grade"] = grade
    if status is not None:
        params["status"] = status
    response = requests.get(f"{API_BASE_URL}/documents/filter", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to filter documents: {response.status_code} {response.text}")


# Step 2: Send the query and available functions to the model
def run_conversation(question: str, *args, **kwargs):
    vectorstore = kwargs.get("vectorstore")
    db = kwargs.get("db")
    top_k = kwargs.get("top_k")
    messages = [
        {
            "role": "user",
            "content": question,
        }
    ]
    print(f"messages: {messages}")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "filter_documents_api",
                "description": "질문에 맞는 데이터베이스 출력을 만드는 함수",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_gpa": {
                            "type": "number",
                            "description": "GPA 조건",
                        },
                        "grade": {
                            "type": "integer",
                            "description": "학년 조건",
                        },
                        "status": {
                            "type": "string",
                            "description": "재학 상태 조건 (재학 또는 휴학)",
                            "enum": ["재학", "휴학"]
                        },
                        "db": {
                            "type": "object",
                            "description": "데이터베이스",
                        }
                    },
                    "required": ["db"],
                },
            },
        },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "ask_llm",
        #         "description": "벡터 저장소에 저장된 데이터를 참고하여 질문에 대한 답변을 생성하는 쿼리 내장 함수",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "question": {
        #                     "type": "string",
        #                     "description": "질문",
        #                 },
        #                 "vectorstore": {
        #                     "type": "object",
        #                     "description": "벡터 저장소",
        #                 },
        #             },
        #             "required": ["question", "vectorstore"],
        #         },
        #     },
        # }
    ]
 
    # Step 3: Check if the model has requested a function call
    # The model identifies that the query requires external data (e.g., real-time weather) and decides to call a relevant function, such as a weather API.
    response = client.chat.completions.create(
        model="solar-pro",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
 
    # Step 4: Execute the function call
    # The JSON response from the model may not always be valid, so handle errors appropriately
    if tool_calls:
        available_functions = {
            "filter_documents_api": filter_documents_api,
            # "ask_llm": ask_llm,
        }  # You can define multiple functions here as needed
        messages.append(response_message)  # Add the assistant's reply to the conversation history
 
        # Step 5: Process each function call and provide the results to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            # 함수에 따른 인자 전달
            if function_name == "filter_documents_api":
                function_response = function_to_call(
                    min_gpa=function_args.get("min_gpa"),
                    grade=function_args.get("grade"),
                    status=function_args.get("status"),
                )
                return function_response
            elif function_name == "ask_llm":
                function_response = function_to_call(
                    question=function_args.get("question"),
                    vectorstore=vectorstore,
                    top_k=top_k
                )
                return function_response
            else:
                raise Exception(f"Unknown function: {function_name}")
            
if __name__ == "__main__":
    vectorstore = make_vectorstore()
    question = "GPA 3.9 이상인 학생은 어떤 장학금을 받을 수 있나요?"
    #question = "예술 전공 학생은 장학금을 어떻게 받을 수 있나요?"
    response = run_conversation(question, vectorstore)
    print(response.choices[0].message.content)