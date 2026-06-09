# Manejo de Strings

## Valores de texto 

### Ejercicio 9: Agregar una clave package con el valor "Bariloche 3 days".

```redis
    SET package "Bariloche 3 days"
```

### Ejercicio 10:Agregar una clave user con el valor "Turismo BD2". Obtener el valor de la clave user.

```redis
    SET user "Turismo BD2" 
```

```redis
    GET user
``` 

### Ejercicio 11: ​Obtener todas las claves almacenadas actualmente.

```redis
    KEYS *
```

### Ejercicio 12: ​Agregar una clave user con el valor "Cronos Turismo". ¿Cuál es el valor actual de la clave user?

```redis
    SET user "Cronos Turismo"
```

- El valor actual es "Cronos Turismo". `user` ya existía con el valor "Turismo BD2" y al hacer `SET` de nuevo sobre la misma clave, Redis la sobreescribe.

>[!NOTE]
> `SET` no distingue entre "crear" y "actualizar", si la clave existe, pisa el valor anterior. 

### Ejercicio 13: ​Concatenar " S.A." a la clave user. ¿Cuál es el valor actual de la clave user?

```redis
    APPEND user " S.A." 
```

### Ejercicio 14: ​Eliminar la clave user. ¿Qué valor retorna si se intenta obtener la clave user luego de eliminarla?

- Primero eliminamos la clave:
    ```redis
        DEL user
    ```
- Despues si queremos obtener de nevo la clave, nos devolverá el valor `(nil)`

## Valores numéricos 

### Ejercicio 15: ​Verificar si existe la clave visits.

Al hacer `GET visits` debería devolver `(nil)`. Pero el comando mas adecuado es:
```redis
    EXISTS visits
```
- Devuelve 1 si existe, 0 si no 

### Ejercicio 16: ​Agregar una clave visits con el valor 0.

```redis
    SET visits 0
```

### Ejercicio 17: ​Incrementar en 1 la clave visits. ¿Cuál es el valor actual?

```redis
    INCR visits
```

- El valor pasa a ser 1

### Ejercicio 18: Incrementar en 5 la clave visits. ¿Cuál es el valor actual?

```redis
    INCRBY visits 5
```

- El valor pasa a ser 6

### Ejercicio 19: Decrementar en 1 la clave visits. ¿Cuál es el valor actual?

```redis
    DECR visits
```

- El valor pasa a ser 5

### Ejercicio 20:​ Incrementar en 2 la clave visits. ¿Cuál es el valor actual?

```redis
    INCRBY visits 2
```

- El valor pasa a ser 7

### Ejercicio 21: Agregar una clave "value package" con el valor 539789.32.

```redis
    SET "value package" 539789.32
```

### Ejercicio 22:​ Incrementar en 20000 la clave "value package". ¿Cuál es el valor actual?

```redis
    INCRBYFLOAT "value package" 20000
```

- El valor actual pasa a ser 559789.32

### Ejercicio 23: ​¿Cual es el tipo de datos de "value package", visits y user?

```redis
    TYPE "value package"
```
- Es de tipo `string`
```redis
    TYPE visits
```
- Es de tipo `string`
```redis
    TYPE user
```
- Es de tipo `none`

>[!NOTE]
> En Redis todos los valores escalares son de tipo `string`, `none` indica que la clave no existe.