import socket
from pathlib import Path

from protocolo.mensajes import PUERTO, TIPO_CONFIRMACION, TIPO_ENTREGA, TIPO_ERROR, emitir, leer
from protocolo.oaep import abrir
from servidor.claves import asegurar, par_cargado, privada
from servidor.registro import guardados, guardar, incorporar

TRAZA = Path("/datos/traza-servidor/entrega")
REINICIO = Path("/datos/traza-servidor/reinicio")
CIERRE = Path("/datos/control/cerrar")


def _trazar(id_v, resultado, detalle):
    TRAZA.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA.open("a", encoding="utf-8") as salida:
        salida.write(f"entrega {id_v.hex()} {resultado} {detalle}\n")


def atender(conexion):
    with conexion:
        tipo, cuerpo = leer(conexion)
        if tipo != TIPO_ENTREGA or len(cuerpo) < 16:
            return
        id_v, cifrado = cuerpo[:16], cuerpo[16:]
        incorporar()
        try:
            sv = abrir(privada()).decrypt(cifrado)
            guardar(id_v, sv)
        except (ValueError, LookupError):
            _trazar(id_v, "error", "no-abre")
            conexion.sendall(emitir(TIPO_ERROR, id_v + b"no-abre"))
            return
        _trazar(id_v, "ok", "confirmada")
        conexion.sendall(emitir(TIPO_CONFIRMACION, id_v))


def anunciar():
    par_cargado()
    REINICIO.parent.mkdir(parents=True, exist_ok=True)
    with REINICIO.open("a", encoding="utf-8") as salida:
        for id_v, pago in guardados():
            salida.write(f"reinicio {id_v.hex()} ok {pago}\n")


def main():
    asegurar()
    anunciar()
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("0.0.0.0", PUERTO))
    servidor.settimeout(0.3)
    servidor.listen()
    while True:
        if CIERRE.is_file():
            CIERRE.unlink()
            return
        try:
            conexion, _ = servidor.accept()
        except socket.timeout:
            continue
        try:
            atender(conexion)
        except Exception:
            continue


if __name__ == "__main__":
    main()
