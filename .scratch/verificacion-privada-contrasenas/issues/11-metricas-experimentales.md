# Métricas experimentales

**Status:** ready-for-agent
**Assignee:** Andres Gomez Rodriguez
**Complexity:** 2
**Spec:** ../spec.md

## What to build

El equipo obtiene un informe repetible del prototipo ya integrado: la tasa empírica de falsos positivos frente a la fórmula, la latencia de una consulta con filtro en caché y sin él, el tamaño y el tiempo de construcción del filtro, y el tiempo que pasa desde rotar la clave hasta que el filtro nuevo está disponible.

El informe usa las mismas interfaces que el resto del sistema. No hace falta mirar el interior de la suite para leerlo.

## Acceptance criteria

- [ ] Al menos 10.000 contraseñas ausentes, generadas para la prueba, se consultan sobre las configuraciones de referencia. El informe compara la tasa empírica con p ≈ (1 − e^(−kn/m))^k.
- [ ] Toda contraseña que sí pertenece al corpus de esa medición sigue respondiendo COMPROMETIDA.
- [ ] El informe da la latencia de una consulta completa (cegado, red, evaluación, unblind y verificación en el filtro) con bloom.bin en caché y sin él.
- [ ] El informe da el tamaño de bloom.bin y el tiempo de `build-filter` para 50.000, 100.000 y 200.000 entradas.
- [ ] El informe da el tiempo entre `rotate-key` y la disponibilidad del filtro nuevo, y confirma que el filtro de la época anterior ya no produce un veredicto aceptado con la clave nueva.
- [ ] El procedimiento queda escrito de forma que otra persona del equipo lo vuelva a ejecutar con Docker Compose o con los mismos comandos locales.

## Blocked by

- 08 Caché e integridad del filtro
- 09 Rotación de clave y de época
