# database.py
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite:///./app.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False}
)

# 과제 조건: autocommit = False
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logging.basicConfig(level=logging.INFO, format='[DB] %(message)s')


@contextmanager
def db_context():
    db = SessionLocal()
    logging.info('open session')
    try:
        yield db
    finally:
        db.close()
        logging.info('close session')


def get_db():
    # FastAPI가 이해할 수 있는 yield 의존성으로 감싸기
    with db_context() as db:
        yield db
