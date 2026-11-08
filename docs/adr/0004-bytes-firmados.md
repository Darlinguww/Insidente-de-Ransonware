# Lo firmado ata la clave RSA a idV y al rol

Firmar solo `pkV` o `pkS` no impediría reutilizar esa firma en otro incidente. Lo firmado es la cadena `actividad-iii/v1`, el rol `V` o `S`, los 16 bytes de `idV` y la clave pública RSA en DER SubjectPublicKeyInfo. La firma ECDSA viaja aparte y la clave de verificación no va en el mensaje, así el intermediario no puede colar la suya.
