# Cegado, unblind y finalize

**Status:** ready-for-agent
**Assignee:** Darlen Arias Aleman
**Complexity:** 5
**Spec:** ../spec.md

## What to build

El usuario comprueba dos veces la misma contraseña y el Cliente envía cada vez un elemento cegado distinto. Tras completar la evaluación con la clave del servicio, las dos consultas producen la misma salida final, y esa salida es la misma que el Administrador obtiene con Evaluate directo sobre los bytes canónicos de esa contraseña y esa época.

Quien solo ve el mensaje hacia el Servidor no recibe la contraseña ni la salida final. El escalar de cegado se queda en el Cliente.

## Acceptance criteria

- [ ] Dos ejecuciones de la misma contraseña generan elementos cegados distintos y ambos deserializan como puntos válidos de 32 bytes.
- [ ] Tras BlindEvaluate con la misma skS, unblind y finalize, las dos ejecuciones producen la misma salida de 64 bytes.
- [ ] Esa salida coincide byte a byte con Evaluate(skS, REGLA_CANONICA(contraseña)) para la misma época.
- [ ] El Cliente aborta antes de cegar si la entrada cae en el elemento identidad, y aborta antes de finalizar si el elemento evaluado no deserializa o es el elemento identidad.
- [ ] El valor enviado en cada consulta es el elemento cegado. La contraseña, el escalar y la salida final no forman parte de ese mensaje.
- [ ] La contraseña entra por la entrada estándar o por un prompt.

## Blocked by

- 01 Regla canónica compartida
- 03 Evaluate y vectores RFC 9497
