import uuid
from datetime import datetime, timezone

from sqlalchemy import Uuid

from app.extensions import db


class Blacklist(db.Model):
    __tablename__ = "blacklists"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    app_uuid = db.Column(
        Uuid(as_uuid=True),
        nullable=False
    )

    blocked_reason = db.Column(
        db.String(255),
        nullable=True
    )

    request_ip = db.Column(
        db.String(45),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Blacklist email={self.email}>"