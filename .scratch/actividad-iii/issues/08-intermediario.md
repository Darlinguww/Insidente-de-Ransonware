# 08: Intermediario

**What to build:** Con la defensa apagada, la vÃ­ctima habla con el intermediario y este reenvÃ­a al servidor. El intermediario sustituye pkS, abre sV, la conserva y la reenvÃ­a cifrada para el servidor. VÃ­ctima y servidor terminan con la misma semilla y el cifrado se completa. DespuÃ©s, con el servidor apagado, el intermediario descifra copias de los cifrados sin pago.

**Blocked by:** 04 Cifrado de notas.txt

**Status:** ready-for-agent

- [ ] La vÃ­ctima envÃ­a sV cifrada con la clave sustituida, y el intermediario la abre con su clave privada de cifrado.
- [ ] El intermediario reenvÃ­a la misma sV cifrada con la pkS real. El servidor la guarda bajo idV junto a la pkV real.
- [ ] La vÃ­ctima cifra `notas.txt` con i igual a 0, 1 y 2, y esas salidas siguen en disco despuÃ©s de cerrar vÃ­ctima y servidor.
- [ ] Con el servidor apagado y copias de esos cifrados, el intermediario recupera los tres archivos sin pago.
- [ ] Las trazas muestran la sustituciÃ³n, la apertura y el reenvÃ­o, y la evidencia queda en `pruebas/mitm`.


## Answer

Implementado y verificado. Corrida conjunta: `17 passed` en `prueba_entrega`.
