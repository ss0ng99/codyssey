# domain/question/question_router.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Question


router = APIRouter(
    prefix='/api/question',
    tags=['question']
)


class QuestionRead(BaseModel):
    id: int
    subject: str
    content: str
    create_date: datetime

    class Config:
        from_attributes = True  # SQLAlchemy ORM 객체 직렬화 허용


@router.get('', response_model=List[QuestionRead])
def question_list(db: Session = Depends(get_db)):
    rows = db.query(Question).order_by(Question.id.desc()).all()
    return rows
