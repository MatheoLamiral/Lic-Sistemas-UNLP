# Threads (Hilos) — Infograma de Repaso

> Repaso denso para parcial de Sistemas Operativos (UNLP).

---

## 1. ¿Qué es un thread?

Un **hilo** es la **unidad básica de ejecución** dentro de un proceso (también *lightweight process*). Se ejecuta secuencialmente y es **interrumpible** para que el procesador pase a otro hilo.

- **Proceso** = unidad de **propiedad de recursos** (espacio de direcciones aislado). Es una colección de uno o más hilos.
- **Hilo** = unidad de **ejecución** dentro del proceso.

Los hilos de un proceso **comparten el espacio de direcciones y los recursos**; cada uno mantiene su propio flujo de ejecución.

### Qué comparten vs qué es propio

| Compartido por los hilos del proceso | Propio de cada hilo |
|---|---|
| **Espacio de direcciones** (TEXT/código, DATA, **HEAP**) | **Stack** |
| Recursos del proceso: **archivos abiertos, señales, sockets** | **Registros** + **Program Counter (PC)** |
| **PID** (común a todos) | **Estado** de ejecución / **contexto** del procesador |
| 1 PCB | 1 TCB (Thread Control Block) por hilo; **TID** propio |

> **Clave:** comparten **memoria/recursos**, pero cada uno tiene **stack, registros y PC propios** → por eso pueden ejecutarse de forma independiente.

### Proceso vs Thread (por qué el hilo es más barato)

| Aspecto | Proceso | Hilo |
|---|---|---|
| **Espacio de direcciones** | Propio y aislado | Compartido con el proceso |
| **Creación / destrucción** | La hace el SO (nuevo espacio, PCB) | Más barato (solo TCB, stack, registros) |
| **Cambio de contexto** | Caro: cambia todo el ambiente | Barato: solo registros, no cambia espacio de direcciones |
| **Protección** | El SO la garantiza | Responsabilidad del desarrollador (comparten memoria) |

---

## 2. Concurrencia vs Paralelismo

- **Concurrencia**: múltiples tareas **progresan intercaladas** en el tiempo, posiblemente sobre **1 solo core** (multiplexación en el tiempo). *Da la ilusión de simultaneidad.*
- **Paralelismo**: múltiples tareas se ejecutan **simultáneamente, de verdad**, en **múltiples cores**.

> Todo paralelismo es concurrencia, pero no toda concurrencia es paralelismo.

---

## 3. ULT vs KLT

- **ULT (User Level Threads):** los gestiona y **planifica una biblioteca de hilos en espacio de usuario** (POSIX Pthreads, GNU Pth, Solaris Threads). El **kernel NO sabe que existen** → ve un único proceso (un solo hilo de ejecución) y planifica el proceso completo.
- **KLT (Kernel Level Threads):** los **conoce y planifica el kernel**, hilo por hilo. En Linux se crean con la syscall `clone()`/`clone3()` (con flags `CLONE_VM` + `CLONE_THREAD`).

### Tabla comparativa

| Criterio | **ULT** | **KLT** |
|---|---|---|
| **¿Quién planifica?** | La **biblioteca de hilos** (espacio de usuario) | El **kernel**, individualmente |
| **Visibilidad al kernel** | Invisible: ve **1 solo proceso** | Visible: cada hilo es entidad planificable |
| **Paralelismo en multicore** | **NO** (no puede repartirlos en varios núcleos) | **SÍ** (paralelismo real, distintos cores a la vez) |
| **Costo de cambio de contexto** | **Barato** (sin pasar a modo kernel) | **Caro** (cada operación requiere syscall / modo kernel) |
| **Bloqueo (syscall bloqueante)** | Bloquea **TODO el proceso** y todos los hilos | Solo se bloquea **ese hilo**; los demás siguen |
| **Portabilidad** | Alta (corren incluso sin soporte del SO) | Dependen del soporte del kernel |

> **Trade-off:** los **KLT** ganan en paralelismo y robustez ante bloqueos, pero pagan **overhead** (modo kernel). Los **ULT** son rápidos y portables, pero **no aprovechan múltiples núcleos** y un bloqueo frena todo el proceso.

**Regla práctica (rendimiento):** KLT/procesos para **CPU-bound** (necesitan paralelismo); ULT excelentes para **IO-bound** (las esperas se solapan con yields, sin overhead de kernel).

---

## 4. Modelos de mapeo ULT ↔ KLT

Los ULT **no pueden ejecutarse directamente**: necesitan mapearse sobre un KLT para obtener CPU.

| Modelo | Relación | Característica | Ejemplo |
|---|---|---|---|
| **N:1** (Muchos a Uno) | Muchos ULT → 1 KLT | Sin paralelismo; un bloqueo frena todo el proceso | Java sobre SO sin KLT |
| **1:1** (Uno a Uno) | 1 ULT → 1 KLT | Paralelismo máximo; costo alto (1 KLT por hilo) | **Linux**, Windows NT, Solaris |
| **M:N** (Muchos a Muchos) | M ULT → N KLT (híbrido) | Balance: paralelismo sin el costo de 1:1 | Solaris (LWP), TRIX |

---

## 5. fork() y exec()

- **`fork()`**: crea un **proceso hijo**, copia (casi) idéntica del padre. Usa **Copy-On-Write (COW)**: comparten páginas en solo-lectura y se copian recién al escribir. **`fork()` asigna el nuevo PID.**
- **`exec()`**: **reemplaza la imagen** del proceso por otro programa. **NO crea proceso ni cambia el PID.**
- **`fork()` + `exec()`**: lanzar **otro programa** (mecanismo clásico de la shell).

### `fork()` SIN `exec()` — característica de parcial

El hijo es una **copia (casi) idéntica del padre**:

- **Mismo código, datos y programa** que el padre (ejecuta el mismo binario).
- **Hereda los descriptores de archivo abiertos**.
- **Distinto PID** (y distinto PPID).
- Se diferencian por el **valor de retorno de `fork()`**: `0` en el hijo, PID del hijo en el padre → cada uno corre una **parte distinta del código**.

> En Linux **tanto `fork()` como `pthread_create()` llaman a `clone()`**; cambia qué se comparte: `fork()` → espacio aislado (COW); `pthread_create()` → espacio de direcciones y recursos compartidos (`CLONE_VM`+`CLONE_THREAD`).

---

## ⚠️ Trampas típicas de parcial

- **¿Quién planifica los ULT?** → La **biblioteca de hilos en espacio de usuario**. **¿Y los KLT?** → El **kernel**, hilo por hilo.
- **Efecto en multicore:** **ULT = SIN paralelismo real** (el kernel ve una sola entidad); **KLT = CON paralelismo real** (el kernel los reparte entre núcleos).
- **¿Bloqueo por syscall?** ULT → se bloquea **todo el proceso**; KLT → solo el hilo que llamó.
- **`fork()` sin `exec()`** → hijo es **copia del padre**, **mismo programa**, **distinto PID**, **hereda descriptores de archivo abiertos** (COW para la memoria).
- **¿Quién asigna el PID nuevo?** → **`fork()`**, no `exec()` (`exec` conserva el PID).
- **Proceso vs thread:** comparten **espacio de direcciones, código, datos, heap y recursos** (archivos/señales/sockets) y el **PID**; **NO comparten** stack, registros, PC, estado ni TID.
- **Hilo principal:** `gettid() == getpid()`. En ULT (GNU Pth), todos comparten el mismo `gettid()` (kernel ve 1 entidad); solo `pth_self()` los distingue.
