from pathlib import Path

from Crypto.PublicKey import RSA

SECRETO = Path("/datos/secreto")
REGISTRO = Path("/datos/registro")


def asegurar():
    SECRETO.mkdir(parents=True, exist_ok=True)
    REGISTRO.mkdir(parents=True, exist_ok=True)
    sk = SECRETO / "skS.der"
    pk = REGISTRO / "pkS.der"
    if sk.is_file() and pk.is_file():
        return
    clave = RSA.generate(2048, e=65537)
    sk.write_bytes(clave.export_key(format="DER"))
    pk.write_bytes(clave.publickey().export_key(format="DER"))


def privada():
    return RSA.import_key((SECRETO / "skS.der").read_bytes())


def par_cargado():
    sk = privada()
    pk = RSA.import_key((REGISTRO / "pkS.der").read_bytes())
    if (sk.n, sk.e) != (pk.n, pk.e):
        raise ValueError("el par RSA no coincide")
    return sk
