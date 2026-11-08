import socket
import sys
from pathlib import Path

PUERTO = 5000
ORIGINALES = Path("/datos/originales")
COPIAS = Path("/datos/copias")


def estado_originales():
    if not ORIGINALES.exists():
        return "ausente"
    sonda = ORIGINALES / ".sonda"
    try:
        sonda.write_bytes(b"x")
    except OSError:
        return "lectura"
    sonda.unlink(missing_ok=True)
    return "escritura"


def preparar():
    from laboratorio.preparar import copiar

    nombres = ",".join(copiar())
    return f"preparado=si nombres={nombres}"


def leer_copia():
    destino = COPIAS / "notas.txt"
    if not destino.is_file():
        return "ausente"
    return destino.read_bytes().hex()


def responder(rol, orden):
    if orden == "estado":
        return f"rol={rol} originales={estado_originales()}"
    if orden == "preparar" and rol == "comparacion":
        return preparar()
    if orden == "leer-copia":
        return leer_copia()
    return "orden=desconocida"


def main():
    rol = sys.argv[1]
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("0.0.0.0", PUERTO))
    servidor.listen()
    while True:
        conexion, _ = servidor.accept()
        with conexion:
            orden = conexion.recv(1024).decode("utf-8").strip()
            conexion.sendall(f"{responder(rol, orden)}\n".encode("utf-8"))


if __name__ == "__main__":
    main()
