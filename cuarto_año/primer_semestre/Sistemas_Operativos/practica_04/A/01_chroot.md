# Chroot

## Ejercicio 1:​ ¿Qué es el comando chroot? ¿Cuál es su finalidad?

`chroot` (*change root*) es un comando que **cambia el directorio raíz (`/`) que ve un proceso y todos sus hijos**. A partir de ejecutarlo, ese proceso pasa a considerar como `/` al directorio que le indicaste, y **no puede ver ni acceder a nada que esté por fuera** de ese subárbol del sistema de archivos. Al entorno virtual que se crea se lo conoce como **"jail chroot"** (cárcel chroot).

**Finalidad:** **aislar un proceso (o servicio) del resto del sistema**, limitando qué parte del filesystem puede ver. Sirve para restringir la información a la que un proceso accede (aislamiento/seguridad) y crear un entorno controlado con solo los archivos y librerías que el proceso necesita.

```bash
chroot /nuevo-directorio-raiz [comando]
```

>[!NOTE]
> `chroot` es la base histórica de los contenedores. Aísla el filesystem pero **no** los procesos, la red, etc.

## Ejercicio 2:​ Crear un subdirectorio llamado sobash dentro del directorio root. Intente ejecutar el comando chroot /root/sobash. ¿Cuál es el resultado? ¿Por qué se obtiene ese resultado?

1. Creamos el directorio `/root/sobash` con `mkdir /root/sobash`
2. Después ejecutamos `chroot /root/sobash` y vemos la siguiente salida:
    ```bash
        chroot: failed to run command '/bin/bash': No such file or directory
    ```
    - Obtenemos este resultado porque `sobash` es un directorio vacío. `chroot` va a intentar entrar ahí y, por defecto, ejecutar una shell (`/bin/bash`) dentro de ese nuevo raíz. Pero ahora, `/bin/bash` significa `/root/sobash/bin/bash` y ese archivo no existe

## Ejercicio 3:​ Cree la siguiente jerarquía de directorios dentro de sobash:

```
sobash/
├── bin
├── lib
│   └── x86_64-linux-gnu
└── lib64
```

Para realizar esto ejecutamos:
```
    cd /root/sobash
    mkdir -p bin lib/x86_64-linux-gnu lib64
```

- Con `-p`, `mkdir` crea toda la cadena automáticamente

## Ejercicio 4:​ Verifique qué bibliotecas compartidas utiliza el binario /bin/bash usando el comando ldd /bin/bash. ¿En qué directorio se encuentra linux-vdso.so.1? ¿Por qué?

bash necesita:
- `linux-vdso.so.1` =>  No tiene ruta
- `libtinfo.so.6` => `/lib/x86_64-linux-gnu/libtinfo.so.6`
- `libc.so.6` => `/lib/x86_64-linux-gnu/libc.so.6`
- `/lib64/ld-linux-x86-64.so.2` 

>[!NOTE]
> Notar que las rutas coinciden con los directorios creados en el punto 3.

Dónde está `linux-vdso.so.1` y por qué?

En la salida original vemos que todos los archivos tienen su directorio en disco y una dirección de memoria, en cambio éste, solo tiene la dirección de memoria. Esto es porque `linux-vdso.so.1` **no es un archivo en el disco**, es una **librería virtual** que el propio kernel inyecta en memoria en el **espacio de cada proceso**.

Esto es así, ya que el vDSO permite ejecutar ciertas system calls muy frecuentes (como `gettimeofday`, `clock_gettime`) sin hacer el costoso cambio a modo kernel. El **kernel expone este código directamente en el espacio de usuario**.

## Ejercicio 5:​ Copie en /root/sobash el programa /bin/bash y todas las librerías utilizadas por el programa bash en los directorios correspondientes. Ejecute nuevamente el comando chroot ¿Qué sucede ahora?

Para realizar esto ejecutamos:
```bash
    cd /root/sobash

    # el ejecutable
    cp /bin/bash bin/

    # las librerías de /lib/x86_64-linux-gnu
    cp /lib/x86_64-linux-gnu/libtinfo.so.6 lib/x86_64-linux-gnu/
    cp /lib/x86_64-linux-gnu/libc.so.6     lib/x86_64-linux-gnu/

    # el loader dinámico
    cp /lib64/ld-linux-x86-64.so.2 lib64/
```

Ahora al ejecutar `chroot /root/sobash` observamos que:
- El promt cambia (en mi caso `bash-5.2#`), lo que indica que estamos **adentro del jail**, ejecutando el bash que copiamos, con `/root/sobash` como su `/`
- Ahora sí están el bash y sus librerías en las rutas que el chroot espera, así que el loader encuentra todo lo que necesita para arrancar la shell.

## Ejercicio 6:​ ¿Puede ejecutar los comandos cd "directorio" o echo? ¿Y el comando ls? ¿A qué se debe esto?

