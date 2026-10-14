# MISO DevOps - Blacklist Microservice

Microservicio REST para la gestión centralizada de
listas negras de correos electrónicos.

## Tecnologías
- Python
- Flask
- Flask-RESTful
- SQLAlchemy
- PostgreSQL

## Endpoints
- POST /blacklists
- GET /blacklists/<email>
- GET /health

## Ejecutar localmente

1. Crear y activar un entorno virtual.
2. Instalar dependencias:
   pip install -r requirements.txt
3. Ejecutar:
   python application.py

## Estado
En desarrollo.