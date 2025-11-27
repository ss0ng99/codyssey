# main.py
from fastapi import FastAPI
from domain.question.router import router as question_router

app = FastAPI(
    title='Board API',
    description='Simple Q&A board with FastAPI + SQLAlchemy + Alembic + SQLite',
    version='0.1.0'
)

# 라우터 등록
app.include_router(question_router)

# 헬스 체크용 루트
@app.get('/')
def read_root():
    return {'message': 'ok'}
