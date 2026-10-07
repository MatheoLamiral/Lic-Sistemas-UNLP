# Infograma de Repaso: Módulos, Drivers, /dev, /proc y System Calls

> Repaso denso para parcial de SO (UNLP). Tema 2.

---

## Módulos (LKM — *Loadable Kernel Module*)

- **Qué es:** fragmento de código (`.ko`) **cargable/descargable en runtime SIN recompilar ni reiniciar** el kernel.
- **Dónde se ejecuta:** en **ESPACIO DE KERNEL / modo supervisor (privilegiado)**. Comparten el espacio de direcciones del kernel → **un bug puede crashear todo el SO** (Kernel Panic / BSOD), no solo un proceso.
- **Dónde se instalan:** `/lib/modules/<version>/` (con `modules.dep`, mapa de dependencias generado por `depmod`).
- **Ciclo de vida:** función **init** (`module_init`, corre al **cargar**; devuelve 0 si OK) y función **exit** (`module_exit`, corre al **descargar**).
- **Built-in vs módulo:** *built-in* = compilado dentro de la imagen del kernel (no se descarga); *módulo* = `.ko` cargable en caliente.
- **Pueden registrar entradas en `/proc`** (tanto built-in **como** cargables).
- **Alternativa si no hubiera módulos:** modificar fuente + recompilar kernel completo + reinstalar + **reiniciar**.

| Comando | Función |
|---|---|
| `insmod <archivo.ko>` | Carga UN módulo por ruta (no resuelve dependencias) |
| `modprobe <nombre>` | Carga por nombre desde `/lib/modules`, **resuelve dependencias** (`modules.dep`); `-r` descarga |
| `rmmod <nombre>` | Descarga (solo si uso = 0) |
| `lsmod` | Lista módulos cargados (= vista "linda" de `/proc/modules`) |
| `modinfo` | Muestra info/metadatos del módulo |

---

## Drivers (controladores de dispositivo)

- **Qué es:** código que actúa de **intermediario entre el SO y un dispositivo de hardware**; traduce operaciones genéricas (open/read/write/close) a instrucciones concretas del HW.
- **Forma correcta de implementarlo:** **COMO UN MÓDULO** (no como servicio, ni syscall, ni kthread). Todo driver puede ser módulo, pero no todo módulo es driver.
- **`register_chrdev(major, "nombre", &fops)`:** registra un **character device** asociando major + tabla de operaciones. **Solo se invoca en espacio de kernel.** Inverso: `unregister_chrdev`.
- **`struct file_operations` (fops):** tabla que asocia cada operación con una función del driver (`read`→`memory_read`, `write`→`memory_write`, etc.). Es cómo el kernel sabe **qué función invocar**.
- **Acceso al kernel:** los drivers usan **directamente la API interna del kernel** (`kmalloc`, `printk`, `register_chrdev`, `copy_to_user`/`copy_from_user`) — **NO** vía system calls.
- Representan ~68.8% del código del kernel; tasa de errores ~7× mayor que el resto.

| Concepto | Identifica |
|---|---|
| **MAJOR number** | El **DRIVER** asociado a un **tipo** de dispositivo (con qué driver redirigir la operación) |
| **MINOR number** | El **dispositivo concreto / instancia** dentro de ese driver |

---

## /dev — device files

- **Qué es:** archivos de dispositivo; **punto de acceso desde espacio de usuario** al driver ("todo es un archivo": `open`, `read`, `write`, `close`).
- **No contienen datos**, son punteros al driver (vía major number).
- Se crean con `mknod <ruta> [b|c] <major> <minor>`.

| Tipo | Marca `ls -l` | Acceso | Ejemplos |
|---|---|---|---|
| **Carácter** | `c` (ej. `crw-...`) | **byte a byte, secuencial** | teclado, mouse, tty, `/dev/null`, `/dev/random` |
| **Bloque** | `b` (ej. `brw-...`) | **bloques de tamaño fijo, acceso aleatorio** | discos: `/dev/sda`, `/dev/nvme0n1` |

