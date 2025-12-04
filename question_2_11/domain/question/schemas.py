# domain/question/schemas.py
from datetime import datetime
from pydantic import BaseModel

class QuestionRead(BaseModel):
  id: int
  subject: str
  content: str
  create_date: datetime

  class Config:
    # Pydantic v2: SQLAlchemy ORM 객체 → 스키마 변환 허용
    from_attributes = True

    # (보너스 실험) v1 스타일:
    # orm_mode = True
