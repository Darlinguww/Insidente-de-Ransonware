# 05: Cierre y reinicio

**What to build:** La pareja cierra la vÃ­ctima y el servidor despuÃ©s del cifrado y los vuelve a arrancar. Cada uno recupera solo lo que le corresponde en disco. El incidente sigue siendo el mismo: no nace otra sV ni otro registro.

**Blocked by:** 04 Cifrado de notas.txt

**Status:** ready-for-agent

- [ ] Tras el reinicio, la vÃ­ctima carga idV, pkV, skV y los tres cifrados.
- [ ] En disco de la vÃ­ctima no estÃ¡n sV, ni Ki, ni la entrega OAEP inicial.
- [ ] Tras el reinicio, el servidor carga su par RSA y, para ese idV, sV, pkV y el pago pendiente.
- [ ] El reinicio no llama otra vez al generador ni repite el registro.
- [ ] La sV del registro es la misma que se entregÃ³ antes de cerrar.


## Answer

Implementado en `protocolo/reinicio.py` (víctima) y `servidor/__main__.py::anunciar()` (servidor). Verificado: `pruebas/contenedores/test_reinicio.py` pasa (2 tests dentro de la corrida `12 passed` de `prueba_entrega`).
