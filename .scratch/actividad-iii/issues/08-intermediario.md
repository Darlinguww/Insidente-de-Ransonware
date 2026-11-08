# 08: Intermediario

**What to build:** Con la defensa apagada, la víctima habla con el intermediario y este reenvía al servidor. El intermediario sustituye pkS, abre sV, la conserva y la reenvía cifrada para el servidor. Víctima y servidor terminan con la misma semilla y el cifrado se completa. Después, con el servidor apagado, el intermediario descifra copias de los cifrados sin pago.

**Blocked by:** 04 Cifrado de notas.txt

**Status:** ready-for-agent

- [ ] La víctima envía sV cifrada con la clave sustituida, y el intermediario la abre con su clave privada de cifrado.
- [ ] El intermediario reenvía la misma sV cifrada con la pkS real. El servidor la guarda bajo idV junto a la pkV real.
- [ ] La víctima cifra `notas.txt` con i igual a 0, 1 y 2, y esas salidas siguen en disco después de cerrar víctima y servidor.
- [ ] Con el servidor apagado y copias de esos cifrados, el intermediario recupera los tres archivos sin pago.
- [ ] Las trazas muestran la sustitución, la apertura y el reenvío, y la evidencia queda en `pruebas/mitm`.
