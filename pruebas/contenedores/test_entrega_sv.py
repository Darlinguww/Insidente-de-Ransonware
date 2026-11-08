"""Entrega de sV, observada desde la red interna."""

import secrets
import time
from pathlib import Path

import pytest
from Crypto.PublicKey import RSA

from protocolo.entrega import EntregaRechazada, entregar, enviar

DESTINO = "entrega"
REGISTRO = Path("/datos/registro")
PUBLICO = Path("/datos/publico/ya-registrado")
IDENTIDAD = Path("/datos/identidad")


def _esperar_pk_s():
    ruta = REGISTRO / "pkS.der"
    for _ in range(200):
        if ruta.is_file() and ruta.stat().st_size > 0:
            return ruta.read_bytes()
        time.sleep(0.15)
    raise AssertionError("pkS no apareció en el registro")


def _incidente_ya_registrado(id_v, pk_v):
    carpeta = PUBLICO / id_v.hex()
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "pkV.der").write_bytes(pk_v)


def test_el_servidor_guarda_la_sv_y_confirma_con_el_idv():
    id_v = secrets.token_bytes(16)
    clave = RSA.generate(2048)
    pk_v = clave.publickey().export_key(format="DER")
    IDENTIDAD.mkdir(parents=True, exist_ok=True)
    (IDENTIDAD / "idV").write_bytes(id_v)
    (IDENTIDAD / "pkV.der").write_bytes(pk_v)
    (IDENTIDAD / "skV.der").write_bytes(clave.export_key(format="DER"))
    _incidente_ya_registrado(id_v, pk_v)

    try:
        sv, confirmacion = entregar(id_v, _esperar_pk_s(), DESTINO)
    except EntregaRechazada as error:
        raise AssertionError(f"la entrega fue rechazada: {error.motivo}") from error

    incidente = REGISTRO / "incidentes" / id_v.hex()
    assert confirmacion == id_v
    assert (incidente / "sV").read_bytes() == sv
    assert len(sv) == 32
    assert (incidente / "pkV.der").read_bytes() == pk_v
    assert (incidente / "pago").read_text() == "pendiente"
    assert not (IDENTIDAD / "sV").exists()


def test_si_la_entrega_no_se_abre_se_informa_y_no_hay_ci():
    id_v = secrets.token_bytes(16)
    pk_v = RSA.generate(2048).publickey().export_key(format="DER")
    _incidente_ya_registrado(id_v, pk_v)
    _esperar_pk_s()

    with pytest.raises(EntregaRechazada) as error:
        enviar(id_v, b"\x00" * 256, DESTINO)

    linea = f"entrega {id_v.hex()} error no-abre"
    assert error.value.motivo == "no-abre"
    assert linea in Path("/datos/traza-servidor/entrega").read_text(encoding="utf-8")
    assert linea in Path("/datos/traza-victima/entrega").read_text(encoding="utf-8")
    assert not (REGISTRO / "incidentes" / id_v.hex() / "sV").exists()
    for nombre in ("0000", "0001", "0002"):
        assert not (Path("/datos/cifrados") / nombre).exists()
