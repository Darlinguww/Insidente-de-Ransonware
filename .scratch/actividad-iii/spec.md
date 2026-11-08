Status: ready-for-agent

# Actividad III: Del incidente a la recuperación

## Problem Statement

La pareja de estudiantes tiene que construir, en un laboratorio aislado, el ciclo de un incidente de ransomware: registro, entrega de la semilla maestra, cifrado, persistencia tras un reinicio, recuperación por pago, recuperación por investigación, sustitución por un intermediario y defensa con firmas. El único código suministrado es el generador de la semilla. El enunciado fija el modelo criptográfico y las cuatro pruebas; este spec fija el modelo B y las decisiones ya tomadas para implementarlas sin abrir variantes nuevas.

## Solution

Una aplicación de terminal, en Python, corre la víctima, el servidor y el intermediario en contenedores distintos de una misma imagen, unidos por una red interna. Hay un solo incidente por víctima, identificado por idV. La copia de práctica es `notas.txt`. Los originales viven aparte y solo entran en la comparación final.

### Modelo elegido

Modelo B. La víctima llama una sola vez al generador suministrado y obtiene sV. Protege esa semilla con OAEP.Enc(pkS, sV). El servidor la abre con skS, la guarda bajo idV junto a pkV y confirma. Si el intercambio falla, se informa el error y no empieza el cifrado. El modelo A queda descartado: el servidor no genera ni envía sV en la entrega inicial.

Repetir el registro del mismo idV no crea otra sV ni otra entrega inicial. Todo mensaje del incidente se asocia a idV. Las claves privadas de cifrado no salen de su participante.

### Mensajes

Cada mensaje TCP lleva su longitud en 4 bytes big-endian, un tipo de un byte y un cuerpo. Los tipos son:

| Tipo | Nombre | Cuerpo |
| --- | --- | --- |
| 1 | Registro | idV, pkV y la firma de la víctima |
| 2 | Respuesta de registro | idV, pkS y la firma del servidor |
| 3 | Entrega de sV | idV y el cifrado OAEP de sV |
| 4 | Confirmación | idV |
| 5 | Solicitud de recuperación | idV |
| 6 | Entrega por pago | idV y el cifrado OAEP de sV bajo la pkV ya guardada |
| 7 | Error | idV y el motivo del rechazo |

idV son 16 bytes. Una clave pública RSA viaja en DER SubjectPublicKeyInfo, precedida por su longitud en 2 bytes big-endian. La firma ECDSA viaja igual, precedida por su longitud. Lo firmado no incluye esas longitudes: es la cadena `actividad-iii/v1`, el byte de rol `V` o `S`, idV y la clave RSA. La clave de verificación no viaja en el mensaje.

En el modelo B el orden legítimo es: registro, respuesta de registro, entrega de sV, confirmación. La víctima solo envía la entrega después de verificar la firma de pkS. El servidor solo guarda pkV después de verificar la firma de la víctima. La recuperación por pago es la solicitud seguida de la entrega por pago. La petición no puede reemplazar la pkV guardada.

### Qué persiste en cada contenedor

| Volumen | Quién lo monta | Qué queda después de cerrar el proceso |
| --- | --- | --- |
| Confianza | víctima y servidor, escritos por preparar | Clave privada de firma propia y clave de verificación del otro |
| Identidad | víctima | idV, pkV y skV. No guarda sV, ni Ki, ni la entrega OAEP inicial |
| Copias | víctima | `notas.txt`, 64 bytes |
| Cifrados | víctima | Tres salidas, `0000`, `0001` y `0002`, con i igual a 0, 1 y 2 |
| Recuperados | víctima, y luego la comparación en solo lectura | Solo descifrados cuya etiqueta GCM verificó |
| Registro | servidor | Par RSA del servidor, y por víctima: idV, sV, pkV y el estado del pago |
| Interceptado | intermediario | sV obtenida en la sustitución, cuando la defensa está apagada |
| Originales | solo la comparación, solo lectura | `notas.txt` reservado para la comparación byte a byte |
| Trazas | cada participante, dentro de la carpeta de su prueba | Una línea `paso idV resultado detalle` por paso |

