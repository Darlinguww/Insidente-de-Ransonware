"""Descifra los tres Ci con sV y los deja en /datos/recuperados."""

from pathlib import Path

from protocolo.cifrado import CifradoRechazado, descifrar

CIFRADOS = Path("/datos/cifrados")
RECUPERADOS = Path("/datos/recuperados")
SALIDAS = ("0000", "0001", "0002")
TRAZA = Path("/datos/traza-victima/descifrado")


def descifrar_todos(id_v, sv):
    """Descifra 0000, 0001, 0002. Devuelve la lista de planos válidos."""
    RECUPERADOS.mkdir(parents=True, exist_ok=True)
    TRAZA.parent.mkdir(parents=True, exist_ok=True)
    validos = []
    for nombre in SALIDAS:
        ruta = CIFRADOS / nombre
        try:
            plano = descifrar(ruta, sv)
        except CifradoRechazado as error:
            with TRAZA.open("a", encoding="utf-8") as salida:
                salida.write(f"descifrado {id_v.hex()} error {nombre} {error}\n")
            continue
        destino = RECUPERADOS / nombre
        destino.write_bytes(plano)
        validos.append(nombre)
        with TRAZA.open("a", encoding="utf-8") as salida:
            salida.write(f"descifrado {id_v.hex()} ok {nombre}\n")
    return validos