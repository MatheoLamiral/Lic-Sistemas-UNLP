# Conceptos generales

## Ejercicio 1:​ ¿Cuál es la diferencia fundamental entre un proceso y un thread?

Un proceso es la unidad de propiedad de recursos, en cambio, un hilo es la unidad de ejecución. Un proceso puede verse como una colección de uno o más hilos. Pero la diferencia principal es que los hilos de un mismo proceso **comparten el espacio de direcciones y los recursos**, mientras que cada proceso **tiene su propio espacio de direcciones** aislado.

>[!IMPORTANT]
> Aunque comparten el espacio del proceso, cada hilo tiene su propio stack, registros, PC y estado. Esto es lo que permite que se ejecuten de forma independiente 

>[!NOTE]
> Los hilos se ejecutan secuencialmente y son interrumpibles para que el procesador pase a otro hilo.

## Ejercicio 2:​ ¿Qué son los User-Level Threads (ULT) y cómo se diferencian de los Kernel-Level Threads (KLT)?

Hay hilos a nivel de usuario (ULT, user level thread) e hilos a nivel de núcleo (KLT, kernel level thread).  
En los **ULT** la administración de los hilos lo hace la **aplicación sin intervención del kernel**. Como la creación y operaciones sobre los mismos se hacen a nivel usuario son **más rápidos de crear y utilizar**. Se trabaja con una **biblioteca de hilos** que son funciones para implementar ULT invocadas desde la aplicación. Todo esto se realiza dentro del **mismo proceso, en su espacio de direcciones**.  
En los **KLT** el trabajo de **gestión de hilos lo hace el núcleo**. La **aplicación gestiona el hilo a través de una API**. Existe un **conjunto de system calls** similar a la de los procesos **específicas para hilos**. El kernel mantiene información del proceso en general y de cada hilo del proceso en particular. La planificación la hace el kernel en base a los hilos.

>[!NOTE]
> En los **ULT**, el kernel **no sabe que existen los hilos**, ve un único proceso (un solo hilo de ejecución) y planifica el proceso completo. En los **KLT**, el kernel **conoce y planifica** cada hilo individualmente.

## Ejercicio 3:​ ¿Quién es responsable de la planificación de los ULT? ¿y los KLT? ¿Cómo afecta esto al rendimiento en sistemas con múltiples núcleos?

En los **ULT** el responsable de la planificación es la biblioteca en espacio de usuario (el kernel planifica el proceso completo). En los **KLT** el responsable de la planificación es el kernel, hilo por hilo.

Esto afecta al rendimiento en sistemas con múltiples núcleos de dos formas:
- Paralelismo:
  - **ULT**: Como el kernel ve una sola entidad ejecutable, no pueden correr en paralelo en múltiples núcleos
  - **KLT**: Como el kernel los planifica individualmente, puede asignar distintos hilos a distintos núcleos simultáneamente, logrando paralelismo real 
- Bloqueo: 
  - **ULT**: Si un hilo hace una syscall bloqueante, se bloquea todo el proceso y con él los demás hilos
  - **KLT**: Si se bloquea un hilo, los otros siguen ejecutándose 

## Ejercicio 4:​ ¿Cómo maneja el sistema operativo los KLT y en qué se diferencian de los procesos?

El SO trata a un KLT de forma parecida a un proceso, manteniendo una estructura por cada hilo, planificándolo como entidad propia y creándolo con `clone()`. Pero los hilos de un proceso comparten el espacio de direcciones y los recursos, mientras que los procesos están aislados. 

>[!NOTE]
> Es por esta razón, que el cambio de contexto entre hilos es más barato que entre procesos

## Ejercicio 5:​ ¿Qué ventajas tienen los KLT sobre los ULT? ¿Cuáles son sus desventajas?

- Ventajas 
  - **Paralelismo real**: puede asignar distintos hilos del mismo proceso a distintos núcleos y ejecutarlos en simultáneo. Los ULT no pueden
  - **Bloqueos**: si un KLT hace una syscall bloqueante, el kernel puede planificar otro hilo del mismo proceso. En los ULT, ese bloqueo frena a todos los hilos 
- Desventajas
  - **Costoso**: crear, destruir, sincronizar y hacer cambios de contexto entre KLT es más caro, porque cada operación requiere una sysem call y pasar a modo kernel. En los ULT rodo eso ocurre en espacio de usuario, sin intervención del kernel, por lo que son más rápidos y livianos.
  - **Portabilidad**: dependen del soporte del SO (API de hilos del kernel), mientras que los ULT se implementan con una biblioteca y pueden correr incluso sobre SO que no soportan hilos