El reinicio carga esos volúmenes. No genera otra sV y no vuelve a registrar el incidente. preparar corre antes del pago, de la sustitución y de las firmas. Copia el original al volumen de copias, instala la confianza y termina. No genera sV ni los pares RSA. La investigación no ejecuta preparar y no monta confianza, identidad, registro, interceptado ni originales: solo una copia de los tres cifrados del pago.

### Cuatro pruebas

Cada prueba escribe en su carpeta: `pruebas/pago`, `pruebas/investigacion`, `pruebas/mitm` y `pruebas/firmas`. Las vías de pago e investigación parten de dos copias del mismo conjunto cifrado y se ejecutan por separado.

1. **Pago.** Defensa encendida. La víctima habla con el servidor. Cifra, ambos procesos se cierran y vuelven a arrancar. El pago recupera sV. El paso 6 descifra los tres contadores y la comparación los iguala, byte a byte, con el original.
2. **Investigación.** Servidor apagado. Con la copia de los cifrados, el procedimiento recupera la misma sV y el paso 6 vuelve a descifrar y a comparar. No usa el registro, claves privadas, sV guardada, variables internas del generador, material de pago ni material del intermediario.
3. **Sustitución.** Defensa apagada. La víctima habla con el intermediario y este reenvía al servidor. El intermediario sustituye pkS por su propia clave de cifrado, abre sV, la reenvía cifrada para el servidor y conserva sV. El servidor guarda esa misma sV bajo idV junto a la pkV real. Tras cerrar víctima y servidor, el intermediario recibe copias de los cifrados, fuera del protocolo, y descifra sin pago.
4. **Firmas.** Víctima nueva, otro idV, defensa encendida, el mismo intermediario. La sustitución se detecta antes de enviar la entrega de sV. Una firma hecha por el intermediario con sus propias claves se rechaza aunque adjunte su clave de verificación. El intercambio legítimo de esta prueba habla con el servidor y completa cifrado, reinicio y recuperación por pago.

### Investigación y candidata correcta

El generador suministrado se usa sin cambios. Devuelve 32 bytes. Esos bytes son un entero entre 0 y `2^24 - 1` escrito en big-endian, con ceros a la izquierda. La búsqueda recorre ese intervalo en orden, de menor a mayor.

Para cada candidata deriva Ki de i = 0 y verifica AES-GCM con el nonce, la etiqueta, el AAD y el Ci guardados de esa salida. Una candidata es correcta cuando esa verificación cuadra. Después, la misma sV debe verificar i = 1 e i = 2. Una etiqueta inválida rechaza esa salida y no la escribe en recuperados.

El costo de recorrer candidatas no depende de cuántos cifrados haya, porque el oráculo es solo i = 0. El costo posterior de descifrar sí depende de la cantidad: aquí son tres salidas de 64 bytes. La prueba registra el entorno, el tiempo, el número de candidatas examinadas y la comparación de esa estimación con lo observado.

### Diseño de firmas

ECDSA P-256 con SHA-256. El par de firma es distinto de (pkV, skV) y de (pkS, skS). La víctima firma el rol `V` y el servidor el rol `S`. Cada uno verifica con la clave de verificación del otro, instalada antes del intercambio. RSA-OAEP sigue protegiendo sV. La firma no lo reemplaza.

Una firma ausente, inválida, de rol distinto, de idV distinto o verificada con una clave que no es la instalada detiene el intercambio. La pkV del registro sigue siendo la que se usa en la recuperación por pago.

### Procedencia

Del Colab 1, sección 7, salen RSA-OAEP con SHA-256, MGF1 basado en SHA-256, etiqueta vacía y el uso de PyCryptodome para cifrar y descifrar. También sale la idea de proteger un secreto de 32 bytes con OAEP. No se reutiliza la clave RSA del cuaderno ni su módulo de 512 bytes. Aquí el módulo es de 2048 bits y el exponente público es 65537.

