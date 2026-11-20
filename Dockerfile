FROM python:3.11-slim

WORKDIR /app

# Instala las dependencias primero (aprovecha la caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Buena práctica de seguridad: no ejecutar como root
RUN useradd --create-home appuser
USER appuser

# 5000 = aplicación web, 8000 = métricas Prometheus
EXPOSE 5000 8000

CMD ["python", "app.py"]
