# MISO DevOps - Blacklist Microservice

Microservicio REST desarrollado con Python y Flask para gestionar una lista negra global de correos electrónicos.

**Proyecto académico:** DevOps: Agilizando el Despliegue Continuo de Aplicaciones  
**Entrega:** 1 - Despliegue manual de un microservicio sobre PaaS

## 1. Tecnologías

- Python y Flask
- Flask-RESTful
- Flask-SQLAlchemy
- Flask-Marshmallow
- PostgreSQL
- Bearer Token estático
- Pytest
- Gunicorn
- AWS Elastic Beanstalk

## 2. Funcionalidades

### POST /blacklists

Registra un correo electrónico en la lista negra.

**Body JSON:**

```json
{
  "email": "usuario@empresa.com",
  "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "blocked_reason": "Actividad sospechosa"
}
```

El campo `blocked_reason` es opcional y admite máximo 255 caracteres.

El sistema registra automáticamente la IP de origen y la fecha/hora de la solicitud.

**Respuesta exitosa:** HTTP 201.  
**Correo duplicado:** HTTP 409.  
**Datos inválidos:** HTTP 400.

### GET /blacklists/{email}

Consulta si un correo está registrado en la lista negra global.

**Ejemplo de respuesta:**

```json
{
  "email": "usuario@empresa.com",
  "is_blacklisted": true,
  "blocked_reason": "Actividad sospechosa"
}
```

**Respuesta exitosa:** HTTP 200.

### GET /health

Permite verificar que el proceso HTTP está disponible.

No requiere autenticación y devuelve HTTP 200 cuando el endpoint responde correctamente. No verifica por sí mismo la conectividad de PostgreSQL.

## 3. Requisitos

- Python compatible con las dependencias utilizadas.
- PostgreSQL.
- Git.
- Variables de entorno configuradas.

## 4. Instalación en Windows

Clonar el repositorio:

```powershell
git clone URL_DEL_REPOSITORIO
cd miso-devops-blacklist
```

Crear el entorno virtual:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

## 5. Variables de entorno

Crear un archivo `.env` utilizando como referencia `.env.example`.

```dotenv
DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/blacklist_db
JWT_SECRET_KEY=replace-with-long-random-secret
FLASK_DEBUG=false
```

La clave `JWT_SECRET_KEY` firma y valida los JWT (Flask-JWT-Extended). Puede generarse con:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Nunca publicar credenciales reales en el repositorio.

## 6. Base de datos

Crear una base PostgreSQL llamada `blacklist_db`.

Para inicializar las tablas en un entorno local nuevo:

```powershell
flask --app application:application init-db
```

El comando crea las tablas inexistentes a partir de los modelos SQLAlchemy. No reemplaza las migraciones cuando ya existe una base de datos con datos.

## 7. Ejecución local

```powershell
python application.py
```

La API estará disponible en:

`http://127.0.0.1:5000`

## 8. Autenticación

Los endpoints POST y GET están protegidos con **Flask-JWT-Extended** y requieren un JWT válido:

```http
Authorization: Bearer <JWT>
```

El JWT se genera con la misma `JWT_SECRET_KEY` del entorno:

```powershell
$env:JWT_SECRET_KEY = "<clave del entorno>"
python scripts/generate_token.py --identity postman-qa --days 30   # --days 0 = sin vencimiento
```

Si el token falta, está mal formado, expiró o fue firmado con otra clave, el servicio devuelve HTTP 401. Si el servicio no tiene `JWT_SECRET_KEY` configurada, devuelve HTTP 503.

El endpoint `/health` no necesita token.

## 9. Pruebas automatizadas

Ejecutar:

```powershell
python -m pytest tests/ -v
```

Las pruebas utilizan SQLite temporal en memoria y no modifican la base de datos PostgreSQL.

Adicionalmente, se recomienda verificar los endpoints contra PostgreSQL utilizando Postman.

## 10. Despliegue manual en AWS

La aplicación está preparada para ejecutarse en AWS Elastic Beanstalk con Gunicorn y PostgreSQL en AWS RDS.

Configuración requerida:

- Plataforma Python compatible.
- Archivo `requirements.txt`.
- Archivo `Procfile`.
- Variable `DATABASE_URL`.
- Variable `JWT_SECRET_KEY`.
- Base de datos PostgreSQL inicializada.
- Conectividad privada entre la aplicación y RDS.
- Health check HTTP en `/health`.

El despliegue debe realizarse manualmente según el alcance de la primera entrega. No se implementa CI/CD en esta iteración.

### 10.1 Generar el paquete de despliegue

1. Cambiar la versión en `app/version.py` (por ejemplo `v1` → `v2`).
2. Ejecutar desde la raíz del repositorio:

```powershell
python scripts/build_zip.py
```

3. Subir `dist/blacklist-<version>.zip` en Elastic Beanstalk con **Upload and deploy**.

No usar *Enviar a → Carpeta comprimida* ni `Compress-Archive`: dejan los archivos dentro de una carpeta o con rutas `\` que Beanstalk no reconoce.

### 10.2 Monitorear un despliegue

`GET /health` devuelve la versión desplegada (`"version": "v2"`). Durante cada despliegue:

```powershell
pip install requests
python scripts/monitor.py http://<url-del-entorno> rolling
```

Al detenerlo con Ctrl+C imprime un resumen (errores/caída y convivencia de versiones) y guarda un CSV con cada petición. Sirve como evidencia de la validación de cada estrategia de despliegue.

`.ebextensions/01-health.config` configura el health check del balanceador en `/health`. La política de despliegue se cambia en la consola antes de cada despliegue y no se fija en `.ebextensions`.

## 11. Estructura principal

```text
app/
  models/
  resources/
  schemas/
  services/
  security/
tests/
application.py
Procfile
requirements.txt
README.md
.ebextensions/
scripts/
```

## 12. Consideraciones

- Los emails son únicos dentro de la lista negra.
- Los correos se normalizan a minúsculas para las búsquedas.
- Los motivos tienen un máximo de 255 caracteres.
- La fecha/hora se registra utilizando UTC.
- El Bearer Token es estático, de acuerdo con lo permitido en el enunciado.
- Las credenciales no deben almacenarse en GitHub.
- La aplicación no incluye interfaz gráfica.
- La disponibilidad del endpoint `/health` no implica necesariamente disponibilidad de la base de datos.