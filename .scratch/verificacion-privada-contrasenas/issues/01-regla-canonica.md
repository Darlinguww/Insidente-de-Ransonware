# Regla canónica compartida

**Status:** ready-for-agent
**Assignee:** Andres Gomez Rodriguez
**Complexity:** 2
**Spec:** ../spec.md

## What to build

El Cliente y el Administrador convierten una contraseña en los mismos bytes antes de cualquier criptografía. Dos escrituras Unicode que son la misma cadena en forma NFC producen la misma secuencia de bytes, y una diferencia real de caracteres produce otra.

Quien ejecuta la herramienta ve esa secuencia en hexadecimal a partir de una contraseña leída por la entrada estándar, no por los argumentos del proceso.

## Acceptance criteria

- [ ] La regla es única: normalizar a Unicode NFC y codificar en UTF-8. El Cliente y el Administrador llaman a esa misma regla.
- [ ] Una contraseña y otra que solo difiere en la forma de composición Unicode producen los mismos bytes.
- [ ] Una contraseña distinta, incluida la cadena vacía frente a una cadena no vacía, produce bytes distintos.
- [ ] La contraseña entra por la entrada estándar o por un prompt, y el resultado visible es el hexadecimal de los bytes canónicos.
- [ ] Los bytes canónicos son la entrada que más adelante consumen Evaluate y el cegado. Esta entrega no calcula el OPRF ni construye el filtro.

## Blocked by

- None (can start immediately).
