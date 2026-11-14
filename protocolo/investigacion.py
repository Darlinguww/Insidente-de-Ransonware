"""Recuperación de sV por búsqueda exhaustiva (0..2^24-1)."""

import time
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256

CIFRADOS = Path("/datos/cifrados")
SALIDAS = ("0000", "0001", "0002")
LIMITE = 1 << 24


def _ki(sv, i):
    return HMAC.new(sv, i.to_bytes(8, "big"), digestmod=SHA256).digest()


def _leer(blob):
    if len(blob) < 59 or blob[:4] != b"A3C1" or blob[4] != 1:
        raise ValueError("formato")
    id_v = blob[5:21]
    i = int.from_bytes(blob[21:29], "big")
    nonce = blob[29:41]
    etiqueta = blob[41:57]
    largo = int.from_bytes(blob[57:59], "big")
    fin = 59 + largo
    nombre = blob[59:fin]
    return id_v, i, nonce, etiqueta, nombre, blob[fin:]


def _verificar(sv, entrada):
    id_v, i, nonce, etiqueta, _nombre, ci = entrada
    try:
        aes = AES.new(_ki(sv, i), AES.MODE_GCM, nonce=nonce, mac_len=16)
        aes.update(id_v + i.to_bytes(8, "big"))
        aes.decrypt_and_verify(ci, etiqueta)
        return True
    except ValueError:
        return False


def _cargar_cifrados():
    return {nombre: _leer((CIFRADOS / nombre).read_bytes()) for nombre in SALIDAS}


def buscar(limite=LIMITE):
    """Recorre candidatas 0..limite-1 en orden. Devuelve (sv, examinadas, segundos)."""
    cifrados = _cargar_cifrados()
    entrada0 = cifrados["0000"]
    if entrada0[1] != 0:
        raise ValueError("la primera salida debe ser i=0")
    inicio = time.monotonic()
    for candidato in range(limite):
        sv = candidato.to_bytes(32, "big")
        if not _verificar(sv, entrada0):
            continue
        if all(_verificar(sv, cifrados[nombre]) for nombre in ("0001", "0002")):
            fin = time.monotonic()
            return sv, candidato + 1, fin - inicio
    raise LookupError("no encontrada")


def escribir_informe(sv, examinadas, segundos, ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(
        f"investigacion ok\n"
        f"candidatas {examinadas}\n"
        f"tiempo_busqueda_s {segundos:.3f}\n"
        f"sv {sv.hex()}\n"
    )