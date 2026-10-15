
import uuid

from app.extensions import db
from app.models.blacklist import Blacklist


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert "version" in response.json


def test_create_blacklist(
    client, auth_headers, valid_payload
):
    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json["data"]["email"] == (
        "usuario@empresa.com"
    )


def test_blacklist_persisted(
    client, app, auth_headers, valid_payload
):
    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    assert response.status_code == 201

    with app.app_context():
        record = db.session.execute(
            db.select(Blacklist).filter_by(
                email="usuario@empresa.com"
            )
        ).scalar_one_or_none()

        assert record is not None
        assert record.blocked_reason == (
            "Actividad sospechosa"
        )
        assert record.request_ip == "127.0.0.1"
        assert record.app_uuid == uuid.UUID(
            valid_payload["app_uuid"]
        )
        assert record.created_at is not None


def test_get_existing_email(
    client, auth_headers, valid_payload
):
    client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    response = client.get(
        "/blacklists/usuario@empresa.com",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json["is_blacklisted"] is True
    assert response.json["blocked_reason"] == (
        "Actividad sospechosa"
    )


def test_get_nonexistent_email(
    client, auth_headers
):
    response = client.get(
        "/blacklists/noexiste@empresa.com",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json["is_blacklisted"] is False
    assert response.json["blocked_reason"] is None


def test_duplicate_email(
    client, auth_headers, valid_payload
):
    first = client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    second = client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_invalid_email(
    client, auth_headers, valid_payload
):
    valid_payload["email"] = "correo-invalido"

    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    assert response.status_code == 400


def test_missing_uuid(
    client, auth_headers, valid_payload
):
    del valid_payload["app_uuid"]

    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    assert response.status_code == 400


def test_invalid_uuid(
    client, auth_headers, valid_payload
):
    valid_payload["app_uuid"] = "uuid-invalido"

    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    assert response.status_code == 400


def test_reason_too_long(
    client, auth_headers, valid_payload
):
    valid_payload["blocked_reason"] = "X" * 256

    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    assert response.status_code == 400


def test_optional_reason(
    client, auth_headers, valid_payload
):
    del valid_payload["blocked_reason"]

    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json["data"]["blocked_reason"] is None


def test_post_without_token(client, valid_payload):
    response = client.post(
        "/blacklists",
        json=valid_payload
    )

    assert response.status_code == 401


def test_get_without_token(client):
    response = client.get(
        "/blacklists/usuario@empresa.com"
    )

    assert response.status_code == 401


def test_invalid_token(client, valid_payload):
    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers={
            "Authorization": "Bearer wrong-token"
        }
    )

    assert response.status_code == 401


def test_invalid_get_email(client, auth_headers):
    response = client.get(
        "/blacklists/correo-invalido",
        headers=auth_headers
    )

    assert response.status_code == 400


def test_malformed_json(client, auth_headers):
    response = client.post(
        "/blacklists",
        data='{"email":',
        content_type="application/json",
        headers=auth_headers
    )

    assert response.status_code == 400


def test_unsupported_media_type(client, auth_headers):
    response = client.post(
        "/blacklists",
        data="email=usuario@empresa.com",
        content_type="text/plain",
        headers=auth_headers
    )

    assert response.status_code == 415


def test_token_firmado_con_otra_clave(client, valid_payload):
    import jwt as pyjwt

    forged = pyjwt.encode(
        {"sub": "atacante", "type": "access", "fresh": False,
         "jti": "x", "iat": 0, "nbf": 0},
        "otra-clave-que-no-es-la-del-servicio-123456",
        algorithm="HS256"
    )

    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers={"Authorization": f"Bearer {forged}"}
    )

    assert response.status_code == 401


def test_token_expirado(client, app, valid_payload):
    from datetime import timedelta
    from flask_jwt_extended import create_access_token

    with app.app_context():
        expired = create_access_token(
            identity="pytest",
            expires_delta=timedelta(seconds=-10)
        )

    response = client.get(
        "/blacklists/usuario@empresa.com",
        headers={"Authorization": f"Bearer {expired}"}
    )

    assert response.status_code == 401


def test_esquema_distinto_a_bearer(client, app):
    from flask_jwt_extended import create_access_token

    with app.app_context():
        token = create_access_token(identity="pytest")

    response = client.get(
        "/blacklists/usuario@empresa.com",
        headers={"Authorization": f"Token {token}"}
    )

    assert response.status_code == 401


def test_sin_clave_configurada_responde_503(client, app, auth_headers):
    app.config["JWT_SECRET_KEY"] = None

    response = client.get(
        "/blacklists/usuario@empresa.com",
        headers=auth_headers
    )

    assert response.status_code == 503
