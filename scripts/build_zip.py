"""
Genera el .zip para subir a Elastic Beanstalk ("Upload and deploy").

- Lee la versión de app/version.py y la usa en el nombre del archivo.
- Deja application.py, Procfile, requirements.txt, app/ y .ebextensions/
  en la RAÍZ del zip (Beanstalk lo exige).
- Usa "/" como separador. Compress-Archive de Windows usa "\" y
  Beanstalk (Linux) no reconoce bien esas rutas.
- Excluye tests, entornos virtuales, cachés, .env y .git.

Uso (desde la raíz del repo):
    python scripts/build_zip.py
Resultado: dist/blacklist-<version>.zip
"""
import re
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INCLUIR = ["application.py", "Procfile", "requirements.txt", "app", ".ebextensions"]
EXCLUIR_DIRS = {"__pycache__", ".venv", "venv", ".git", ".pytest_cache"}

version = re.search(
    r'APP_VERSION\s*=\s*"([^"]+)"',
    (RAIZ / "app" / "version.py").read_text(encoding="utf-8"),
).group(1)

reqs = (RAIZ / "requirements.txt").read_bytes()
if reqs.startswith((b"\xff\xfe", b"\xfe\xff")):
    raise SystemExit("requirements.txt está en UTF-16: guárdalo en UTF-8 antes de empaquetar.")

dist = RAIZ / "dist"
dist.mkdir(exist_ok=True)
destino = dist / f"blacklist-{version}.zip"

archivos = []
for item in INCLUIR:
    ruta = RAIZ / item
    if ruta.is_file():
        archivos.append(ruta)
    elif ruta.is_dir():
        for f in sorted(ruta.rglob("*")):
            if f.is_file() and not (set(f.relative_to(RAIZ).parts) & EXCLUIR_DIRS) and f.suffix != ".pyc":
                archivos.append(f)
    else:
        raise SystemExit(f"Falta {item}")

with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
    for f in archivos:
        z.write(f, f.relative_to(RAIZ).as_posix())

print(f"Versión: {version}")
print(f"Generado: {destino.relative_to(RAIZ)} ({len(archivos)} archivos)")
for f in archivos:
    print("  ", f.relative_to(RAIZ).as_posix())
