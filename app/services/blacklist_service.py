
from datetime import timezone

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.blacklist import Blacklist


class DuplicateEmailError(Exception):
    pass


class BlacklistService:

    @staticmethod
    def normalize_email(email):
        return email.strip().lower()

    @staticmethod
    def add_email(data, request_ip):

        email = BlacklistService.normalize_email(
            data["email"]
        )

        existing = db.session.execute(
            db.select(Blacklist).filter_by(email=email)
        ).scalar_one_or_none()

        if existing is not None:
            raise DuplicateEmailError(
                "El correo ya se encuentra en la lista negra."
            )

        record = Blacklist(
            email=email,
            app_uuid=data["app_uuid"],
            blocked_reason=data.get("blocked_reason"),
            request_ip=request_ip
        )

        try:
            db.session.add(record)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise DuplicateEmailError(
                "El correo ya se encuentra en la lista negra."
            )

        return {
            "id": record.id,
            "email": record.email,
            "app_uuid": str(record.app_uuid),
            "blocked_reason": record.blocked_reason,
            "created_at": record.created_at.astimezone(
                timezone.utc
            ).isoformat()
        }

    @staticmethod
    def check_email(email):

        normalized_email = (
            BlacklistService.normalize_email(email)
        )

        record = db.session.execute(
            db.select(Blacklist).filter_by(
                email=normalized_email
            )
        ).scalar_one_or_none()

        if record is None:
            return {
                "email": normalized_email,
                "is_blacklisted": False,
                "blocked_reason": None
            }

        return {
            "email": record.email,
            "is_blacklisted": True,
            "blocked_reason": record.blocked_reason
        }
