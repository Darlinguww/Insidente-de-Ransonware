# Estructura del Bloom filter

**Status:** ready-for-agent
**Assignee:** Roger Marenco Argote
**Complexity:** 3
**Spec:** ../spec.md

## What to build

Dada una lista de cadenas de bytes y una tasa objetivo de falsos positivos, el Administrador obtiene un filtro consultable: toda cadena insertada se reconoce como miembro, el tamaño y el número de funciones salen de las fórmulas del entregable, y el binario publicado coincide con el digest escrito en el manifiesto.

Esta entrega inserta bytes arbitrarios. Todavía no pasa las contraseñas por el OPRF.

## Acceptance criteria

- [ ] Con n elementos y tasa objetivo p, m y k quedan en m = ceil(−n · ln(p) / (ln 2)^2) y k = round((m / n) · ln 2). La fila n = 100000, p = 0.01 produce m = 958506 y k = 7.
- [ ] Insertar un byte-string y consultarlo devuelve miembro. Una batería de cadenas insertadas no produce falsos negativos.
- [ ] bloom.bin es big-endian: el bit 0 es el bit más significativo del byte 0, y el archivo se rellena con 0x00 hasta el byte completo cuando m no es múltiplo de 8.
- [ ] Las k posiciones de una cadena se derivan de sus primeros 16 bytes como h1 y h2 enteros de 64 bits big-endian, con la posición i = (h1 + i·h2) módulo m. Si la cadena tiene menos de 16 bytes, se rellena con ceros a la derecha. Si h2 es 0, se usa 1.
- [ ] El manifiesto guarda n, m, k, la tasa objetivo y el SHA-256 hexadecimal de bloom.bin. Alterar un byte del binario hace que el digest deje de coincidir.
- [ ] La consulta de una cadena ausente en un filtro de prueba de tasa muy baja devuelve no-miembro. La medición de la tasa real de falsos positivos queda en el ticket de métricas.

## Blocked by

- None (can start immediately).
