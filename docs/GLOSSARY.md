# Actividad III

Simulación de un incidente de ransomware entre una víctima y un servidor, con un intermediario en la prueba de sustitución.

## Participantes

**víctima**:
El participante dueño de los archivos del incidente.
_Avoid_: cliente, Bob, Alice

**servidor**:
El participante que conserva el registro de la víctima.
_Avoid_: Alice, Bob

**intermediario**:
El participante situado entre la víctima y el servidor.
_Avoid_: proxy, atacante, MITM

## Incidente

**idV**:
El identificador del único incidente de una víctima.
_Avoid_: id, uuid, victim_id

**sV**:
La semilla maestra de la víctima para ese incidente.
_Avoid_: clave, secreto de sesión, semilla de OAEP

**pago**:
El evento del protocolo que marca el incidente como pagado.
_Avoid_: dinero, transacción, factura

## Claves de cifrado

**pkV**:
La clave pública RSA de la víctima para el cifrado.
_Avoid_: clave de firma, certificado

**skV**:
La clave privada RSA de la víctima, pareja de pkV.
_Avoid_: clave de firma

**pkS**:
La clave pública RSA del servidor para el cifrado.
_Avoid_: clave de firma, certificado

**skS**:
La clave privada RSA del servidor, pareja de pkS.
_Avoid_: clave de firma

## Firmas

**clave de verificación**:
La clave pública de firma que un participante ya acepta como del otro.
_Avoid_: pkV, pkS, certificado

## Archivos

**i**:
El contador que distingue un archivo dentro del incidente.
_Avoid_: índice de nonce, número de sesión

**Ki**:
La clave del archivo identificado por i.
_Avoid_: clave de sesión, sV

**Ci**:
El contenido cifrado del archivo i.
_Avoid_: archivo original, paquete TCP

**copia**:
El archivo de trabajo que la víctima cifra en el incidente.
_Avoid_: original, Ci

**original**:
El archivo reservado para la comparación final.
_Avoid_: copia, Ci
