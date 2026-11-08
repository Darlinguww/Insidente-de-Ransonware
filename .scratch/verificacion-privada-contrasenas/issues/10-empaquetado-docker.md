# Empaquetado con Docker Compose

**Status:** ready-for-agent
**Assignee:** Daniel Cruzado Agudelo
**Complexity:** 2
**Spec:** ../spec.md

## What to build

Otra persona del equipo levanta el prototipo con Docker Compose y repite la comprobación sin instalar Go a mano. Quedan en marcha el Administrador, el Servidor OPRF y el Cliente, con las versiones fijadas de Go, de circl y de la suite. Un corpus sintético pequeño se publica al arrancar, y consultar una contraseña de ese corpus responde COMPROMETIDA.

## Acceptance criteria

- [ ] `docker compose up` deja servidos los tres actores: admin, servidor y cliente. El Servidor responde GET /v1/parameters con la suite y la época del corpus de demostración.
- [ ] El arranque construye y publica el filtro de un corpus sintético. Una contraseña de ese corpus, introducida al Cliente por la entrada estándar, obtiene COMPROMETIDA.
- [ ] Una contraseña fuera de ese corpus, en las condiciones del fixture, obtiene NO ENCONTRADA EN LA LISTA.
- [ ] Las versiones de Go, de circl y el `suite_id` que usa el contenedor son las mismas que fijó el ticket de Evaluate, y quedan escritas donde el equipo las encuentra.
- [ ] skS del contenedor de demostración entra por el mecanismo de pruebas locales y no aparece en una imagen ni en un registro.

## Blocked by

- 07 Veredicto de pertenencia
