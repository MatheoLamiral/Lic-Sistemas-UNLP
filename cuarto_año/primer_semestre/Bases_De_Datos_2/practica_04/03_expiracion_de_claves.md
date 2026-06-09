# Expiración de claves

### Ejercicio 30: Agregar una clave agency con el valor "Cronos Tours".

```redis
    SET agency "Cronos Tours"
```

### Ejercicio 31: ¿Cuál es el tiempo de vida (TTL) de la clave agency?

```redis
    TTL agency
```

>[!NOTE]
> un número positivo indica los segundos que le quedan de vida, -1 indica que la clave existe pero no tiene expiración, -2 indica que la clave no existe

### Ejercicio 32: Agregar una expiración de 30 segundos a la clave agency.


```redis
    EXPIRE agency 30
```

### Ejercicio 33: ¿Cuál es el tiempo de vida de la clave agency luego de agregar la expiración?

El tiempo de vida de la clave `agency` ahora es de 30 segundos

### Ejercicio 34: Pasados los 30 segundos: ¿cuál es el TTL de agency? ¿Que retorna si se solicita el valor de agency?

Pasados los 30 segundos del, el comando TTL retonra -2, indicando que la clave no existe. Una clave con TTL vencido se elimina sola, y a partir de ahí se comporta como una clave borrada. `TTL` -> `-2` y `GET` -> `(nil)`

### Ejercicio 35: Agregar una clave agency con el valor "Cronos Tours" que expire en 20 segundos desde su creación.

```redis
    SET agency "Cronos Tours" EX 20
```