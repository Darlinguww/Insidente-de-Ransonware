# 03: Entrega de sV

**What to build:** Con el incidente ya registrado y la defensa apagada, la víctima genera sV una sola vez y se la entrega al servidor. El servidor la abre, la guarda bajo ese idV junto a pkV y confirma. Si el intercambio falla, ambos lo informan y el cifrado no empieza.

**Blocked by:** 02 Registro del incidente

**Status:** ready-for-agent

- [ ] sV sale de una sola llamada al generador suministrado, hecha en la víctima.
- [ ] La víctima envía OAEP.Enc(pkS, sV) con SHA-256, MGF1-SHA256 y etiqueta vacía.
- [ ] El servidor recupera esa misma sV con skS y la deja en el registro junto a idV y pkV, con el pago pendiente.
- [ ] El servidor confirma la recepción con ese idV.
- [ ] Si la entrega no se puede abrir, la traza muestra el error y no aparece ningún Ci.
