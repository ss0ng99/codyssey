# domain/question/router.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import Question

router = APIRouter(prefix='/questions', tags=['questions'])


# 요청/응답 스키마 (간단 버전)
class QuestionCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class QuestionRead(BaseModel):
    id: int
    subject: str
    content: str
    create_date: datetime

    class Config:
        from_attributes = True


@router.post('', response_model=QuestionRead, status_code=201)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    obj = Question(
        subject=payload.subject,
        content=payload.content
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get('', response_model=List[QuestionRead])
def list_questions(db: Session = Depends(get_db)):
    rows = db.query(Question).order_by(Question.id.desc()).all()
    return rows


@router.get('/{question_id}', response_model=QuestionRead)
def get_question(question_id: int, db: Session = Depends(get_db)):
    obj = db.query(Question).get(question_id)
    if obj is None:
        raise HTTPException(status_code=404, detail='Question not found')
    return obj
