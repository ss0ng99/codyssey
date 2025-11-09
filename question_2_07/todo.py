# 가상환경 생성/활성화
# python3 -m venv .venv


# todo.py
from __future__ import annotations

from fastapi import FastAPI, APIRouter, HTTPException
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
import csv

# CSV 파일 경로와 메모리 캐시 리스트
CSV_FILE = Path('todo_data.csv')
todo_list: List[Dict[str, Any]] = []

router = APIRouter(prefix='/todo', tags=['todo'])


def _ensure_csv_exists() -> None:
  if not CSV_FILE.exists():
    with CSV_FILE.open('w', newline='') as f:
      writer = csv.DictWriter(f, fieldnames=['id', 'title', 'done', 'created_at'])
      writer.writeheader()


def _load_from_csv() -> List[Dict[str, Any]]:
  _ensure_csv_exists()
  items: List[Dict[str, Any]] = []
  with CSV_FILE.open('r', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
      # CSV는 문자열이므로 타입 보정
      items.append({
        'id': row.get('id', ''),
        'title': row.get('title', ''),
        'done': row.get('done', 'False') in ('True', 'true', '1'),
        'created_at': row.get('created_at', '')
      })
  return items


def _append_to_csv(item: Dict[str, Any]) -> None:
  _ensure_csv_exists()
  with CSV_FILE.open('a', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'title', 'done', 'created_at'])
    writer.writerow({
      'id': item['id'],
      'title': item['title'],
      'done': 'True' if item.get('done') else 'False',
      'created_at': item['created_at']
    })


@router.post('/add')
def add_todo(payload: Dict[str, Any]) -> Dict[str, Any]:
  # 보너스: 빈 입력 처리
  if not payload:
    raise HTTPException(status_code=400, detail={'warning': '빈 입력입니다. title 등을 포함해 주세요.'})

  title = str(payload.get('title', '')).strip()
  done = bool(payload.get('done', False))

  if not title:
    raise HTTPException(status_code=422, detail={'error': 'title 필드는 필수입니다.'})

  # 간단한 id 생성: 타임스탬프 기반
  now = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
  item: Dict[str, Any] = {
    'id': now,
    'title': title,
    'done': done,
    'created_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z'
  }

  # 메모리/CSV 동시 반영
  todo_list.append(item)
  _append_to_csv(item)

  return {
    'message': 'added',
    'item': item
  }


@router.get('/list')
def retrieve_todo() -> Dict[str, Any]:
  # 최신 CSV를 읽어 반환 (동시성 단순화)
  items = _load_from_csv()
  return {'todo_list': items}


def create_app() -> FastAPI:
  app = FastAPI(title='Simple TODO API', version='1.0.0')
  # 시작 시 CSV → 메모리 캐시 적재
  global todo_list
  todo_list = _load_from_csv()
  app.include_router(router)
  return app


app = create_app()

# 로컬 실행 시:
# uvicorn todo:app --reload
