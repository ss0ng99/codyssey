#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from urllib import request, error
from typing import Any, Dict, Optional


API_BASE = 'http://127.0.0.1:8000'
TODO_PREFIX = '/todo'


def _url(path: str) -> str:
  if not path.startswith('/'):
    path = '/' + path
  return API_BASE + path


def _http(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
  url = _url(path)
  data: Optional[bytes] = None
  headers = {
    'Content-Type': 'application/json'
  }
  if body is not None:
    data = json.dumps(body).encode('utf-8')
  req = request.Request(url=url, data=data, method=method, headers=headers)
  try:
    with request.urlopen(req) as resp:
      text = resp.read().decode('utf-8')
      if not text:
        return {'status': resp.status, 'data': None}
      return {'status': resp.status, 'data': json.loads(text)}
  except error.HTTPError as e:
    try:
      detail = e.read().decode('utf-8')
      parsed = json.loads(detail) if detail else {'detail': 'HTTPError'}
    except Exception:
      parsed = {'detail': 'HTTPError'}
    return {'status': e.code, 'error': parsed}
  except error.URLError as e:
    return {'status': 0, 'error': {'detail': f'Connection failed: {e.reason}'}}
  except Exception as e:
    return {'status': 0, 'error': {'detail': str(e)}}


def list_todos() -> None:
  res = _http('GET', f'{TODO_PREFIX}/list')
  _print_response(res)


def add_todo() -> None:
  title = input('title: ').strip()
  done_str = input('done? [y/N]: ').strip().lower()
  done = done_str in ('y', 'yes', '1', 'true')
  payload: Dict[str, Any] = {'title': title, 'done': done}
  res = _http('POST', f'{TODO_PREFIX}/add', payload)
  _print_response(res)


def get_single() -> None:
  todo_id = input('id: ').strip()
  res = _http('GET', f'{TODO_PREFIX}/{todo_id}')
  _print_response(res)


def update_todo() -> None:
  todo_id = input('id: ').strip()
  title = input('new title: ').strip()
  done_str = input('done? [y/N]: ').strip().lower()
  done = done_str in ('y', 'yes', '1', 'true')
  payload: Dict[str, Any] = {'title': title, 'done': done}
  res = _http('PUT', f'{TODO_PREFIX}/{todo_id}', payload)
  _print_response(res)


def delete_todo() -> None:
  todo_id = input('id: ').strip()
  res = _http('DELETE', f'{TODO_PREFIX}/{todo_id}')
  _print_response(res)


def _print_response(res: Dict[str, Any]) -> None:
  status = res.get('status', 0)
  print(f'\n[status] {status}')
  if 'data' in res:
    _pretty(res['data'])
  if 'error' in res:
    print('[error]')
    _pretty(res['error'])
  print()


def _pretty(obj: Any) -> None:
  try:
    print(json.dumps(obj, ensure_ascii=False, indent=2))
  except Exception:
    print(obj)


def menu() -> None:
  print('--- Simple TODO Client ---')
  print(f'API: {API_BASE}')
  print('1) List')
  print('2) Add')
  print('3) Get single')
  print('4) Update')
  print('5) Delete')
  print('0) Exit')


def main() -> None:
  # 옵션: 서버 주소를 인자로 바꾸고 싶다면
  # 사용법: python client.py http://127.0.0.1:8000
  global API_BASE
  if len(sys.argv) >= 2:
    API_BASE = sys.argv[1].rstrip('/')

  actions = {
    '1': list_todos,
    '2': add_todo,
    '3': get_single,
    '4': update_todo,
    '5': delete_todo
  }

  while True:
    menu()
    choice = input('Select: ').strip()
    if choice == '0':
      print('bye.')
      return
    action = actions.get(choice)
    if action is None:
      print('invalid selection.\n')
      continue
    action()


if __name__ == '__main__':
  main()
