import os
from dotenv import load_dotenv

load_dotenv()


def _database_url():
    """Lee DATABASE_URL y fija el driver psycopg2.

    SQLAlchemy 2.1 cambió el driver por defecto de "postgresql://" a psycopg (v3),
    pero el proyecto instala psycopg2-binary. Normalizamos el esquema para que
    funcione con "postgres://", "postgresql://" o "postgresql+psycopg2://".
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        return url
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg2://" + url[len(prefix):]
    return url


class Config:
    SQLALCHEMY_DATABASE_URI = _database_url()

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }
