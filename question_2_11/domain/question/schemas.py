# domain/question/schemas.py
from datetime import datetime
from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    subject: str = Field(min_length=1)
    content: str = Field(min_length=1)


class QuestionRead(BaseModel):
    id: int
    subject: str
    content: str
    create_date: datetime

    class Config:
        from_attributes = True
