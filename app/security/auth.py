from functools import wraps

from flask import current_app
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError

UNAUTHORIZED_BODY = {"error": "Token ausente o invalido."}
UNAUTHORIZED_HEADERS = {"WWW-Authenticate": 'Bearer realm="blacklists"'}


def require_bearer_token(func):
    """Exige un JWT válido (Flask-JWT-Extended) en "Authorization: Bearer <jwt>".

    Responde 401 si el token falta, está mal formado, expiró o fue firmado
    con otra clave, y 503 si el servicio no tiene JWT_SECRET_KEY configurada.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        if not current_app.config.get("JWT_SECRET_KEY"):
            current_app.logger.error("JWT_SECRET_KEY no está configurada.")
            return {"error": "Servicio no configurado."}, 503

        try:
            verify_jwt_in_request()
        except (JWTExtendedException, PyJWTError):
            return UNAUTHORIZED_BODY, 401, UNAUTHORIZED_HEADERS

        return func(*args, **kwargs)

    return decorated