>[!NOTE]
> El trade-off central es que, los KLT ganan en paralelismo y robustez ante bloqueos, pero pagan con mayor overhead (modo kernel). Los ULT son más rápidos de gestionar pero no aprovechan múltiples núcleos y un bloqueo frena todo el proceso.

## Ejercicio 6:​ Qué retornan las siguientes funciones:

### a. getpid()

Retorna el **PID** (Process ID) del **proceso que la llama**. Tipo `pid_t`

### b. getppid()

Retorna el **PID** (Process ID) del **proceso padre** del proceso que la llama. Tipo `pid_t`

### c. gettid()

Retorna el **TID** (Thread ID) del **hilo que la llama**, el identificador que le asigna el kernel (KLT). En el hilo principal de un proceso, `gettid() == getpid()`. Tipo `pid_t`.

### d. pthread_self()

Retorna el **identificador del hilo dentro de la biblioteca pthreads** (tipo `pthread_t`). Es un ID interno de la librería, no el del kernel: sirve para identificar el hilo en llamadas pthread (`pthread_join`, etc.), pero no es comparable con el TID del kernel

### e. pth_self()

Retorna el **identificador del hilo en la biblioteca GNU Pth (ULT)**. Como Pth implementa hilos a **nivel de usuario**, este ID identifica el hilo **solo dentro de la biblioteca**, el kernel no lo conoce.

---

> [!NOTE]
> Distinción clave: `getpid`/`getppid` operan a nivel proceso. `gettid` da el ID del kernel (KLT), `pthread_self` y `pth_self` dan IDs internos de la biblioteca de hilos (pthreads y GNU Pth respectivamente), no del kernel.

## Ejercicio 7:​ ¿Qué mecanismos de sincronización se pueden usar? ¿Es necesario usar mecanismos de sincronización si se usan ULT?

-  Se pueden usar, entre otros:
   -  exclusión mutua (mutex)
   -  semáforos
   -  variales de condición
   -  spinlocks
   -  barreras

En el caso de los ULT, el riesgo es menor, pero sigue siendo necesario usar mecanismos de sincronización, siempre que los hilos compartan datos, porque comparten el mismo espacio de direcciones y una actualización a medias puede dejar los datos inconsistentes.

## Ejercicio 8:​ Procesos

### a. ¿Qué utilidad tiene ejecutar fork() sin ejecutar exec()?

Sirve para crear un **proceso hijo que ejecuta el mismo programa que el padre** (una copia). Es útil cuando se quiere **paralelizar el trabajo** dentro de la misma aplicación. El hijo es una copia del padre, y según el valor que retorna `fork()` (0 en el hijo, el PID del hijo en el padre), cada uno ejecuta una **parte distinta del código**. Un ejemplo típico es, cuando un servidor hace `fork()` para que un hijo atienda una conexión mientras el padre sigue aceptando otras

### b. ¿Qué utilidad tiene ejecutar fork() + exec()?

Sirve para **lanzar un programa distinto**. `fork()` crea el proceso hijo (copia del padre) y luego el hijo llama a `exec()`, que **reemplaza su imagen en memoria** por la de otro ejecutable. Es el mecanismo clásico con el que una shell ejecuta comandos

### c. ¿Cuál de las 2 asigna un nuevo PID fork() o exec()?

`fork()` es quien crea un nuevo proceso y, por lo tanto, le asigna un **nuevo PID**. `exec()` no crea un proceso nuevo ni cambia el PID, solo **reemplaza el programa que corre el proceso existente** (conserva el mismo PID).

### d. ¿Qué implica el uso de Copy-On-Write (COW) cuando se hace fork()?

Al hacer `fork()` **no se copia físicamente toda la memoria** del padre de inmediato. Padre e hijo **comparten las mismas páginas** marcadas como **solo lectura**, y la copia real de una página se hace **solo cuando alguno de los dos intenta escribirla.** Esto hace que `fork()` sea **mucho más rápido y eficiente en memoria**, y evita duplicar páginas que nunca se modifican (muy útil cuando el hijo va a hacer `exec()` enseguida y descartaría esa copia).

### e. ¿Qué consecuencias tiene no hacer wait() sobre un proceso hijo?

Cuando el hijo termina, el kernel **conserva su entrada en la tabla de procesos** (con su código de salida) **hasta que el padre la recoja** con `wait()`. Si el padre **no hace** `wait()`, el hijo queda como **proceso zombie** (defunct), ya no ejecuta, pero **ocupa una entrada en la tabla de procesos**. Si se acumulan muchos zombies, se puede **agotar la tabla de PIDs** y no poder crear nuevos procesos

### f. ¿Quién tendrá la responsabilidad de hacer el wait() si el proceso padre termina sin hacer wait()?

