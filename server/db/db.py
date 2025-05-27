from sqlalchemy import (
    create_engine, Column, Integer, String, Float, ForeignKey, Date
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# --- DB 설정 ----------------------------
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/up_db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
# ----------------------------------------

# --- 모델 정의 ---------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    nickname = Column(String)
    gpa = Column(Float)
    grade = Column(Integer)  # 학년: 1,2,3,4 등
    status = Column(String)  # 재학생 / 휴학생 (예: "재학", "휴학")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    link = Column(String)
    content = Column(String)
    gpa = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String)      # 재학/휴학 여부
    grade = Column(Integer)      # 대상 학년
# ----------------------------------------

# --- DB 초기화 함수 -----------------------
def init_db():
    Base.metadata.create_all(bind=engine)
# ----------------------------------------
