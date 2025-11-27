# model.py
from __future__ import annotations

from pydantic import BaseModel


class TodoItem(BaseModel):
  title: str
  done: bool = False