El proceso hijo queda **huérfano** y es **adoptado por** `init`/`systemd` (PID 1), el proceso raíz del sistema. `init` ejecuta periódicamente `wait()` sobre sus hijos adoptados (reaping), liberando así la entrada del zombie en la tabla de procesos.

>[!NOTE]
> Una diferencia clave es que, un **zombie** es un **hijo que terminó pero cuyo padre aún no hizo** `wait()` (ocupa la tabla de procesos). Un **huérfano** es un **hijo vivo cuyo padre murió**, y pasa a ser adoptado por `init`, que se encargará de hacerle `wait()` cuando termine.

## Ejercicio 9:​ Kernel Level Threads

### a. ¿Qué elementos del espacio de direcciones comparten los threads creados con pthread_create()?

Comparten el **código**, **datos** y el **heap**. También comparten los **recursos del proceso** (archivos abiertos, señales, sockets).  
Lo que **no comparten**: cada hilo tiene su propio stack, además de su contexto de procesador (PC, registros) y estado

### b. ¿Qué relaciones hay entre getpid() y gettid() en los KLT?

`getpid()` devuelve el **PID del proceso**, que es el **mismo para todos los hilos del proceso** (todos pertenecen al mismo proceso). `gettid()` devuelve el **TID** (identificador del hilo a nivel del SO), que es **distinto para cada hilo**. Dentro de un proceso multihilo, `getpid()` es común a todos, mientras que `gettid()` los distingue individualmente.

>[!NOTE]
> El **hilo principal** del proceso tiene `gettid() == getpid()`

### c. ¿Por qué pthread_join() es importante en programas que usan múltiples hilos? ¿Cuándo se liberan los recursos de un hilo zombie?

`pthread_join()` es importante porque espera la finalización de un hilo y recoge su resultado. Si no se hace `join`, el hilo terminado queda como **zombie**, igual que ocurre con los procesos sin `wait()`. **Los recursos de un hilo zombie se liberan al terminar el proceso que lo creó**. Por eso, para liberarlos antes y evitar fugas, se usa `pthread_join`.

### d. ¿Qué pasaría si un hilo del proceso bloquea en read()? ¿Afecta a los demás hilos?

**No afecta a los demás**. En los KLT hay **independencia de bloqueos entre hilos del mismo proceso**. Como el kernel planifica cada hilo individualmente, si uno se bloquea en una syscall bloqueante como `read()`, el kernel puede **seguir planificando los otros hilos**, que continúan ejecutándose normalmente.

>[!NOTE]
> Esto es lo opuesto a los ULT, donde un `read()` bloqueante frena a todos los hilos del proceso.

### e. Describí qué ocurre a nivel de sistema operativo cuando se invoca pthread_create() (¿es syscall? ¿usa clone?).

`pthread_create()` **no es una syscall en sí**, es una **función de la biblioteca de hilos** (NPTL, Native POSIX Threads Library, la implementación de pthreads en Linux). Por debajo, invoca la **syscall** `clone()` (más precisamente `clone3()`) para crear el nuevo hilo. A través de los flags de `clone()`, el nuevo hilo se **crea compartiendo el espacio de direcciones y los recursos** del proceso (a diferencia de `fork()`, que con `clone()` crea un proceso con espacio separado). En Linux el modelo es **1:1** (cada KLT mapea a un hilo del kernel), por lo que el SO lo registra como una entidad planificable propia

>[!NOTE]
> En Linux tanto `fork()` como `pthread_create()` terminan llamando a `clone()`, la diferencia está en qué se comparte según los flags:
> - `fork()`:espacio aislado (COW)
> - `pthread_create()`: espacio de direcciones y recursos compartidos.

## Ejercicio 10:​ User Level Threads

### a. ¿Por qué los ULTs no se pueden ejecutar en paralelo sobre múltiples núcleos?

Porque el **kernel no sabe que existen**, ve un único proceso (una sola entidad planificable) y planifica el proceso completo, no los hilos. Como toda la gestión y planificación de los ULT la hace una **biblioteca en espacio de usuario** dentro de ese único hilo de ejecución que el kernel reconoce, el SO **solo puede asignar el proceso a un núcleo a la vez**. Por eso los ULT corren concurrentemente (multiplexados en el tiempo) pero **no en paralelo** sobre varios cores

### b. ¿Qué ventajas tiene el uso de ULTs respecto de los KLTs?

Las ventajas de los ULTs sobre los KLTs son:
- **Muy bajo costo de creación y de cambio de contexto**: el intercambio entre hilos se hace sin intervención del kernel, no hay cambio de modo usuario a modo kernel
- **Planificación independiente**: cada proceso planifica sus hilos como le conviene
- **Portabilidad**: pueden correr en distintas plataformas, incluspo sobre SO que no soportan hilos (no requieren soporte del kernel)
- Posibilidad de reemplazar llamadas bloqueantes por no bloqueantes desde la biblioteca

