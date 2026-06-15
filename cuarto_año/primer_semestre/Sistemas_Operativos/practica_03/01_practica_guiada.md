# Práctica guiada

## Ejercicio 1:​ Instale las dependencias necesarias para la práctica (strace, git, gcc, make, libc6-dev, libpth-dev, python3, htop y podman):

```bash
apt update
apt install build-essential libpth-dev python3 python3-venv strace git htop podman
```

- Primero ejecutamos `su -` y luego los comandos anteriores

## Ejercicio 2:​ Clone el repositorio con el código a usar en la práctica

```bash
git clone https://gitlab.com/unlp-so/codigo-para-practicas.git
```

## Ejercicio 3:​ Resuelva y responda utilizando el contenido del directorio practica3/01-strace:

### a. Compile los 3 programas C usando el comando make.

```bash
    cd ~/codigo-para-practicas/practica3/01-strace
    make
```

### b. Ejecute cada programa individualmente, observe las diferencias y similitudes del PID y THREAD_ID en cada caso. Conteste en qué mecanismo de concurrencia las distintas tareas:

```bash
    ./01-subprocess
    ./02-kl-thread
    ./03-ul-thread
```

- Estas son las salidas:
    ```bash
        so@so:~/codigo-para-practicas/practica3/01-strace$ ./01-subprocess
        Parent process: PID = 4018, THREAD_ID = 4018
        Child process: PID = 4019, THREAD_ID = 4019
        so@so:~/codigo-para-practicas/practica3/01-strace$ ./02-kl-thread 
        Parent process: PID = 4022, THREAD_ID = 4022
        Child thread: PID = 4022, THREAD_ID = 4023
        so@so:~/codigo-para-practicas/practica3/01-strace$ ./03-ul-thread 
        Parent process: PID = 4024, THREAD_ID = 4024, PTH_ID = 94284600649968
        Child thread: PID = 4024, THREAD_ID = 4024, PTH_ID = 94284600652512
    ```
- `01-subprocess`: padre e hijo tienen **PID y THREAD_ID distinto** (fork crea un proceso nuevo)
- `02-kl-thread`: **mismo PID, pero THREAD_ID distinto** (un KLT, mismo proceso, hilo de kernel propio)
- `03-ul-thread`: **mismo PID y mismo THREAD_ID**, solo cambia el PTH_ID (el ULT corre sobre un único hilo de kernel, el kernel no lo distingue)

#### i. Comparten el mismo PID y THREAD_ID

`03-ul-thread`

#### ii. Comparten el mismo PID pero con diferente THREAD_ID

`02-kl-thread`

#### iii. Tienen distinto PID

`01-subprocess`

### c. Ejecute cada programa usando strace (`strace ./nombre_programa > /dev/null`) y responda:

```bash
    strace ./01-subprocess > /dev/null
    strace ./02-kl-thread   > /dev/null
    strace ./03-ul-thread   > /dev/null
```

#### i. ¿En qué casos se invoca a la systemcall clone o clone3 y en cuál no? ¿Por qué?

- En el caso de `01-subprocess` se invoca a `clone()`. `fork()` le pide al kernel un proceso nuevo, necesita una syscall
- En el caso de `02-kl-thread` se invoca a `clone3()`. `pthread_create()` le pide al kernel un hilo nuevo (KLT). También necesita una syscall
- En el caso de `03-ul-thread` no se invoca ninguno de los dos, porque `pth_spawn()` crea el hilo en espacio de usuario, el kernel ni se entera

>[!NOTE]
> `01` y `02` usan `clone` porque crear una entidad que el kernel debe conocer y planificar (un proceso o un KLT) solo se puede pedir mediante una syscall, y esa syscall es la familia `clone`. En cambio, como `03` crea un hilo dentro de la biblioteca, en espacio de usuario, el kernel no participa, por eso no hay ninguna syscall de creación 

>[!NOTE]
> Si se usa `clone()` o `clone3()` no lo decide el kernel ni el tipo de entidad, lo **decide cómo está implementada cada función en la biblioteca (glibc)**. Ambas syscalls **hacen lo mismo** (crear un flujo de ejecución según flags), pero clone3 es la versión moderna (Linux 5.3+) que **recibe sus parámetros en una estructura extensible** (struct clone_args) en vez de como argumentos sueltos.
> Se usa clone cuando alcanza con el **comportamiento clásico** (el hijo de fork hereda el stack del padre), y clone3 cuando **hace falta pasarle al kernel un stack propio con su tamaño** (el caso del hilo, que tiene stack separado)