Del Colab 1, sección 8, salen el prefijo de longitud TCP de 4 bytes big-endian, AES-GCM con nonce de 12 bytes y etiqueta de 16 bytes, y el hábito de guardar nonce, etiqueta y cifrado. No salen de ahí la derivación de la clave de archivo, el nonce ni el transporte de la semilla. Ki es HMAC-SHA256 con sV como clave e i en 8 bytes big-endian como mensaje. Esos 32 bytes son la clave AES, sin HKDF ni sal de sesión. El nonce sale de la aleatoriedad de la biblioteca y no se repite con la misma Ki. Los participantes no comparten proceso ni se atienden en `127.0.0.1`.

Del Colab 6 y del PDF de firmas salen ECDSA P-256 con SHA-256, la biblioteca `cryptography`, y la comprobación de que un mensaje alterado, otra clave pública o una firma inválida no verifican. También sale la exigencia de saber, antes de verificar, que la clave de verificación pertenece al participante esperado. No se usa el RSA de juguete del cuaderno ni RSA-PKCS1-v1.5 como esquema de la defensa.

## User Stories

1. Como pareja de estudiantes, quiero ejecutar la víctima y el servidor en contenedores distintos de una red interna, para que el incidente ocurra en un laboratorio aislado.
2. Como pareja de estudiantes, quiero una interfaz de terminal, para repetir el ciclo sin una interfaz gráfica.
3. Como pareja de estudiantes, quiero que la infección empiece solo al ejecutar la aplicación a propósito, para cumplir el alcance del laboratorio.
4. Como pareja de estudiantes, quiero usar el generador suministrado sin modificarlo, para que sV sea el valor que la práctica exige.
5. Como víctima, quiero un solo idV durante el cifrado y la recuperación, para que todo el incidente apunte al mismo registro.
6. Como víctima, quiero generar idV, pkV y skV al iniciar, para registrar el incidente sin entregar skV.
7. Como servidor, quiero generar pkS y skS al iniciar, para responder al registro sin entregar skS.
8. Como víctima, quiero enviar idV y pkV firmados, para que el servidor acepte mi clave de cifrado solo si la firma verifica.
9. Como servidor, quiero responder con idV y pkS firmados, para que la víctima compruebe mi clave antes de usarla.
10. Como víctima, quiero conocer de antemano la clave de verificación del servidor, para rechazar una clave llegada por la red.
11. Como servidor, quiero conocer de antemano la clave de verificación de la víctima, para rechazar una clave llegada por la red.
12. Como víctima del modelo B, quiero generar sV una sola vez, para que el incidente tenga una sola semilla maestra.
13. Como víctima, quiero enviar OAEP.Enc(pkS, sV) solo después de verificar la firma, para no exponer sV a una clave sustituida.
14. Como servidor, quiero abrir esa entrega con skS y guardarla bajo idV junto a pkV, para conservarla después del reinicio.
15. Como servidor, quiero confirmar la recepción, para que la víctima sepa que puede cifrar.
16. Como víctima, quiero que un intercambio fallido se informe y no cifre, para no producir Ci sin una sV compartida.
17. Como servidor, quiero que un segundo registro del mismo idV no cree otra sV ni otra entrega inicial, para conservar un solo incidente.
18. Como víctima, quiero cifrar `notas.txt` tres veces, con i igual a 0, 1 y 2, para poder medir el efecto de la cantidad de archivos.
19. Como víctima, quiero derivar cada Ki en local con HMAC-SHA256, para no pedir al servidor una clave por archivo.
20. Como víctima, quiero guardar Ci, el nonce, la etiqueta, idV, i y el nombre de la copia, para reconstruir el AAD al descifrar.
21. Como víctima, quiero un nonce nuevo por cifrado, para no repetirlo con la misma Ki.
22. Como víctima, quiero cerrar el proceso y volver a abrirlo sin sV, sin Ki y sin la entrega OAEP en disco, para que la recuperación no reuse esa entrega.
23. Como servidor, quiero cerrar el proceso y volver a cargarlo con mi par RSA, sV, pkV y el estado del pago, para continuar el mismo incidente.
24. Como víctima, quiero solicitar la recuperación con idV, para que el pago sea un evento del protocolo.
25. Como servidor, quiero registrar el pago y devolver OAEP.Enc(pkV, sV) con la pkV ya guardada, para que la petición no cambie esa clave.
26. Como víctima, quiero abrir esa entrega con skV y descifrar los tres Ci, para recuperar la copia.
27. Como pareja de estudiantes, quiero que una etiqueta GCM inválida rechace esa salida, para no guardar un descifrado falso.
28. Como pareja de estudiantes, quiero comparar byte a byte los recuperados con el original, para evidenciar la recuperación por pago.
29. Como pareja de estudiantes, quiero repetir el descifrado sobre otra copia de los mismos cifrados, con el servidor apagado, para que la investigación no reciba la solución del pago.
30. Como investigador, quiero probar las candidatas en orden contra i = 0, para recuperar sV sin el registro del servidor.
31. Como investigador, quiero aceptar la candidata solo cuando GCM verifica, para justificar cuál sV es correcta.
32. Como investigador, quiero comprobar después i = 1 e i = 2 con esa misma sV, para separar el costo de la búsqueda del costo de descifrar tres archivos.
33. Como pareja de estudiantes, quiero registrar entorno, tiempo y candidatas examinadas, para comparar la estimación con lo observado.
34. Como intermediario, quiero sustituir pkS hacia la víctima cuando la defensa está apagada, para obtener sV en la entrega inicial.
35. Como intermediario, quiero reenviar la misma sV cifrada para el servidor, para que víctima y servidor terminen con la misma semilla.
36. Como intermediario, quiero descifrar copias de los cifrados con el servidor apagado y sin pago, para demostrar el resultado de la sustitución.
37. Como víctima con la defensa encendida, quiero rechazar la pkS sustituida antes de enviar sV, para que la firma impida la entrega.
38. Como servidor, quiero rechazar una firma del intermediario aunque venga acompañada de su clave de verificación, para no aceptar una confianza que él mismo presenta.
39. Como pareja de estudiantes, quiero una víctima nueva en la prueba de firmas, para no reutilizar el idV de las pruebas anteriores.
40. Como pareja de estudiantes, quiero que el intercambio legítimo de esa prueba complete cifrado, reinicio y pago, para mostrar que la defensa no impide el ciclo.
41. Como comparación, quiero ser el único que monta los originales, en solo lectura, para que la investigación y la sustitución no los usen de guía.
42. Como pareja de estudiantes, quiero una línea de traza por paso en la carpeta de cada prueba, para relacionar la evidencia con el diagrama.
43. Como pareja de estudiantes, quiero instrucciones para repetir las cuatro pruebas, para entregar el laboratorio sin sustentación oral.

