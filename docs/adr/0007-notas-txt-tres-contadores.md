# Una sola copia, tres contadores

La búsqueda de `sV` usa un solo cifrado, así que archivos grandes no cambian ese costo. La página 3 del enunciado pide, además, ver cómo la cantidad de archivos cambia el descifrado posterior. Por eso la única copia es `notas.txt`, de 64 bytes, y se cifra tres veces con `i` igual a 0, 1 y 2. La investigación prueba candidatos solo contra `i = 0`.
