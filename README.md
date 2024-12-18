Cambios realizados:

- Se ha añadido un bucle que itera las 4 primeras paginas ya que antes se nos olvido y solo cogia la primera pagina.

- Se han cambiado las lineas: 71 resultado_valoracion = datos.search(patron_valoracion, valoracion) y 80 resultado_votos = datos.search(patron_votos, votos) ya que ambas hacen datos.search y hay que usar re.search,
    Esta correccion es la que soluciona el problema de carga

- Los metodos: def buscar_por_categoria():, def buscar_por_ingrediente(): y def buscar_por_fecha_categoria(): han sido actualizados debido a que los 3 tenian el mismo fallo, la consulta a la base de datos estaba mal
    y devolvia algunas categorias o ingredientes agrupados, debido al uso de Distinct en la consulta sql.

- Al llamar a fecha le hemos añadido un .date() al final para que solo devuelva la fecha ya que la creamos como datetime
