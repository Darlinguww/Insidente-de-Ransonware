# La víctima genera la semilla maestra

La Actividad III ofrece dos modelos. Elegimos el B: la víctima llama una sola vez a `generar_semilla_maestra()`, protege `s_V` con RSA-OAEP bajo `pk_S` y el servidor la guarda bajo `id_V` junto a `pk_V`. El modelo A queda descartado, así que el servidor no genera ni envía la maestra en la entrega inicial.
