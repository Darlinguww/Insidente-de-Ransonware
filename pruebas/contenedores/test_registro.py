"""Registro del incidente, observado desde la red interna."""

from pathlib import Path

from Crypto.PublicKey import RSA

from protocolo.registro import registrar, repetir

DESTINO = "entrega"
REGISTRO = Path("/datos/registro")
TRAZA_SERVIDOR = Path("/datos/traza-servidor/registro")
TRAZA_VICTIMA = Path("/datos/traza-victima/registro")


def _rsa_publica(der):
    clave = RSA.import_key(der)
    assert not clave.has_private()
    assert clave.e == 65537
    assert clave.n.bit_length() == 2048
    return clave


def test_el_registro_intercambia_idv_y_las_claves_publicas():
    resultado = registrar(DESTINO)
    id_v = resultado["id_v"]
    assert len(id_v) == 16
    assert id_v in resultado["enviado"]
    assert id_v in resultado["recibido"]
    _rsa_publica(resultado["pk_v"])
    recibida = _rsa_publica(resultado["pk_s"])
    en_disco = RSA.import_key((REGISTRO / "pkS.der").read_bytes())
    assert (en_disco.n, en_disco.e) == (recibida.n, recibida.e)
    assert resultado["sk_v"] not in resultado["enviado"]
    assert resultado["sk_v"] not in resultado["recibido"]
    assert not Path("/datos/secreto").exists()

    incidente = REGISTRO / "incidentes" / id_v.hex()
    assert (incidente / "pkV.der").read_bytes() == resultado["pk_v"]
    assert (incidente / "pago").read_text() == "pendiente"
    assert not (incidente / "sV").exists()
    assert resultado["sk_v"] not in (incidente / "pkV.der").read_bytes()
    linea = f"registro {id_v.hex()} ok asociada"
    assert linea in TRAZA_SERVIDOR.read_text(encoding="utf-8")
    assert linea in TRAZA_VICTIMA.read_text(encoding="utf-8")


def test_repetir_el_registro_no_abre_otro_incidente():
    primero = registrar(DESTINO)
    incidente = REGISTRO / "incidentes" / primero["id_v"].hex()
    segundo = repetir(primero["id_v"], primero["pk_v"], primero["sk_v"], DESTINO)
    assert segundo["pk_s"] == primero["pk_s"]
    assert segundo["id_v"] == primero["id_v"]
    assert (incidente / "pkV.der").read_bytes() == primero["pk_v"]
    assert not (incidente / "sV").exists()
    assert not (incidente / "entrega").exists()
    assert [ruta.name for ruta in (REGISTRO / "incidentes").iterdir() if ruta.name == primero["id_v"].hex()] == [
        primero["id_v"].hex()
    ]