#### ii. Observe los flags que se pasan al invocar a clone o clone3 y verifique en qué caso se usan los flags CLONE_THREAD y CLONE_VM.

- `01-subprocess`(`clone()`): No aparecen `CLONE_VM` ni `CLONE_THREAD`. Aparece `SIGCHLD` (el hijo le avisará al padre cuando muera)
- `02-kl-thread`(`clone3()`): Si aparecen `CLONE_VM` y `CLONE_THREAD`

#### iii. Investigue qué significan los flags CLONE_THREAD y CLONE_VM usando la manpage de clone y explique cómo se relacionan con las diferencias entre procesos e hilos.

- `CLONE_VM`("share virtual memory"): El nuevo flujo **comparte el mismo espacio de direcciones que el padre**, las mismas páginas físicas de RAM. Si uno escribe una variable global, el otro ve el cambio al instante. Sin este flag, el hijo recibe una copia del espacio de memoria (que en `fork()` se optimiza con Copy-On-Write).
- `CLONE_THREAD` ("same thread group"): El nuevo flujo se coloca en el **mismo thread group que el padre**. Como el PID que ves con `getpid()` es en realidad el TGID (Thread Group ID), esto hace que padre e hijo compartan el mismo PID. **Cada uno tiene además su TID propio** (lo que devuelve `gettid()`).

>[!NOTE]
> La conclusión es que los flags `CLONE_VM` y `CLONE_THREAD` se usan solo al crear el KLT, no al crear el proceso. Porque un KLT, por definición, es un hilo del mismo proceso, y esos dos flags son justamente lo que hace que el **nuevo flujo "pertenezca" al proceso en vez de ser uno aparte**. `CLONE_VM` se usa porque los hilos deben **compartir memoria** y `CLONE_THREAD` se usa porque el hilo debe **pertenecer al mismo proceso** (mismo PID). `fork()` no los usa porque el hijo debe tener su **propia memoria** y debe ser un **proceso separado con su propio PID**

#### iv. printf() eventualmente invoca la syscall write (con primer argumento 1, indicando que el file descriptor donde se escribirá el texto es STDOUT). Vea la salida de strace y verifique qué invocaciones a write(1, ...) ocurren en cada caso.

- En `01` y `02` solo se ve el write del padre, porque por defecto, `strace` **traza únicamente al proceso/hilo que lanzó** (el "principal"). Cuando ese proceso hace `clone`, el hijo es una entidad de kernel nueva e independiente, y strace no la sigue salvo que se le pida.
- En `03` si se ven los dos, porque el ULT hijo **no es una entidad de kernel separada**, **corre sobre el mismo hilo de kernel** que `strace` ya está trazando. Cuando el ULT hijo hace su `printf` → `write`, ese `write` lo ejecuta el mismo proceso que `strace` observa.

#### v. Pruebe invocar de nuevo strace con la opción -f y vea qué sucede respecto a las invocaciones a write(1, …). Investigue qué es esa opción en la manpage de strace. ¿Por qué en el caso del ULT se puede ver la invocación a write(1, …) por parte del thread hijo aún sin usar -f?

```bash
    strace -f ./01-subprocess > /dev/null
    strace -f ./02-kl-thread   > /dev/null
    strace -f ./03-ul-thread   > /dev/null
```

`-f` significa *follow forks*, le dice a `strace` que cuando el programa haga `clone`/`fork` también empiece a trazar al hijo/hilo nuevo.

- En `01` y `02` ahora **sí** aparece el `write(1, ...)` del hijo. Además strace muestra `Process XXXX attached` (se enganchó a la nueva entidad) y antepone `[pid ...]` para distinguir quién hace cada syscall.
- En `03` **no cambia nada**: no hay `Process attached` ni prefijos distintos, porque no se creó ninguna entidad de kernel nueva (no hubo `clone`).

