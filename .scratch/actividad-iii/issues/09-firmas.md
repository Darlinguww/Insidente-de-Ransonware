# 09: Firmas

**What to build:** Con una víctima nueva y la defensa encendida, el intermediario no consigue que la entrega de sV salga. Su sustitución de pkS se rechaza, y también se rechaza una firma hecha con sus propias claves aunque adjunte su clave de verificación. En un intercambio aparte, la víctima legítima y el servidor completan cifrado, reinicio y pago.

**Blocked by:** 06 Pago y comparación, 08 Intermediario

**Status:** ready-for-agent

- [ ] preparar instala, antes del paso 1, la clave de verificación del otro en la víctima y en el servidor. El intermediario recibe un par de firma propio que ninguno de los dos acepta.
- [ ] Cada firma es ECDSA P-256 con SHA-256 y usa un par distinto de (pkV, skV) y de (pkS, skS). Lo firmado es `actividad-iii/v1`, el rol `V` o `S`, idV y la clave RSA pública. La clave de verificación no viaja en el mensaje.
- [ ] Con la defensa encendida, una pkS sustituida o una firma del intermediario detiene el intercambio antes de que exista una entrega de sV.
- [ ] El idV de esta prueba es distinto del de las pruebas anteriores.
- [ ] El intercambio legítimo de `pruebas/firmas` cifra, reinicia y recupera sV por pago, y la comparación con el original cuadra.