> Dispositivos de **red** NO se representan como archivos en `/dev` (se usan vía sockets, `eth0`/`wlan0`).

---

## /proc — pseudo-filesystem

- **Pseudo-FS / sistema de archivos virtual:** interfaz a las **estructuras internas del kernel**.
- **NO ocupa espacio en disco**; la mayoría de sus archivos tienen **tamaño 0**.
- Contiene **info de procesos** y del kernel (`/proc/modules`, `/proc/self/fd/...`).
- **Al leer/escribir un archivo de `/proc` se ejecuta una función del kernel** (se genera al vuelo).

---

## System Calls (llamadas al sistema)

- **Qué es:** la **API del kernel** para que un proceso de usuario solicite un servicio (pasar de **modo usuario → modo kernel**).
- **Mecanismo:** **interrupción de software (TRAP)**: `int 0x80` (x86 32b) / `syscall` (x86_64). **Todas usan la misma interrupción**.
- **Se identifican por un NÚMERO único** (cargado en `EAX`/`RAX`). Máx. **6 parámetros**. El **dispatcher** busca el número en la tabla y ejecuta el handler.
- **Dónde se definen:** en el **código fuente del kernel** — **NO en módulos, NO en libc**.
- **Cómo se adjuntan:** **estáticamente, en tiempo de COMPILACIÓN** del kernel.
- **Cómo se agrega una nueva:** (A) **declararla en la tabla de syscalls** (`syscall_32.tbl` / `syscall_64.tbl`) con un **número único** + (B) **implementar el handler en espacio de kernel**. *(A y B correctas)*
- **libc:** **wrapper de usuario** que **envuelve** las syscalls (carga número + params + trap). **NO las implementa.** `syscall()` permite invocar una syscall por número **sin** wrapper específico.
- **POSIX:** interfaz **uniforme** para **portabilidad** de aplicaciones; en Unix la libc es el API que respeta POSIX. **Se puede invocar una syscall sin libc** (assembler directo).
- **`strace`** monitorea syscalls en runtime; **`ausyscall`** mapea nombre↔número estáticamente.
- Manejo de punteros de usuario: validar con `get_user`/`put_user`/`copy_from_user`/`copy_to_user` (riesgo de Kernel Panic / fuga de memoria del kernel).

> **3 file descriptors de todo proceso:** `0` = stdin, `1` = stdout, `2` = stderr.

---

## ⚠️ Trampas típicas de parcial

| Afirmación | V/F | Por qué |
|---|---|---|
| "libc es el componente del kernel donde se definen las syscalls" | **FALSO** | libc es wrapper de USUARIO; las syscalls se definen en el kernel |
| "Las syscalls se definen en módulos administrables con insmod/modprobe/rmmod" | **FALSO** | Son parte del kernel base, estáticas |
| "Las syscalls se implementan como módulos del kernel" | **FALSO** | (la falsa típica) son estáticas, en compilación |
| "Las syscalls se ejecutan en modo privilegiado y se identifican por un número" | **VERDADERO** | — |
| "Cada driver implementa una system call" | **FALSO** | Implementa `file_operations`; **usa** syscalls, no las define |
| "Los drivers acceden a funcionalidades del kernel a través de system calls" | **FALSO** | Acceso **directo** por API interna (kmalloc, printk, register_chrdev) |
| Forma correcta de implementar un driver | **COMO UN MÓDULO** | No servicio, no syscall, no kthread |
| "register_chrdev se puede invocar desde espacio de usuario" | **FALSO** | Solo espacio de kernel; asocia major + tabla de operaciones |
| "Los módulos se ejecutan en espacio de usuario" | **FALSO** | Modo supervisor / kernel |
| "Un módulo permite implementar system calls dinámicas" | **FALSO** | No describe a un módulo |
| "Solo los módulos built-in pueden crear entradas en /proc" | **FALSO** | También los módulos **cargables** |
| Major number | identifica el **driver** de un **tipo** de dispositivo (un mismo major puede referenciar HW distinto vía minor) | — |
| Agregar syscall | declarar en **tabla** + **número unívoco** + implementación en kernel | A y B correctas |
