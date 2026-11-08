import sys
from pathlib import Path

IDENTIDAD = Path("/datos/identidad")
CIFRADOS = Path("/datos/cifrados")
TRAZA = Path("/datos/traza-victima/reinicio")
PERMITIDOS = ("idV", "pkV.der", "skV.der")
SALIDAS = ("0000", "0001", "0002")


def _nombres(carpeta):
    if not carpeta.is_dir():
        raise FileNotFoundError(carpeta)
    return {ruta.name for ruta in carpeta.iterdir() if ruta.is_file()}


def cargar():
    if _nombres(IDENTIDAD) != set(PERMITIDOS) or _nombres(CIFRADOS) != set(SALIDAS):
        raise FileNotFoundError("el disco de la víctima no es el del reinicio")
    id_v = (IDENTIDAD / "idV").read_bytes()
    pk_v = (IDENTIDAD / "pkV.der").read_bytes()
    sk_v = (IDENTIDAD / "skV.der").read_bytes()
    if len(id_v) != 16:
        raise ValueError("idV")
    partes = [f"pkV={pk_v[:4].hex()}", f"skV={sk_v[:4].hex()}"]
    for nombre in SALIDAS:
        partes.append(f"{nombre}={(CIFRADOS / nombre).read_bytes()[:1].hex()}")
    TRAZA.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA.open("a", encoding="utf-8") as salida:
        salida.write(f"reinicio {id_v.hex()} ok {','.join(partes)}\n")
    return id_v, pk_v, sk_v


def main():
    try:
        cargar()
    except (OSError, ValueError):
        sys.exit(1)


if __name__ == "__main__":
    main()
