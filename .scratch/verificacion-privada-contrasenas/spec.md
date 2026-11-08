# Verificación privada de contraseñas comprometidas

**Status:** ready-for-agent

Spec del prototipo descrito en el Entregable 1 (Criptografía, Ricardo Villanueva Polanco, 1 de octubre de 2026). El repositorio aún no tiene código: este documento es el contrato que parten los tickets en `.scratch/verificacion-privada-contrasenas/issues/`.

## Problem Statement

Quien va a elegir o reutilizar una contraseña necesita saber si esa contraseña ya apareció en un conjunto conocido de contraseñas comprometidas. Preguntarle eso a un servidor enviando la contraseña, o enviando un hash ordinario, le entrega el secreto al mismo servicio que debería protegerlo.

El equipo tiene que construir un prototipo local en el que la persona obtiene una respuesta de pertenencia y el servidor que colabora en el cálculo no recibe la contraseña, no recibe un hash ordinario y no obtiene la salida final de la función.

## Solution

Tres actores se reparten el trabajo.

El usuario escribe la contraseña en el Cliente. El Cliente la codifica con una regla canónica, la lleva a un punto del grupo ristretto255, la ciega con un escalar aleatorio nuevo y le envía al Servidor OPRF solo ese elemento cegado, junto con la época de clave. El Servidor multiplica el elemento por su clave secreta skS y devuelve el elemento evaluado. El Cliente deshace el cegado, calcula la salida final del OPRF y consulta un Bloom filter publicado. Responde COMPROMETIDA o NO ENCONTRADA EN LA LISTA.

El Administrador, fuera de línea, recorre el corpus con la misma regla canónica y con Evaluate(skS, entrada), inserta esas salidas en el Bloom filter, firma el manifiesto y publica el filtro de la época vigente. Cuando rota skS, publica un filtro nuevo y la época anterior deja de aceptarse.

La suite es la de RFC 9497: OPRF ristretto255-SHA512, vía cloudflare/circl. El filtro admite falsos positivos y, construido y configurado correctamente, no admite falsos negativos.

## User Stories

