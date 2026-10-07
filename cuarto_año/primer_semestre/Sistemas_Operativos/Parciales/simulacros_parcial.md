# Simulacros de Parcial — Sistemas Operativos

> **Formato real del parcial:** 10 preguntas choice/VF + 10 de desarrollo corto (máx. 3-4 renglones).
> Cada respuesta vale **0,50**. Aprobás con **14 bien (7 pts)**, promocionás con **16 bien (8 pts)**.
> **Regla de oro:** los V/F y choice SIEMPRE se justifican brevemente. Sin justificación no valen.
>
> Armado a partir de los parciales 2022-2026, el banco de Moodle y las prácticas 1 a 6.
> Las respuestas están al final de cada simulacro. Hacé cada simulacro de corrido, cronometrado, y recién después corregí.

---

# SIMULACRO 1

## Parte A — Choice / Verdadero-Falso (justificar todo)

**A1.** Verdadero o falso: *"El kernel de Linux es un sistema operativo en sentido estricto, ya que contiene todo lo necesario para gestionar el hardware y los procesos."*

**A2.** ¿Cuál de las siguientes afirmaciones sobre módulos del kernel de Linux es **falsa**?
- a. Pueden cargarse y descargarse de memoria con comandos específicos.
- b. Pueden usarse para implementar drivers u otras funcionalidades.
- c. Se ejecutan en espacio de usuario.
- d. Para crear un módulo hay que implementar una función que se ejecuta al cargarlo y otra al descargarlo.

**A3.** Verdadero o falso: *"La librería libc implementa directamente las system calls en modo kernel, sin necesidad de ningún mecanismo de trap o interrupción."*

**A4.** Un usuario ejecuta `ls -l` y ve:
```
brw-rw---- 1 root root 240, 0 Jun 10 18:05 weird
```
¿Cuál/es de las siguientes es/son verdadera/s?
- a. `weird` hace referencia a un dispositivo de bytes (caracter).
- b. `weird` hace referencia a un dispositivo de bloques.
- c. El driver asociado a `weird` debería vincularse al major number 240.
- d. `weird` ocupa 240 bytes.
- e. El comando `echo 'Hello world' > weird` incrementa el tamaño de `weird`.

**A5.** Verdadero o falso: *"Si un proceso crea N User-Level Threads (ULTs), entonces con el comando `strace` podremos observar que invoca N veces la system call `clone3`."*

**A6.** Verdadero o falso: *"En un hypervisor tipo 2, el SO host es el que se ejecuta directamente sobre el hardware físico y gestiona los drivers de dispositivo reales."*

**A7.** ¿Cuál de las siguientes opciones es correcta respecto a los containers?
- a. Es necesario contar con un software de virtualización, tipo un hypervisor.
- b. No es posible ejecutar un SO con un kernel diferente al del SO base.
- c. Cada container ejecuta su propio kernel.
- d. No es posible que un container tenga un nombre diferente al del nodo donde ejecuta.

**A8.** Verdadero o falso: *"Al remover un archivo dentro de un Dockerfile con el comando `RUN rm`, dicho archivo se elimina definitivamente de la imagen, reduciendo su tamaño total."*

**A9.** Verdadero o falso: *"RAID 1 provee striping y paridad distribuida."*

**A10.** Verdadero o falso: *"En la planificación por pandillas (gang scheduling), todos los hilos de un proceso se programan para ejecutarse simultáneamente en distintas CPUs durante el mismo intervalo de tiempo."*

## Parte B — Desarrollo (máx. 3-4 renglones cada una)

**B1.** ¿Qué es el kernel de GNU/Linux? ¿Cuáles son sus funciones principales dentro del sistema operativo?

**B2.** Una vez que el kernel es compilado e instalado con `make modules_install && make install`, ¿en qué directorios se instalan la imagen del kernel y los módulos?

**B3.** ¿Qué contiene el initramfs y qué funcionalidad provee? ¿Bajo qué condiciones puede no ser necesario?

**B4.** ¿Qué es una system call y cuál es su propósito principal?

**B5.** ¿Quién es responsable de la planificación de los ULT? ¿Y de los KLT? ¿Cómo afecta esto al rendimiento en sistemas con múltiples núcleos?

**B6.** Describa brevemente la diferencia entre hypervisors de tipo 1 y de tipo 2. Dé un ejemplo de cada uno.

**B7.** Suponga que un usuario desea limitar el uso de CPU de un proceso para que no supere el 80%. ¿Qué mecanismo provisto por el kernel Linux podría utilizar y cómo?

**B8.** En el contexto de Docker: ¿qué es una imagen? ¿Y un contenedor? ¿Cuál es la principal diferencia entre ambos?

