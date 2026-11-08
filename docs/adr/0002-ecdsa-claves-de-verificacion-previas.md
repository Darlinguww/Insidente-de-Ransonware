# La verificación usa claves de firma ya instaladas

La defensa necesita distinguir firma y cifrado, y rechazar al intermediario aunque presente su propia clave. Elegimos ECDSA P-256 con SHA-256 y un par de firma distinto de `(pkV, skV)` y de `(pkS, skS)`. Cada contenedor conoce de antemano la clave de verificación del otro; una clave llegada por la red no sustituye esa confianza, y la comprobación termina antes de cifrar `sV`.