>[!NOTE]
> En el ULT se ve el `write` del hijo aún sin `-f` porque lo ejecuta **el mismo y único hilo de kernel** que strace ya está trazando, no hay un segundo flujo de kernel que seguir (el "cambio de hilo" ocurre dentro de la biblioteca Pth, invisible para el kernel). En procesos y KLT, en cambio, el hijo **sí** es un flujo de kernel distinto, por eso strace necesita `-f` para seguirlo.

## Ejercicio 4:​ Resuelva y responda utilizando el contenido del directorio practica3/02-memoria:

### a. Compile los 3 programas C usando el comando make.

```bash
    cd ~/codigo-para-practicas/practica3/02-memoria
    make
```

### b. Ejecute los 3 programas.

```bash
    ./01-subprocess
    ./02-kl-thread
    ./03-ul-thread
```

- Estas son las salidas:
    ```bash
        so@so:~/codigo-para-practicas/practica3/02-memoria$ ./01-subprocess 
        Parent process: number = 42
        Child process: number = 84
        Parent process: number = 42
        so@so:~/codigo-para-practicas/practica3/02-memoria$ ./02-kl-thread 
        Parent process: number = 42
        Child process: number = 84
        Parent process: number = 84
        so@so:~/codigo-para-practicas/practica3/02-memoria$ ./03-ul-thread 
        Parent process: number = 42
        Child thread: number = 84
        Parent process: number = 84
    ```

### c. Observe qué pasa con la modificación a la variable number en cada caso. ¿Por qué suceden cosas distintas en cada caso?

El hijo siempre duplica `number` (42 → 84), pero lo que ve el **padre al final** cambia según si la memoria se comparte:

- `01-subprocess`: el padre sigue viendo **42**. `fork()` crea un proceso con su **propio espacio de direcciones** (sin `CLONE_VM`). El hijo recibe una **copia** de la memoria vía **Copy-On-Write**: al escribir `number = 84` se duplica esa página y modifica **su copia**. La variable del padre nunca cambia, son dos variables distintas.
- `02-kl-thread`: el padre ve **84**. El KLT se crea con `CLONE_VM`, comparte el **mismo espacio de direcciones**. `number` es **la misma variable** para el hilo y el principal.
- `03-ul-thread`: el padre ve **84**. El ULT vive dentro del **mismo proceso** (mismo hilo de kernel), comparte toda la memoria, así que también es **la misma variable**.

>[!NOTE]
> **procesos = memoria aislada** (sin `CLONE_VM`, con COW) → el cambio del hijo no se propaga; **KLT y ULT = memoria compartida** → el cambio es visible para todos.

## Ejercicio 5:​ El directorio practica3/03-cpu-bound contiene programas en C y en Python que ejecutan una tarea CPU-Bound (calcular el enésimo número primo).

### a. Ejecute htop en una terminal separada para monitorear el uso de CPU en los siguientes incisos.

- En otra terminal ejecutamos `htop`

### b. Ejecute los distintos ejemplos con make (usar make help para ver cómo) y observe cómo aparecen los resultados, cuánto tarda cada thread y cuanto tarda el programa completo en finalizar.

```bash
    make help        # ver targets
    make run_klt     # C, KLT
    make run_ult     # C, ULT
    make run_klt_py  # Python, KLT (threading)
    make run_ult_py  # Python, ULT (gevent/greenlets)
```

>[!NOTE]
> Con `run_klt` (C) se encienden varios cores al 100% a la vez. Con `run_ult` (C), `run_klt_py` y `run_ult_py` se usa prácticamente un solo core.

### c. ¿Cuántos threads se crean en cada caso?

En los 4 casos, 5 (la constante `NUM_THREADS = 5`), más el hilo principal. La diferencia es qué tipo de hilo:

- `klt.c` → 5 **KLT** (pthreads), cada uno visible al kernel.  
- `ult.c` → 5 **ULT** (GNU Pth) corriendo sobre un único hilo de kernel.  
- `klt.py` → 5 **KLT** (threading.Thread), pero sujetos al GIL.  
- `ult.py` → 5 **ULT** (greenlets de gevent) sobre un único hilo de kernel.

### d. ¿Cómo se comparan los tiempos de ejecución de los programas escritos en C (ult y klt)?

