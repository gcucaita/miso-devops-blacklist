"""Pruebas unitarias del endpoint GET /blacklists/{email}."""
from datetime import timedelta

from flask_jwt_extended import create_access_token


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


def test_get_email_en_mayusculas(
    client, auth_headers, valid_payload
):
    client.post(
        "/blacklists",
        json=valid_payload,
        headers=auth_headers
    )

    response = client.get(
        "/blacklists/USUARIO@Empresa.COM",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json["is_blacklisted"] is True
    assert response.json["email"] == "usuario@empresa.com"


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


def test_invalid_get_email(client, auth_headers):
    response = client.get(
        "/blacklists/correo-invalido",
        headers=auth_headers
    )

    assert response.status_code == 400


def test_get_without_token(client):
    response = client.get(
        "/blacklists/usuario@empresa.com"
    )

    assert response.status_code == 401


def test_token_expirado(client, app):
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
