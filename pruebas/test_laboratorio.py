"""Costura del spec: el laboratorio, observado desde la red interna."""

import hashlib
import socket
from pathlib import Path

NOTAS = b"Notas de la Actividad III, copia de practica de 64 bytes. lista\n"


def _preguntar(participante, orden):
    with socket.create_connection((participante, 5000), timeout=10) as conexion:
        conexion.sendall(f"{orden}\n".encode("utf-8"))
        return conexion.recv(4096).decode("utf-8").strip()


def test_los_cuatro_participantes_responden_en_la_red_interna():
    for participante in ("victima", "servidor", "intermediario", "comparacion"):
        respuesta = _preguntar(participante, "estado")
        assert respuesta.startswith(f"rol={participante}")


def test_los_originales_solo_se_leen_en_la_comparacion():
    for participante in ("victima", "servidor", "intermediario"):
        respuesta = _preguntar(participante, "estado")
        assert "originales=ausente" in respuesta
    respuesta = _preguntar("comparacion", "estado")
    assert "originales=lectura" in respuesta


def test_preparar_deja_la_copia_sin_semilla_ni_cifrado():
    assert len(NOTAS) == 64
    respuesta = _preguntar("comparacion", "preparar")
    assert respuesta == "preparado=si nombres=notas.txt"
    copia = _preguntar("victima", "leer-copia")
    assert bytes.fromhex(copia) == NOTAS


def test_el_generador_suministrado_no_cambia_y_devuelve_32_bytes():
    contenido = Path("/app/generador_semillas.py").read_bytes()
    assert hashlib.sha256(contenido).hexdigest() == (
        "5f9a08a63fecbfd64ad81b120cb3eb545e3b0218f8335b63754253bc9a63de2a"
    )
    from generador_semillas import generar_semilla_maestra

    assert len(generar_semilla_maestra()) == 32


def test_la_red_no_publica_puertos_ni_tiene_salida():
    compose = Path("/app/docker-compose.yml").read_text(encoding="utf-8")
    assert "ports:" not in compose
    assert "internal: true" in compose
    try:
        socket.create_connection(("1.1.1.1", 443), timeout=3)
    except OSError:
        return
    raise AssertionError("la red laboratorio tiene salida")
