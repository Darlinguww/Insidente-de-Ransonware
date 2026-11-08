# Rotación de clave y de época

**Status:** ready-for-agent
**Assignee:** Daniel Cruzado Agudelo
**Complexity:** 3
**Spec:** ../spec.md

## What to build

El Administrador rota la clave del servicio. A partir de ese momento el Servidor evalúa con la skS nueva, rechaza la época anterior, y el filtro publicado es el reconstruido con esa clave. Una persona que tenía el filtro viejo en caché recibe el filtro nuevo en la siguiente consulta, y una contraseña del corpus vuelve a salir COMPROMETIDA.

Consultar el filtro anterior contra la clave nueva no se acepta como una comprobación válida.

## Acceptance criteria

- [ ] `rotate-key` genera una skS nueva y una `key_epoch` nueva, distinta de la anterior. La clave anterior deja de ser la que el Servidor usa para evaluar.
- [ ] Tras `build-filter` y `publish` de la época nueva, GET /v1/parameters anuncia la época nueva y las rutas del filtro sirven el manifiesto y el binario nuevos.
- [ ] POST /v1/oprf/evaluate con la `key_epoch` anterior responde HTTP 409 y no devuelve un elemento evaluado.
- [ ] El Cliente, al ver la época nueva, descarta el filtro local, descarga el vigente, lo verifica y obtiene COMPROMETIDA para una contraseña del corpus reconstruido.
- [ ] Una comprobación que mezcle el filtro de la época anterior con la clave nueva no produce un veredicto aceptado.
- [ ] skS nueva queda custodiada con el mismo mecanismo que la clave anterior: cifrada en disco, o por el entorno en las pruebas locales.

## Blocked by

- 05 Servidor OPRF
- 08 Caché e integridad del filtro