## Implementation Decisions

- Una sola imagen. Los procesos son víctima, servidor, intermediario, preparar y comparación. La red interna se llama `laboratorio`. Sin intermediario, la víctima habla con el servidor. En la sustitución habla con el intermediario, y este reenvía al servidor.
- La defensa es un modo del mismo programa. Va apagada solo en la prueba de sustitución. En pago, investigación y firmas va encendida. La investigación no llega a usar las firmas porque no habla con nadie: solo lee cifrados.
- preparar genera el par de firma de la víctima y el del servidor, instala cada clave de verificación en el otro y copia el original al volumen de copias. En la prueba de firmas genera además un par de firma para el intermediario, que nadie instala como clave de verificación. Los pares RSA nacen en el paso 1, dentro de cada participante.
- RSA de cifrado: 2048 bits, exponente 65537, OAEP con SHA-256, MGF1-SHA256 y etiqueta vacía, mediante PyCryptodome 3.23.0. El cifrado OAEP de sV ocupa el tamaño del módulo.
- AES-256-GCM mediante la misma biblioteca. Nonce de 12 bytes tomado de su aleatoriedad. Etiqueta de 16 bytes. El AAD es idV seguido de i en 8 bytes big-endian, y se reconstruye con los campos guardados.
- Ki es el HMAC-SHA256 de sV sobre i en 8 bytes big-endian. No hay derivación HKDF ni clave de sesión.
- Firmas con la biblioteca `cryptography`: ECDSA sobre P-256 y SHA-256. Lo firmado es `actividad-iii/v1`, el rol, idV y el DER de la clave RSA.
- Cada salida cifrada es un solo binario de nombre `0000`, `0001` o `0002`. Por dentro: magia `A3C1`, versión 1, idV, i en 8 bytes, nonce, etiqueta, longitud del nombre, el nombre `notas.txt` y Ci.
- La única copia es `notas.txt`, de 64 bytes. Se cifra tres veces. La búsqueda usa únicamente la salida i = 0.
- El generador suministrado no se modifica y se llama una vez por víctima, en la víctima. La búsqueda no lee sus variables internas: prueba los enteros de 0 a `2^24 - 1` codificados en 32 bytes big-endian.
- El estado del pago distingue pendiente de pagado. La entrega por pago usa la pkV del registro.
- Cada prueba deja sus volúmenes en su propia carpeta de host. La investigación recibe solo la copia de los tres cifrados producidos por el pago.