1. Como usuario del Cliente, quiero escribir una contraseña y obtener COMPROMETIDA o NO ENCONTRADA EN LA LISTA, para decidir si esa contraseña ya está en el conjunto publicado.
2. Como usuario del Cliente, quiero que la contraseña permanezca en el Cliente, para que el Servidor OPRF no la reciba.
3. Como usuario del Cliente, quiero que el mensaje enviado al Servidor sea un elemento cegado y no un hash ordinario de la contraseña, para cumplir la privacidad de la entrada.
4. Como usuario del Cliente, quiero que la salida final del OPRF se calcule en el Cliente, para que el Servidor no conozca el valor con el que se consulta el filtro.
5. Como usuario del Cliente, quiero que cada consulta use un cegado nuevo, para que dos consultas de la misma contraseña produzcan elementos cegados distintos.
6. Como usuario del Cliente, quiero que la misma contraseña evaluada con la misma skS produzca siempre la misma salida final, para que el resultado de pertenencia sea estable dentro de una época.
7. Como usuario del Cliente, quiero que una contraseña y su forma Unicode NFC equivalente se traten como la misma entrada, para que el Cliente y el Administrador no discrepen por la codificación.
8. Como usuario del Cliente, quiero que el Cliente aborte si la codificación cae en el elemento identidad, para no continuar un caso degenerado.
9. Como usuario del Cliente, quiero que el Cliente rechace un elemento evaluado mal formado o que sea el elemento identidad, para no finalizar a partir de una respuesta inválida.
10. Como usuario del Cliente, quiero leer en la respuesta que COMPROMETIDA puede ser un falso positivo, para interpretar el resultado con el límite que el filtro tiene.
11. Como usuario del Cliente, quiero leer que NO ENCONTRADA EN LA LISTA solo habla del conjunto publicado, para no tomar esa respuesta como una evaluación de fortaleza.
12. Como usuario del Cliente, quiero que el Cliente compare la época del Servidor con la de su caché antes de consultar, para no mezclar una clave nueva con un filtro viejo.
13. Como usuario del Cliente, quiero que el Cliente reutilice manifest.json y bloom.bin cuando la época y el ETag coinciden, para no volver a descargar el mismo filtro.
14. Como usuario del Cliente, quiero que el Cliente descargue el manifiesto y el filtro nuevos cuando la época cambia, para consultar el conjunto que corresponde a la clave vigente.
15. Como usuario del Cliente, quiero que el Cliente rechace un bloom.bin cuyo digest no coincide con el manifiesto, para no consultar un filtro alterado.
16. Como usuario del Cliente, quiero que el Cliente rechace un manifiesto cuya firma institucional no verifica, para no aceptar un conjunto plantado.
17. Como usuario del Cliente, quiero introducir la contraseña por la entrada estándar o por un prompt, para que no quede en los argumentos del proceso.
18. Como Administrador, quiero importar un corpus sintético o autorizado, una contraseña por línea, para construir el conjunto comprometido sin usar filtraciones reales en el prototipo.
19. Como Administrador, quiero que la herramienta aplique la misma REGLA_CANONICA que el Cliente, para que la misma contraseña produzca la misma entrada en los dos lados.
20. Como Administrador, quiero ejecutar Evaluate(skS, entrada) sin cegado sobre cada contraseña del corpus, para insertar en el filtro la misma salida que el Cliente obtendrá.
21. Como Administrador, quiero un Bloom filter dimensionado a partir de n y de la tasa objetivo de falsos positivos, para acotar el error que luego se va a medir.
22. Como Administrador, quiero manifest.json y bloom.bin coherentes, con el digest del binario dentro del manifiesto, para que el Cliente pueda verificarlos.
23. Como Administrador, quiero firmar el manifiesto con la clave institucional, distinta de skS, para que la autenticidad del conjunto no dependa de la clave OPRF.
24. Como Administrador, quiero publicar el manifiesto y el filtro en el almacenamiento que el Servidor expone, para que el Cliente los descargue.
25. Como Administrador, quiero construir el filtro con 1, 1.000 y 100.000 contraseñas y obtener un manifiesto cuyo digest corresponde al binario, para comprobar que la construcción escala dentro del prototipo.
26. Como Administrador, quiero rotar skS y key_epoch y volver a construir y publicar el filtro, para que el conjunto publicado siga siendo compatible con la clave.
27. Como Administrador, quiero que una consulta hecha con el filtro de la época anterior deje de ser aceptada por el Servidor, para evitar los falsos negativos masivos de mezclar clave y filtro.
28. Como operador del Servidor OPRF, quiero custodiar únicamente la skS de la época vigente, para evaluar elementos cegados sin almacenar contraseñas.
29. Como operador del Servidor OPRF, quiero que GET /v1/parameters entregue suite_id, key_epoch y la versión de API, para que el Cliente sepa con qué servicio habla.
30. Como operador del Servidor OPRF, quiero que POST /v1/oprf/evaluate reciba el elemento cegado y la época y devuelva el elemento evaluado, para completar el protocolo.
31. Como operador del Servidor OPRF, quiero rechazar un blindedElement que no deserializa, para no evaluarlo.
32. Como operador del Servidor OPRF, quiero rechazar el elemento identidad, para cortar el caso degenerado en el Servidor y en el Cliente.
33. Como operador del Servidor OPRF, quiero rechazar una key_epoch distinta de la vigente, para obligar al Cliente a actualizar el filtro.
34. Como operador del Servidor OPRF, quiero que la multiplicación por skS no introduzca ramas que dependan de esa clave, para que el tiempo de respuesta no filtre información sobre skS.
35. Como operador del Servidor OPRF, quiero servir manifest.json y bloom.bin sin pasar por la evaluación, para separar la publicación del filtro de la custodia de la clave.
36. Como operador del Servidor OPRF, quiero que el Servidor no registre contraseñas, elementos cegados, elementos evaluados ni sesiones de usuario, para conservar el estado mínimo del diseño.
37. Como operador del Servidor OPRF, quiero guardar skS cifrada en disco, o en una variable de entorno durante las pruebas locales, para no dejar la clave en claro en el almacenamiento del prototipo.
38. Como revisor del equipo, quiero que la salida del Cliente coincida con Evaluate(skS, entrada) del Administrador para la misma época, para demostrar la equivalencia de los dos caminos.
39. Como revisor del equipo, quiero reproducir byte a byte los vectores oficiales de ristretto255-SHA512 del RFC 9497, apéndice A.1.1, para comprobar que la suite integrada es la del estándar.
40. Como revisor del equipo, quiero que toda contraseña incluida en el corpus consulte como COMPROMETIDA, para sostener la ausencia de falsos negativos bajo una construcción correcta.
41. Como revisor del equipo, quiero medir al menos 10.000 consultas de contraseñas ausentes y comparar la tasa empírica con p ≈ (1 − e^(−kn/m))^k, para informar la tasa de falsos positivos.
42. Como revisor del equipo, quiero medir la latencia de una consulta con filtro en caché y sin él, para separar el costo de red del costo criptográfico.
43. Como revisor del equipo, quiero medir el tamaño de bloom.bin y el tiempo de construcción para 50.000, 100.000 y 200.000 entradas, para documentar el costo del filtro.
44. Como revisor del equipo, quiero medir el tiempo entre rotar skS y tener el filtro nuevo disponible, y comprobar que el filtro anterior ya no produce coincidencias válidas con la clave nueva, para cerrar el experimento de rotación.
45. Como docente o integrante del equipo, quiero levantar Administrador, Servidor y Cliente con Docker Compose, para repetir el prototipo en local con las mismas versiones de Go, circl y de la suite.

