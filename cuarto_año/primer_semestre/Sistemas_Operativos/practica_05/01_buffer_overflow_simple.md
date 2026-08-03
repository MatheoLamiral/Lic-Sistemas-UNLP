# Buffer Overflow simple

## Ejercicio 1: Compilar usando el makefile provisto el ejemplo 00-stack-overflow.c provisto en el repositorio de la cátedra.

1. `cd ~/codigo-para-practicas/practica5/overflow`
2. `make`  

## Ejercicio 2: Ejecutar el programa y observar las direcciones de las variables `access` y `password`, así como la distancia entre ellas.

1. `./00-stack-overflow` 
- access pointer:   0x7ffcaf24ff5f
- password pointer: 0x7ffcaf24ff40
- distance: 31
- `distance = access - password = 0x5f - 0x40 = 0x1f = **31 bytes**`

## Ejercicio 3: Probar el programa con una password cualquiera y con "big secret" para verificar que funciona correctamente.

```bash
so@so:~/codigo-para-practicas/practica5/overflow$ ./00-stack-overflow
access pointer: 0x7ffc7d00616f, password pointer: 0x7ffc7d006150, distance: 31
Write password: cualquiera
Access denied
so@so:~/codigo-para-practicas/practica5/overflow$ ./00-stack-overflow
access pointer: 0x7ffcb95c62bf, password pointer: 0x7ffcb95c62a0, distance: 31
Write password: big secret
Now you know the secret
```

## Ejercicio 4: Volver a ejecutar pero ingresar una password lo suficientemente larga para sobreescribir `access`. Usar distance como referencia para establecer la longitud de la password.

```bash
so@so:~/codigo-para-practicas/practica5/overflow$ ./00-stack-overflow
access pointer: 0x7ffe307de3cf, password pointer: 0x7ffe307de3b0, distance: 31
Write password: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Now you know the secret
```

Como la distancia es de 31, necesitamos 31 caracteres para llegar hasta access + 1 caracter más (no 0) que caiga justo sobre access

## Ejercicio 5: Después de realizar la explotación, reflexiona sobre las siguientes preguntas:

### a. ¿Por qué el uso de gets() es peligroso?

Porque `gets()` **lee la entrada sin verificar el límite del buffer**. Si el usuario ingresa más mas caracteres de los que entran, sigue escribiendo más allá del buffer, pisando variables adyacentes, el rbp (register base pointer) guardado o la dirección de retorno. Es la puerta directa al buffer overflow.

### b. ¿Cómo se puede prevenir este tipo de vulnerabilidad?

- Usar funciones que reciben el tamaño del buffer: `fgets(buf, sizeof(buf), stdin)` en vez de `gets()`
- Validar la logitud de la entrada antes de copiarla
- En general, nunca copiar datos de tamaño no controlado a un buffer fijo

### c. ¿Qué medidas de seguridad ofrecen los compiladores modernos para evitar estas vulnerabilidades?

- **Stack canary**: coloca un valor centinela entre las variables y la dirección de retorno; si un overflow lo altera, aborta el programa.
- **NX / stack no ejecutable**: impide ejecutar código inyectado en el stack.
- **ASLR + PIE**: aleatoriza las direcciones para que el atacante no las pueda predecir.
- **Fortify**: reemplaza funciones inseguras por versiones con chequeo de tamaño.
- **CFI**: protege el flujo de control.