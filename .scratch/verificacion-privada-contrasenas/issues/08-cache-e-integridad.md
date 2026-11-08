# Caché e integridad del filtro

**Status:** ready-for-agent
**Assignee:** Roger Marenco Argote
**Complexity:** 3
**Spec:** ../spec.md

## What to build

La segunda consulta de una persona, mientras la época y el ETag no cambian, reutiliza el manifiesto y el filtro que el Cliente ya tiene. Si la época cambia, el Cliente descarta esa copia y baja la versión vigente antes de volver a consultar.

Si alguien modifica un byte de bloom.bin o del manifiesto, o sustituye la firma, el Cliente se niega a consultar y no emite veredicto.

## Acceptance criteria

- [ ] Con la misma `key_epoch` y el mismo ETag (`bloombin_digest`), una segunda consulta no vuelve a transferir bloom.bin y el veredicto se mantiene.
- [ ] Si GET /v1/parameters entrega otra `key_epoch`, el Cliente descarta la caché, descarga manifiesto y filtro nuevos, verifica digest y firma, y solo entonces consulta.
- [ ] La descarga del manifiesto usa If-None-Match. El ETag fuerte es el digest del binario.
- [ ] Cambiar un byte de bloom.bin hace fallar el digest. Cambiar un campo firmado del manifiesto, o la firma, hace fallar la verificación ECDSA P-256. En ambos casos no hay veredicto.
- [ ] La clave pública institucional está anclada en el Cliente por fuera de la respuesta del Servidor. Una firma válida hecha con otra clave se rechaza.
- [ ] El Cliente no consulta un filtro cuya época es distinta de la época con la que pidió la evaluación.

## Blocked by

- 06 Construcción y publicación del filtro
- 07 Veredicto de pertenencia
