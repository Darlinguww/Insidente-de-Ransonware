# 04: Cifrado de notas.txt

**What to build:** Después de una entrega confirmada, la víctima cifra la única copia, `notas.txt`, tres veces. Quedan tres salidas distinguibles por i igual a 0, 1 y 2. Una etiqueta GCM alterada hace que esa salida se rechace.

**Blocked by:** 03 Entrega de sV

**Status:** ready-for-agent

- [ ] Existen tres cifrados, `0000`, `0001` y `0002`, de la misma copia de 64 bytes.
- [ ] Cada Ki es HMAC-SHA256 de sV sobre i en 8 bytes big-endian, y esa salida de 32 bytes es la clave AES-256-GCM.
- [ ] Cada salida guarda idV, i, un nonce de 12 bytes, una etiqueta de 16 bytes, el nombre `notas.txt` y Ci. El nonce no se repite con la misma Ki.
- [ ] El AAD reconstruible es idV seguido de i en 8 bytes big-endian.
- [ ] Si se altera la etiqueta de una salida, esa salida se rechaza y no se acepta como descifrado válido.
