import sys
from pathlib import Path

ORIGINALES = Path("/datos/originales/notas.txt")
COPIAS = Path("/datos/copias")


def copiar():
    COPIAS.mkdir(parents=True, exist_ok=True)
    (COPIAS / "notas.txt").write_bytes(ORIGINALES.read_bytes())
    return sorted(ruta.name for ruta in COPIAS.iterdir() if ruta.is_file())


def main():
    if copiar() != ["notas.txt"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
