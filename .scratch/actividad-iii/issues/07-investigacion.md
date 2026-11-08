# 07: Investigación

**What to build:** Con el servidor apagado y solo otra copia de los tres cifrados, la pareja recupera sV sin el registro, sin claves privadas y sin los originales. La candidata correcta es la primera cuyo GCM verifica en i = 0. Después se comprueban i = 1 e i = 2, se mide el costo y se comparan los descifrados con el original.

**Blocked by:** 04 Cifrado de notas.txt

**Status:** ready-for-agent

- [ ] El contenedor de la investigación monta únicamente la copia de los tres cifrados. No monta registro, identidad, originales ni interceptado.
- [ ] La búsqueda recorre en orden los enteros de 0 a `2^24 - 1`, escritos en 32 bytes big-endian, sin leer variables internas del generador.
- [ ] Una candidata se acepta cuando AES-GCM verifica en i = 0 con su nonce, su etiqueta y su AAD. Luego esa misma sV verifica i = 1 e i = 2.
- [ ] La prueba anota el entorno, el tiempo, las candidatas examinadas y separa el costo de buscar sV del costo de descifrar los tres archivos.
- [ ] Los tres descifrados coinciden byte a byte con el original, y la evidencia queda en `pruebas/investigacion`.
