import os
import secrets
from pathlib import Path

from Crypto.PublicKey import RSA

from protocolo.firmas import (
    FirmaInvalida,
    ROL_S,
    ROL_V,
    defensa_activa,
    firmar,
    verificar,
)
from protocolo.mensajes import TIPO_REGISTRO, TIPO_RESPUESTA, conectar, emitir, leer

IDENTIDAD = Path("/datos/identidad")
CONFIANZA = Path("/datos/confianza")
TRAZA = Path("/datos/traza-victima/registro")


def _prefijo(datos, inicio):
    if inicio + 2 > len(datos):
        raise ValueError("campo incompleto")
    largo = int.from_bytes(datos[inicio:inicio + 2], "big")
    fin = inicio + 2 + largo
    if fin > len(datos):
        raise ValueError("campo incompleto")
    return datos[inicio + 2:fin], fin


def empaquetar(id_v, publica, firma):
    return (
        id_v
        + len(publica).to_bytes(2, "big")
        + publica
        + len(firma).to_bytes(2, "big")
        + firma
    )


def desempaquetar(cuerpo):
    id_v = cuerpo[:16]
    publica, pos = _prefijo(cuerpo, 16)
    firma, pos = _prefijo(cuerpo, pos)
    if len(id_v) != 16 or pos != len(cuerpo) or not publica:
        raise ValueError("registro mal formado")
    return id_v, publica, firma


def _trazar(id_v, detalle):
    TRAZA.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA.open("a", encoding="utf-8") as salida:
        salida.write(f"registro {id_v.hex()} ok {detalle}\n")


def _intercambiar(id_v, pk_v, firma, destino):
    enviado = emitir(TIPO_REGISTRO, empaquetar(id_v, pk_v, firma))
    with conectar(destino) as conexion:
        conexion.sendall(enviado)
        try:
            tipo, cuerpo = leer(conexion)
        except ConnectionError as error:
            raise ValueError("el servidor cerró la conexión antes de responder") from error
    if tipo != TIPO_RESPUESTA:
        raise ValueError("respuesta de registro")
    id_resp, pk_s, firma_s = desempaquetar(cuerpo)
    if id_resp != id_v:
        raise ValueError("idV")
    return pk_s, enviado, emitir(tipo, cuerpo), firma_s


def _verificar_servidor(id_v, pk_s, firma_s):
    if not defensa_activa():
        return
    try:
        verificar(CONFIANZA / "verificacion_servidor.pem", ROL_S, id_v, pk_s, firma_s)
    except FirmaInvalida as error:
        _trazar(id_v, "error-firma-servidor")
        raise ValueError(f"firma del servidor no verifica: {error}") from error


def registrar(destino):
    clave = RSA.generate(2048, e=65537)
    id_v = secrets.token_bytes(16)
    pk_v = clave.publickey().export_key(format="DER", pkcs=8)
    sk_v = clave.export_key(format="DER")
    IDENTIDAD.mkdir(parents=True, exist_ok=True)
    (IDENTIDAD / "idV").write_bytes(id_v)
    (IDENTIDAD / "pkV.der").write_bytes(pk_v)
    (IDENTIDAD / "skV.der").write_bytes(sk_v)
    firma = firmar(CONFIANZA / "propia.pem", ROL_V, id_v, pk_v)
    pk_s, enviado, recibido, firma_s = _intercambiar(id_v, pk_v, firma, destino)
    _verificar_servidor(id_v, pk_s, firma_s)
    _trazar(id_v, "asociada")
    return {
        "id_v": id_v,
        "pk_v": pk_v,
        "sk_v": sk_v,
        "pk_s": pk_s,
        "firma_s": firma_s,
        "enviado": enviado,
        "recibido": recibido,
    }


def repetir(id_v, pk_v, sk_v, destino):
    firma = firmar(CONFIANZA / "propia.pem", ROL_V, id_v, pk_v)
    pk_s, _enviado, _recibido, firma_s = _intercambiar(id_v, pk_v, firma, destino)
    _verificar_servidor(id_v, pk_s, firma_s)
    _trazar(id_v, "misma")
    return {"id_v": id_v, "pk_v": pk_v, "sk_v": sk_v, "pk_s": pk_s, "firma_s": firma_s}