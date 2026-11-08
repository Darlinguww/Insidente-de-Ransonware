# Servidor OPRF

**Status:** ready-for-agent
**Assignee:** Daniel Cruzado Agudelo
**Complexity:** 4
**Spec:** ../spec.md

## What to build

El Cliente, u otra herramienta, pregunta los parámetros del servicio y envía un elemento cegado de la época vigente. El Servidor devuelve el elemento evaluado. Si el elemento está mal formado, es el elemento identidad o trae otra época, el Servidor lo rechaza y no lo evalúa.

El Servidor también entrega el manifiesto y el binario ya publicados, sin usar la clave para esa descarga. No guarda la contraseña, no guarda la consulta y no abre una sesión de usuario.

## Acceptance criteria

- [ ] GET /v1/parameters responde `suite_id` = `OPRF-ristretto255-SHA512`, la `key_epoch` vigente y `api_version` = `v1`, sin autenticación.
- [ ] POST /v1/oprf/evaluate acepta `blindedElement` en base64 estándar del punto de 32 bytes y `key_epoch`, y responde `evaluatedElement` en el mismo base64. El resultado coincide con BlindEvaluate(skS, elemento) de la suite.
- [ ] Un elemento que no deserializa y el elemento identidad responden HTTP 400 y no se evalúan. Una `key_epoch` distinta de la vigente responde HTTP 409 y no se evalúa.
- [ ] La evaluación no añade ramas que dependan de skS. skS se guarda cifrada con AES-GCM, con la clave de cifrado en el entorno, o entra por el entorno en las pruebas locales.
- [ ] GET /v1/filter/manifest y GET /v1/filter/bloom sirven los artefactos publicados. El manifiesto incluye un ETag fuerte igual a `bloombin_digest`. Esas rutas no ejecutan la evaluación.
- [ ] El registro del Servidor no contiene contraseñas, elementos cegados, elementos evaluados ni identificadores de sesión.

## Blocked by

- 03 Evaluate y vectores RFC 9497
