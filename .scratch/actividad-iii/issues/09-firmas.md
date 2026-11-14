# 09: Firmas

**What to build:** Con una vÃ­ctima nueva y la defensa encendida, el intermediario no consigue que la entrega de sV salga. Su sustituciÃ³n de pkS se rechaza, y tambiÃ©n se rechaza una firma hecha con sus propias claves aunque adjunte su clave de verificaciÃ³n. En un intercambio aparte, la vÃ­ctima legÃ­tima y el servidor completan cifrado, reinicio y pago.

**Blocked by:** 06 Pago y comparaciÃ³n, 08 Intermediario

**Status:** ready-for-agent

- [ ] preparar instala, antes del paso 1, la clave de verificaciÃ³n del otro en la vÃ­ctima y en el servidor. El intermediario recibe un par de firma propio que ninguno de los dos acepta.
- [ ] Cada firma es ECDSA P-256 con SHA-256 y usa un par distinto de (pkV, skV) y de (pkS, skS). Lo firmado es `actividad-iii/v1`, el rol `V` o `S`, idV y la clave RSA pÃºblica. La clave de verificaciÃ³n no viaja en el mensaje.
- [ ] Con la defensa encendida, una pkS sustituida o una firma del intermediario detiene el intercambio antes de que exista una entrega de sV.
- [ ] El idV de esta prueba es distinto del de las pruebas anteriores.
- [ ] El intercambio legÃ­timo de `pruebas/firmas` cifra, reinicia y recupera sV por pago, y la comparaciÃ³n con el original cuadra.


## Answer

Implementado en:
- `protocolo/firmas.py` (ECDSA P-256/SHA-256).
- `laboratorio/preparar_entrega.py` (pares + instalación cruzada + par del intermediario).
- `protocolo/registro.py` y `servidor/__main__.py` (firman y verifican; defensa ON por defecto vía `DEFENSA`).
- `pruebas/contenedores/test_firmas.py` (4 tests, dentro de `12 passed`).

Pendiente: el ítem "el intercambio legítimo cifra, reinicia y paga" depende del issue 06 (pago y comparación).

## Answer (item pendiente resuelto)

El item "el intercambio legitimo cifra, reinicia y paga" quedo cubierto:
- `pruebas/contenedores/test_pago.py` verifica cifrado + pago + descifrado.
- `pruebas/contenedores/test_reinicio.py` verifica cierre y reinicio.
- Corrida conjunta: `17 passed` (12 previos + 2 pago + 2 investigacion + 1 mitm).