**B9.** ¿Qué es ASLR (Address Space Layout Randomization)? ¿Linux provee ASLR para los procesos de usuario? ¿Y para el kernel?

**B10.** Enuncie las cuatro condiciones de Coffman necesarias para que ocurra un deadlock. ¿Deben cumplirse todas simultáneamente?

---

## Respuestas — Simulacro 1

### Parte A

**A1. FALSO.** El kernel es el núcleo del SO (gestiona memoria, CPU, procesos, E/S), pero el SO completo en sentido amplio agrega shell, utilidades y bibliotecas (GNU + Linux). *(Ojo: en 2023 preguntaron lo inverso — "el kernel ES el SO en sentido estricto" como definición aislada es válida; acá la trampa es "contiene TODO lo necesario", y las utilidades/shell no están en el kernel.)*

**A2. c.** Los módulos se ejecutan en **espacio de kernel / modo supervisor**, comparten el espacio de direcciones del kernel; por eso un bug en un módulo puede causar un Kernel Panic.

**A3. FALSO.** libc es una biblioteca de **espacio de usuario** que provee *wrappers*: carga el número de syscall en un registro y dispara el **trap** (`int 0x80` / `syscall`). La syscall se define y ejecuta en el kernel.

**A4. b y c.** La `b` inicial indica dispositivo de **bloques**; `240, 0` son **major y minor**: el major 240 identifica al driver. No son 240 bytes (d falsa), no es de caracter (a falsa) y escribirle no cambia su "tamaño" porque no es un archivo regular, es un punto de acceso al driver (e falsa).

**A5. FALSO.** Los ULT los crea y gestiona la biblioteca de hilos en espacio de usuario: **el kernel no se entera** de su existencia, por lo que no hay syscalls. `clone3` se vería con KLT (`pthread_create`) o procesos (`fork`).

**A6. VERDADERO.** En tipo 2 el hypervisor es una aplicación que corre **sobre un SO anfitrión**; ese SO host es quien corre sobre el hardware real y maneja los drivers reales (ej.: VirtualBox sobre Linux).

**A7. b.** Los containers **comparten el kernel del host** (no tienen kernel propio → c falsa), no necesitan hypervisor (a falsa) y sí pueden tener su propio hostname gracias al UTS namespace (d falsa).

**A8. FALSO.** Las capas de una imagen son de **solo lectura**: el archivo queda en la capa donde se agregó. `RUN rm` solo crea una capa nueva que lo *oculta*; el tamaño total no se reduce.

**A9. FALSO.** RAID 1 es **mirroring** (copia espejo): no hace striping ni usa paridad. Striping con paridad distribuida es RAID 5.

**A10. VERDADERO.** En gang scheduling los hilos relacionados forman una "pandilla" que se planifica junta: corren simultáneamente en distintas CPUs e inician/terminan el intervalo juntos, acelerando la sincronización entre ellos.

### Parte B

**B1.** Es el núcleo del SO: código que reside en memoria principal, corre en modo privilegiado y actúa de intermediario entre hardware y aplicaciones, exponiendo una interfaz controlada (system calls). Funciones principales: administración de memoria principal, manejo de CPU (scheduling), administración de procesos, gestión de E/S, y comunicación/concurrencia.

**B2.** Los módulos se instalan en `/lib/modules/<versión>/` (con `make modules_install`) y la imagen del kernel (`vmlinuz`), junto con `System.map`, `.config` e initramfs, en `/boot/` (con `make install`). Luego hay que actualizar GRUB.

**B3.** Es un filesystem temporal en RAM que se monta durante el arranque, antes del root real. Contiene los módulos/drivers y programas mínimos (disco, filesystem, LVM/RAID, init temporal) para que el kernel pueda montar el root definitivo. Puede no ser necesario si todos esos drivers están compilados built-in en el kernel.

**B4.** Es la API que el kernel expone al espacio de usuario para solicitar servicios que requieren modo privilegiado (archivos, red, procesos). Se invoca mediante una interrupción de software (trap) y se identifica por un número único en la tabla de syscalls. Es el único puente controlado usuario → kernel.

**B5.** Los ULT los planifica la **biblioteca de hilos en espacio de usuario**; los KLT los planifica el **kernel**. Como el kernel no ve los ULT (ve un solo proceso), no puede repartirlos en varios núcleos: no hay paralelismo real. Los KLT sí se planifican individualmente en distintos cores → paralelismo real.

**B6.** Tipo 1 (bare-metal): corre directamente sobre el hardware, sin SO anfitrión; mayor rendimiento; ej.: ESXi, Xen, KVM. Tipo 2 (hosted): corre como aplicación sobre un SO anfitrión que maneja el hardware real; ej.: VirtualBox, VMware Workstation.

