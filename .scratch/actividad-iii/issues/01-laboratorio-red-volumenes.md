# 01: Laboratorio: red, volúmenes y copias

**What to build:** La pareja de estudiantes levanta la víctima, el servidor, el intermediario y la comparación en contenedores de una misma imagen, unidos por una red interna. El generador suministrado queda intacto. Los originales solo los ve la comparación, en solo lectura. Un comando preparar copia `notas.txt` al volumen de copias y termina sin generar sV ni los pares RSA.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Víctima, servidor, intermediario y comparación arrancan en la red interna `laboratorio` y no publican puertos hacia fuera.
- [ ] El generador suministrado se usa tal cual: no recibe argumentos y devuelve 32 bytes.
- [ ] El volumen de originales está montado solo en la comparación y solo se puede leer.
- [ ] preparar deja una copia de `notas.txt`, de 64 bytes, en el volumen de copias.
- [ ] preparar no genera sV, no genera pares RSA y no cifra.