## Implementation Decisions

- Un solo lenguaje, Go, para el Administrador, el Servidor OPRF y el Cliente. Los tres ejecutan la misma suite a través de cloudflare/circl. Las versiones de Go, de circl y el identificador de suite quedan fijados y documentados para que el prototipo sea repetible.
- La suite es OPRF-ristretto255-SHA512, modo OPRF de RFC 9497 (no VOPRF ni POPRF). HashToGroup, Blind, BlindEvaluate, Unblind, Finalize y Evaluate son las operaciones de esa suite tal como las expone circl. El relato por etapas del entregable explica el protocolo; la codificación que debe coincidir con el apéndice A.1.1 es la del RFC, no un hash casero distinto. Tamaños de la suite: elemento de 32 bytes, escalar de 32 bytes, salida de 64 bytes.
- REGLA_CANONICA es única y compartida por el Cliente y el Administrador: normalizar Unicode a NFC y codificar el resultado en UTF-8. La contraseña en claro y el escalar de cegado no salen del Cliente.
- El Cliente lee la contraseña desde la entrada estándar o desde un prompt. No la toma como argumento de la línea de comandos.
- El elemento cegado y el elemento evaluado viajan en JSON como base64 estándar, sin saltos de línea, del elemento comprimido de 32 bytes. POST /v1/oprf/evaluate recibe `blindedElement` y `key_epoch` y responde `evaluatedElement`.
- GET /v1/parameters responde `suite_id` (`OPRF-ristretto255-SHA512`), `key_epoch` y `api_version` (`v1`). No pide autenticación.
- Un elemento que no deserializa y el elemento identidad se rechazan con HTTP 400, antes de evaluar. Una `key_epoch` distinta de la vigente se rechaza con HTTP 409. Esos rechazos ocurren en el Servidor y el Cliente también rechaza identidad y elementos mal formados antes de cegar o de finalizar.
- La evaluación usa la multiplicación de la biblioteca y no agrega ramas que dependan de skS. El Servidor no escribe en el registro la contraseña, el elemento cegado, el elemento evaluado ni una sesión de usuario.
- skS de la época vigente se guarda cifrada con AES-GCM. La clave de cifrado sale del entorno. Las pruebas locales pueden inyectar skS por variable de entorno. skS y la clave institucional de firma son claves distintas.
- El Bloom filter se dimensiona con n y con la tasa objetivo p:

  m = ceil( −n · ln(p) / (ln 2)^2 )

  k = round( (m / n) · ln 2 )

  p real ≈ (1 − e^(−kn/m))^k

  La fila de referencia que el entregable fija con cifras es n = 100000, p = 0.01, m = 958506 bits, k = 7. El binario es big-endian: el bit 0 es el bit más significativo del byte 0, y el final se rellena con 0x00 cuando m no es múltiplo de 8.
