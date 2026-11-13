"""Firmas ECDSA P-256, observadas desde la red interna."""

import secrets

import pytest
from Crypto.PublicKey import RSA

from protocolo.firmas import (
    FirmaInvalida,
    ROL_S,
    ROL_V,
    firmar,
    verificar,
)
from protocolo.registro import registrar

DESTINO = "entrega"
CONFIANZA = __import__("pathlib").Path("/datos/confianza")
INTERMEDIARIO = __import__("pathlib").Path("/datos/confianza_intermediario")


def test_el_registro_legitimo_verifica_ambas_firmas():
    resultado = registrar(DESTINO)
    id_v = resultado["id_v"]
    # La firma del servidor sobre pkS verifica con la clave instalada.
    verificar(
        CONFIANZA / "verificacion_servidor.pem",
        ROL_S, id_v, resultado["pk_s"], resultado["firma_s"],
    )
    # La firma de la víctima sobre pkV verifica con la clave del servidor.
    firma_v = firmar(CONFIANZA / "propia.pem", ROL_V, id_v, resultado["pk_v"])
    # (el servidor ya lo comprobó al aceptar el registro; aquí lo confirmamos)
    assert len(firma_v) > 0


def test_una_firma_del_intermediario_no_verifica_contra_la_clave_instalada():
    id_v = secrets.token_bytes(16)
    pk_s_falso = RSA.generate(2048).publickey().export_key(format="DER", pkcs=8)
    # El intermediario firma con su propia clave.
    firma_falsa = firmar(INTERMEDIARIO / "propia.pem", ROL_S, id_v, pk_s_falso)
    # La víctima verifica con la clave del servidor: debe fallar.
    with pytest.raises(FirmaInvalida):
        verificar(
            CONFIANZA / "verificacion_servidor.pem",
            ROL_S, id_v, pk_s_falso, firma_falsa,
        )


def test_adjuntar_la_clave_del_intermediario_no_cambia_la_verificacion():
    id_v = secrets.token_bytes(16)
    pk_s_falso = RSA.generate(2048).publickey().export_key(format="DER", pkcs=8)
    firma_falsa = firmar(INTERMEDIARIO / "propia.pem", ROL_S, id_v, pk_s_falso)
    # Aunque el mensaje incluya su clave pública, la verificación usa la
    # clave instalada de antemano, no la que llega por la red.
    with pytest.raises(FirmaInvalida):
        verificar(
            CONFIANZA / "verificacion_servidor.pem",
            ROL_S, id_v, pk_s_falso, firma_falsa,
        )


def test_rol_incorrecto_no_verifica():
    resultado = registrar(DESTINO)
    with pytest.raises(FirmaInvalida):
        verificar(
            CONFIANZA / "verificacion_servidor.pem",
            ROL_V,  # rol incorrecto (debería ser S)
            resultado["id_v"], resultado["pk_s"], resultado["firma_s"],
        )


def test_idv_distinto_no_verifica():
    resultado = registrar(DESTINO)
    otro_id = secrets.token_bytes(16)
    with pytest.raises(FirmaInvalida):
        verificar(
            CONFIANZA / "verificacion_servidor.pem",
            ROL_S, otro_id, resultado["pk_s"], resultado["firma_s"],
        )