**B7.** **cgroups** (control groups), con el controlador `cpu`: se crea un cgroup, se establece la cuota de CPU al 80% (`cpu.max` en v2 o `cfs_quota_us`/`cfs_period_us` en v1) y se agrega el PID del proceso a `cgroup.procs`. El proceso no necesita modificarse.

**B8.** Imagen: template/molde de **solo lectura** con la app + dependencias + instrucciones. Contenedor: **instancia en ejecución** de esa imagen, con una capa escribible propia encima. Diferencia principal: la imagen es estática y no se ejecuta; el contenedor sí, y de una misma imagen pueden crearse varios contenedores.

**B9.** ASLR aleatoriza las direcciones de memoria de un proceso en cada ejecución (stack, heap, librerías, y código si es PIE) para dificultar exploits de memoria (buffer overflow). Linux lo provee para procesos de usuario (`/proc/sys/kernel/randomize_va_space`, configurable sin recompilar) y también para el kernel mediante **KASLR**, mecanismo separado.

**B10.** 1) Exclusión mutua, 2) Retención y espera (hold and wait), 3) No apropiación (no preemption), 4) Espera circular. Sí: **deben cumplirse las cuatro simultáneamente**; si falta una sola, no puede haber deadlock (base de las estrategias de prevención).

---

# SIMULACRO 2

## Parte A — Choice / Verdadero-Falso (justificar todo)

**A1.** Verdadero o falso: *"En un microkernel, los drivers y servidores de filesystem se ejecutan en modo kernel para mejorar el rendimiento."*

**A2.** ¿Por qué se considera que Linux es portable?
- a. Porque los programas ELF pueden ejecutarse en computadoras de cualquier arquitectura siempre que corran Linux.
- b. Porque se pueden usar distintos lenguajes de programación para generar programas para Linux.
- c. Porque su tamaño es pequeño, lo que facilita copiarlo a distintas computadoras.
- d. Porque el mismo binario del kernel se puede ejecutar en distintas arquitecturas de CPU.
- e. Porque su código puede ser modificado fácilmente para funcionar en distintas arquitecturas de CPU.

**A3.** ¿Cuál de estas afirmaciones respecto a las system calls es **falsa**?
- a. Las system calls se pueden monitorear con el comando `strace`.
- b. Las system calls pueden ser invocadas por los programas.
- c. LibC implementa wrappers para las system calls.
- d. Las system calls se implementan como módulos del kernel.

**A4.** Verdadero o falso: *"La tabla de syscalls en GNU/Linux (syscall_64.tbl) permite que el dispatcher, al recibir una interrupción, identifique qué función del kernel debe ejecutarse según el número almacenado en el registro."*

**A5.** Verdadero o falso: *"Un User-Level Thread (ULT) en el modelo M:1 puede aprovechar de manera directa múltiples procesadores físicos sin ningún mecanismo adicional."*

**A6.** ¿En cuál de las siguientes técnicas de virtualización se debe modificar el kernel del SO invitado (guest) para mejorar el rendimiento?
- a. Hypervisores tipo 1.
- b. Hypervisores tipo 2.
- c. Paravirtualización.
- d. Emuladores.
- e. Todas las técnicas necesitan un SO invitado modificado para funcionar.

**A7.** ¿Cuál de las siguientes opciones es correcta respecto de cgroups v2?
- a. Los procesos deben agregarse a los cgroups sin hijos (hojas), salvo el cgroup root.
- b. Un proceso debe ser modificado para poder ser agregado a una jerarquía de cgroups.
- c. Cada container puede tener su propia dirección IP pero el nombre siempre es el mismo que el host anfitrión.
- d. En cgroupv1, un proceso solo puede pertenecer a una jerarquía.
- e. Los cgroups se implementan utilizando un filesystem de tipo Ext4 o XFS.

**A8.** Indicar cuál/es de las siguientes opciones es/son correctas con respecto a Docker:
- a. A partir de una imagen solo se puede generar un solo contenedor.
- b. Docker necesita un hypervisor para poder ejecutarse.
- c. Dockerfile es un archivo con instrucciones que permite crear un container.
- d. Cada imagen está compuesta por un conjunto de capas de las cuales solo la última puede ser modificada.
- e. Docker hace uso de namespaces, cgroups y union filesystems para proveer contenedores.
- f. No es posible generar una imagen a partir de un contenedor.

**A9.** Si se tienen 5 discos de 1 TB cada uno en RAID 5, la capacidad total para almacenar datos es de:
- a. 4 TB
- b. 3 TB
- c. 5 TB
- d. Depende del chunk size elegido.