- Las k posiciones salen de los primeros 16 bytes de la cadena insertada (la salida OPRF de 64 bytes en el camino real). Si la cadena trae menos de 16 bytes, se rellena con ceros a la derecha. h1 y h2 son enteros sin signo de 64 bits en big-endian. La posición i, para i de 0 a k−1, es (h1 + i·h2) módulo m. Si h2 sale 0, se usa 1 para que las posiciones avancen.
- manifest.json lleva `version`, `key_epoch`, `suite_id`, `created_at`, `parameters` (`n_elements`, `m_bits`, `k_hashes`, `target_fpp`), `hash_algorithm` (`SHA-256`), `bloombin_digest` (SHA-256 hex de bloom.bin) y `signature`. Esos campos vienen del entregable. `key_epoch` es una cadena opaca; la comparación es por igualdad.
- La firma cubre los bytes UTF-8 del manifiesto canónico sin el campo `signature`: objeto JSON con claves ordenadas y sin espacio insignificante. El algoritmo es ECDSA P-256 con SHA-256, codificada en DER. El Cliente lleva anclada la clave pública institucional por fuera del canal del Servidor. El digest y la firma se comprueban antes de cualquier consulta de pertenencia.
- La caché del Cliente usa GET /v1/parameters para la época. Si la época coincide con la caché, pide el manifiesto con If-None-Match y el ETag fuerte es el `bloombin_digest`. Si la época difiere, o el ETag difiere, descarga manifiesto y bloom.bin, verifica digest y firma, y solo entonces consulta. Esta regla junta el chequeo de época del flujo completo y el ETag del entregable.
- El Servidor entrega GET /v1/filter/manifest y GET /v1/filter/bloom desde los artefactos publicados. Esos GET no ejecutan la evaluación OPRF.
- La herramienta administrativa es una CLI local, sin API de red: `build-filter` (corpus y skS vigente → manifest.json + bloom.bin firmado), `rotate-key` (nueva skS y nueva key_epoch) y `publish` (copia los artefactos al almacenamiento que sirven las rutas del filtro).
- El resultado visible del Cliente es exactamente una de estas dos cadenas: `COMPROMETIDA` o `NO ENCONTRADA EN LA LISTA`. Junto a COMPROMETIDA, el Cliente recuerda que la coincidencia puede ser un falso positivo.
- Tres procesos se empaquetan con Docker Compose: admin, servidor y cliente. El corpus de demostración es sintético.

El manifiesto de referencia, tomado del entregable y recortado a la forma que el Cliente tiene que aceptar:

```json
{
  "version": "1.0.0",
  "key_epoch": "2026-Q1-v1",
  "suite_id": "OPRF-ristretto255-SHA512",
  "created_at": "2026-09-26T10:00:00Z",
  "parameters": {
    "n_elements": 100000,
    "m_bits": 958506,
    "k_hashes": 7,
    "target_fpp": 0.01
  },
  "hash_algorithm": "SHA-256",
  "bloombin_digest": "<sha256 hex de bloom.bin>",
  "signature": "<ECDSA P-256 DER>"
}
```

## Testing Decisions

Una prueba buena observa el comportamiento externo. El repositorio no tiene pruebas previas; las costuras se crean en el borde del sistema.

Hay dos costuras, y la segunda existe solo porque la primera no puede ver bytes del RFC.

1. Costura principal, la más alta: las tres interfaces de los actores. La CLI del Administrador, la API HTTP del Servidor y la CLI del Cliente. Las pruebas funcionales, negativas, de caché, de integridad, de rotación y de extremo a extremo hablan con esas interfaces y afirman respuestas, códigos HTTP y artefactos publicados. No afirman escalares internos, layouts de módulos ni el orden de las llamadas.
2. Costura estrecha de la suite: entrada de bytes, cegado, elemento cegado, elemento evaluado y salida, comparados byte a byte con el apéndice A.1.1 de RFC 9497. La respuesta COMPROMETIDA no conserva esos bytes, así que esta costura es el único lugar donde el estándar se comprueba.

Los cuatro frentes del entregable se apoyan en esas costuras:

