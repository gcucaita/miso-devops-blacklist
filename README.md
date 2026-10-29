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

Hay al menos un escenario por endpoint, en un archivo por endpoint:

| Archivo | Endpoint | Escenarios |
|---|---|---|
| `tests/test_health.py` | `GET /health` | 200, versión desplegada, no requiere token |
| `tests/test_post_blacklists.py` | `POST /blacklists` | 201, persistencia, normalización, 409, 400, 415, 401 |
| `tests/test_get_blacklists.py` | `GET /blacklists/{email}` | 200 true/false, mayúsculas, 400, 401, 503 |

Adicionalmente, se recomienda verificar los endpoints contra PostgreSQL utilizando Postman.

### 9.1 Pruebas con Postman contra AWS

La carpeta `postman/` contiene la colección completa y el environment listo para ejecutar contra el entorno desplegado en Elastic Beanstalk:

| Archivo | Contenido |
|---|---|
| `postman/blacklist.postman_collection.json` | Colección **Blacklist Microservice · Entrega 1**: 20 peticiones y 91 asserts (salud, registro 201/409, validaciones 400/415, autenticación 401 y consultas). |
| `postman/blacklist.postman_environment.json` | Environment **Blacklist · AWS** con `base_url`, `jwt_token` y `app_uuid` ya configurados. |

El environment incluye un JWT de pruebas (`sub: postman-qa`) firmado con la `JWT_SECRET_KEY` del entorno de AWS. **Vence el 13 de noviembre de 2026.** Se publica porque es un proyecto académico de pruebas; no reutilizar este esquema en un sistema real.

**Desde Postman**

1. *Import* → seleccionar los dos archivos de `postman/`. Si ya existía una versión anterior de la colección o del environment, eliminarla antes (la variable antigua se llamaba `api_token`).
2. Arriba a la derecha, seleccionar el environment **Blacklist · AWS**.
3. Clic derecho en la colección → *Run* → *Run Blacklist Microservice · Entrega 1*.
4. Resultado esperado: todas las pruebas en *Passed* y 0 en *Failed*.

**Desde la terminal (Newman)**

```powershell
npx newman run postman/blacklist.postman_collection.json -e postman/blacklist.postman_environment.json
```

**Si el token vence o se cambia la clave**

Si las peticiones autenticadas responden 401, generar un token nuevo con la `JWT_SECRET_KEY` del entorno (Elastic Beanstalk → Configuración → Propiedades del entorno) y reemplazar el valor de `jwt_token`:

```powershell
$env:JWT_SECRET_KEY = "<valor de JWT_SECRET_KEY en Beanstalk>"
python scripts/generate_token.py --identity postman-qa --days 30
```

Para probar contra la API local, cambiar `base_url` a `http://127.0.0.1:5000` y generar el token con la `JWT_SECRET_KEY` del archivo `.env`.

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

## 11. Integración continua (AWS CodeBuild)

`buildspec.yml` define el build que ejecuta AWS CodeBuild en cada commit:

| Fase | Qué hace |
|---|---|
| `install` | Python 3.12 y `pip install -r requirements.txt` |
| `build` | `pytest` con reporte JUnit (`reports/junit.xml`). Si una prueba falla, el build termina en **FAILED** y no hay artefacto. |
| `post_build` | `scripts/build_zip.py` genera el paquete y se descomprime en `package/` |
| `reports` | Publica los resultados de pytest en la pestaña *Reports* de CodeBuild |
| `artifacts` | Publica el contenido de `package/` (application.py, Procfile, requirements.txt, app/, .ebextensions/) |

El artefacto solo se **genera**; no se despliega (sin CD en esta entrega).

Las pruebas no necesitan PostgreSQL ni variables de entorno: usan SQLite en memoria y una clave JWT propia de pruebas.

Para reproducir el build localmente:

```powershell
python -m pytest tests/ -v --junitxml=reports/junit.xml
python scripts/build_zip.py
```

`.gitattributes` fuerza saltos de línea LF en `Procfile`, `buildspec.yml` y `.ebextensions/`, para que un clon en Windows no los convierta a CRLF.

## 12. Estructura principal

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
buildspec.yml
README.md
.ebextensions/
scripts/
```

## 13. Consideraciones

- Los emails son únicos dentro de la lista negra.
- Los correos se normalizan a minúsculas para las búsquedas.
- Los motivos tienen un máximo de 255 caracteres.
- La fecha/hora se registra utilizando UTC.
- El Bearer Token es estático, de acuerdo con lo permitido en el enunciado.
- Las credenciales no deben almacenarse en GitHub.
- La aplicación no incluye interfaz gráfica.
- La disponibilidad del endpoint `/health` no implica necesariamente disponibilidad de la base de datos.