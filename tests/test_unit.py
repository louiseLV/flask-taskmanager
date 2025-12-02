import pytest
from datetime import date, timedelta
from models import Task, User
from app import _build_postgres_uri

def test_task_is_overdue():
    task = Task(due_date=date.today() - timedelta(days=1))
    assert task.is_overdue() is True

    task_future = Task(due_date=date.today() + timedelta(days=1))
    assert task_future.is_overdue() is False

    task_none = Task(due_date=None)
    assert task_none.is_overdue() is False

    task_done = Task(due_date=date.today() - timedelta(days=5))
    task_done.is_completed = True
    assert task_done.is_overdue() is False

def test_user_password():
    user = User()
    user.set_password("secret")
    assert user.check_password("secret") is True
    assert user.check_password("wrong") is False

def test_build_postgres_uri(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "louiselavergne")
    monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
    uri = _build_postgres_uri()
    assert "louiselavergne" in uri
    assert "pass" in uri
