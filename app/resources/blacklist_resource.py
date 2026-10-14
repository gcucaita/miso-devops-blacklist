
from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from app.security.auth import require_bearer_token

from app.schemas.blacklist_schema import (
    BlacklistCreateSchema
)
from app.services.blacklist_service import (
    BlacklistService,
    DuplicateEmailError
)


class BlacklistResource(Resource):

    @require_bearer_token
    def post(self):

        if not request.is_json:
            return {
                "error": "Content-Type debe ser application/json"
            }, 415

        body = request.get_json(silent=True)

        if not isinstance(body, dict):
            return {
                "error": "Se requiere un objeto JSON valido."
            }, 400

        schema = BlacklistCreateSchema()

        try:
            # Normalizar antes de validar
            if isinstance(body.get("email"), str):
                body["email"] = (
                    body["email"].strip().lower()
                )

            data = schema.load(body)

        except ValidationError as error:
            return {
                "error": "Datos de entrada invalidos.",
                "details": error.messages
            }, 400

        try:
            result = BlacklistService.add_email(
                data=data,
                request_ip=request.remote_addr or "unknown"
            )

            return {
                "message": "Correo agregado correctamente.",
                "data": result
            }, 201

        except DuplicateEmailError as error:
            return {
                "error": str(error)
            }, 409


class BlacklistQueryResource(Resource):

    @require_bearer_token
    def get(self, email):

        schema = BlacklistCreateSchema(
            only=("email",)
        )

        try:
            data = schema.load({
                "email": email.strip().lower()
            })

        except ValidationError as error:
            return {
                "error": "Email invalido.",
                "details": error.messages
            }, 400

        result = BlacklistService.check_email(
            data["email"]
        )

        return result, 200
