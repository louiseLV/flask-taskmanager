import pytest
import uuid
from app import create_app, db


@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_login_and_create_task(client):
    username = "user_" + str(uuid.uuid4())[:8]
    password = "secret"

    response = client.post(
        "/register",
        data={"username": username, "password": password, "confirm": password},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    response = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Logged in successfully" in response.data

    response = client.post(
        "/tasks/new",
        data={"title": "Test Task", "description": "Integration test task"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Task created" in response.data
    assert b"Test Task" in response.data