- **klt (KLT) es mucho más rápido** (~5× si hay ≥5 cores). Como el kernel planifica cada KLT por separado, los 5 corren en paralelo en distintos cores. El tiempo total ≈ el de un hilo. En `htop` se ven varios cores al 100%
- **ult (ULT) es ~5× más lento** (≈ suma de los 5). Los 5 ULT comparten un solo hilo de kernel y Pth es cooperativo. Como la tarea CPU-bound nunca cede el control (nth_prime_number no tiene puntos de yield), se ejecutan uno tras otro, secuencialmente. En `htop` se ve un solo core al 100%

>[!NOTE]
> Para CPU-bound, KLT gana porque logra paralelismo real y el ULT no

### e. ¿Cómo se comparan los tiempos de ejecución de los programas escritos en Python (ult.py y klt.py)?

Son parecidos entre sí (ambos ≈ secuenciales, ~5× el de un hilo). Ninguno acelera.

- `klt.py` usa **KLT reales**, pero el **GIL permite que solo un hilo ejecute bytecode a la vez**, no hay paralelismo, se serializan **igual que si fueran ULT**.
- `ult.py` usa **greenlets (ULT) sobre un solo hilo**, cooperativos, también secuencial.
- En htop, en ambos casos se usa un solo core.

>[!NOTE]
> En C, KLT ≫ ULT; en Python, KLT ≈ ULT, porque el GIL le quita al KLT su ventaja (el paralelismo).

>[!NOTE]
> En `htop`, `klt.py` parece usar los dos cores (~50% cada uno), pero **no es paralelismo real**. La pista está en el CPU% total del proceso: ~**104%**, es decir el equivalente a **un solo core**, no ~200% como el `klt` de C. Lo que ocurre es que el **GIL** permite que solo un hilo ejecute bytecode de Python a la vez, y el scheduler va **migrando ese único hilo activo entre los dos cores**; htop promedia eso como "50% en cada uno", pero nunca computan los dos en simultáneo. Por eso `klt.py` tarda casi lo mismo que `ult.py` y no acelera.

>[!NOTE]
> En `htop`, `ult.py` usará un solo core al 100%

### f. Modifique la cantidad de threads en los scripts Python con la variable NUM_THREADS para que en ambos casos se creen solamente 2 threads, vuelva a ejecutar y comparar los tiempos. ¿Nota algún cambio? ¿A qué se debe?

- El tiempo total baja (≈ a la mitad respecto de 5), porque ahora se hace menos trabajo total (2 tandas en vez de 5), pero como siguen serializados, el total ≈ 2× el de un hilo. 
- Entre `klt.py` y `ult.py` siguen siendo parecidos. Reducir hilos no le da paralelismo a ninguno.
- Esto se debe a GIL (en `klt.py`) y a la naturaleza cooperativa de los greenlets (en `ult.py`), ninguno ejecuta dos hilos de Python a la vez, así que el tiempo escala linealmente con la cantidad de hilos.

### g. ¿Qué conclusión puede sacar respecto a los ULT en tareas CPU-Bound?

Los ULT **no sirven para acelerar tareas CPU-bound**. Como todos corren sobre un único hilo de kernel, no hay paralelismo real, y como la tarea CPU-bound no cede el control voluntariamente (scheduling cooperativo), los ULT se ejecutan secuencialmente, dando un **tiempo total ≈ la suma de todos**. **Para CPU-bound conviene usar KLT** (como en klt.c) **o procesos** (para esquivar el GIL en Python).

## Ejercicio 6:​ El directorio practica3/04-io-bound contiene programas en C y en Python que ejecutan una tarea que simula ser IO-Bound (tiene una llamada a sleep lo que permite interleaving de forma similar al uso de IO).

### a. Ejecute htop en una terminal separada para monitorear el uso de CPU en los siguientes incisos.

- En una terminal nueva ejecutamos `htop`

### b. Ejecute los distintos ejemplos con make (usar make help para ver cómo) y observe cómo aparecen los resultados, cuánto tarda cada thread y cuanto tarda el programa completo en finalizar.

```bash
    cd ~/codigo-para-practicas/practica3/04-io-bound
    make run_klt     # C, KLT
    make run_ult     # C, ULT
    make run_klt_py  # Python, KLT
    make run_ult_py  # Python, ULT
```

>[!NOTE]
> Los 4 terminan en ~10 segundos, y en `htop` los cores quedan casi al 0% porque nadie computa, todos esperan (los hilos están en estado `S`/sleeping, no `R`)

