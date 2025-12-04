# domain/question/question_router.py
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Question
from domain.question.schemas import QuestionRead

router = APIRouter(prefix='/api/question', tags=['question'])


@router.get('', response_model=List[QuestionRead])
def question_list(db: Session = Depends(get_db)):
    rows = db.query(Question).order_by(Question.id.desc()).all()
    return rows
