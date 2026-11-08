# 02: Registro del incidente

**What to build:** La víctima y el servidor, ya en el laboratorio, registran un incidente por la terminal. La víctima crea idV, pkV y skV. El servidor crea pkS y skS. Intercambian idV y las claves públicas. Las privadas no salen de su contenedor. Repetir el registro del mismo idV no abre otro incidente. Esta demostración corre con la defensa apagada.

**Blocked by:** 01 Laboratorio: red, volúmenes y copias

**Status:** ready-for-agent

- [ ] idV son 16 bytes y todos los mensajes de este intercambio lo llevan.
- [ ] pkV y pkS son RSA de 2048 bits con exponente 65537. skV y skS no aparecen en la red ni en el contenedor del otro.
- [ ] El servidor responde con pkS asociada a ese idV.
- [ ] Un segundo registro del mismo idV no crea otra víctima, otra sV ni otra entrega inicial.
- [ ] La traza del registro queda en la carpeta de la prueba.
