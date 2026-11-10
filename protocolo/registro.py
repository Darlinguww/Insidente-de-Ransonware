import secrets
from pathlib import Path

from Crypto.PublicKey import RSA

from protocolo.mensajes import TIPO_REGISTRO, TIPO_RESPUESTA, conectar, emitir, leer

IDENTIDAD = Path("/datos/identidad")
TRAZA = Path("/datos/traza-victima/registro")


def _prefijo(datos, inicio):
    if inicio + 2 > len(datos):
        raise ValueError("campo incompleto")
    largo = int.from_bytes(datos[inicio:inicio + 2], "big")
    fin = inicio + 2 + largo
    if fin > len(datos):
        raise ValueError("campo incompleto")
    return datos[inicio + 2:fin], fin


def empaquetar(id_v, publica):
    return id_v + len(publica).to_bytes(2, "big") + publica + (0).to_bytes(2, "big")


def desempaquetar(cuerpo):
    id_v = cuerpo[:16]
    publica, pos = _prefijo(cuerpo, 16)
    _firma, pos = _prefijo(cuerpo, pos)
    if len(id_v) != 16 or pos != len(cuerpo) or not publica:
        raise ValueError("registro mal formado")
    return id_v, publica


def _trazar(id_v, detalle):
    TRAZA.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA.open("a", encoding="utf-8") as salida:
        salida.write(f"registro {id_v.hex()} ok {detalle}\n")


def _intercambiar(id_v, pk_v, destino):
    enviado = emitir(TIPO_REGISTRO, empaquetar(id_v, pk_v))
    with conectar(destino) as conexion:
        conexion.sendall(enviado)
        tipo, cuerpo = leer(conexion)
    if tipo != TIPO_RESPUESTA:
        raise ValueError("respuesta de registro")
    id_resp, pk_s = desempaquetar(cuerpo)
    if id_resp != id_v:
        raise ValueError("idV")
    return pk_s, enviado, emitir(tipo, cuerpo)


def registrar(destino):
    clave = RSA.generate(2048, e=65537)
    id_v = secrets.token_bytes(16)
    pk_v = clave.publickey().export_key(format="DER", pkcs=8)
    sk_v = clave.export_key(format="DER")
    IDENTIDAD.mkdir(parents=True, exist_ok=True)
    (IDENTIDAD / "idV").write_bytes(id_v)
    (IDENTIDAD / "pkV.der").write_bytes(pk_v)
    (IDENTIDAD / "skV.der").write_bytes(sk_v)
    pk_s, enviado, recibido = _intercambiar(id_v, pk_v, destino)
    _trazar(id_v, "asociada")
    return {
        "id_v": id_v,
        "pk_v": pk_v,
        "sk_v": sk_v,
        "pk_s": pk_s,
        "enviado": enviado,
        "recibido": recibido,
    }


def repetir(id_v, pk_v, sk_v, destino):
    pk_s, _enviado, _recibido = _intercambiar(id_v, pk_v, destino)
    _trazar(id_v, "misma")
    return {"id_v": id_v, "pk_v": pk_v, "sk_v": sk_v, "pk_s": pk_s}
