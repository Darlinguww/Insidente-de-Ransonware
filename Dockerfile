FROM python:3.12-slim

WORKDIR /app

COPY generador_semillas.py .
COPY docker-compose.yml .
COPY laboratorio ./laboratorio
COPY protocolo ./protocolo
COPY servidor ./servidor
COPY intermediario ./intermediario
COPY pruebas ./pruebas

RUN pip install --no-cache-dir pytest==8.3.5 pycryptodome==3.23.0 cryptography==44.0.0

CMD ["python", "-m", "laboratorio"]