- Funcional: ciclo completo con una contraseña presente y una ausente; reutilización de caché cuando la época coincide y nueva descarga cuando cambia; build-filter sobre 1, 1.000 y 100.000 contraseñas con manifiesto y binario coherentes.
- Criptográfico: cegado fresco, misma salida final con elementos cegados distintos, equivalencia Cliente–Administrador, vectores A.1.1.
- Negativo: elemento mal formado, elemento identidad, época incompatible, manifiesto o filtro alterado.
- Experimental: falsos positivos (≥ 10.000 ausentes), latencia con y sin caché, tamaño y tiempo de construcción (50.000, 100.000, 200.000), tiempo de rotación y retirada del filtro anterior.

La prueba funcional de ausencia usa un fixture con tasa objetivo muy baja y una contraseña fija fuera del corpus, de modo que el resultado esperado sea NO ENCONTRADA EN LA LISTA. La tasa empírica de falsos positivos se mide en el frente experimental, no como aserción de esa prueba. Toda contraseña que sí se insertó debe producir COMPROMETIDA.

## Out of Scope

- VOPRF, POPRF y cualquier modo que no sea el OPRF básico de RFC 9497.
- Varios servidores, reparto de la clave o anonimato de red. El Servidor puede ver IP, hora y frecuencia de las consultas.
- Evaluación de fortaleza de la contraseña, políticas de composición y bloqueo de cuentas.
- Resistencia al compromiso total del Cliente o del Servidor: memoria del dispositivo, robo de skS o sustitución de la implementación criptográfica.
- Corpus de filtraciones reales. El prototipo usa listas sintéticas o autorizadas para el curso.
- Interfaz web. El entregable la deja como alternativa; esta especificación exige la CLI.
- API de red para construir el filtro. build-filter, rotate-key y publish son locales.
- Un CDN externo. El Servidor sirve los artefactos desde el almacenamiento local publicado.

## Further Notes

### Costuras

La costura principal es el borde Administrador CLI / Servidor HTTP / Cliente CLI. La costura estrecha de vectores RFC queda al lado porque el veredicto de pertenencia no conserva los bytes del apéndice A.1.1. Si el equipo prefiere una sola costura, los vectores se pueden mover a una prueba externa de la misma CLI; el criterio de aceptación no cambia: comparación byte a byte con A.1.1.

### Reparto

La complejidad es un peso relativo del problema, no un conteo de tickets ni una estimación de calendario. Cada persona suma 9. El trabajo criptográfico de integrar la suite pesa más que un ticket de empaquetado, así que Andres y Darlen cargan menos tickets y los de mayor peso. Roger empieza en paralelo por la estructura del filtro, que no necesita la suite. Daniel y Darlen esperan a que Evaluate esté integrado: el Servidor y el cegado se apoyan en esa misma suite.

| Persona | Tickets | Peso |
| --- | --- | --- |
| Andres Gomez Rodriguez | 01 Regla canónica (2), 03 Evaluate y vectores RFC (5), 11 Métricas (2) | 9 |
| Darlen Arias Aleman | 04 Cegado, unblind y finalize (5), 07 Veredicto de pertenencia (4) | 9 |
| Daniel Cruzado Agudelo | 05 Servidor OPRF (4), 09 Rotación de clave (3), 10 Docker Compose (2) | 9 |
| Roger Marenco Argote | 02 Estructura del Bloom filter (3), 06 Construcción y publicación (3), 08 Caché e integridad (3) | 9 |

El camino crítico es el 03 de Andres: de ahí salen en paralelo el 04 de Darlen, el 05 de Daniel y el 06 de Roger. El 01 no bloquea a la suite; sí bloquea al cegado y a la construcción del filtro, porque ahí la contraseña ya entra por la regla canónica. Roger puede terminar el 02 mientras Andres cierra 01 y 03. El veredicto 07 junta las tres ramas. La caché 08 y la rotación 09 cierran el ciclo de época. Docker se demuestra con el veredicto; las métricas esperan también a la rotación.

### Cómo se escribieron estos tickets

Siguen el corte de `/to-tickets`: cada ticket atraviesa las capas que necesita para dejar un comportamiento demostrable, declara qué tickets lo bloquean y cabe en una sesión nueva. El estado `ready-for-agent` está en cada archivo. No hay un tablero externo: el tracker de este repositorio son los markdown de `.scratch/`, como quedó en `docs/agents/issue-tracker.md`.