### c. ¿Cómo se comparan los tiempos de ejecución de los programas escritos en C (ult y klt)?

Ambos terminan en ~10s (las 5 esperas se solapan). Pero por razones distintas:

- `klt.c`: los 5 KLT hacen `sleep(10)`. El kernel los planifica por separado, así que los 5 pueden dormir a la vez → total ≈ 10s.
- `ult.c`: los 5 ULT usan `pth_sleep(10)`, que es la versión de la biblioteca Pth que cede el control (es un punto de yield cooperativo). Mientras un ULT "duerme", el scheduler de Pth corre los otros, así que las 5 esperas también se solapan → total ≈ 10s.

>[!IMPORTANT]
> Esto funciona porque `ult.c` usa `pth_sleep` y no el `sleep()` normal. Si usara `sleep()` (una syscall bloqueante real), bloquearía a todo el proceso (y con él a los otros 4 ULT) → tardaría ~50s. La biblioteca Pth provee envoltorios no bloqueantes justamente para esto.

### d. ¿Cómo se comparan los tiempos de ejecución de los programas escritos en Python (ult.py y klt.py)?

Ambos terminan en ~10s también:

- `klt.py`: los 5 KLT hacen `time.sleep(10)`. El GIL se libera durante sleep (y durante cualquier I/O bloqueante), así que los otros hilos avanzan → las 5 esperas se solapan → ~10s. Acá el GIL NO molesta, porque no se necesita CPU.
- `ult.py`: los 5 greenlets usan `gevent.sleep(10)`, que cede el control al hub de gevent → las 5 esperas se solapan → ~10s.

### e. ¿Qué conclusión puede sacar respecto a los ULT en tareas IO-Bound?

Los **ULT son muy útiles para tareas IO-bound**. Mientras un ULT espera I/O (mediante una llamada que cede el control, como `pth_sleep`/`gevent.sleep`), el scheduler aprovecha para correr los otros ULT, logrando que **todas las esperas se solapen**, el tiempo total ≈ el de una sola espera, no la suma. Y todo esto **sin paralelismo real ni overhead de kernel**.

>[!NOTE]
> Cabe aclarar que ULT y KLT empatan en IO-bound, pero los ULT lo logran con mínimo overhead

>[!NOTE]
> El GIL solo es un problema de CPU-bound, en IO-bound se libera durante la espera 

## Ejercicio 7:​ Diríjase nuevamente en la terminal a practica3/03-cpu-bound y modifique klt.py de forma que vuelva a crear 5 threads.

### a. Ejecute htop en una terminal separada para monitorear el uso de CPU en los siguientes incisos.

- En una nueva terminal ejecutamos `htop`

### b. Ejecute una versión de Python que tenga el GIL deshabilitado usando: `make run_klt_py_nogil` (esta operación tarda la primera vez ya que necesita descargar un container con una versión de Python compilada explícitamente con el GIL deshabilitado).

```bash
    cd ~/codigo-para-practicas/practica3/03-cpu-bound
    make run_klt_py         # Python NORMAL (con GIL) — para comparar
    make run_klt_py_nogil   # Python SIN GIL (baja un container con podman la 1ª vez)
```

### c. ¿Cómo se comparan los tiempos de ejecución de klt.py usando la versión normal de Python en contraste con la versión sin GIL?

La versión **sin GIL es más rápida** (317s vs 435s, ~1.37×). El menor tiempo se debe a que, sin el GIL, los 5 KLT **se ejecutan en paralelo** en los 2 cores. Con GIL se **serializan** en un solo core. La ganancia no llega a 2× porque (a) solo hay 2 cores y (b) el intérprete sin-GIL tiene más overhead por hilo.

### d. ¿Qué conclusión puede sacar respecto a los KLT con el GIL de Python en tareas CPU-Bound?

El **GIL es lo que impide a los KLT de Python aprovechar el paralelismo** en CPU-bound.Con GIL, los 5 hilos reales se turnan (1 core efectivo), **al quitarlo, los mismos KLT logran paralelismo real** y usan todos los cores, bajando el tiempo. Queda demostrado que la **limitación no es de los KLT sino del GIL** (por eso, mientras el GIL exista en CPython, para CPU-bound se recomienda multiprocessing).