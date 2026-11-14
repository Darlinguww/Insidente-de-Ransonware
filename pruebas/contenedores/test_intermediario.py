"""Intermediario (MITM): sustitución, captura y descifrado sin pago."""

import os
from pathlib import Path

from protocolo.cifrado import cifrar
from protocolo.descifrado import descifrar_todos
from protocolo.entrega import entregar
from protocolo.registro import registrar

DESTINO = "intermediario_mitm"
REGISTRO = Path("/datos/registro")
PUBLICO = Path("/datos/publico/ya-registrado")
IDENTIDAD = Path("/datos/identidad")
INTERCEPTADO = Path("/datos/interceptado")
TRAZA_MITM = Path("/datos/traza-mitm/eventos")
CIFRADOS = Path("/datos/cifrados")
RECUPERADOS = Path("/datos/recuperados")
COPIA = Path("/datos/copias/notas.txt")
NOTAS = b"Notas de la Actividad III, copia de practica de 64 bytes. lista\n"


def _limpiar():
    """Borra solo lo que el contenedor puede escribir: cifrados y recuperados."""
    for carpeta in (CIFRADOS, RECUPERADOS):
        if carpeta.is_dir():
            for ruta in carpeta.iterdir():
                if ruta.is_file():
                    ruta.unlink()


def test_mitm_captura_sv_sin_pago():
    _limpiar()
    os.environ["DEFENSA"] = "off"
    try:
        resultado = registrar(DESTINO)
        id_v = resultado["id_v"]
        pk_v = resultado["pk_v"]

        carpeta = PUBLICO / id_v.hex()
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "pkV.der").write_bytes(pk_v)

        IDENTIDAD.mkdir(parents=True, exist_ok=True)
        (IDENTIDAD / "idV").write_bytes(id_v)
        (IDENTIDAD / "pkV.der").write_bytes(pk_v)
        (IDENTIDAD / "skV.der").write_bytes(resultado["sk_v"])

        # La víctima entrega sV cifrada con la pkS SUSTITUIDA
        sv_victima, confirmacion = entregar(id_v, resultado["pk_s"], DESTINO)
        assert confirmacion == id_v
    finally:
        os.environ["DEFENSA"] = "on"

    # El intermediario capturó sV
    capturada = (INTERCEPTADO / "sV").read_bytes()
    assert len(capturada) == 32
    assert capturada == sv_victima

    # El servidor guardó la misma sV, sin que la víctima pagara
    sv_servidor = (REGISTRO / "incidentes" / id_v.hex() / "sV").read_bytes()
    assert sv_servidor == sv_victima
    pago = REGISTRO / "incidentes" / id_v.hex() / "pago"
    assert pago.read_text() == "pendiente"

    # Traza del MITM: filtra por idV para no depender de corridas viejas
    traza = TRAZA_MITM.read_text() if TRAZA_MITM.is_file() else ""
    assert f"idV={id_v.hex()} sustitucion" in traza
    assert f"idV={id_v.hex()} interceptada" in traza

    # Con sV capturada, descifra los tres Ci sin pago
    COPIA.parent.mkdir(parents=True, exist_ok=True)
    COPIA.write_bytes(NOTAS)
    cifrar(id_v, sv_victima)
    validos = descifrar_todos(id_v, sv_victima)
    assert validos == ["0000", "0001", "0002"]
    for nombre in validos:
        assert (RECUPERADOS / nombre).read_bytes() == NOTAS