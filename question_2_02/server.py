#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import os

HOST = '0.0.0.0'
PORT = 8080
INDEX_FILE = 'index.html'
ENCODING = 'utf-8'


def now_str() -> str:
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def index_abs_path() -> str:
  base_dir = os.path.dirname(os.path.abspath(__file__))
  return os.path.join(base_dir, INDEX_FILE)


class AssignmentHandler(BaseHTTPRequestHandler):
  server_version = 'SpacePirateHTTP/1.0'

  def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler 관례 유지)
    self._log_access()

    if self.path in ('/', '/index', '/index.html'):
      self._send_index()
      return

    self._send_not_found()

  def _log_access(self) -> None:
    ip, _ = self.client_address
    print(f'[ACCESS] time={now_str()} ip={ip}')

  def _send_index(self) -> None:
    path = index_abs_path()
    if not os.path.exists(path):
      body = (
        '<!doctype html><meta charset="utf-8">'
        '<title>Server Error</title>'
        '<h1>500 - index.html not found</h1>'
      ).encode(ENCODING)
      self.send_response(500)
      self.send_header('Content-Type', f'text/html; charset={ENCODING}')
      self.send_header('Content-Length', str(len(body)))
      self.end_headers()
      self.wfile.write(body)
      return

    with open(path, 'rb') as f:
      body = f.read()

    self.send_response(200)
    self.send_header('Content-Type', f'text/html; charset={ENCODING}')
    self.send_header('Content-Length', str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def _send_not_found(self) -> None:
    body = (
      '<!doctype html><meta charset="utf-8">'
      '<title>Not Found</title>'
      '<h1>404 - Not Found</h1>'
    ).encode(ENCODING)
    self.send_response(404)
    self.send_header('Content-Type', f'text/html; charset={ENCODING}')
    self.send_header('Content-Length', str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def log_message(self, format: str, *args) -> None:  # 기본 access 로그 억제(선택)
    return


def main() -> None:
  httpd = HTTPServer((HOST, PORT), AssignmentHandler)
  print(f'[START] {now_str()} bind={HOST}:{PORT}')
  print('[INFO] Open a browser: http://localhost:8080/')
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    print('\n[SHUTDOWN] KeyboardInterrupt received.')
  finally:
    httpd.server_close()
    print('[STOP] Server closed.')


if __name__ == '__main__':
  main()
