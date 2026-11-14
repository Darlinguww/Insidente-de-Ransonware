# 10: Instrucciones de las cuatro pruebas

**What to build:** La pareja puede repetir, con la terminal, las pruebas de pago, investigaciÃ³n, sustituciÃ³n y firmas, y recoger de cada una las trazas, los cifrados y el resultado de la comparaciÃ³n. Las instrucciones dicen cÃ³mo preparar las copias y cÃ³mo mantener separados los datos de cada prueba.

**Blocked by:** 06 Pago y comparaciÃ³n, 07 InvestigaciÃ³n, 08 Intermediario, 09 Firmas

**Status:** ready-for-agent

- [ ] Las instrucciones nombran las dependencias, la preparaciÃ³n del entorno y el comando de cada prueba.
- [ ] Explican cÃ³mo crear `notas.txt` y cÃ³mo separar `pruebas/pago`, `pruebas/investigacion`, `pruebas/mitm` y `pruebas/firmas`.
- [ ] Dicen dÃ³nde queda la traza `paso idV resultado detalle` y dÃ³nde queda la comparaciÃ³n byte a byte.
- [ ] Repetir las cuatro pruebas no mezcla la sV del pago con la investigaciÃ³n, ni la defensa apagada de la sustituciÃ³n con la defensa encendida de las firmas.
- [ ] El generador suministrado sigue sin cambios en el material que se entrega.


## Answer

`LEEME.txt` reescrito con dependencias, preparación, modo defensa, comando por prueba (pago, investigación, mitm, firmas), ubicación de trazas y comparación, aislamiento entre pruebas, y confirmación de que el generador no cambia.
