from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Signature.pss import MGF1


def _mgf1(semilla, longitud):
    return MGF1(semilla, longitud, SHA256)


def abrir(clave):
    return PKCS1_OAEP.new(clave, hashAlgo=SHA256, mgfunc=_mgf1, label=b"")