**A10.** Verdadero o falso: *"En un sistema distribuido, todos los nodos deben ejecutar el mismo sistema operativo y disponer del mismo hardware para garantizar la interoperabilidad."*

## Parte B — Desarrollo (máx. 3-4 renglones cada una)

**B1.** Explique brevemente la arquitectura del kernel Linux: tipo de kernel, modularidad y portabilidad.

**B2.** ¿Qué es un módulo del kernel de Linux y qué ventaja/s provee compilar una funcionalidad como módulo respecto a compilarla built-in?

**B3.** ¿Qué tipos de archivos se encuentran en `/dev`? ¿Qué representan estos archivos?

**B4.** Describa para qué se usa la función `register_chrdev()`. ¿Se puede usar en espacio de usuario, espacio de kernel o en ambos?

**B5.** ¿Qué características tendrá el proceso creado si se ejecuta un `fork()` pero no se ejecuta `exec()`?

**B6.** Describa brevemente las funcionalidades provistas por cgroups y por namespaces (no hace falta enumerarlos todos).

**B7.** Un usuario ejecuta `docker exec <id> ps aux` y ve el proceso `mi_proceso` con PID 1; luego ejecuta `ps aux` en el host y ve el mismo proceso con PID 423548. Explique por qué tiene distinto PID y qué mecanismo específico del kernel lo produce.

**B8.** ¿Qué es un Union Filesystem? ¿Cómo lo utiliza Docker?

**B9.** ¿Qué es un link simbólico? ¿En qué se diferencia de un hard link? ¿Cuál/es consumen un inodo al crearse?

**B10.** ¿Qué diferencia hay entre deadlock y starvation?

---

## Respuestas — Simulacro 2

### Parte A

**A1. FALSO.** En un microkernel los drivers y servidores (FS, red) corren en **espacio de usuario** como servicios; en modo kernel queda solo lo mínimo (procesos, memoria, IPC). Eso da aislamiento a costa de rendimiento. Ejecutar todo en modo kernel es lo del monolítico.

**A2. e.** La portabilidad de Linux es del **código fuente** (escrito mayormente en C, con Assembler solo para lo específico de cada plataforma): se adapta y recompila para cada arquitectura. El mismo binario NO corre en distintas arquitecturas (d falsa).

**A3. d.** Las syscalls son parte del **kernel base**, se adjuntan estáticamente en tiempo de compilación; no son módulos cargables con insmod/rmmod. Las otras tres son verdaderas.

**A4. VERDADERO.** Todas las syscalls entran por la misma interrupción/trap; se distinguen por el número cargado en el registro (EAX/RAX). El dispatcher busca ese número en la tabla (`syscall_64.tbl`) y ejecuta el handler correspondiente.

**A5. FALSO.** En M:1 todos los ULT se mapean sobre **un único KLT**: el kernel ve una sola entidad planificable, así que no puede repartir los hilos entre núcleos. Sin KLTs adicionales no hay paralelismo real.

**A6. c. Paravirtualización.** El kernel del guest se modifica para reemplazar instrucciones privilegiadas por *hypercalls* a la API del hypervisor, lo que mejora el rendimiento. Por eso no sirve para SO cerrados como Windows.

**A7. a.** Es la restricción "no internal process constraint" de cgroups v2 (jerarquía única): los procesos van en las hojas, salvo el root. b es falsa (no hay que modificar procesos), d es falsa (en v1 un proceso pertenece a un cgroup POR CADA jerarquía, hay varias), e es falsa (usan un pseudo-filesystem propio).

**A8. d y e.** De una imagen se generan varios contenedores (a falsa); Docker no usa hypervisor (b falsa); un Dockerfile crea una **imagen**, no un container (c falsa); `docker commit` crea una imagen desde un contenedor (f falsa).

**A9. a. 4 TB.** RAID 5 usa paridad distribuida equivalente a un disco: capacidad útil = (N−1) × tamaño = 4 × 1 TB. El chunk size no afecta la capacidad.

**A10. FALSO.** Los sistemas distribuidos son justamente nodos heterogéneos (distinto SO, HW, FS); la capa de **middleware** por encima del SO resuelve la heterogeneidad y da interfaces comunes.

### Parte B

**B1.** Linux es **monolítico híbrido**: toda la funcionalidad corre en un solo bloque en modo privilegiado, pero admite cargar/descargar **módulos** en tiempo de ejecución (que una vez cargados también corren en modo kernel). Es altamente **portable** porque está escrito mayormente en C (Assembler solo para bajo nivel específico), de modo que el mismo código fuente se recompila para muchas arquitecturas.

