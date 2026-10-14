
import os
import hmac

from functools import wraps
from flask import request, current_app


def require_bearer_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):

        expected_token = os.getenv("API_TOKEN")

        if not expected_token:
            current_app.logger.error(
                "API_TOKEN no está configurado."
            )
            return {
                "error": "Servicio no configurado."
            }, 503

        authorization = request.headers.get(
            "Authorization", ""
        )

        parts = authorization.split()

        if (
            len(parts) != 2
            or parts[0].lower() != "bearer"
            or not hmac.compare_digest(
                parts[1], expected_token
            )
        ):
            return {
                "error": "Token ausente o invalido."
            }, 401, {
                "WWW-Authenticate": 'Bearer realm="blacklists"'
            }

        return func(*args, **kwargs)

    return decorated
