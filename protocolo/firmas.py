"""Firmas ECDSA P-256 con SHA-256 para la Actividad III.

Lo firmado es: b"actividad-iii/v1" + rol (1 byte) + idV (16 bytes) + DER
SubjectPublicKeyInfo de la clave RSA. La clave de verificación no viaja en
el mensaje: cada participante la tiene instalada de antemano.
"""

from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

PREFIJO = b"actividad-iii/v1"
ROL_V = b"V"
ROL_S = b"S"


class FirmaInvalida(Exception):
    pass


def _mensaje(rol, id_v, pk_der):
    if rol not in (ROL_V, ROL_S):
        raise ValueError("rol")
    if len(id_v) != 16:
        raise ValueError("idV")
    return PREFIJO + rol + id_v + pk_der


def generar_par(ruta_privada, ruta_publica):
    """Genera un par ECDSA P-256 y lo guarda en PEM."""
    clave = ec.generate_private_key(ec.SECP256R1())
    ruta_privada = Path(ruta_privada)
    ruta_publica = Path(ruta_publica)
    ruta_privada.parent.mkdir(parents=True, exist_ok=True)
    ruta_publica.parent.mkdir(parents=True, exist_ok=True)
    ruta_privada.write_bytes(
        clave.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    ruta_publica.write_bytes(
        clave.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def _cargar_privada(ruta):
    clave = serialization.load_pem_private_key(Path(ruta).read_bytes(), password=None)
    if not isinstance(clave, ec.EllipticCurvePrivateKey) or not isinstance(
        clave.curve, ec.SECP256R1
    ):
        raise ValueError("la clave privada no es ECDSA P-256")
    return clave


def _cargar_publica(ruta):
    try:
        clave = serialization.load_pem_public_key(Path(ruta).read_bytes())
    except (OSError, ValueError) as error:
        raise FirmaInvalida("clave de verificación ausente") from error
    if not isinstance(clave, ec.EllipticCurvePublicKey) or not isinstance(
        clave.curve, ec.SECP256R1
    ):
        raise FirmaInvalida("clave de verificación no es ECDSA P-256")
    return clave


def firmar(ruta_privada, rol, id_v, pk_der):
    return _cargar_privada(ruta_privada).sign(
        _mensaje(rol, id_v, pk_der), ec.ECDSA(hashes.SHA256())
    )


def verificar(ruta_publica, rol, id_v, pk_der, firma):
    clave = _cargar_publica(ruta_publica)
    try:
        clave.verify(firma, _mensaje(rol, id_v, pk_der), ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as error:
        raise FirmaInvalida("firma") from error
    return True


def defensa_activa():
    import os

    return os.environ.get("DEFENSA", "on").strip().lower() != "off"