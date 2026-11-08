# 06: Pago y comparación

**What to build:** Sobre un incidente ya reiniciado, la víctima pide la recuperación. El pago es un evento del protocolo: el servidor marca el registro como pagado y devuelve sV cifrada con la pkV que ya guardaba. La víctima descifra los tres Ci y la comparación los iguala, byte a byte, con el original. La prueba queda en su propia carpeta.

**Blocked by:** 05 Cierre y reinicio

**Status:** ready-for-agent

- [ ] La solicitud lleva idV y no puede cambiar la pkV del registro.
- [ ] La respuesta es OAEP.Enc(pkV, sV) usando esa pkV guardada, y el estado del pago pasa a pagado.
- [ ] La víctima abre sV con skV, regenera cada Ki, reconstruye el mismo AAD y descifra con el nonce y la etiqueta guardados.
- [ ] Solo los descifrados con etiqueta válida se guardan, y los tres coinciden byte a byte con el original.
- [ ] Toda la evidencia queda en `pruebas/pago`, separada de las otras pruebas.