**B2.** Es un fragmento de código (.ko) que puede cargarse/descargarse en el kernel en tiempo de ejecución (insmod/rmmod), sin recompilar ni reiniciar. Ventajas vs built-in: consume memoria solo cuando se usa, se actualiza "en vuelo" sin reiniciar, y agiliza el desarrollo (probar un driver es cargar/descargar un .ko).

**B3.** Device files: archivos que representan los dispositivos y son el punto de acceso desde espacio de usuario al driver (se usan con open/read/write y el kernel redirige al driver según el major number). Dos tipos: de **caracter** (`c`, acceso byte a byte secuencial: teclado, tty) y de **bloque** (`b`, bloques de tamaño fijo con acceso aleatorio: discos, /dev/sda).

**B4.** Registra un dispositivo de caracter en el kernel: asocia un **major number** con la tabla de operaciones del driver (`struct file_operations`), de modo que cuando un proceso opera sobre el device file con ese major, el kernel redirige la operación a las funciones del driver. Solo puede usarse en **espacio de kernel** (es API interna del kernel).

**B5.** El hijo es una copia casi idéntica del padre: ejecuta el **mismo programa/código** (no se reemplaza), su memoria es copia de la del padre (con copy-on-write), hereda descriptores de archivo y recursos, pero tiene **PID propio**. Se distinguen por el retorno de `fork()`: 0 en el hijo, PID del hijo en el padre.

**B6.** **cgroups:** organiza procesos en grupos jerárquicos para **limitar, priorizar, contabilizar (accounting) y controlar** (p. ej. freezar) su uso de recursos (CPU, memoria, E/S). **Namespaces:** dan a un proceso una **vista aislada** de un recurso global (PIDs, red, montajes, hostname, IPC, usuarios), haciéndole creer que tiene su propia instancia.

**B7.** Es el **PID namespace**. El contenedor tiene su propio árbol de PIDs aislado: `mi_proceso` es el primer proceso de su namespace y por eso dentro se ve como PID 1 (su "init"), mientras que en el host tiene su PID real (423548). Es un único proceso con dos identificadores según la vista.

**B8.** Mecanismo de montaje por el cual varios directorios se montan en un mismo punto y se ven como un único FS: capas inferiores de solo lectura, capa superior escribible. Docker construye cada imagen como capas apiladas (cada una guarda solo diferencias); al ejecutar un contenedor apila las capas read-only, agrega una capa escribible propia y fija ese union-FS como raíz con chroot.

**B9.** El symlink apunta a una **ruta/nombre**; el hard link apunta al **mismo inodo** que el original. Si se borra el original, el symlink queda roto, pero el hard link sigue funcionando (los datos viven hasta que el link count llega a 0). El symlink **sí** consume un inodo nuevo; el hard link **no** (comparte el existente).

**B10.** Deadlock: conjunto de procesos **mutuamente bloqueados** en espera circular; ninguno avanza ni libera recursos. Starvation: un proceso **nunca obtiene** el recurso porque siempre es pospuesto (por prioridades/planificación), sin necesidad de ciclo. El deadlock se rompe abortando/expropiando; la starvation se evita con políticas justas (aging).

---

# SIMULACRO 3

## Parte A — Choice / Verdadero-Falso (justificar todo)

**A1.** ¿Cuál es la razón por la que, una vez compilado el nuevo kernel, es necesario reconfigurar el gestor de arranque instalado?
- a. Para que se instale LILO, que reemplaza a GRUB en las nuevas versiones del kernel.
- b. Para actualizar el menú de arranque incorporando el nuevo kernel en la configuración.
- c. Para que almacene la imagen del kernel en el sector de arranque.
- d. Para que se instale el binario del gestor de arranque generado al compilar el nuevo kernel.

**A2.** ¿Qué opción u opciones describen un initramfs?
- a. Inicializa la RAM del dispositivo con ceros como prueba de integridad.
- b. Es un componente del kernel que ya no se utiliza en distribuciones modernas.
- c. No siempre es necesario.
- d. Aloja módulos del kernel y programas útiles para el arranque del sistema.

**A3.** ¿Cuál de las siguientes afirmaciones sobre `/proc` es **falsa**?
- a. `/proc` no ocupa espacio en disco.
- b. Los módulos pueden registrar entradas en `/proc`.
- c. Solo los módulos compilados como built-in pueden crear entradas en `/proc`.
- d. `/proc` contiene información sobre los procesos.
- e. Al leer o escribir un archivo de `/proc` se ejecuta una función del kernel asociada que devuelve o recibe los datos.

**A4.** ¿Cuál es la forma correcta de implementar un driver para el kernel Linux?
- a. Como un servicio.
- b. Como una system call.
- c. Como un módulo.
- d. Como un kthread.

