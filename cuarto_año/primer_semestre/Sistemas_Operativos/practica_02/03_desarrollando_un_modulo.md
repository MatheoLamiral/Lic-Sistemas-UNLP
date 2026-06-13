# Desarrollando un módulo simple para Linux

El objetivo de este ejercicio es crear un módulo sencillo y poder cargarlo en nuestro kernel con el fin de consultar que el mismo se haya registrado correctamente.

## Ejercicio 1:​ Crear el archivo memory.c con el siguiente código (puede estar en cualquier directorio, incluso fuera del directorio del kernel):

```c
#include <linux/module.h>
MODULE_LICENSE("Dual BSD/GPL");
```

- Para hacer esto:
    1. `nano memory.c`
    2. pegamos adentro:
        ```c
            #include <linux/module.h>
            MODULE_LICENSE("Dual BSD/GPL"); 
        ```
        - `#include <linux/module.h>` trae las macros y definiciones necesarias para que el código se pueda compilar como módulo del kernel
        - `MODULE_LICENSE("Dual BSD/GPL")` declara la licencia del módulo.

## Ejercicio 2:​ Crear el archivo Makefile con el siguiente contenido:

```makefile
    obj-m := memory.o   
```

- Para hacer esto:
    1. En el mismo direcorio donde creamos `memory.c`: `nano Makefile`

### Responda lo siguiente:

#### a. Explique brevemente cual es la utilidad del archivo Makefile.

El `Makefile` es el archivo que usa la herramienta make para saber qué compilar y cómo. En el caso de un módulo del kernel, no se compila "a mano" con gcc, sino que se delega al sistema kbuild del kernel. La línea `obj-m := memory.o` le indica a kbuild que el objetivo es generar un módulo cargable (`.ko`) a partir de `memory.o`. Así se automatiza todo el proceso de compilación con los flags y headers correctos del kernel.

#### b. ¿Para qué sirve la macro `MODULE_LICENSE`? ¿Es obligatoria?

`MODULE_LICENSE` declara bajo qué licencia se distribuye el módulo (en este caso `Dual BSD/GPL`). El kernel la usa para decidir si el módulo puede acceder a símbolos exportados como GPL-only (`EXPORT_SYMBOL_GPL`).  
No es obligatoria para que compile, pero si falta (o declara una licencia no compatible con GPL), al cargar el módulo el kernel lo marca como tainted (contaminado) y emite una advertencia en `dmesg`. En la práctica siempre se incluye.

## Ejercicio 3:​ Ahora es necesario compilar nuestro módulo usando el mismo kernel en que correrá el mismo, utilizaremos el que instalamos en el primer paso del ejercicio guiado.

```bash
$ make -C <KERNEL_CODE> M=$(pwd) modules
```

- Para hacer esto:
  1. Ejercutamos `make -C /home/so/kernel/linux-6.13 M=$(pwd) modules` 

### Responda lo siguiente:

#### a. ¿Cuál es la salida del comando anterior?

La compilación termina sin errores, mostrando cada etapa del build:

```
make: se entra en el directorio '/home/so/kernel/linux-6.13'
make[1]: se entra en el directorio '/home/so/practica2'
  CC [M]  memory.o
  MODPOST Module.symvers
  CC [M]  memory.mod.o
  CC [M]  .module-common.o
  LD [M]  memory.ko
make[1]: se sale del directorio '/home/so/practica2'
make: se sale del directorio '/home/so/kernel/linux-6.13'
```

- `CC [M] memory.o` → compila `memory.c` a código objeto.
- `MODPOST Module.symvers` → procesa y verifica los símbolos del módulo.
- `CC [M] memory.mod.o` / `.module-common.o` → compila los archivos autogenerados con los metadatos del módulo.
- `LD [M] memory.ko` → enlaza todo y genera el módulo cargable final `memory.ko`.

#### b. ¿Qué tipos de archivo se generan? Explique para qué sirve cada uno.

| Archivo | Para qué sirve |
|---|---|
| `memory.o` | Código objeto compilado de `memory.c` (todavía no es un módulo). |
| `memory.ko` | **Kernel Object**: el módulo cargable final. Es el que se carga con `insmod memory.ko`. |
| `memory.mod.c` / `memory.mod.o` | Código y objeto autogenerados con metadatos del módulo (versión, info de símbolos) que MODPOST necesita para construir el `.ko`. |
| `Module.symvers` | Tabla de símbolos exportados y sus versiones (CRC), usada para verificar compatibilidad. |
| `modules.order` | Orden en que se construyen los módulos. |
| `.memory.*.cmd` (ocultos) | Comandos internos que kbuild usa para las compilaciones incrementales. |

