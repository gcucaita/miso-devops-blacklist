from flask import Flask, jsonify
from flask_restful import Api


def create_app():
    app = Flask(__name__)

    api = Api(app)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "service": "blacklist-microservice"
        }), 200

    return app