**A5.** Verdadero o falso: *"Un hilo (thread) es la unidad básica de utilización de CPU en los sistemas operativos modernos."*

**A6.** Verdadero o falso: *"El SO guest en un entorno virtualizado tiene acceso directo y completo al hardware real de la máquina, sin ningún tipo de intermediación."*

**A7.** ¿Cuál de las siguientes afirmaciones NO es correcta con respecto a cgroups v1?
- a. Un controlador solo puede ser desmontado si no tiene cgroups hijos.
- b. Es posible montar un controlador en particular.
- c. Dentro de una jerarquía, un proceso puede estar en varios cgroups a la vez.
- d. Un proceso creado por un fork pertenece al mismo cgroup que el padre.

**A8.** Verdadero o falso: *"Docker utiliza una arquitectura cliente-servidor donde el daemon (dockerd) es el servidor responsable de crear, ejecutar y monitorear los contenedores."*

**A9.** Verdadero o falso: *"Un sistema con muchas características y funcionalidades tiende a ser más seguro porque ofrece más herramientas de defensa."*

**A10.** ¿En cuál de los siguientes tipos de filesystem NO se puede disminuir su tamaño?
- a. Ext2
- b. Ext3
- c. Ext4
- d. XFS
- e. Todos pueden hacerlo.

## Parte B — Desarrollo (máx. 3-4 renglones cada una)

**B1.** Describa los motivos que puede tener un usuario de Linux para compilar un kernel (al menos tres).

**B2.** ¿Qué diferencia hay entre `insmod` y `modprobe`? ¿Qué rol cumple el archivo `modules.dep`?

**B3.** Indique si es verdadero o falso y justifique: *"Los drivers acceden a las funcionalidades del kernel a través de system calls."*

**B4.** ¿Qué pasos se requieren para agregar una nueva system call al kernel de Linux?

**B5.** ¿Qué comparten los hilos de un mismo proceso y qué tiene cada hilo como propio?

**B6.** ¿Qué implica la técnica de binary translation? ¿El SO guest debe modificarse?

**B7.** ¿Qué características del kernel Linux utiliza Docker para proveer containers, y para qué se usa cada una?

**B8.** ¿De qué manera puede lograrse que los datos sean persistentes en Docker? Nombre las dos formas y sus diferencias.

**B9.** En el contexto de los filesystems, defina brevemente inodo, bloque y extent.

**B10.** En un grafo de asignación de recursos: ¿qué significa que exista un ciclo cuando cada recurso tiene una sola instancia? ¿Y cuando hay múltiples instancias?

---

## Respuestas — Simulacro 3

### Parte A

**A1. b.** GRUB no detecta el kernel nuevo automáticamente: hay que actualizar el menú de arranque (`update-grub` regenera `grub.cfg` con la ruta de la nueva imagen y su initramfs). No se reinstala el binario del gestor (d falsa) ni se toca el sector de arranque (c falsa).

**A2. c y d.** El initramfs aloja módulos/drivers y programas mínimos para el arranque, y puede no ser necesario si todo lo requerido para montar el root está built-in. No inicializa RAM con ceros (a) y sigue usándose en distros modernas (b).

**A3. c.** Cualquier módulo (cargable o built-in) puede registrar entradas en `/proc`. Las demás son verdaderas: es un pseudo-FS generado al vuelo, sin ocupar disco.

**A4. c.** Un driver se implementa como **módulo** del kernel (o built-in). No es un servicio de usuario, no es una syscall (el driver implementa `file_operations`, no syscalls) ni un kthread.

**A5. VERDADERO.** En los SO modernos el hilo es la unidad de planificación/uso de CPU, mientras que el proceso es la unidad de propiedad de recursos (colección de hilos que comparten espacio de direcciones y recursos).

**A6. FALSO.** El VMM/hypervisor siempre intermedia: presenta hardware virtual, controla recursos e intercepta/emula las instrucciones privilegiadas del guest (trap al VMM). El guest nunca ve el hardware real directamente.

**A7. c.** En cgroups v1, dentro de UNA jerarquía un proceso pertenece a **un solo** cgroup (puede estar en varios cgroups solo porque hay varias jerarquías, una por controlador). a, b y d son correctas.

**A8. VERDADERO.** `dockerd` (daemon) es el servidor que crea, ejecuta y monitorea contenedores e imágenes; el cliente `docker` (CLI) se comunica con él mediante una API REST.

**A9. FALSO.** Más features = más código = más **superficie de ataque** y más bugs potenciales. La seguridad se favorece con el principio de mínimo privilegio (POLA) y eliminando lo que no se usa.

**A10. d. XFS.** XFS solo puede crecer (extenderse); no soporta reducción. Los Ext sí pueden reducirse (desmontados).

