
from flask import Flask, jsonify
from flask_restful import Api

from app.config import Config
from app.extensions import db
from app.version import APP_VERSION


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app import models

    from app.resources.blacklist_resource import (
        BlacklistResource,
        BlacklistQueryResource
    )

    api = Api(app)

    api.add_resource(
        BlacklistResource,
        "/blacklists"
    )

    api.add_resource(
        BlacklistQueryResource,
        "/blacklists/<string:email>"
    )

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "service": "blacklist-microservice",
            "version": APP_VERSION
        }), 200

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database tables created successfully.")

    return app