`cd` y `echo` si funcionan porque son **built-in de bash**, es decir, su código ya esta dentro del `/bin/bash`. En cambio `ls` no funciona, ya que es un programa externo (archivo `/bin/ls`) y como no lo copiamos, no existe en la jail, entonces al intentar ejecutarlo vemos `command not found`

>[!NOTE]
> Si quisieramos poder utilizarlo, tendriamos que copiar sus propias librerías también (`ldd /bin/ls`) igual que con bash

## Ejercicio 7:​ ¿Qué muestra el comando pwd? ¿A qué se debe esto?

El comando `pwd` muestra `/`. Esto se debe a que `pwd` reporta el directorio actual **relativo a la raíz del proceso**, y el chroot cambió esa raíz a `/root/sobash`. El proceso **no tiene forma de saber** que su `/` es en realidad `/root/sobash` en el sistema real, el chroot le oculta todo lo que está por encima, así que solo puede expresar rutas **dentro del jail**. 

## Ejercicio 8:​ Salir del entorno chroot usando exit

Salimos del entorno con `exit` (también es **built-in**)

## Ejercicio 9:​ Usando el repositorio de la cátedra acceda a los materiales en practica4/02-chroot:

### a. Verifique que tiene instalado busybox en /bin/busybox

- Para verificarlo ejecutamos `ls -l /bin/busybox`
- Deberíamos ver algo como:
    ```bash
        -rwxr-xr-x 1 root root 772880 abr 23  2023 /bin/busybox
    ```

### b. Cree un chroot con busybox usando /buildbusyboxroot.sh

Para hacer esto ejecutamos:

```bash
    su -
    cd /home/so/codigo-para-practicas/practica4/02-chroot
    ./buildbusyboxroot.sh        # o: make build
```

### c. Entre en el chroot

Entramos con: `chroot busyboxroot /bin/sh`

>[!NOTE]
> El `/bin/sh` final es el **comando que chroot ejecuta dentro del nuevo raíz** (una shell para poder trabajar adentro). Se usa `/bin/sh` y no `/bin/bash` porque en este jail la shell la provee **busybox** (el script crea un symlink `/bin/sh → busybox`), no hay bash. La sintaxis es `chroot <nuevo_raiz> [comando]`.

### d. Busque el directorio /home/so ¿Qué sucede? ¿Por qué?

No encontramos el directorio, porque el nuevo `/` es `busyboxroot/`, que dentro solo tiene `bin`, `lib`, `lib64` y `proc`. `/home/so` existe en el sistema real, pero el `chroot` oculta todo lo de afuera, haciendo que para el proceso, ese directorio no exista

### e. Ejecute el comando "ps aux" ¿Qué procesos ve? ¿Por qué (pista: ver contenido de /proc)?

No se ve ningún proceso, ya que ps no "pregunta" al kernel por los procesos, sino que **lee la información de** `/proc`, y este está vacío (es el directorio que creó el script sin montar nada). 

### f. Monte /proc con "mount -t proc proc /proc" y vuelva a ejecutar "ps aux" ¿Qué procesos ve? ¿Por qué?

Ahora se ven todos los procesos del sistema (host). Al montar `/proc` dentor del chroot, montas el `/proc` real del kernel, que lista todos los procesos del sistema, no solo los del jail. 

>[!IMPORTANT]
> `chroot` NO aisla los procesos, solo el filesystem, por eso vemos procesos fuera del jail

### g. Acceda a /proc/1/root/home/so ¿Qué sucede?

Podemos acceder al `/home/so` del sistema real (el mismo que en el inciso d "no existía"). Esto pasa porque `/proc/1/root` es un **symlink al directorio raíz del proceso 1** (`init`/`systemd`), que corre con el **raíz real del sistema**. Como ahora `/proc` está montado, podemos "viajar" a través de `/proc/1/root` y llegar al filesystem completo del host.

>[!IMPORTANT]
> Esto significa que **nos escapamos del chroot**: estando dentro del jail, logramos leer archivos que están fuera de él. Demuestra que el aislamiento de chroot es débil y evitable (sobre todo siendo root).

### h. ¿Qué conclusiones puede sacar sobre el nivel de aislamiento provisto por chroot?

`chroot` provee un aislamiento limitado y débil, solo acota la vista del sistema de archivos.
- Solo aisla el filesystem
- No aisla los procesos
- Es evitable (se puede escapar)

`chroot` no es un mecanismo de seguridad ni de aislamiento real. Sirve para acotar qué parte del filesystem ve un proceso, pero no contiene a un proceso malicioso ni lo aisla del resto del sistema

>[!NOTE]
> Para un aislamiento verdadero hacen falta los namespaces (asilan procesos, red y demás recursos) junto con los cgroups (limitan recursos)