### Parte B

**B1.** Soportar nuevos dispositivos (drivers de HW no reconocido); agregar funcionalidad (nuevos filesystems, protocolos); optimizar el rendimiento para el hardware donde corre; adaptar/aligerar quitando soporte que no se usa; corregir bugs de seguridad o de programación aplicando parches.

**B2.** `insmod` carga UN módulo indicando la ruta del .ko y **no resuelve dependencias** (falla si faltan símbolos). `modprobe` carga por nombre desde `/lib/modules` y resuelve automáticamente las dependencias consultando `modules.dep`, el mapa de dependencias entre módulos que genera `depmod -a`.

**B3.** **FALSO.** Los drivers corren en espacio de kernel/modo privilegiado, así que no necesitan syscalls: invocan directamente la API interna del kernel (`kmalloc`, `printk`, `register_chrdev`, etc.). Las syscalls son el mecanismo del **espacio de usuario** para pedir servicios al kernel.

**B4.** (1) Declararla en la tabla de syscalls (`syscall_64.tbl` / `syscall_32.tbl`) asignándole un **número único**; (2) implementar el handler en el código del kernel (espacio kernel); (3) **recompilar el kernel** e instalar/reiniciar. No alcanza con reiniciar ni puede hacerse como módulo.

**B5.** Comparten: espacio de direcciones (código, datos, heap), archivos abiertos, señales, sockets, el PID y el PCB del proceso. Cada hilo tiene: stack propio, registros y program counter propios, estado de ejecución y su TCB con un TID único.

**B6.** El hypervisor escanea y **reescribe en tiempo de ejecución** las instrucciones sensibles/privilegiadas del guest, reemplazándolas por llamadas seguras al VMM. El SO guest **no se modifica** (ni sabe que está virtualizado), a diferencia de la paravirtualización. Costo mayor porque se emula todo el hardware.

**B7.** **chroot:** fija el union-FS como directorio raíz del contenedor (aislamiento de filesystem). **Namespaces:** dan la vista aislada de recursos (PID, red, montajes, hostname, IPC, usuarios). **cgroups:** limitan y controlan los recursos que consume (CPU, memoria, E/S). **Union filesystem:** apila las capas de la imagen + capa escribible del contenedor.

**B8.** Guardando los datos en el host: **Volumes** — gestionados por Docker en `/var/lib/docker/volumes`; opción recomendada, más portables y desacoplados del host. **Bind mounts** — mapean cualquier ruta del host elegida por el usuario; atados a esa ruta y modificables por procesos ajenos a Docker.

**B9.** **Inodo:** estructura con los metadatos de un archivo (permisos, dueño, tamaño, fechas, punteros a bloques, contador de links) — no incluye el nombre, que vive en el directorio. **Bloque:** unidad mínima de almacenamiento del FS (definida al crearlo). **Extent:** rango de bloques contiguos descripto como inicio + longitud; menos metadatos y mejor rendimiento para archivos grandes.

**B10.** Con **una instancia por recurso**, el ciclo es condición necesaria **y suficiente**: hay deadlock seguro. Con **múltiples instancias**, el ciclo es solo condición necesaria: indica **posibilidad** de deadlock (otro proceso con instancias libres puede terminar y romper la espera).

---

# BONUS — Preguntas extra de alta probabilidad

Preguntas que aparecieron en Moodle/parciales y no entraron en los simulacros. Repasalas sueltas.

**X1.** *Ordene los 7 pasos de la compilación del kernel.*
→ 1. Obtener el código fuente · 2. Preparar el árbol de archivos · 3. Configurar (`.config`) · 4. Construir el kernel e instalar los módulos · 5. Reubicar el kernel y crear el initrd · 6. Configurar el gestor de arranque · 7. Reiniciar y probar.

**X2.** *¿Qué es el major y el minor number?*
→ Major: identifica el **driver** asociado a un tipo de dispositivo. Minor: identifica la **instancia/dispositivo concreto** dentro de ese driver (ej.: sda1 y sda2 comparten major, difieren en minor).

**X3.** *¿Cuáles son los 3 file descriptors que todo proceso tiene abiertos al iniciarse?*
→ 0 = stdin, 1 = stdout, 2 = stderr.

**X4.** *V/F: "Con la variable UMASK es posible indicar los permisos por defecto en la creación de un archivo o directorio."*
→ **VERDADERO.** Se resta de los permisos base: 666 (archivos) y 777 (directorios). Ej.: umask 022 → archivo 644, directorio 755.

**X5.** *V/F: "El sticky bit en un directorio indica que los archivos dentro solo pueden ser renombrados o eliminados por el propietario del archivo (o del directorio, o root)."*
→ **VERDADERO.** Ejemplo clásico: `/tmp`.

