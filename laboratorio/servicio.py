import socket
import sys
from pathlib import Path

PUERTO = 5000
ORIGINALES = Path("/datos/originales")
COPIAS = Path("/datos/copias")
ORIGINALES = Path("/datos/originales/notas.txt")
RECUPERADOS = Path("/datos/recuperados")
EVIDENCIA = Path("/datos/comparacion")


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
    if orden == "comparar" and rol == "comparacion":
        return comparar()
    return "orden=desconocida"

def comparar():
    """Compara recuperados vs original. Escribe evidencia y devuelve resumen."""
    EVIDENCIA.mkdir(parents=True, exist_ok=True)
    original = ORIGINALES.read_bytes()
    lineas = []
    ok = True
    for nombre in ("0000", "0001", "0002"):
        ruta = RECUPERADOS / nombre
        if not ruta.is_file():
            lineas.append(f"comparacion - error faltante {nombre}")
            ok = False
            continue
        recuperado = ruta.read_bytes()
        if recuperado == original:
            lineas.append(f"comparacion - ok {nombre}")
        else:
            linea = f"comparacion - error {nombre}"
            for i, (a, b) in enumerate(zip(original, recuperado)):
                if a != b:
                    linea += f" byte={i}"
                    break
            lineas.append(linea)
            ok = False
    (EVIDENCIA / "comparacion.txt").write_text("\n".join(lineas) + "\n")
    return "comparado=si" if ok else "comparado=no"



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
