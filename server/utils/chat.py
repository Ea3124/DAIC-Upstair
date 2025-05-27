from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_upstage import UpstageEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from typing import List, Dict, Any, Optional


from openai import OpenAI # openai==1.52.2
from dotenv import load_dotenv
import os
load_dotenv()

client = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1"
)
dim_size = 4096

def make_prompt(question: str, search_result: List[str], messages: List[Dict[str, str]]) -> str:
    prompt = f"""
    You are a helpful assistant that can answer questions and help with tasks.
    You are given a question, a search result, and a conversation history.
    Use the search result to answer the question.
    answer concisely and in Korean.
    Question:
    {question}"""
    if search_result:
        for i, result in enumerate(search_result):
            prompt += f"""
            Search result {i+1}:
            {result}"""
    if messages:
        prompt += f"""
        Conversation history:
        {messages}
        answer in Korean."""
    return prompt

def chat_with_solar(question: str, search_result: List[str], messages: List[Dict[str, str]]) -> str:
    """
    args:
        question: 질문(str)
        search_result: 검색 결과(str)
        messages: 대화 기록(list)
    returns: 
        response: 응답(str)
    """
    prompt = make_prompt(question, search_result, messages)
    response = client.chat.completions.create(
        model="solar-pro",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
 
def RAG_chat(question: str, vectorstore: FAISS, top_k: int = 3, messages: Optional[List[Dict[str, str]]] = [], use_history: bool = False) -> str:
    """
    args:
        question: 질문(str)
        vectorstore: 벡터 저장소(FAISS)
        top_k: 검색 결과 개수(int)
        messages: 대화 기록(list)
        use_history: 대화 기록 사용 여부(bool)
    returns: 
        response: 응답(str)
    """
    search_result = vectorstore.similarity_search(question, k=top_k)
    response = chat_with_solar(question, search_result, messages)
    if use_history:
        if messages:
            messages.append({"role": "user", "content": question})
            messages.append({"role": "assistant", "content": response})
        else:
            messages = [{"role": "user", "content": question}, {"role": "assistant", "content": response}]
    return response

if __name__ == "__main__":

    # 쿼리 전용 임베딩 모델
    query_embeddings = UpstageEmbeddings(model="solar-embedding-1-large-query")

    # 문장 전용 임베딩 모델
    passage_embeddings = UpstageEmbeddings(model="solar-embedding-1-large-passage")

    vectorstore = FAISS(
        embedding_function=query_embeddings,
        index=faiss.IndexFlatL2(dim_size),
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
        distance_strategy=DistanceStrategy.COSINE
    )

    vectorstore.add_texts(
        # 장학금 관련 예시 문장들
        texts=[
            "2023년 봄학기 장학금 신청이 시작되었습니다. 신청 마감일은 3월 15일입니다.",
            "우수 학생을 위한 특별 장학금 프로그램이 개설되었습니다. 지원 자격은 GPA 3.5 이상입니다.",
            "신입생을 위한 장학금 신청이 가능합니다. 자세한 사항은 학교 웹사이트를 참조하세요.",
            "해외 유학 장학금 신청이 시작되었습니다. 지원 마감일은 4월 1일입니다.",
            "과학 전공 학생을 위한 장학금이 마련되었습니다. 신청 마감일은 5월 10일입니다.",
            "예술 전공 학생을 위한 장학금이 개설되었습니다. 포트폴리오 제출이 필요합니다.",
            "경제적 지원이 필요한 학생을 위한 장학금이 있습니다. 신청 마감일은 6월 30일입니다.",
            "여름학기 장학금 신청이 가능합니다. 지원 마감일은 7월 15일입니다.",
            "장애 학생을 위한 특별 장학금이 마련되었습니다. 자세한 사항은 학생 지원 센터에 문의하세요.",
            "지역 사회 봉사 활동을 위한 장학금이 있습니다. 신청 마감일은 8월 20일입니다."
        ],
        embedding=passage_embeddings
    )

    # First turn
    history = []
    question = "과학 장학금 신청 마감일은 언제인가요?"
    response = RAG_chat(question, vectorstore, use_history=True, top_k=1)
    print("Assistant:", response)
    # history.append({"role": "user", "content": question})
    # history.append({"role": "assistant", "content": response})

    # Second turn
    question = "우수 학생을 위한 특별 장학금 지원 자격은 무엇인가요?"
    response = RAG_chat(question, vectorstore, use_history=True, top_k=1)
    print("Assistant:", response)
    # history.append({"role": "user", "content": question})
    # history.append({"role": "assistant", "content": response})

    # Third turn
    question = "해외 유학 장학금 신청 마감일은 언제인가요?"
    response = RAG_chat(question, vectorstore, use_history=True, top_k=1)
    print("Assistant:", response)