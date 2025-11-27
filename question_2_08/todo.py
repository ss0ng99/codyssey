# todo.py
from __future__ import annotations

from fastapi import FastAPI, APIRouter, HTTPException
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
import csv

from model import TodoItem  # ← 추가

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


def _save_all_to_csv(items: List[Dict[str, Any]]) -> None:
  _ensure_csv_exists()
  with CSV_FILE.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'title', 'done', 'created_at'])
    writer.writeheader()
    for it in items:
      writer.writerow({
        'id': it['id'],
        'title': it['title'],
        'done': 'True' if it.get('done') else 'False',
        'created_at': it['created_at']
      })


def _find_index_by_id(items: List[Dict[str, Any]], todo_id: str) -> int:
  for idx, it in enumerate(items):
    if it.get('id') == todo_id:
      return idx
  return -1


@router.post('/add')
def add_todo(payload: Dict[str, Any]) -> Dict[str, Any]:
  if not payload:
    raise HTTPException(status_code=400, detail={'warning': '빈 입력입니다. title 등을 포함해 주세요.'})

  title = str(payload.get('title', '')).strip()
  done = bool(payload.get('done', False))

  if not title:
    raise HTTPException(status_code=422, detail={'error': 'title 필드는 필수입니다.'})

  now_id = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
  item: Dict[str, Any] = {
    'id': now_id,
    'title': title,
    'done': done,
    'created_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z'
  }

  todo_list.append(item)
  _append_to_csv(item)

  return {
    'message': 'added',
    'item': item
  }


@router.get('/list')
def retrieve_todo() -> Dict[str, Any]:
  items = _load_from_csv()
  return {'todo_list': items}


# --- 새로 추가된 과제 기능들 ---

@router.get('/{todo_id}')
def get_single_todo(todo_id: str) -> Dict[str, Any]:
  items = _load_from_csv()
  idx = _find_index_by_id(items, todo_id)
  if idx == -1:
    raise HTTPException(status_code=404, detail={'error': '해당 id가 없습니다.'})
  return {'item': items[idx]}


@router.put('/{todo_id}')
def update_todo(todo_id: str, body: TodoItem) -> Dict[str, Any]:
  """
  TodoItem 모델로 전체 필드(title, done) 업데이트.
  id, created_at은 유지.
  """
  global todo_list
  items = _load_from_csv()
  idx = _find_index_by_id(items, todo_id)
  if idx == -1:
    raise HTTPException(status_code=404, detail={'error': '해당 id가 없습니다.'})

  original = items[idx]
  updated: Dict[str, Any] = {
    'id': original['id'],
    'title': body.title.strip(),
    'done': bool(body.done),
    'created_at': original['created_at']
  }

  items[idx] = updated
  todo_list = items[:]  # 메모리 캐시 동기화
  _save_all_to_csv(items)

  return {
    'message': 'updated',
    'item': updated
  }


@router.delete('/{todo_id}')
def delete_single_todo(todo_id: str) -> Dict[str, Any]:
  """
  해당 id 항목 삭제.
  """
  global todo_list
  items = _load_from_csv()
  idx = _find_index_by_id(items, todo_id)
  if idx == -1:
    raise HTTPException(status_code=404, detail={'error': '해당 id가 없습니다.'})

  removed = items.pop(idx)
  todo_list = items[:]
  _save_all_to_csv(items)

  return {
    'message': 'deleted',
    'deleted_id': removed['id']
  }


def create_app() -> FastAPI:
  app = FastAPI(title='Simple TODO API', version='1.1.0')
  global todo_list
  todo_list = _load_from_csv()
  app.include_router(router)

  @app.get('/')
  def root() -> Dict[str, Any]:
    return {
      'message': 'Simple TODO API',
      'endpoints': {
        'list': '/todo/list (GET)',
        'add': '/todo/add (POST)',
        'get_single': '/todo/{id} (GET)',
        'update': '/todo/{id} (PUT)',
        'delete': '/todo/{id} (DELETE)',
        'docs': '/docs'
      }
    }

  return app


app = create_app()

# 실행: uvicorn todo:app --reload
