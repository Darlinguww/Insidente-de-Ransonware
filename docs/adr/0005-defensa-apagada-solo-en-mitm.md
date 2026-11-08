# La defensa va apagada solo en la prueba MITM

Las cuatro pruebas salen del mismo programa. El MITM necesita que la sustitución de la clave pública llegue a cifrar `sV`; con la defensa encendida ese envío no ocurre. Por eso el MITM corre con la defensa apagada, y el pago, la investigación y la prueba de firmas corren con la defensa encendida. La investigación usa otra copia de los mismos cifrados y no monta el registro ni los originales.
