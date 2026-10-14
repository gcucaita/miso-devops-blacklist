
from marshmallow import Schema, fields, validate


class BlacklistCreateSchema(Schema):
    email = fields.Email(
        required=True,
        validate=validate.Length(max=255)
    )

    app_uuid = fields.UUID(
        required=True
    )

    blocked_reason = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255)
    )
