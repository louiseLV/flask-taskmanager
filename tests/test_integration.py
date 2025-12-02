import pytest
from app import create_app
from models import Task


@pytest.fixture
def client():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.test_client() as client:
        yield client


def register(client, username="alice", password="secret"):
    return client.post(
        "/register",
        data={
            "username": username,
            "password": password,
            "confirm": password,
        },
        follow_redirects=True,
    )


def login(client, username="alice", password="secret"):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )


def test_register_and_login(client):
    resp = register(client)
    assert b"Registration successful" in resp.data

    resp = login(client)
    assert b"Logged in successfully" in resp.data


def test_create_task(client):
    register(client)
    login(client)

    resp = client.post(
        "/tasks/new",
        data={
            "title": "Test task",
            "description": "Do something",
            "due_date": "2025-12-31",
        },
        follow_redirects=True,
    )

    assert b"Task created" in resp.data

    with client.application.app_context():
        task = Task.query.first()
        assert task is not None
        assert task.title == "Test task"


def test_toggle_task(client):
    register(client)
    login(client)

    client.post(
        "/tasks/new",
        data={
            "title": "Toggle me",
            "description": "",
        },
        follow_redirects=True,
    )

    with client.application.app_context():
        task = Task.query.first()
        task_id = task.id

    resp = client.post(f"/tasks/{task_id}/toggle", follow_redirects=True)
    assert b"Task status updated" in resp.data

    with client.application.app_context():
        task = Task.query.get(task_id)
        assert task.is_completed is True
