"""Investigación: recuperar sV solo con los tres cifrados."""

import secrets
from pathlib import Path

import pytest

from protocolo.cifrado import cifrar
from protocolo.investigacion import buscar, escribir_informe

CIFRADOS = Path("/datos/cifrados")
COPIA = Path("/datos/copias/notas.txt")
INFORME = Path("/datos/traza-investigacion/test.txt")
NOTAS = b"Notas de la Actividad III, copia de practica de 64 bytes. lista\n"


def _limpiar():
    if CIFRADOS.is_dir():
        for ruta in CIFRADOS.iterdir():
            if ruta.is_file():
                ruta.unlink()
    INFORME.unlink(missing_ok=True)


def _cifrar_con(sv):
    _limpiar()
    id_v = secrets.token_bytes(16)
    COPIA.parent.mkdir(parents=True, exist_ok=True)
    COPIA.write_bytes(NOTAS)
    cifrar(id_v, sv)
    return id_v


def test_investigacion_encuentra_la_sv_con_solo_los_cifrados():
    # sv con valor pequeño para que la búsqueda termine rápido
    # incluso en máquinas lentas. 0x0DEA = 3562.
    sv = (0x0DEA).to_bytes(32, "big")
    _cifrar_con(sv)

    encontrada, examinadas, segundos = buscar(limite=1 << 17)

    assert encontrada == sv
    assert examinadas == 0x0DEA + 1  # +1 porque empieza en 0
    assert segundos < 10
    escribir_informe(encontrada, examinadas, segundos, INFORME)
    texto = INFORME.read_text()
    assert "sv " in texto
    assert "candidatas 3563" in texto


def test_investigacion_falla_si_no_encuentra_en_el_limite():
    # sv muy alta, pero buscamos solo hasta 1000.
    sv = (1 << 23).to_bytes(32, "big")
    _cifrar_con(sv)
    with pytest.raises(LookupError):
        buscar(limite=1000)