**X6.** *V/F: "setuid hace que el ejecutable corra con los privilegios del usuario que lo lanza."*
→ **FALSO.** Corre con los privilegios del **dueño del archivo** (ej.: `passwd` corre como root). Es el mecanismo de cambio de dominio dinámico en UNIX.

**X7.** *¿Dónde se almacenan las contraseñas de los usuarios en Linux?*
→ En `/etc/shadow` (hasheadas), legible/modificable solo por root. `/etc/passwd` es legible por todos y NO contiene contraseñas.

**X8.** *V/F: "El journaling es un log que almacena todas las operaciones que se realizan sobre un archivo."*
→ **FALSO.** Registra operaciones/transacciones **antes de aplicarlas** al FS para poder recuperar un estado consistente tras una caída; no es un historial completo por archivo.

**X9.** *Describa cómo BTRFS usa Copy-on-Write.*
→ Al modificar un dato no sobrescribe el bloque original: escribe en un bloque nuevo y actualiza los punteros. Da consistencia ante cortes y snapshots baratos (comparten bloques; solo se copia lo que cambia).

**X10.** *¿Cuáles opciones son correctas sobre snapshots LVM?*
→ Usan **CoW**; al crearse **no** se copian datos ni metadatos; el espacio ocupado **crece a medida que se modifica** el LV original; no se eliminan solos.

**X11.** *Si se desea achicar un LV, ¿en qué orden se procede?*
→ Primero se achica el **filesystem**, después el **LV**. (Para extender: primero el LV, después el FS. "Para crecer, primero el contenedor; para achicar, primero el contenido.")

**X12.** *Se tienen 3 discos de 1, 2 y 3 GB en RAID 5. ¿Tamaño máximo para datos de usuario?*
→ El RAID se limita al disco más chico: 3 × 1 GB, menos 1 GB de paridad → **2 GB** útiles.

**X13.** *¿En qué nivel de RAID no existe striping de datos?*
→ **RAID 1** (mirroring puro).

**X14.** *¿Cuántos discos pueden fallar en RAID 5 sin pérdida de datos? ¿Y en RAID 6?*
→ RAID 5: **1** disco. RAID 6 (doble paridad distribuida): **2** discos.

**X15.** *V/F: "En un multiprocesador alcanza con deshabilitar interrupciones para proteger estructuras del kernel."*
→ **FALSO.** Solo deshabilita interrupciones de la CPU local; otra CPU puede acceder igual. Se necesita mutex por HW: **TSL bloqueando el bus** (spinlock).

**X16.** *¿Qué es SMP y qué ventaja tiene sobre maestro-esclavo?*
→ Una sola copia del SO que **cualquier CPU** puede ejecutar (la syscall la atiende la CPU que la invocó). Elimina el cuello de botella del maestro; el costo es sincronizar el acceso concurrente al kernel (locks por estructura).

**X17.** *¿Qué es la afinidad de CPU y por qué el planificador la respeta?*
→ Ejecutar un hilo en la CPU donde ya corrió: sus datos siguen en la cache. Migrarlo implica cache misses y tráfico de coherencia; por eso se usan colas por CPU (planificación de 2 niveles).

**X18.** *Diferencia UMA vs NUMA.*
→ UMA: tiempo de acceso a memoria **igual** para todas las CPUs (SMP por bus, escala poco). NUMA: espacio de direcciones único pero acceso **local rápido / remoto lento**; escala más.

**X19.** *¿Qué es un estado seguro? ¿Estado inseguro implica deadlock?*
→ Seguro: existe una secuencia `<P0..Pn>` en la que todos los procesos pueden terminar con los recursos disponibles → garantiza que no hay deadlock. Inseguro: no existe tal secuencia; es solo **posibilidad** de deadlock. Deadlock ⇒ inseguro, pero inseguro ⇏ deadlock.

**X20.** *Nombre las 4 estrategias de manejo de deadlocks.*
→ **Prevención** (anular alguna condición de Coffman), **evitación** (algoritmo del Banquero: solo asignar si el estado sigue seguro), **detección y recuperación** (grafo wait-for + abortar/expropiar), **avestruz** (ignorarlo; lo que hacen UNIX/Windows en la práctica).

---

## Tabla de autoevaluación

| Simulacro | Bien (de 20) | Nota equivalente | ¿Aprobado (≥14)? | ¿Promoción (≥16)? |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

> Si en algún tema fallás 2 o más veces entre los tres simulacros, volvé al capítulo correspondiente del `RESUMEN_FINAL.md` y a las "trampas típicas" de ese tema.
