
import pytest

from app import create_app
from app.config import Config
from app.extensions import db

TEST_JWT_SECRET = "clave-jwt-solo-para-pruebas-0123456789"


@pytest.fixture
def app(monkeypatch):

    # Evitamos conectarnos a PostgreSQL
    monkeypatch.setattr(
        Config,
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///:memory:"
    )

    # Clave JWT exclusiva para pruebas
    monkeypatch.setattr(
        Config,
        "JWT_SECRET_KEY",
        TEST_JWT_SECRET
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
def auth_headers(app):
    from flask_jwt_extended import create_access_token

    token = create_access_token(identity="pytest")
    return {
        "Authorization": f"Bearer {token}"
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