## Testing Decisions

Un buen test mira el comportamiento externo. Sirven los volúmenes que quedan al cerrar los contenedores, las líneas de traza, el rechazo antes de que aparezca una entrega de sV y la comparación byte a byte. No sirve afirmar detalles internos de OAEP, de HMAC o del formato DER más allá de lo que esos resultados demuestran.

La costura de prueba es una sola: las cuatro pruebas del laboratorio, ejecutadas como cajas negras sobre la imagen. El repositorio no tiene pruebas previas que imitar. El generador suministrado se deja intacto y no es la superficie que se prueba.

- Pago: tras reiniciar, el registro está pagado, la identidad no contiene sV y los tres recuperados coinciden con el original.
- Investigación: el contenedor no tiene registro, identidad, originales ni interceptado. La sV hallada descifra los tres cifrados copiados del pago. El informe de la prueba separa el tiempo de la búsqueda del tiempo de descifrar.
- Sustitución: la traza muestra la clave sustituida, la apertura y el reenvío. El intermediario descifra las copias con el servidor apagado y sin pago.
- Firmas: con una víctima nueva, la traza de rechazo aparece y la entrega de sV no se envía. La firma propia del intermediario no verifica. Una corrida legítima de esa prueba completa el ciclo hasta el pago.

La comparación corre al final de cada vía que descifra. Un byte distinto es un fallo de esa prueba.

## Out of Scope

- Propagación hacia otras máquinas.
- Arranque automático al iniciar el sistema.
- Dinero real. El pago es solo el evento del protocolo que cambia el estado del registro.
- Cualquier archivo que no sea la copia de práctica `notas.txt`. No hay otros nombres, tamaños ni tipos.
- El modelo A.
- Crear issues en GitHub, GitLab, Linear o cualquier tracker remoto.
- Sustentación oral.
- Montar los originales en la víctima, el servidor o el intermediario.
- Usar skV o skS para firmar, o aceptar como confianza una clave de verificación recibida en el mensaje.
- La sesión del Colab 1 sección 8: HKDF, sal, nonce igual al contador, hilos en un solo proceso y conocimiento previo de pkS sin firma.

## Further Notes

La entrega del curso sigue siendo el código con el generador intacto, las instrucciones para repetir las cuatro pruebas y el informe en PDF. Este spec no redacta ese informe. Describe la aplicación que el informe debe explicar.

Las decisiones de dominio que este texto no vuelve a abrir están en los ADR 0001 a 0007. El vocabulario es el de `docs/GLOSSARY.md`.
