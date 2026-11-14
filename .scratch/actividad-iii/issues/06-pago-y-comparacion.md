# 06: Pago y comparaciÃ³n

**What to build:** Sobre un incidente ya reiniciado, la vÃ­ctima pide la recuperaciÃ³n. El pago es un evento del protocolo: el servidor marca el registro como pagado y devuelve sV cifrada con la pkV que ya guardaba. La vÃ­ctima descifra los tres Ci y la comparaciÃ³n los iguala, byte a byte, con el original. La prueba queda en su propia carpeta.

**Blocked by:** 05 Cierre y reinicio

**Status:** ready-for-agent

- [ ] La solicitud lleva idV y no puede cambiar la pkV del registro.
- [ ] La respuesta es OAEP.Enc(pkV, sV) usando esa pkV guardada, y el estado del pago pasa a pagado.
- [ ] La vÃ­ctima abre sV con skV, regenera cada Ki, reconstruye el mismo AAD y descifra con el nonce y la etiqueta guardados.
- [ ] Solo los descifrados con etiqueta vÃ¡lida se guardan, y los tres coinciden byte a byte con el original.
- [ ] Toda la evidencia queda en `pruebas/pago`, separada de las otras pruebas.


## Answer

Implementado y verificado. Corrida conjunta: `17 passed` en `prueba_entrega`.
