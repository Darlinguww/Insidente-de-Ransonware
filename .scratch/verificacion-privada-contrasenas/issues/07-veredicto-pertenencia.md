# Veredicto de pertenencia

**Status:** ready-for-agent
**Assignee:** Darlen Arias Aleman
**Complexity:** 4
**Spec:** ../spec.md

## What to build

Una persona escribe una contraseña en el Cliente y recibe una de dos respuestas: COMPROMETIDA, si el filtro publicado marca todas las posiciones de la salida OPRF, o NO ENCONTRADA EN LA LISTA, si falta alguna. La contraseña que el Administrador incluyó en el corpus sale COMPROMETIDA. Una contraseña fuera del corpus, en el fixture de prueba, sale NO ENCONTRADA EN LA LISTA.

Antes de responder, el Cliente pide la época al Servidor, descarga el manifiesto y el filtro de esa época, y completa el OPRF con el Servidor real. COMPROMETIDA va acompañada de la advertencia de que la coincidencia puede ser un falso positivo. NO ENCONTRADA EN LA LISTA no se presenta como una medida de fortaleza.

## Acceptance criteria

- [ ] El Cliente lee la contraseña por la entrada estándar o por un prompt, consulta GET /v1/parameters, descarga el manifiesto y bloom.bin de la época vigente, envía el elemento cegado a POST /v1/oprf/evaluate y responde con el veredicto.
- [ ] Una contraseña incluida en el corpus publicado se responde COMPROMETIDA, y el texto recuerda que puede tratarse de un falso positivo.
- [ ] Una contraseña del fixture ausente, con una tasa objetivo muy baja, se responde NO ENCONTRADA EN LA LISTA, y el texto la limita al conjunto publicado.
- [ ] La salida OPRF usada para consultar el filtro coincide con Evaluate(skS, bytes canónicos) de esa época.
- [ ] Dos consultas seguidas de la misma contraseña envían elementos cegados distintos y obtienen el mismo veredicto.
- [ ] El Cliente no responde el veredicto si el Servidor rechaza el elemento o si la época de la respuesta no es la del filtro que va a usar.

## Blocked by

- 04 Cegado, unblind y finalize
- 05 Servidor OPRF
- 06 Construcción y publicación del filtro
