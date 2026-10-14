"""Genera el JWT que usan los clientes (Postman, otras apps) para llamar la API.

Usa Flask-JWT-Extended con la MISMA clave JWT_SECRET_KEY configurada en
Elastic Beanstalk. El token no se guarda en ningún archivo: se imprime una vez.

Uso (PowerShell):
    $env:JWT_SECRET_KEY = "<la clave del entorno>"
    python scripts/generate_token.py                 # vence en 30 días
    python scripts/generate_token.py --days 90 --identity postman-qa
    python scripts/generate_token.py --days 0        # sin vencimiento

Si JWT_SECRET_KEY no está definida, la pide sin mostrarla en pantalla.
"""
import argparse
import getpass
import os
from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

parser = argparse.ArgumentParser(description="Genera un JWT para la API Blacklist")
parser.add_argument("--identity", default="blacklist-client",
                    help="Identificador del cliente (claim sub)")
parser.add_argument("--days", type=int, default=30,
                    help="Días de vigencia; 0 = sin vencimiento")
args = parser.parse_args()

secret = os.getenv("JWT_SECRET_KEY") or getpass.getpass("JWT_SECRET_KEY: ")
if not secret:
    raise SystemExit("Se requiere JWT_SECRET_KEY.")

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = secret
JWTManager(app)

with app.app_context():
    expires = False if args.days == 0 else timedelta(days=args.days)
    token = create_access_token(identity=args.identity, expires_delta=expires)

vigencia = "sin vencimiento" if args.days == 0 else f"{args.days} días"
print(f"JWT para '{args.identity}' ({vigencia}):")
print(token)
