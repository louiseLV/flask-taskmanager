# tests/test_unit.py
from datetime import date, timedelta
from app import _build_postgres_uri
from models import Task, User


def test_task_is_overdue_when_due_date_in_past_and_not_completed():
    task = Task(
        title="Test overdue",
        user_id=1,
        due_date=date.today() - timedelta(days=1),
        is_completed=False,
    )

    assert task.is_overdue() is True


def test_task_is_not_overdue_when_completed_or_no_due_date():
    past_date = date.today() - timedelta(days=1)

    completed_task = Task(
        title="Completed",
        user_id=1,
        due_date=past_date,
        is_completed=True,
    )

    no_due_date_task = Task(
        title="No due date",
        user_id=1,
        due_date=None,
        is_completed=False,
    )

    assert completed_task.is_overdue() is False
    assert no_due_date_task.is_overdue() is False


def test_user_set_and_check_password():
    user = User(username="alice")
    user.set_password("secret123")

    assert user.password_hash is not None
    assert user.password_hash != "secret123"

    assert user.check_password("secret123") is True
    assert user.check_password("wrongpassword") is False


def test_build_postgres_uri_uses_database_url_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@h:1234/dbname")

    uri = _build_postgres_uri()

    assert uri == "postgresql+psycopg://u:p@h:1234/dbname"


def test_build_postgres_uri_builds_from_postgres_env_vars(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    monkeypatch.setenv("POSTGRES_USER", "myuser")
    monkeypatch.setenv("POSTGRES_PASSWORD", "mypass")
    monkeypatch.setenv("POSTGRES_HOST", "myhost")
    monkeypatch.setenv("POSTGRES_PORT", "5555")
    monkeypatch.setenv("POSTGRES_DB", "mydb")

    uri = _build_postgres_uri()

    assert uri == "postgresql+psycopg2://myuser:mypass@myhost:5555/mydb"
