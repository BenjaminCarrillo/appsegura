## @file app.py
#  @brief Servicio web de ejemplo "appsegura" (Flask).
#
#  Expone métricas para Prometheus en el puerto 8000 y envía sus logs
#  a Logstash para visualizarlos en Kibana.
#
#  @author [Tu nombre]
#  @version 1.0

import json
import logging
import os
import random
import time
import urllib.request

from flask import Flask, request
from prometheus_client import Counter, Summary, start_http_server

app = Flask(__name__)

# ---------------- Métricas Prometheus ----------------
REQUEST_TIME = Summary(
    "request_processing_seconds", "Tiempo empleado en procesar la petición"
)
HTTP_REQUESTS = Counter(
    "http_requests_total", "Total de peticiones HTTP", ["endpoint", "status"]
)

# ---------------- Envío de logs a Logstash ----------------
LOGSTASH_URL = os.getenv("LOGSTASH_URL", "http://host.docker.internal:5000")


## @brief Manejador de logs que envía cada mensaje a Logstash.
#
#  Convierte el registro en JSON y lo envía por HTTP al input de Logstash.
#  Si Logstash no está disponible, la aplicación sigue funcionando.
class LogstashHTTPHandler(logging.Handler):

    ## @brief Envía un registro de log a Logstash.
    #  @param record Registro de log generado por la aplicación.
    def emit(self, record):
        payload = {
            "service": "appsegura",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        try:
            req = urllib.request.Request(
                LOGSTASH_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            # Si Logstash no está disponible, la app sigue funcionando.
            pass


logger = logging.getLogger("appsegura")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())      # logs en consola (docker logs)
logger.addHandler(LogstashHTTPHandler())        # logs hacia Logstash


# ---------------- Endpoints ----------------
## @brief Página principal del servicio.
#  @return Texto con las rutas disponibles.
@app.route("/")
def index():
    HTTP_REQUESTS.labels(endpoint="/", status="200").inc()
    logger.info("Acceso a la página principal")
    return "Servicio de ejemplo funcionando. Prueba /hello?name=Ana, /slow o /error\n"


## @brief Saluda al usuario indicado en el parámetro "name".
#  @return Saludo (200) o mensaje de error si falta el nombre (400).
@app.route("/hello")
@REQUEST_TIME.time()
def hello():
    name = request.args.get("name")
    if not name:
        HTTP_REQUESTS.labels(endpoint="/hello", status="400").inc()
        logger.warning("Petición a /hello sin parámetro 'name'")
        return "Falta el parámetro 'name'\n", 400
    HTTP_REQUESTS.labels(endpoint="/hello", status="200").inc()
    logger.info(f"Saludo enviado a {name}")
    return f"Hello, {name}!\n"


## @brief Simula una petición lenta (entre 0,5 y 2 segundos).
#  @return Texto con el tiempo de respuesta.
@app.route("/slow")
@REQUEST_TIME.time()
def slow():
    espera = random.uniform(0.5, 2.0)
    time.sleep(espera)
    HTTP_REQUESTS.labels(endpoint="/slow", status="200").inc()
    logger.info(f"Petición lenta atendida en {espera:.2f} s")
    return f"Respuesta lenta ({espera:.2f} s)\n"


## @brief Simula un error interno del servidor.
#  @return Mensaje de error con código 500.
@app.route("/error")
def error():
    HTTP_REQUESTS.labels(endpoint="/error", status="500").inc()
    logger.error("Error simulado en el endpoint /error")
    return "Error simulado\n", 500


if __name__ == "__main__":
    start_http_server(8000)                        # métricas en :8000/metrics
    logger.info("Servicio appsegura iniciado")
    # host 0.0.0.0 para que sea accesible desde fuera del contenedor.
    # debug=False para que no se ejecute dos veces (evita "Address already in use" en el 8000).
    app.run(host="0.0.0.0", port=5000, debug=False)
