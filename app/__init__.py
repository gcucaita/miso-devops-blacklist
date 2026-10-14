from flask import Flask, jsonify
from flask_restful import Api

from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Registrar modelos en SQLAlchemy
    from app import models

    api = Api(app)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "service": "blacklist-microservice"
        }), 200

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database tables created successfully.")

    return app