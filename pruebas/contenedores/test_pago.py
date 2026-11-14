"""Recuperación por pago, desde la red interna."""

import secrets
import time
from pathlib import Path

import pytest
from Crypto.PublicKey import RSA

from protocolo.cifrado import cifrar
from protocolo.descifrado import descifrar_todos
from protocolo.entrega import entregar
from protocolo.pago import PagoRechazado, recuperar

DESTINO = "entrega"
REGISTRO = Path("/datos/registro")
PUBLICO = Path("/datos/publico/ya-registrado")
IDENTIDAD = Path("/datos/identidad")
RECUPERADOS = Path("/datos/recuperados")
CIFRADOS = Path("/datos/cifrados")
COPIA = Path("/datos/copias/notas.txt")
NOTAS = b"Notas de la Actividad III, copia de practica de 64 bytes. lista\n"


def _esperar_pk_s():
    ruta = REGISTRO / "pkS.der"
    for _ in range(200):
        if ruta.is_file() and ruta.stat().st_size > 0:
            return ruta.read_bytes()
        time.sleep(0.15)
    raise AssertionError("pkS no apareció en el registro")


def _limpiar():
    for carpeta in (CIFRADOS, RECUPERADOS):
        if carpeta.is_dir():
            for ruta in carpeta.iterdir():
                if ruta.is_file():
                    ruta.unlink()


def _preparar_incidente():
    """Genera idV/pkV/skV, registra, entrega sV y cifra los tres Ci."""
    _limpiar()
    id_v = secrets.token_bytes(16)
    clave = RSA.generate(2048)
    pk_v = clave.publickey().export_key(format="DER")
    IDENTIDAD.mkdir(parents=True, exist_ok=True)
    (IDENTIDAD / "idV").write_bytes(id_v)
    (IDENTIDAD / "pkV.der").write_bytes(pk_v)
    (IDENTIDAD / "skV.der").write_bytes(clave.export_key(format="DER"))
    carpeta = PUBLICO / id_v.hex()
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "pkV.der").write_bytes(pk_v)
    pk_s = _esperar_pk_s()
    # 1) Entrega inicial: la víctima genera sV y la envía al servidor.
    sv, _confirmacion = entregar(id_v, pk_s, DESTINO)
    # 2) La víctima cifra los tres Ci con sV (como en el flujo real).
    COPIA.parent.mkdir(parents=True, exist_ok=True)
    COPIA.write_bytes(NOTAS)
    cifrar(id_v, sv)
    return id_v


def test_pago_recupera_la_sv_y_descifra_los_tres():
    id_v = _preparar_incidente()
    sv = recuperar(id_v, DESTINO)
    assert len(sv) == 32
    pago = REGISTRO / "incidentes" / id_v.hex() / "pago"
    assert pago.read_text() == "pagado"
    validos = descifrar_todos(id_v, sv)
    assert validos == ["0000", "0001", "0002"]
    for nombre in validos:
        assert (RECUPERADOS / nombre).read_bytes() == NOTAS


def test_pago_con_id_desconocido_se_rechaza():
    _esperar_pk_s()
    id_v = secrets.token_bytes(16)
    with pytest.raises(PagoRechazado) as error:
        recuperar(id_v, DESTINO)
    assert error.value.motivo == "sin-sv"