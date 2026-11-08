# Los originales solo los ve la comparación

La investigación y el MITM no pueden usar los archivos originales para guiar la búsqueda. Esos archivos quedan en un volumen de solo lectura montado únicamente por el servicio `comparacion`. Víctima, servidor e intermediario no lo montan; la comparación byte a byte ocurre después de recuperar.