### c. ¿Qué relaciones hay entre getpid(), gettid() y pth_self() (en GNU Pth)?

- `getpid()` → **PID del proceso**: el mismo para todo.
- `gettid()` → **TID a nivel del SO**: como los ULT no son visibles al kernel, todos los ULT comparten el mismo gettid() (el del único hilo de kernel que ejecuta el proceso). A diferencia de los KLT, acá gettid() no distingue los hilos.
`pth_self()` → **identificador del hilo dentro de la biblioteca GNU Pth**: es el único de los tres que distingue cada ULT, pero solo tiene sentido a nivel de la biblioteca (el kernel no lo conoce).

>[!NOTE]
> En resumen, en GNU Pth, `getpid()` y `gettid()` coinciden y son comunes a todos los ULT (porque el kernel ve una sola entidad), mientras que `pth_self()` es el único que los diferencia, operando en un nivel aparte (el de la biblioteca, invisible al kernel).

### d. ¿Qué pasaría si un ULT realiza una syscall bloqueante como read()?

Se **bloquea todo el proceso** y, con él, **todos los demás ULT**. Como el kernel ve una sola entidad y no sabe que hay varios hilos, al bloquear esa syscall **no tiene a quién más planificar dentro del proceso**, así que ninguno de los otros ULT puede avanzar. 

>[!NOTE]
> Esto es lo opuesto a los KLT, donde solo se bloquea el hilo que llamó a `read()`.

### e. ¿Qué tipos de scheduling pueden tener los ULTs? ¿Cuál es el más común?

- **Non-preemptive (cooperativo)**: cada hilo debe ceder voluntariamente el control (un yield). Es el más común.
- **Preemptive**: usa un quantum para apropiarse de la CPU. Es posible, pero no hay implementaciones populares.

> [!**NOTE**]
> Resumen del punto 10: 
> - como el kernel no conoce a los ULT, de ahí se derivan sus tres rasgos: no hay paralelismo real, un bloqueo frena todo el proceso, y `gettid()` no los distingue. Pero a cambio son rapidísimos y portables y suelen planificarse de forma cooperativa.

## Ejercicio 11:​ Global Interpreter Lock

### a. ¿Qué es el GIL (Global Interpreter Lock)? ¿Qué impacto tiene sobre programas multi-thread en Python y Ruby?

El **GIL** es un **lock global del intérprete** que está presente en CPython y MRI (las implementaciones oficiales de Python y Ruby, respectivamente). Su efecto es que el **intérprete ejecuta un solo hilo por vez**. Aunque el programa cree varios hilos (KLT), el GIL **serializa su ejecución**, permitiendo que solo uno corra código del intérprete en un instante dado.  
Los lenguajes interpretados manejan estructuras internas y un **garbage collector por conteo de referencias** que corre todo el tiempo que necesitarían locks finos para ser thread-safe.
El GIL es un único lock grueso que **simplifica la implementación del intérprete y de bibliotecas nativas**.

Impacto sobre programas multi-thread:  
- Aunque los hilos sean KLT (visibles al kernel), **no logran paralelismo real** en CPU. El GIL impide que dos hilos ejecuten bytecode simultáneamente, incluso en máquinas multinúcleo.
- Es **aceptable para tareas IO-Bound** (los hilos pasan mucho tiempo esperando E/S y el GIL se libera mientras esperan, así otro hilo avanza). 
- Es **poco conveniente para tareas CPU-Bound** (no hay ganancia por usar varios cores, los hilos se turnan en uno solo).


### b. ¿Por qué en CPython o MRI se recomienda usar procesos en vez de hilos para tareas intensivas en CPU?

Porque, debido al **GIL**, varios **hilos no se ejecutan en paralelo** y por lo tanto **no aprovechan los múltiples núcleos** en tareas CPU-Bound (se serializan en un solo core). Los **procesos**, en cambio, **no comparten el GIL**, cada proceso tiene su **propio intérprete y su propio GIL**, así que **sí pueden correr en paralelo** en distintos núcleos y lograr paralelismo real. Por eso, para CPU-Bound se recomienda usar procesos.

>[!NOTE]
> Regla práctica: con CPython/MRI, hilos para IO-Bound (el GIL se libera durante la espera de E/S) y procesos para CPU-Bound (cada proceso tiene su propio GIL → paralelismo real en varios cores). En CPython se está trabajando en eliminar el GIL o hacerlo opcional.
