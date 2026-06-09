# Conjuntos ordenados

### Ejercicio 65: Agregar a un conjunto ordenado llamado passengers con los siguientes datos (score nombre): 2.5 federico, 4 alejandra, 3 julian, 1 ivan, 2 tomas, 2 luciana, 2.4 natalia.

```redis
    ZADD passengers 2.5 federico 4 alejandra 3 julian 1 ivan 2 tomas 2 luciana 2.4 natalia
```

### Ejercicio 66: Obtener los valores del conjunto passengers.

```redis
    ZRANGE passengers 0 -1 
```
    
### Ejercicio 67: Actualizar el score de luciana a 2.7.

```redis
    ZADD passengers 2.7 luciana
```

### Ejercicio 68: Agregar al conjunto passengers a silvia con score 5.1.

```redis
    ZADD passengers 5.1 silvia
```

### Ejercicio 69: Incrementar en 2 el score de alejandra.

```redis
    ZINCRBY passengers 2 alejandra
```

### Ejercicio 70: Obtener los valores del conjunto passengers con sus scores.

```redis
    ZRANGE passengers 0 -1 WITHSCORES
```

### Ejercicio 71: Obtener los valores del conjunto passengers con sus scores en orden inverso.

```redis
    ZREVRANGE passengers 0 -1 WITHSCORES
```

### Ejercicio 72: Obtener la cantidad de elementos del conjunto passengers.

```redis
    ZCARD passengers
```

### Ejercicio 73: Obtener la cantidad de elementos que tienen scores entre 2 y 3.

```redis    
    ZCOUNT passengers 2 3
``` 

### Ejercicio 74: Obtener el ranking de julian en el conjunto passengers.

```redis
    ZRANK passengers julian
```
- También podríamos usar `ZREVRANK` si se entiende "ranking" como mayor puntaje = mejor puesto:
```redis
    ZREVRANK passengers julian
```

>[!NOTE]
> `ZRANK` cuenta desde el menor score (0-based, ascendente) y `ZREVRANK` desde el mayor. Como julian tiene un score alto, con `ZRANK` queda en una posición alta ("peor") y con `ZREVRANK` queda cerca del puesto 0 ("mejor").

### Ejercicio 75: Obtener el score de tomas en el conjunto passengers.

```redis
    ZSCORE passengers tomas
```

### Ejercicio 76: Extraer el elemento con menor score del conjunto passengers.

```redis
    ZPOPMIN passengers
```

### Ejercicio 77: Extraer el elemento con mayor score del conjunto passengers.

```redis
    ZPOPMAX passengers
```

### Ejercicio 78: Eliminar del conjunto passengers al valor silvia.

```redis
    ZREM passengers silvia
```
