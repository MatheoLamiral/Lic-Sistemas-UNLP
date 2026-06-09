# Conjuntos (Sets)

### Ejercicio 53: Agregar un conjunto llamado airports con los siguientes valores: eze, aep, nqn, mdz, mdq, ush, fte, sla, aep, nqn, brc, cpc, juj, aep, tuc, eqs.

```redis
    SADD airports eze aep nqn mdz mdq ush fte sla aep nqn brc cpc juj aep tuc eqs
```

### Ejercicio 54: ¿Cuántos valores tiene el conjunto? ¿Por qué puede diferir de la cantidad de valores ingresados?

```redis
    SCARD airports
```
- Difiere porque en realidad no se insertaron 16 valores, ingresamos 16 en la consulta, pero se insertaron 13, ya que un `Set` no admite valores duplicados. Redis simplemente lo ignora

### Ejercicio 55: Listar los valores del conjunto airports.

```redis
    SMEMBERS airports
```

### Ejercicio 56: Quitar el valor "cpc" del conjunto airports.

```redis
    SREM airports cpc
```

### Ejercicio 57: Quitar un valor aleatorio del conjunto airports.

```redis
    SPOP airports
```

### Ejercicio 58: ¿Qué cantidad de valores tiene airports ahora?

Ahora `SCARD airports` devuelve 11

### Ejercicio 59: Comprobar si "cpc" es miembro del conjunto airports.

```redis
    SISMEMBER airports cpc
```
- Devolvió 0, porque lo eliminamos en el ejercicio 56, si perteneciera al conjunto devolvería 1

### Ejercicio 60: Mover los valores "sla" y "juj" a un nuevo conjunto denominado noa_airports.

```redis
    SMOVE airports noa_airports sla
    SMOVE airports noa_airports juj
```

### Ejercicio 61: Obtener la unión de los conjuntos airports y noa_airports. ¿Modifica los conjuntos originales?

```redis
    SUNION airports noa_airports
```
- No modifica los conjuntos originales, devuelve una copia con la unión de los mismos

### Ejercicio 62: Realizar la unión de airports y noa_airports y almacenar el resultado en un nuevo conjunto llamado total_airports.

```redis
    SUNIONSTORE total_airports airports noa_airports
```

### Ejercicio 63: Realizar la intersección entre total_airports y noa_airports.

```redis
    SINTER total_airports noa_airports
```

### Ejercicio 64: Realizar la diferencia entre total_airports y noa_airports.

```redis
    SDIFF total_airports noa_airports
```