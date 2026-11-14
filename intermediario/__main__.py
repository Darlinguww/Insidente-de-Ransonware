"""Intermediario (MITM): sustituye pkS, captura sV, reenvía al servidor."""

import os
import socket
from pathlib import Path

from Crypto.PublicKey import RSA

from protocolo.mensajes import (
    PUERTO,
    TIPO_CONFIRMACION,
    TIPO_ENTREGA,
    TIPO_ERROR,
    TIPO_REGISTRO,
    TIPO_RESPUESTA,
    conectar,
    emitir,
    leer,
)
from protocolo.oaep import abrir
from protocolo.registro import desempaquetar, empaquetar

CONFIANZA = Path("/datos/confianza")
INTERCEPTADO = Path("/datos/interceptado")
TRAZA = Path("/datos/traza-mitm/eventos")
PK_S_REAL = INTERCEPTADO / "pkS_real.der"
DESTINO_REAL = os.environ.get("DESTINO_REAL", "entrega")


def _trazar(detalle):
    TRAZA.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA.open("a", encoding="utf-8") as salida:
        salida.write(f"mitm {detalle}\n")


def _par_rsa():
    CONFIANZA.mkdir(parents=True, exist_ok=True)
    sk = CONFIANZA / "skS-mitm.der"
    pk = CONFIANZA / "pkS-mitm.der"
    if not (sk.is_file() and pk.is_file()):
        clave = RSA.generate(2048, e=65537)
        sk.write_bytes(clave.export_key(format="DER"))
        pk.write_bytes(clave.publickey().export_key(format="DER"))
    return RSA.import_key(sk.read_bytes()), RSA.import_key(pk.read_bytes())


def _manejar_registro(conexion, cuerpo, pk_mitm):
    try:
        id_v, pk_v, firma_v = desempaquetar(cuerpo)
    except ValueError:
        return
    _trazar(f"registro idV={id_v.hex()} recibido")
    with conectar(DESTINO_REAL) as s:
        s.sendall(emitir(TIPO_REGISTRO, empaquetar(id_v, pk_v, firma_v)))
        try:
            tipo_r, cuerpo_r = leer(s)
        except (ConnectionError, ValueError):
            conexion.sendall(emitir(TIPO_ERROR, id_v + b"servidor"))
            return
    if tipo_r != TIPO_RESPUESTA:
        conexion.sendall(emitir(TIPO_ERROR, id_v + b"servidor"))
        return
    try:
        id_resp, pk_s_real, _firma_s = desempaquetar(cuerpo_r)
    except ValueError:
        conexion.sendall(emitir(TIPO_ERROR, id_v + b"servidor"))
        return
    if id_resp != id_v:
        conexion.sendall(emitir(TIPO_ERROR, id_v + b"idV"))
        return
    INTERCEPTADO.mkdir(parents=True, exist_ok=True)
    PK_S_REAL.write_bytes(pk_s_real)
    pk_s_falsa = pk_mitm.export_key(format="DER", pkcs=8)
    conexion.sendall(emitir(TIPO_RESPUESTA, empaquetar(id_v, pk_s_falsa, b"")))
    _trazar(f"registro idV={id_v.hex()} sustitucion")


def _manejar_entrega(conexion, cuerpo, sk_mitm):
    id_v = cuerpo[:16]
    try:
        sv = abrir(sk_mitm).decrypt(cuerpo[16:])
    except (ValueError, LookupError):
        conexion.sendall(emitir(TIPO_ERROR, id_v + b"no-abre"))
        _trazar(f"entrega idV={id_v.hex()} no-abre")
        return
    if len(sv) != 32:
        conexion.sendall(emitir(TIPO_ERROR, id_v + b"largo"))
        return
    INTERCEPTADO.mkdir(parents=True, exist_ok=True)
    (INTERCEPTADO / "sV").write_bytes(sv)
    _trazar(f"entrega idV={id_v.hex()} interceptada")
    if not PK_S_REAL.is_file():
        conexion.sendall(emitir(TIPO_ERROR, id_v + b"sin-pks"))
        return
    cifrado_real = abrir(RSA.import_key(PK_S_REAL.read_bytes())).encrypt(sv)
    with conectar(DESTINO_REAL) as s:
        s.sendall(emitir(TIPO_ENTREGA, id_v + cifrado_real))
        try:
            tipo, cuerpo = leer(s)
        except (ConnectionError, ValueError):
            conexion.sendall(emitir(TIPO_ERROR, id_v + b"servidor"))
            return
    if tipo == TIPO_CONFIRMACION and cuerpo == id_v:
        conexion.sendall(emitir(TIPO_CONFIRMACION, id_v))
        _trazar(f"entrega idV={id_v.hex()} reenviada")
        return
    if tipo == TIPO_ERROR and cuerpo[:16] == id_v:
        conexion.sendall(emitir(TIPO_ERROR, cuerpo))
        return
    conexion.sendall(emitir(TIPO_ERROR, id_v + b"respuesta"))


def _atender(conexion, sk_mitm, pk_mitm):
    with conexion:
        try:
            tipo, cuerpo = leer(conexion)
        except (ConnectionError, ValueError):
            return
        if tipo == TIPO_REGISTRO:
            _manejar_registro(conexion, cuerpo, pk_mitm)
        elif tipo == TIPO_ENTREGA and len(cuerpo) >= 16:
            _manejar_entrega(conexion, cuerpo, sk_mitm)


def main():
    sk_mitm, pk_mitm = _par_rsa()
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("0.0.0.0", PUERTO))
    servidor.listen()
    while True:
        conexion, _ = servidor.accept()
        try:
            _atender(conexion, sk_mitm, pk_mitm)
        except Exception:
            continue


if __name__ == "__main__":
    main()