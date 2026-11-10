import socket
import time

PUERTO = 7000
TIPO_REGISTRO = 1
TIPO_RESPUESTA = 2
TIPO_ENTREGA = 3
TIPO_CONFIRMACION = 4
TIPO_ERROR = 7
_MAXIMO = 65536


def emitir(tipo, cuerpo):
    return (1 + len(cuerpo)).to_bytes(4, "big") + bytes([tipo]) + cuerpo


def _exacto(conexion, cantidad):
    datos = b""
    while len(datos) < cantidad:
        parte = conexion.recv(cantidad - len(datos))
        if not parte:
            raise ConnectionError("la conexión se cerró antes de completar el mensaje")
        datos += parte
    return datos


def leer(conexion):
    cantidad = int.from_bytes(_exacto(conexion, 4), "big")
    if not 1 <= cantidad <= _MAXIMO:
        raise ValueError("la longitud del mensaje está fuera de límite")
    resto = _exacto(conexion, cantidad)
    return resto[0], resto[1:]


def conectar(destino):
    ultimo = None
    for _ in range(50):
        try:
            return socket.create_connection((destino, PUERTO), timeout=5)
        except OSError as error:
            ultimo = error
            time.sleep(0.1)
    raise ConnectionError(ultimo)
