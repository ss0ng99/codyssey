# main.py
from fastapi import FastAPI
from domain.question.question_router import router as question_router

app = FastAPI(title='Board API')

# 라우터 등록 (과제 조건: include_router 사용)
app.include_router(question_router)


@app.get('/')
def health():
    return {'message': 'ok'}
