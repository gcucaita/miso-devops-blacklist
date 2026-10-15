"""
Monitor de despliegues en Elastic Beanstalk.

Consulta GET /health cada 0,5 s mientras corre un despliegue y registra
qué versión responde (o el error). Al terminar (Ctrl+C) imprime un resumen
que sirve como evidencia para el informe:
  - total de peticiones por respuesta (v1, v2, HTTP 502, ERROR...)
  - segundos con errores (caída) y cuándo empezaron/terminaron
  - periodo en que convivieron dos versiones
Además guarda cada petición en un CSV.

Uso:
    pip install requests
    python monitor.py http://TU-ENTORNO.us-east-1.elasticbeanstalk.com all-at-once
"""
import csv
import sys
import time
from collections import Counter
from datetime import datetime

import requests

if len(sys.argv) < 3:
    print("Uso: python monitor.py <URL del entorno> <nombre-estrategia>")
    sys.exit(1)

URL = sys.argv[1].rstrip("/") + "/health"
ESTRATEGIA = sys.argv[2]
ARCHIVO = f"monitor_{ESTRATEGIA}_{datetime.now():%Y%m%d_%H%M%S}.csv"

conteo = Counter()
registros = []  # (timestamp, respuesta, ms)

print(f"Monitoreando {URL}  →  {ARCHIVO}   (Ctrl+C para terminar)\n")
try:
    while True:
        t0 = time.time()
        try:
            r = requests.get(URL, timeout=2)
            if r.ok:
                resp = str(r.json().get("version", "sin-version"))
            else:
                resp = f"HTTP {r.status_code}"
        except Exception:
            resp = "ERROR"
        ms = int((time.time() - t0) * 1000)
        ahora = datetime.now()
        conteo[resp] += 1
        registros.append((ahora, resp, ms))
        print(f"{ahora:%H:%M:%S}  {resp:<10} {ms:>5} ms   {dict(conteo)}", flush=True)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

with open(ARCHIVO, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["hora", "respuesta", "latencia_ms"])
    for t, resp, ms in registros:
        w.writerow([t.strftime("%H:%M:%S.%f")[:-3], resp, ms])

def es_error(resp):
    return resp == "ERROR" or resp.startswith("HTTP")

errores = [t for t, resp, _ in registros if es_error(resp)]
versiones = {}
for t, resp, _ in registros:
    if not es_error(resp):
        versiones.setdefault(resp, []).append(t)

print("\n" + "=" * 60)
print(f"RESUMEN · estrategia: {ESTRATEGIA}")
print("=" * 60)
if registros:
    dur = (registros[-1][0] - registros[0][0]).total_seconds()
    print(f"Monitoreo: {registros[0][0]:%H:%M:%S} → {registros[-1][0]:%H:%M:%S} ({dur:.0f} s, {len(registros)} peticiones)")
print("Respuestas:", dict(conteo))

if errores:
    caida = (errores[-1] - errores[0]).total_seconds()
    print(f"Errores: {len(errores)} peticiones fallidas entre {errores[0]:%H:%M:%S} y {errores[-1]:%H:%M:%S} (~{caida:.0f} s de caída)")
else:
    print("Errores: ninguno → despliegue SIN caída")

if len(versiones) > 1:
    print("Versiones observadas:")
    for v, ts in versiones.items():
        print(f"  {v}: de {ts[0]:%H:%M:%S} a {ts[-1]:%H:%M:%S} ({len(ts)} respuestas)")
    vs = list(versiones.values())
    ini = max(ts[0] for ts in vs)
    fin = min(ts[-1] for ts in vs)
    if fin > ini:
        print(f"Convivencia de versiones: {ini:%H:%M:%S} → {fin:%H:%M:%S} (~{(fin - ini).total_seconds():.0f} s)")
    else:
        print("Convivencia de versiones: no hubo (el cambio fue de golpe)")
print(f"\nDetalle guardado en {ARCHIVO}")
