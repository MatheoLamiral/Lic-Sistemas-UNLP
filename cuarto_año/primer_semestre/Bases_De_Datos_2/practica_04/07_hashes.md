# Hashes

### Ejercicio 79: Agregar a un hash llamado user:cronos los siguientes campos: "razon social" "cronos s.a", domicilio "47 236 La Plata", "telefono" 2215556677.

```redis
    HSET user:cronos "razon social" "cronos s.a" domicilio "47 236 La Plata" telefono 2215556677
```

### Ejercicio 80: Agregar el campo mail con el valor info@cronos.com.ar al hash user:cronos.

```redis
    HSET user:cronos mail info@cronos.com.ar
```

### Ejercicio 81: Obtener todos los campos y valores de user:cronos.

```redis
    HGETALL user:cronos
```

### Ejercicio 82: Obtener únicamente el valor del campo mail de user:cronos.

```redis
    HGET user:cronos mail
```

### Ejercicio 83: Eliminar el campo teléfono de user:cronos.

```redis
    HDEL user:cronos telefono
```

### Ejercicio 84: Obtener la cantidad de campos de user:cronos.

```redis
    HLEN user:cronos
```

### Ejercicio 85: Obtener las claves (nombres de campos) de user:cronos.

```redis
    HKEYS user:cronos
```

### Ejercicio 86: Determinar si existe el campo cuil en user:cronos.

```redis
    HEXISTS user:cronos cuil
```
- Devuelve 1 si existe, 0 si no

### Ejercicio 87: Obtener todos los valores (sin los nombres de campos) de user:cronos.

```redis
    HVALS user:cronos
```

### Ejercicio 88: Obtener la longitud del valor del campo mail de user:cronos.

```redis
    HSTRLEN user:cronos mail
```