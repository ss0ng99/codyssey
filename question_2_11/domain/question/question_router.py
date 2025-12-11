# domain/question/question_router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Question
from domain.question.schemas import QuestionRead, QuestionCreate

router = APIRouter(prefix='/api/question', tags=['question'])


@router.get('', response_model=List[QuestionRead])
def question_list(db: Session = Depends(get_db)):
    rows = db.query(Question).order_by(Question.id.desc()).all()
    return rows


@router.post('', response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def question_create(payload: QuestionCreate, db: Session = Depends(get_db)):
    # ORM 객체 생성
    obj = Question(
        subject=payload.subject,
        content=payload.content,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
