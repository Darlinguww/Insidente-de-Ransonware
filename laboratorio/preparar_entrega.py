import sys
from pathlib import Path

from protocolo.firmas import generar_par


def preparar(base="/datos"):
    base = Path(base)
    victima = base / "confianza_victima"
    servidor = base / "confianza_servidor"
    intermediario = base / "confianza_intermediario"
    # Pares propios
    generar_par(victima / "propia.pem", victima / "publica.pem")
    generar_par(servidor / "propia.pem", servidor / "publica.pem")
    generar_par(intermediario / "propia.pem", intermediario / "publica.pem")
    # Instalación cruzada: cada lado recibe la pública del otro.
    (servidor / "verificacion_victima.pem").write_bytes(
        (victima / "publica.pem").read_bytes()
    )
    (victima / "verificacion_servidor.pem").write_bytes(
        (servidor / "publica.pem").read_bytes()
    )
    # El intermediario no se instala en nadie: su par solo lo usa él.
    return {
        "victima": victima,
        "servidor": servidor,
        "intermediario": intermediario,
    }


def main():
    preparar()
    return 0


if __name__ == "__main__":
    sys.exit(main())