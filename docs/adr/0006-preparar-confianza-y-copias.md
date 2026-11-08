# La confianza y las copias se preparan antes del paso 1

Los pares RSA nacen en el paso 1, dentro de cada participante. Un comando `preparar` de la misma imagen, anterior a ese paso, genera los pares de firma, instala en cada lado la clave de verificación del otro y copia los originales al volumen de copias. No genera `sV`. El intermediario no recibe esas claves; en la prueba de firmas recibe un par propio que la víctima y el servidor no aceptan. La investigación no lo ejecuta.
