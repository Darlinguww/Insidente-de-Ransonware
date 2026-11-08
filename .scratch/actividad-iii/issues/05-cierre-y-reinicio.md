# 05: Cierre y reinicio

**What to build:** La pareja cierra la víctima y el servidor después del cifrado y los vuelve a arrancar. Cada uno recupera solo lo que le corresponde en disco. El incidente sigue siendo el mismo: no nace otra sV ni otro registro.

**Blocked by:** 04 Cifrado de notas.txt

**Status:** ready-for-agent

- [ ] Tras el reinicio, la víctima carga idV, pkV, skV y los tres cifrados.
- [ ] En disco de la víctima no están sV, ni Ki, ni la entrega OAEP inicial.
- [ ] Tras el reinicio, el servidor carga su par RSA y, para ese idV, sV, pkV y el pago pendiente.
- [ ] El reinicio no llama otra vez al generador ni repite el registro.
- [ ] La sV del registro es la misma que se entregó antes de cerrar.