#### c. Con lo visto en la Práctica 1 sobre Makefiles, construya un Makefile de manera que si ejecuto:
- i. **make**, nuestro módulo se compila
- ii. **make clean**, limpia el módulo y el código objeto generado
- iii. **make run**, ejecuta el programa

Combinando lo de kbuild con reglas propias:

```makefile
KERNEL_CODE := /home/so/kernel/linux-6.13

obj-m := memory.o

all:
	make -C $(KERNEL_CODE) M=$(PWD) modules

clean:
	make -C $(KERNEL_CODE) M=$(PWD) clean

run:
	sudo insmod memory.ko
	lsmod | grep memory
```

- `make` → compila el módulo (objetivo `all`).
- `make clean` → borra `.ko`, `.o` y todos los archivos intermedios (lo hace el propio kbuild con `clean`).
- `make run` → carga el módulo y verifica que quedó registrado.

> Nota: como el módulo de este punto todavía no tiene `module_init`/`module_exit`, `make run` lo carga pero no imprime nada en `dmesg`; eso recién aplica desde el Ejercicio 7. Para descargarlo: `sudo rmmod memory`.

## Ejercicio 4:​ El paso que resta es agregar y eventualmente quitar nuestro módulo al kernel en tiempo de ejecución.

Ejecutamos:

```bash
    # insmod memory.ko
```

- Para hacer esto (el `#` indica que se ejecuta como root):
  1. `su -`
  2. `cd /home/so/practica2`
  3. `insmod memory.ko` (si todo sale bien no imprime nada).

### Responda lo siguiente:

#### a. ¿Para qué sirven el comando insmod y el comando modprobe? ¿En qué se diferencian?

Ambos sirven para **cargar módulos** (`.ko`) al kernel en tiempo de ejecución, pero se diferencian en cómo manejan las **dependencias**:

- **`insmod`** (*insert module*): carga **un único** archivo `.ko` indicándole la ruta exacta. Es "literal", no resuelve dependencias. Si el módulo necesita de otro que no está cargado, falla con un error de símbolos no resueltos (*unknown symbol*).
- **`modprobe`**: carga el módulo **por su nombre** (sin ruta ni extensión) buscándolo en `/lib/modules/<version>/`. Antes de cargarlo, consulta el archivo `modules.dep` y **carga automáticamente todas sus dependencias** en el orden correcto. También permite descargar módulos con `modprobe -r`.

>[!NOTE]
> En resumen, `insmod` es de bajo nivel y carga un solo módulo, `modprobe` es más inteligente, resuelve la cadena completa de dependencias y trabaja por nombre. Para módulos propios en desarrollo (como este) se suele usar `insmod` porque el `.ko` está en el directorio local y no se instaló en `/lib/modules/`.

## Ejercicio 5:​ Ahora ejecutamos:

```bash
$ lsmod | grep memory
```

### Responda lo siguiente:

#### a. ¿Cuál es la salida del comando? Explique cuál es la utilidad del comando lsmod.

La salida es la línea correspondiente a nuestro módulo, algo como:

```
memory                  8192  0
```

Las tres columnas son: **nombre** del módulo, **tamaño** que ocupa en memoria (en bytes) y **uso** (cantidad de módulos/procesos que dependen de él. `0` significa que nadie lo usa y por lo tanto se puede descargar).

>[!NOTE]
> `lsmod` (*list modules*) muestra la **lista de todos los módulos actualmente cargados** en el kernel. En realidad es una forma "linda" de mostrar el contenido del archivo `/proc/modules`. Su utilidad es verificar qué módulos están activos y si alguno está siendo usado por otros.

#### b. ¿Qué información encuentra en el archivo /proc/modules?

`/proc/modules` es un archivo virtual (no existe en disco, lo genera el kernel al vuelo) que contiene la información cruda de **todos los módulos cargados**. Por cada módulo lista, nombre, tamaño en memoria, contador de uso, módulos que dependen de él, estado de carga (`Live`, `Loading`, `Unloading`) y la dirección de memoria donde está cargado.

#### c. Si ejecutamos `more /proc/modules` encontramos los siguientes fragmentos ¿Qué información obtenemos de aquí?:

    ```
    memory 8192 0 - Live 0x0000000000000000 (OE)
    binfmt_misc 24576 1 - Live 0x0000000000000000
    intel_rapl_msr 16384 0 - Live 0x0000000000000000
    intel_rapl_common 32768 1 intel_rapl_msr, Live 0x0000000000000000
    ```

Cada línea tiene el formato: `nombre  tamaño  uso  dependencias  estado  dirección  [flags]`. Interpretando los fragmentos:

- **`memory 8192 0 - Live 0x... (OE)`** → nuestro módulo `memory`, ocupa 8192 bytes, lo usan `0` módulos, no depende de otros (`-`), está `Live` (cargado y activo), y los flags `(OE)` indican: `O` = *Out-of-tree* (no viene con el kernel oficial) y `E` = *unsigned/Experimental* (sin firmar). La dirección `0x0000...` aparece en cero porque, por seguridad, solo root la ve real.
- **`binfmt_misc 24576 1 - Live ...`** → módulo `binfmt_misc`, 24576 bytes, usado por `1` (algo depende de él), sin dependencias propias, `Live`.
- **`intel_rapl_common 32768 1 intel_rapl_msr, Live ...`** → ocupa 32768 bytes, lo usa `1` módulo, y en la columna de dependencias aparece **`intel_rapl_msr`**, que es el módulo que depende de él. Esto muestra cómo `/proc/modules` refleja las **relaciones de dependencia** entre módulos.

#### d. ¿Con qué comando descargamos el módulo de la memoria?

Con **`rmmod`** (*remove module*), pasándole el **nombre** del módulo (sin la extensión `.ko`):

1. `su -`
2. `rmmod memory`

(También se puede con `modprobe -r memory`). Solo se puede descargar si su contador de uso es `0`.

## Ejercicio 6:​ Descargue el módulo memory. Para corroborar que efectivamente el mismo ha sido eliminado del kernel ejecute el siguiente comando:

```bash
lsmod | grep memory
```

- Para hacer esto (como root):
  1. Ejecutamos los comandos del ejercicio 5.d
  2. `lsmod | grep memory`


>[!NOTE]
> Que `lsmod | grep memory` no devuelva ninguna línea confirma que el módulo **ya no está cargado** en el kernel. `rmmod` ejecutó la descarga, el módulo se quitó de la lista de `/proc/modules` y por eso `grep` no encuentra coincidencias.

## Ejercicio 7:​ Modifique el archivo memory.c de la siguiente manera:

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
MODULE_LICENSE("Dual BSD/GPL");

static int hello_init(void) {
    printk("Hello world!\n");
    return 0;
}

static void hello_exit(void) {
    printk("Bye, cruel world\n");
}

module_init(hello_init);
module_exit(hello_exit);
```

- Para hacer esto:
    1. `nano memory.c`
    2. reemplazamos el contenido con el nuevo código 

### a. Compile y cargue en memoria el módulo.

1. `make -C /home/so/kernel/linux-6.13 M=$(pwd) modules`
2. `su -`
3. `cd /home/so/practica2`
4. `insmod memory.ko`

### b. Invoque al comando dmesg

`dmesg | tail`

- Debería mostrar algo asi:
```
    [    6.256508] Console: switching to colour frame buffer device 160x50
    [    6.263632] vmwgfx 0000:00:02.0: [drm] fb0: vmwgfxdrmfb frame buffer device
    [    6.390792] snd_intel8x0 0000:00:05.0: allow list rate for 1028:0177 is 48000
    [   11.987569] systemd-journald[266]: Oldest entry in /var/log/journal/baf801e24c5d4e5095130bb275c1c853/user-1000.journal is older than the configured file retention duration (1month), suggesting rotation.
    [   11.987589] systemd-journald[266]: /var/log/journal/baf801e24c5d4e5095130bb275c1c853/user-1000.journal: Journal header limits reached or header out-of-date, rotating.
    [   20.231907] clocksource: Long readout interval, skipping watchdog check: cs_nsec: 1367682540 wd_nsec: 1367682409
    [   40.358094] clocksource: Long readout interval, skipping watchdog check: cs_nsec: 10545682727 wd_nsec: 10545681608
    [ 1921.220774] memory: loading out-of-tree module taints kernel.
    [ 1921.220783] memory: module verification failed: signature and/or required key missing - tainting kernel
    [ 2793.935453] Hello world!
