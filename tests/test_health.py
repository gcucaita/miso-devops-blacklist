"""Pruebas unitarias del endpoint GET /health."""
from app.version import APP_VERSION


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert response.json["service"] == "blacklist-microservice"


def test_health_devuelve_version_desplegada(client):
    response = client.get("/health")

    assert response.json["version"] == APP_VERSION


def test_health_no_requiere_token(client, app):
    # El balanceador consulta /health sin Authorization:
    # aunque falte la clave JWT, no debe responder 401 ni 503.
    app.config["JWT_SECRET_KEY"] = None

    response = client.get("/health")

    assert response.status_code == 200
