"""Cierre y reinicio, observados desde la red interna."""

import secrets
import subprocess
import sys
import time
from pathlib import Path

from Crypto.PublicKey import RSA

from protocolo.entrega import entregar

DESTINO = "entrega"
REGISTRO = Path("/datos/registro")
PUBLICO = Path("/datos/publico/ya-registrado")
CONTROL = Path("/datos/control/cerrar")
TRAZA = Path("/datos/traza-servidor/reinicio")


def _esperar_pk_s():
    ruta = REGISTRO / "pkS.der"
    for _ in range(200):
        if ruta.is_file() and ruta.stat().st_size > 0:
            return ruta.read_bytes()
        time.sleep(0.15)
    raise AssertionError("pkS no apareció en el registro")


def test_el_reinicio_carga_la_misma_sv_sin_otro_registro():
    CONTROL.unlink(missing_ok=True)
    id_v = secrets.token_bytes(16)
    pk_v = RSA.generate(2048).publickey().export_key(format="DER")
    carpeta = PUBLICO / id_v.hex()
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "pkV.der").write_bytes(pk_v)
    sv, confirmacion = entregar(id_v, _esperar_pk_s(), DESTINO)
    assert confirmacion == id_v

    incidente = REGISTRO / "incidentes" / id_v.hex()
    pk_s = (REGISTRO / "pkS.der").read_bytes()
    antes = TRAZA.read_text(encoding="utf-8") if TRAZA.is_file() else ""
    CONTROL.parent.mkdir(parents=True, exist_ok=True)
    CONTROL.write_bytes(b"cerrar")

    linea = f"reinicio {id_v.hex()} ok pendiente"
    texto = antes
    for _ in range(80):
        if TRAZA.is_file():
            texto = TRAZA.read_text(encoding="utf-8")
            if linea in texto[len(antes):]:
                break
        time.sleep(0.25)
    else:
        raise AssertionError("el servidor no anunció el reinicio")

    assert texto[len(antes):].count(linea) == 1
    assert (incidente / "sV").read_bytes() == sv
    assert len(sv) == 32
    assert (incidente / "pkV.der").read_bytes() == pk_v
    assert (incidente / "pago").read_text() == "pendiente"
    assert (REGISTRO / "pkS.der").read_bytes() == pk_s
    assert [ruta.name for ruta in (REGISTRO / "incidentes").iterdir() if ruta.name == id_v.hex()] == [
        id_v.hex()
    ]


def test_la_victima_al_reiniciar_carga_identidad_y_cifrados_sin_sv():
    id_v = secrets.token_bytes(16)
    clave = RSA.generate(2048)
    pk_v = clave.publickey().export_key(format="DER")
    sk_v = clave.export_key(format="DER")
    identidad = Path("/datos/identidad")
    cifrados = Path("/datos/cifrados")
    identidad.mkdir(parents=True, exist_ok=True)
    cifrados.mkdir(parents=True, exist_ok=True)
    for ruta in identidad.iterdir():
        if ruta.is_file():
            ruta.unlink()
    for ruta in cifrados.iterdir():
        if ruta.is_file():
            ruta.unlink()
    (identidad / "idV").write_bytes(id_v)
    (identidad / "pkV.der").write_bytes(pk_v)
    (identidad / "skV.der").write_bytes(sk_v)
    salidas = {"0000": b"\x10cifrado-0", "0001": b"\x11cifrado-1", "0002": b"\x12cifrado-2"}
    for nombre, datos in salidas.items():
        (cifrados / nombre).write_bytes(datos)

    try:
        resultado = subprocess.run(
            [sys.executable, "-m", "protocolo.reinicio"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        assert resultado.returncode == 0
        detalle = ",".join(
            [
                f"pkV={pk_v[:4].hex()}",
                f"skV={sk_v[:4].hex()}",
                f"0000={salidas['0000'][:1].hex()}",
                f"0001={salidas['0001'][:1].hex()}",
                f"0002={salidas['0002'][:1].hex()}",
            ]
        )
        linea = f"reinicio {id_v.hex()} ok {detalle}"
        assert linea in Path("/datos/traza-victima/reinicio").read_text(encoding="utf-8")
        assert {ruta.name for ruta in identidad.iterdir() if ruta.is_file()} == {
            "idV",
            "pkV.der",
            "skV.der",
        }
        assert {ruta.name for ruta in cifrados.iterdir() if ruta.is_file()} == {"0000", "0001", "0002"}
        for nombre, datos in salidas.items():
            assert (cifrados / nombre).read_bytes() == datos
        for nombre in ("sV", "Ki", "entrega"):
            assert not (identidad / nombre).exists()
            assert not (cifrados / nombre).exists()
    finally:
        for nombre in salidas:
            (cifrados / nombre).unlink(missing_ok=True)
