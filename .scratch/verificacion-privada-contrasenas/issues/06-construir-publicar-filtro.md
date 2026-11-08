# Construcción y publicación del filtro

**Status:** ready-for-agent
**Assignee:** Roger Marenco Argote
**Complexity:** 3
**Spec:** ../spec.md

## What to build

El Administrador toma un corpus, una contraseña por línea, y la clave de la época vigente, y publica un manifiesto firmado y un bloom.bin. Cada contraseña del corpus queda insertada como la salida de Evaluate, no como la contraseña en claro. El Cliente, cuando más adelante consulte ese filtro con la misma clave, verá esas contraseñas como miembros.

Publicar deja los dos artefactos en el almacenamiento que el Servidor sirve en las rutas del filtro.

## Acceptance criteria

- [ ] `build-filter` aplica REGLA_CANONICA y Evaluate(skS, entrada) a cada línea del corpus, e inserta esas salidas de 64 bytes en el filtro del ticket 02.
- [ ] Toda contraseña del corpus se consulta como miembro. El manifiesto y bloom.bin quedan coherentes: `bloombin_digest` es el SHA-256 hexadecimal del binario.
- [ ] El manifiesto incluye versión, `key_epoch`, `suite_id`, `created_at`, parámetros n/m/k/tasa y `hash_algorithm` = `SHA-256`. La firma es ECDSA P-256 SHA-256 en DER sobre el JSON canónico del manifiesto sin el campo `signature`.
- [ ] Corpus de 1, de 1.000 y de 100.000 contraseñas producen cada uno un par manifiesto/binario cuyo digest verifica. El tamaño del binario corresponde a m bits rellenados al byte.
- [ ] `publish` copia manifest.json y bloom.bin al almacenamiento que GET /v1/filter/manifest y GET /v1/filter/bloom ya saben servir.
- [ ] El filtro publicado no contiene las contraseñas ni las salidas OPRF en claro ligadas a un usuario.

## Blocked by

- 01 Regla canónica compartida
- 02 Estructura del Bloom filter
- 03 Evaluate y vectores RFC 9497
