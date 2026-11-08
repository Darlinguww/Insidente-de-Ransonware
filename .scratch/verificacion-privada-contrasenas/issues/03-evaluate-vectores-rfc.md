# Evaluate y vectores RFC 9497

**Status:** ready-for-agent
**Assignee:** Andres Gomez Rodriguez
**Complexity:** 5
**Spec:** ../spec.md

## What to build

El Administrador puede evaluar una entrada de bytes con la clave secreta de la época y obtener la salida OPRF de 64 bytes. La misma entrada y la misma clave dan siempre la misma salida. Un revisor reproduce, byte a byte, los vectores oficiales de ristretto255-SHA512 del apéndice A.1.1 de RFC 9497: semilla, clave derivada, entrada, cegado, elemento cegado, elemento evaluado y salida.

La suite es la de circl para OPRF(ristretto255, SHA-512). El elemento identidad se rechaza y no se evalúa.

## Acceptance criteria

- [ ] La suite integrada es OPRF-ristretto255-SHA512 en el modo OPRF de RFC 9497. HashToGroup, Blind, BlindEvaluate, Unblind, Finalize y Evaluate se delegan en circl y coinciden con el RFC, no con un hash paralelo.
- [ ] Los vectores del apéndice A.1.1 coinciden byte a byte en el cegado, el elemento cegado, el elemento evaluado y la salida.
- [ ] Evaluate(skS, entrada) es determinista para una clave y una entrada fijas, y la salida mide 64 bytes. El elemento del grupo mide 32 bytes.
- [ ] Si HashToGroup produce el elemento identidad, la evaluación aborta y no hay salida.
- [ ] skS de prueba puede inyectarse por el entorno. Esta entrega no abre la API HTTP ni publica el filtro.
- [ ] Las versiones de Go y de circl quedan fijadas junto al identificador de suite, de forma que otra máquina repita los mismos vectores.

## Blocked by

- None (can start immediately).