```

### c. Descargue el módulo de memoria y vuelva a invocar a dmesg

1. `rmmod memory`
2. `dmesg | tail`

- Debería mostrar algo asi:
```
    root@so:/home/so/practica2# rmmod memory
    root@so:/home/so/practica2# dmesg | tail
    [    6.263632] vmwgfx 0000:00:02.0: [drm] fb0: vmwgfxdrmfb frame buffer device
    [    6.390792] snd_intel8x0 0000:00:05.0: allow list rate for 1028:0177 is 48000
    [   11.987569] systemd-journald[266]: Oldest entry in /var/log/journal/baf801e24c5d4e5095130bb275c1c853/user-1000.journal is older than the configured file retention duration (1month), suggesting rotation.
    [   11.987589] systemd-journald[266]: /var/log/journal/baf801e24c5d4e5095130bb275c1c853/user-1000.journal: Journal header limits reached or header out-of-date, rotating.
    [   20.231907] clocksource: Long readout interval, skipping watchdog check: cs_nsec: 1367682540 wd_nsec: 1367682409
    [   40.358094] clocksource: Long readout interval, skipping watchdog check: cs_nsec: 10545682727 wd_nsec: 10545681608
    [ 1921.220774] memory: loading out-of-tree module taints kernel.
    [ 1921.220783] memory: module verification failed: signature and/or required key missing - tainting kernel
    [ 2793.935453] Hello world!
    [ 2929.160058] Bye, cruel world
```

## Ejercicio 8:​ Responda lo siguiente:

### a. ¿Para qué sirven las funciones module_init y module_exit?. ¿Cómo haría para ver la información del log que arrojan las mismas?.

Las macros `module_init` y `module_exit` registran cuál es la función que el kernel debe ejecutar en cada etapa del ciclo de vida del módulo:

- `module_init(hello_init)` indica la función que corre **cuando se carga** el módulo (`insmod`/`modprobe`). Sirve para inicializar (reservar memoria, registrar dispositivos, etc.). Devuelve `int`: `0` si la carga fue exitosa, distinto de `0` si falló (y el módulo no se carga).
- `module_exit(hello_exit)` indica la función que corre **cuando se descarga** el módulo (`rmmod`). Sirve para limpiar lo que se inicializó (liberar memoria, desregistrar dispositivos). No devuelve nada (`void`).

Para **ver la información del log** que arrojan (los `printk`), se usa el comando `dmesg`, que muestra el *ring buffer* del kernel. Como vimos, al cargar el módulo aparece `Hello world!` y al descargarlo `Bye, cruel world`. Conviene usar `dmesg | tail` para ver solo los últimos mensajes.

### b. Hasta aquí hemos desarrollado, compilado, cargado y descargado un módulo en nuestro kernel. En este punto y sin mirar lo que sigue. ¿Qué nos falta para tener un driver completo?.

Hasta acá tenemos un módulo que solo se carga y descarga, pero **no controla ningún dispositivo ni permite interactuar con él**. Para tener un **driver completo** nos falta:

- **Registrar un dispositivo** en el kernel (por ejemplo con `register_chrdev` para un dispositivo de caracter), obteniendo un *major number* que lo identifique.
- **Definir las operaciones** que se pueden hacer sobre el dispositivo mediante la estructura `struct file_operations`, asociando funciones propias a `open`, `read`, `write`, `release`, etc.
- **Crear el archivo de dispositivo** en `/dev` (con `mknod`) para que las aplicaciones de espacio de usuario puedan acceder a él como si fuera un archivo.
- **Transferir datos** entre el espacio de usuario y el kernel con `copy_to_user` / `copy_from_user`.
- **Desregistrar el dispositivo** (`unregister_chrdev`) en la función de salida.

>[!NOTE]
> Es decir, falta todo lo que convierte al módulo en un intermediario entre el SO y un dispositivo.

### c. Clasifique los tipos de dispositivos en Linux. Explique las características de cada uno.

En GNU/Linux los dispositivos (y sus drivers) se clasifican en tres tipos:

- **Dispositivos de bloque (*block devices*)**: acceden a los datos en **bloques de tamaño fijo** (típicamente 1024 bytes o múltiplos). Permiten **acceso aleatorio** (se puede leer/escribir cualquier bloque directamente) y suelen estar bufereados por el kernel. Ejemplos: discos rígidos, SSD, pendrives, particiones (`/dev/sda`).
- **Dispositivos de caracter (*character devices*)**: acceden a los datos **byte a byte** y de forma **secuencial** (cada byte se lee una sola vez). No permiten acceso aleatorio. Ejemplos: mouse, teclado, puerto serie, terminales (`/dev/tty`, `/dev/random`). *Nuestro driver de memoria será de este tipo.*
- **Dispositivos de red (*network devices*)**: manejan interfaces de red (Ethernet, WiFi). **No se representan como archivos** en `/dev`, sino que se acceden a través de la API de sockets y se identifican por nombre de interfaz (`eth0`, `wlan0`). Trabajan con **paquetes** en lugar de flujos de bytes o bloques.

>[!NOTE]
> Cada dispositivo de bloque o de caracter se identifica con un **major number** (qué driver lo maneja) y un **minor number** (qué instancia concreta dentro de ese driver).
