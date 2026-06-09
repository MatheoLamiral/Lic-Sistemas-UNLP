# Manejo de claves

### Ejercicio 24: ​Obtener todas las claves que empiecen con "v".

```redis
    KEYS v*
```

### Ejercicio 25: ​Obtener todas las claves que contengan la letra "t".

```redis
    KEYS *t*
```

### Ejercicio 26: Obtener todas las claves que terminan con "age".

```redis
    KEYS *age
```

### Ejercicio 27:​ Renombrar la clave "package" por "bariloche package".

```redis
    RENAME package "bariloche package"
```

### Ejercicio 28: ¿Qué comando se utiliza para renombrar una clave solo si el nombre destino no existe aún?

El comando es `RENAMENX`, el sufijo `NX` significa "Not eXists", devuelve 1 si renombró, 0 si no hizo nada

### Ejercicio 29: ​Eliminar todas las claves.

```redis
    FLUSHALL
```