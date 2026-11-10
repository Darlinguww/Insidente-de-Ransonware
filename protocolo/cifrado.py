import secrets
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256

COPIA = Path("/datos/copias/notas.txt")
CIFRADOS = Path("/datos/cifrados")
NOMBRE = b"notas.txt"


class CifradoRechazado(Exception):
    pass


def _ki(sv, i):
    return HMAC.new(sv, i.to_bytes(8, "big"), digestmod=SHA256).digest()


def _empaquetar(id_v, i, nonce, etiqueta, ci):
    return (
        b"A3C1"
        + bytes([1])
        + id_v
        + i.to_bytes(8, "big")
        + nonce
        + etiqueta
        + len(NOMBRE).to_bytes(2, "big")
        + NOMBRE
        + ci
    )


def _leer(blob):
    if len(blob) < 59 or blob[:4] != b"A3C1" or blob[4] != 1:
        raise CifradoRechazado("salida")
    id_v = blob[5:21]
    i = int.from_bytes(blob[21:29], "big")
    nonce = blob[29:41]
    etiqueta = blob[41:57]
    largo = int.from_bytes(blob[57:59], "big")
    fin = 59 + largo
    if fin > len(blob):
        raise CifradoRechazado("salida")
    nombre = blob[59:fin]
    return id_v, i, nonce, etiqueta, nombre, blob[fin:]


def cifrar(id_v, sv):
    plano = COPIA.read_bytes()
    if len(id_v) != 16 or len(sv) != 32 or len(plano) != 64:
        raise ValueError("la copia no está lista")
    CIFRADOS.mkdir(parents=True, exist_ok=True)
    for i in range(3):
        nonce = secrets.token_bytes(12)
        aes = AES.new(_ki(sv, i), AES.MODE_GCM, nonce=nonce, mac_len=16)
        aes.update(id_v + i.to_bytes(8, "big"))
        ci, etiqueta = aes.encrypt_and_digest(plano)
        (CIFRADOS / f"{i:04d}").write_bytes(_empaquetar(id_v, i, nonce, etiqueta, ci))


def descifrar(ruta, sv):
    id_v, i, nonce, etiqueta, nombre, ci = _leer(Path(ruta).read_bytes())
    if nombre != NOMBRE or len(nonce) != 12 or len(etiqueta) != 16 or len(sv) != 32:
        raise CifradoRechazado("salida")
    aes = AES.new(_ki(sv, i), AES.MODE_GCM, nonce=nonce, mac_len=16)
    aes.update(id_v + i.to_bytes(8, "big"))
    try:
        return aes.decrypt_and_verify(ci, etiqueta)
    except ValueError as error:
        raise CifradoRechazado("etiqueta") from error
