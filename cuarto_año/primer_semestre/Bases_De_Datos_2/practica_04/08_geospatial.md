# Geospatial

### Ejercicio 89: Agregar en un conjunto denominado cities las siguientes localidades con sus coordenadas (longitud, latitud):

| Ciudad | Latitud | Longitud |
|---|---|---|
| Buenos Aires | -34.61315 | -58.37723 |
| Cordoba | -31.41350 | -64.18105 |
| Rosario | -32.94682 | -60.63932 |
| Mendoza | -32.89084 | -68.82717 |
| San Miguel de Tucuman | -26.82414 | -65.22260 |
| La Plata | -34.92145 | -57.95453 |
| Mar del Plata | -38.00042 | -57.55620 |
| Salta | -24.78590 | -65.41166 |
| Santa Fe | -31.64881 | -60.70868 |
| San Juan | -31.53750 | -68.53639 |
| Resistencia | -27.46056 | -58.98389 |
| Santiago del Estero | -27.79511 | -64.26149 |
| Posadas | -27.36708 | -55.89608 |
| San Salvador de Jujuy | -24.19457 | -65.29712 |
| Bahia Blanca | -38.71959 | -62.27243 |
| Parana | -31.73271 | -60.52897 |

> [!NOTE]
> En Redis, los datos geoespaciales se almacenan como conjuntos ordenados (Sorted Sets). Las coordenadas se pasan en el orden **longitud, latitud** (no latitud, longitud).

```redis
    GEOADD cities -58.37723 -34.61315 "Buenos Aires" -64.18105 -31.41350 "Cordoba" -60.63932 -32.94682 "Rosario" -68.82717 -32.89084 "Mendoza" -65.22260 -26.82414 "San Miguel de Tucuman" -57.95453 -34.92145 "La Plata" -57.55620 -38.00042 "Mar del Plata" -65.41166 -24.78590 "Salta" -60.70868 -31.64881 "Santa Fe" -68.53639 -31.53750 "San Juan" -58.98389 -27.46056 "Resistencia" -64.26149 -27.79511 "Santiago del Estero" -55.89608 -27.36708 "Posadas" -65.29712 -24.19457 "San Salvador de Jujuy" -62.27243 -38.71959 "Bahia Blanca" -60.52897 -31.73271 "Parana"

```

### Ejercicio 90: Obtener todos los miembros del conjunto cities.

```redis
    ZRANGE cities 0 -1
```

### Ejercicio 91: Obtener las coordenadas almacenadas de Santa Fe.

```redis
    GEOPOS cities "Santa Fe"
```

### Ejercicio 92: Obtener la distancia en kilómetros entre Buenos Aires y Córdoba.

```redis
    GEODIST cities "Buenos Aires" Cordoba km
```

### Ejercicio 93: Obtener las ciudades que se encuentran en un radio de 100 km de la coordenada (-27.37, -55.9), incluyendo la distancia de cada una.

```redis
    GEOSEARCH cities FROMLONLAT -55.9 -27.37 BYRADIUS 100 km WITHDIST
```

### Ejercicio 94: Obtener las ciudades que se encuentran a menos de 700 km de Córdoba.

```redis
    GEOSEARCH cities FROMMEMBER "Cordoba" BYRADIUS 700 km
```