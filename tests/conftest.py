
import pytest

from app import create_app
from app.config import Config
from app.extensions import db


@pytest.fixture
def app(monkeypatch):

    # Evitamos conectarnos a PostgreSQL
    monkeypatch.setattr(
        Config,
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///:memory:"
    )

    # Token exclusivo para pruebas
    monkeypatch.setenv(
        "API_TOKEN",
        "test-token-devops-123"
    )

    application = create_app()
    application.config.update(
        TESTING=True
    )

    with application.app_context():
        db.create_all()

        yield application

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    return {
        "Authorization": "Bearer test-token-devops-123"
    }


@pytest.fixture
def valid_payload():
    return {
        "email": "usuario@empresa.com",
        "app_uuid": (
            "550e8400-e29b-41d4-a716-446655440000"
        ),
        "blocked_reason": "Actividad sospechosa"
    }
