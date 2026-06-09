# Listas

### Ejercicio 36: ​Insertar una lista llamada pets con el valor "dog".

```redis
    RPUSH pets "dog"
```

### Ejercicio 37: ¿Qué sucede si se ejecuta el comando GET sobre pets? ¿Cómo se obtienen los valores de una lista?

si hacemos `GET` sobre pets, nos devuelve el error `WRONGTYPE Operation against a key holding the wrong kind of value`, ya que los valores de las listas se obtienen con:
- `LRANGE clave inicio fin` para un rango de elementos
- `LINDEX clave i` para el elemento de la posición i (negativos desde el final)
- `LLEN clave` cantidad de elementos

### Ejercicio 38: Agregar a la lista pets el valor "cat" por la izquierda.

```redis
    LPUSH pets "cat"
```

### Ejercicio 39: Agregar a la lista pets el valor "fish" por la derecha.

```redis
    RPUSH pets "fish"
```

### Ejercicio 40: ¿Qué tipo de dato es el valor de pets?

El valor `pets` es de tipo `list`, lo confirmamos realizando `TYPE pets`

### Ejercicio 41: Eliminar el valor del extremo izquierdo de la lista.

```redis
    LPOP pets
```

### Ejercicio 42: Eliminar el valor del extremo derecho de la lista.

```redis
    RPOP pets
```

### Ejercicio 43: Agregar a una clave "vuelo:ar389" los valores: aep, mdz, brc, nqn y mdq.

```redis
    RPUSH "vuelo:ar389" aep mdz brc nqn mdq
```

### Ejercicio 44: Ordenar los valores de la lista "vuelo:ar389". ¿Qué sucede si se solicitan todos los valores de la lista luego de ordenarla?

```redis
    SORT "vuelo:ar389" ALPHA 
```
-  Si luego ejecutamos `LRANGE "vuelo:ar389" 0 -1` devolverá la lista con el orden original, ya que `SORT` no modifica la lista original, solo devuelva una copia ordenada

### Ejercicio 45: Insertar el valor "fte" inmediatamente después de "brc".

```redis
    LINSERT "vuelo:ar389" AFTER brc fte
```

### Ejercicio 46: Insertar el valor "ush" inmediatamente antes de "fte".

```redis
    LINSERT "vuelo:ar389" BEFORE fte ush
```

### Ejercicio 47: Modificar el último elemento de la lista por "sla".

```redis
    LSET "vuelo:ar389" -1 sla
```

### Ejercicio 48: Obtener la cantidad de elementos de "vuelo:ar389".

```redis
    LLEN "vuelo:ar389"
```

### Ejercicio 49: Obtener el tercer valor de "vuelo:ar389".

```redis
    LINDEX "vuelo:ar389" 2
```

>[!NOTE]
> Ponemos 2 ya que el índice arranca en 0 

### Ejercicio 50: Eliminar el valor "aep" de "vuelo:ar389".

```redis
    LREM "vuelo:ar389" 1 "aep"
```

>[!NOTE]
> Esto borra la primera ocurrencia de aep, si hubiese mas ocurrencias, podriamos elegir cuantas eliminar. >0 elimina desde la izquierda, <0 desde la derecha y 0 elimina todas

### Ejercicio 51: Quedarse únicamente con los valores de las posiciones 3 a 5 de "vuelo:ar389".

```redis
    LTRIM "vuelo:ar389" 2 4
```

>[!NOTE]
> Asumo que posiciones se refiere a las posiciones naturales "humanas", si se interpretan como índices entonces seria `LTRIM "vuelo:ar389" 3 5` 

### Ejercicio 52: Agregar en "vuelo:ar389" el valor "fte". ¿Cuántas veces aparece ahora en la lista?

```redis
    RPUSH "vuelo:ar389" fte
```
- Ahora `fte` aparece dos veces en la lista 
