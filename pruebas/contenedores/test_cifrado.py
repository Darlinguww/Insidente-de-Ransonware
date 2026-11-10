"""Cifrado de notas.txt, observado en las tres salidas."""

import secrets
from pathlib import Path

import pytest
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256

from protocolo.cifrado import CifradoRechazado, cifrar, descifrar

NOTAS = b"Notas de la Actividad III, copia de practica de 64 bytes. lista\n"
COPIA = Path("/datos/copias/notas.txt")
CIFRADOS = Path("/datos/cifrados")
RECUPERADOS = Path("/datos/recuperados")
SV = bytes(range(32))


def _abrir(blob, sv):
    assert blob[:4] == b"A3C1"
    assert blob[4] == 1
    id_v = blob[5:21]
    i = int.from_bytes(blob[21:29], "big")
    nonce = blob[29:41]
    etiqueta = blob[41:57]
    largo = int.from_bytes(blob[57:59], "big")
    nombre = blob[59:59 + largo]
    ci = blob[59 + largo:]
    assert len(nonce) == 12 and len(etiqueta) == 16
    ki = HMAC.new(sv, i.to_bytes(8, "big"), digestmod=SHA256).digest()
    aes = AES.new(ki, AES.MODE_GCM, nonce=nonce, mac_len=16)
    aes.update(id_v + i.to_bytes(8, "big"))
    plano = aes.decrypt_and_verify(ci, etiqueta)
    return id_v, i, nonce, nombre, plano


def test_la_copia_queda_cifrada_tres_veces_y_una_etiqueta_rota_se_rechaza():
    assert len(NOTAS) == 64
    id_v = secrets.token_bytes(16)
    COPIA.parent.mkdir(parents=True, exist_ok=True)
    COPIA.write_bytes(NOTAS)
    CIFRADOS.mkdir(parents=True, exist_ok=True)
    for ruta in CIFRADOS.iterdir():
        if ruta.is_file():
            ruta.unlink()
    try:
        cifrar(id_v, SV)
        nonces = set()
        for i, nombre in enumerate(("0000", "0001", "0002")):
            blob = (CIFRADOS / nombre).read_bytes()
            leido, contador, nonce, archivo, plano = _abrir(blob, SV)
            assert leido == id_v
            assert contador == i
            assert archivo == b"notas.txt"
            assert plano == NOTAS
            assert nonce not in nonces
            nonces.add(nonce)
            assert descifrar(CIFRADOS / nombre, SV) == NOTAS

        rota = bytearray((CIFRADOS / "0001").read_bytes())
        rota[41] ^= 0x01
        (CIFRADOS / "0001").write_bytes(rota)
        with pytest.raises(CifradoRechazado):
            descifrar(CIFRADOS / "0001", SV)
        assert not any(RECUPERADOS.glob("*")) if RECUPERADOS.exists() else True
        assert not (Path("/datos/identidad") / "sV").exists()
        assert not (Path("/datos/identidad") / "Ki").exists()
    finally:
        for nombre in ("0000", "0001", "0002"):
            (CIFRADOS / nombre).unlink(missing_ok=True)
