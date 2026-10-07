# Sistemas Operativos — Repaso de conceptos (recuperatorio)

> Preguntas y respuestas de los temas centrales que se evalúan. Material para repaso general.
> (No incluye RAID/LVM, que no entran en el programa actual.)

---

## Kernel

**¿Qué es el kernel de GNU/Linux y cuáles son sus funciones principales?**
Es una porción de código que reside en memoria principal, se ejecuta en modo privilegiado y actúa como intermediario entre el hardware y las aplicaciones (a las que ofrece una interfaz vía system calls). Sus funciones principales son: administración de la memoria, manejo de la CPU, administración de procesos y gestión de E/S (a veces se agrega comunicación/concurrencia).

**¿Por qué se considera que Linux es un kernel monolítico-híbrido?**
Es monolítico porque tiene todos los servicios en un único bloque ejecutándose en modo privilegiado, pero es híbrido porque admite módulos cargables en tiempo de ejecución, lo que le da flexibilidad sin dejar de ser monolítico.

**¿Por qué se considera que Linux es portable?**
Porque su código puede modificarse y compilarse fácilmente para distintas arquitecturas de CPU: una misma base de código soporta muchas arquitecturas ya que está escrito mayormente en C, dejando el Assembler solo para lo específico de bajo nivel de cada arquitectura. El binario NO es el mismo para todas las arquitecturas.

**En un microkernel, ¿los drivers y servidores de filesystem se ejecutan en modo kernel para mejorar el rendimiento? (V/F)**
Falso. En un microkernel los drivers y servicios (filesystem, red, etc.) corren en espacio de usuario, y solo lo mínimo va en modo kernel. Eso da más aislamiento y robustez pero menos rendimiento (más cambios de modo). Correr todo en modo kernel es lo del monolítico.

**Tipos de kernel: ¿qué es un kernel monolítico?**
Un kernel monolítico es aquel que tiene toda la funcionalidad linkeada en una única imagen, ejecutándose en modo kernel. El microkernel, en cambio, deja lo mínimo en el núcleo y el resto (drivers, filesystem) en espacio de usuario.

**¿Qué contiene el initramfs y bajo qué condición puede NO ser necesario?**
Es un sistema de archivos temporal en RAM que se monta al arranque, antes de montar el root real. Contiene los drivers/módulos que el kernel necesita para poder montar el filesystem raíz (además de un init temporal y utilidades). Puede no ser necesario si todos esos drivers ya están compilados built-in en el kernel, porque entonces monta el root directamente.

**¿El kernel de Linux es un sistema operativo en sentido estricto? (V/F)**
Falso. El kernel es el núcleo del SO, pero un sistema operativo completo incluye además utilidades, bibliotecas (libc), shell, etc. Linux (kernel) + GNU (userland) = GNU/Linux.

**¿Por qué, una vez compilado el kernel, hay que reconfigurar el gestor de arranque (GRUB)?**
Para actualizar el menú de arranque incorporando el nuevo kernel. Se ejecuta `update-grub` para que GRUB agregue una entrada al menú apuntando al nuevo kernel (y su initramfs). El binario de GRUB no se genera al compilar el kernel.

**¿Bajo qué situaciones puede ser necesaria una compilación del kernel?**
Para agregar soporte de nuevos dispositivos, corregir bugs de código built-in, optimizar o quitar soporte no usado, y agregar funcionalidad. Agregar "nuevos usuarios" no tiene nada que ver con compilar el kernel.

**Enumere los pasos (1 a 7) del proceso de compilación del kernel.**
1) Obtener el código fuente. 2) Preparar el árbol de archivos. 3) Configurar el kernel (.config). 4) Construir el kernel e instalar los módulos. 5) Reubicar el kernel y crear el initramfs. 6) Configurar el gestor de arranque (GRUB). 7) Reiniciar y probar el nuevo kernel.

**Al compilar con `make modules_install && make install`, ¿en qué directorios se instalan la imagen del kernel y los módulos?**
Los módulos se instalan en `/lib/modules/<version>/` y la imagen del kernel (vmlinuz), el initrd/initramfs y el System.map se copian a `/boot/`. Luego se actualiza GRUB.

---

## make y Makefiles

**¿Qué es `make` y para qué sirve un Makefile?**
`make` es una herramienta que automatiza la compilación (y otras tareas). Lee un archivo llamado `Makefile` donde están definidas las directivas o reglas que indican qué compilar y cómo. En vez de compilar a mano con `gcc`, `make` ejecuta esas reglas resolviendo dependencias. En la compilación del kernel, `make` ejecuta las directivas definidas en los Makefiles dentro del árbol de directorios del código fuente.

**¿Qué es un target (regla) en un Makefile? Dé ejemplos.**
Un target es una tarea con un nombre y una receta de comandos. Se invoca con `make <target>`. Ejemplos típicos: `make` o `make all` (compila), `make clean` (borra los archivos generados: objetos y ejecutables) y `make run` (ejecuta el programa). Cada receta se escribe indentada con un TAB.

**¿Cómo se compila un módulo del kernel con `make`?**
Con `make -C <KERNEL_CODE> M=$(pwd) modules`. La opción `-C` entra al directorio del código del kernel y usa su sistema de compilación (kbuild); `M=$(pwd)` le indica que el módulo a compilar está en el directorio actual; y `modules` es el objetivo. El Makefile del módulo suele tener una sola línea: `obj-m := memory.o`, que le dice a kbuild que genere el módulo cargable `.ko` a partir de `memory.o`.

**¿El comando `make` puede recibir parámetros? (V/F)**
Verdadero. `make` acepta parámetros/variables, por ejemplo `make -C <ruta> M=$(pwd) modules` o `make VARIABLE=valor`. Es falso decir que no recibe parámetros.

**¿Qué es un parche (patch) y cómo se aplica al código del kernel?**
Un parche es un archivo con las diferencias (cambios) respecto de una versión del código. Los parches del kernel son incrementales (se aplican en orden, uno sobre otro). Se aplican con el comando `patch`, que modifica el código fuente del kernel incorporando esos cambios.

---

## Módulos

**¿Los módulos del kernel se ejecutan en espacio de usuario? (V/F)**
Falso. Un módulo, una vez cargado con `insmod`, se ejecuta en espacio de kernel / modo supervisor (privilegiado). Por eso un bug en un módulo puede comprometer todo el sistema.

**¿Cuál de las siguientes NO describe a un módulo del kernel?**
La falsa es "permiten implementar system calls dinámicas". Los módulos sirven para drivers y funcionalidad, pero las system calls NO se agregan cargando módulos (requieren modificar la tabla de syscalls y recompilar). Sí es cierto que se cargan/descargan dinámicamente, que su funcionalidad puede ir built-in, y que se instalan en /lib/modules.

**¿Qué ventaja tiene compilar una funcionalidad como módulo en vez de built-in?**
El built-in ocupa memoria aunque no se use; el módulo se carga solo cuando se necesita y se puede quitar. Además, para cambiar o actualizar algo built-in hay que recompilar el kernel y reiniciar; un módulo se agrega/actualiza en caliente (`insmod`/`rmmod`), manteniendo el kernel base más liviano.

**¿Qué sucede al cargar un módulo con `insmod`?**
El módulo se carga en espacio de kernel, corre su función de inicialización (`module_init`/`init_module`) y desde ahí puede registrar interfaces o drivers (con `register_chrdev` o `platform_driver_register`). No reemplaza el kernel: se agrega a él.

**¿Para qué sirven `insmod` y `modprobe`? ¿En qué se diferencian?**
Ambos cargan módulos. `insmod` carga un `.ko` por su ruta, sin resolver dependencias. `modprobe` lo carga por nombre (busca en `/lib/modules`) y resuelve automáticamente las dependencias según `modules.dep`. Para descargar: `rmmod` o `modprobe -r`.

---

## System Calls

**¿Cuál de estas afirmaciones sobre system calls es falsa?**
La falsa es "se implementan como módulos del kernel". Las syscalls son parte del kernel base; agregarlas requiere editar la `syscall_table` y recompilar, no cargar un módulo. Sí es cierto que se monitorean con strace, que las invocan los programas y que libc implementa wrappers.

**¿La librería libc implementa directamente las system calls en modo kernel, sin trap ni interrupción? (V/F)**
Falso. libc corre en espacio de usuario y solo provee wrappers: acomoda los argumentos y ejecuta la instrucción que dispara un trap/interrupción de software para pasar a modo kernel. La implementación real de la syscall está en el kernel.

**¿La tabla de syscalls (syscall_64.tbl) permite que el dispatcher identifique qué función ejecutar según el número del registro? (V/F)**
Verdadero. Cada syscall tiene un número único; ese número (en un registro) es el índice en la tabla de system calls, que apunta a la función del kernel que la implementa.

**¿Cuál es correcto para agregar una System Call?**
Hay que declararla en la tabla (`syscall_64.tbl`) con un número unívoco, definir su código en el kernel, aumentar `__NR_syscalls` y recompilar el kernel. Para usarla no alcanza con reiniciar: hay que recompilar.

**¿Qué es una system call y cuál es su propósito principal?**
Es la interfaz (API) que provee el kernel para que un programa de espacio de usuario pueda solicitar servicios que requieren modo privilegiado (acceder a archivos, hardware, red, crear procesos). Es el puente controlado usuario→kernel, mediante un trap que cambia de modo.

**¿Cuáles son los 3 file descriptors que todo proceso tiene abiertos al iniciarse?**
0 = STDIN (entrada), 1 = STDOUT (salida), 2 = STDERR (errores). Por eso `printf` termina en `write(1, ...)`.

**Sobre POSIX y System Calls, ¿qué es correcto?**
POSIX es un estándar de interfaz que busca la portabilidad de las aplicaciones; en Unix, libc es la API que respeta POSIX. No toda función de libc es una syscall (muchas son de biblioteca), aunque técnicamente se puede invocar una syscall sin libc.

---

## Drivers y /dev

**¿Cuál es la forma correcta de implementar un driver para el kernel Linux?**
Como un módulo del kernel (aunque puede ir built-in). Registra el dispositivo con `register_chrdev` y define sus operaciones con `struct file_operations`. No es un servicio, ni una system call, ni un kthread.

**Al ejecutar `ls -l` se ve `brw-rw---- 1 root root 240, 0 weird`. ¿Qué es verdadero?**
La `b` inicial indica que es un dispositivo de bloques. El 240 es el major number (identifica al driver) y el 0 es el minor. NO ocupa 240 bytes (240 es el major, no el tamaño). Es un device file: escribir con `echo` no aumenta su tamaño. Correctas: es dispositivo de bloques y el driver se vincula al major number 240.

**¿Qué son el major y el minor number?**
El major identifica qué driver maneja el dispositivo (el kernel lo usa para redirigir las operaciones). El minor identifica qué instancia concreta dentro de ese driver (por ejemplo `/dev/sda1` y `/dev/sda2` comparten major pero difieren en minor).

**¿Los drivers acceden a las funcionalidades del kernel a través de system calls? (V/F)**
Falso. Los drivers corren en espacio de kernel, así que invocan la API interna del kernel directamente (`kmalloc`, `printk`, `register_chrdev`). Las system calls son el mecanismo del espacio de usuario.

**¿Qué tipos de archivos hay en /dev y qué representan?**
Son device files que representan dispositivos y son el punto de acceso desde el espacio de usuario (se abren/leen/escriben como archivos, y el kernel los redirige al driver por su major/minor). Tipos: de caracter (c), acceso byte a byte secuencial (teclado, tty), y de bloque (b), bloques de tamaño fijo con acceso aleatorio (discos). Los de red no aparecen en /dev.

---

## Filesystems

**¿Qué propiedad de un archivo NO está en el i-nodo?**
El nombre NO está en el inodo. El inodo guarda metadata (permisos, dueño, tamaño, fechas) y punteros a los bloques. El nombre vive en el directorio, que asocia nombre → número de inodo.

**Defina inodo, bloque y extent.**
Bloque: unidad mínima de almacenamiento en disco (tamaño fijo). Inodo: estructura con la metadata del archivo más punteros a sus bloques (sin el nombre). Extent: forma de describir un rango contiguo de bloques de una sola vez (en vez de un puntero por bloque); reduce metadata y fragmentación (ext4, XFS, BTRFS).

**¿Qué es un link simbólico? ¿En qué se diferencia de un hard-link? ¿Cuál consume un inodo?**
Symlink: archivo aparte (con su propio inodo) cuyo contenido es una ruta; si borrás el original queda roto; puede cruzar filesystems. Hard-link: otro nombre para el mismo inodo (NO consume inodo nuevo); sobrevive aunque borres el nombre original. Consume inodo nuevo solo el symlink.

**¿Cada vez que se crea un hard-link se utiliza un nuevo inodo? (V/F)**
Falso. El hard-link reutiliza el inodo del archivo original (solo agrega una entrada nombre→inodo y suma 1 al contador de links). El que sí crea un inodo nuevo es el symlink.

**¿En cuál de estos file systems NO se puede disminuir (achicar) su tamaño?**
En XFS. XFS se puede agrandar pero no reducir (por su diseño: inodos dinámicos y allocation groups dispersos por todo el volumen). Los ext (2/3/4) sí permiten reducirse.

**Describa cómo BTRFS usa Copy-on-Write (CoW).**
BTRFS no sobrescribe datos in-place: ante un cambio escribe los datos en bloques nuevos y luego actualiza los punteros/árbol. Ventajas: consistencia ante cortes (nunca queda a medias) y snapshots baratos (comparten bloques, solo se copia lo que cambia).

**Sobre snapshots en LVM, ¿qué es correcto?**
Usan Copy-on-Write: al crearse casi no ocupan; a medida que el LV original cambia, el snapshot guarda las versiones viejas de esos bloques, creciendo con las modificaciones.

**Sobre /proc (procFS), ¿cuál lo define mejor?**
Provee una interfaz a las estructuras del kernel y la mayoría de sus archivos tienen tamaño 0. Es un filesystem virtual: no ocupa disco (se genera al vuelo) y expone información del kernel (procesos, configuración).

**¿Solo los módulos compilados como built-in pueden crear entradas en /proc? (V/F)**
Falso. Tanto los módulos built-in como los cargables pueden registrar entradas en /proc. Al leer/escribir esas entradas se ejecuta una función del kernel asociada.

---

## Virtualización

**¿Qué diferencia hay entre virtualización y emulación?**
Virtualización: el guest corre sobre la misma arquitectura que el host, por eso la mayoría de las instrucciones se ejecutan directo en la CPU (rápido). Emulación: se simula por software todo el hardware, traduciendo cada instrucción, por eso puede correr otra arquitectura, pero es mucho más lento.

**¿Qué es un hypervisor y cómo se clasifican?**
Es el VMM (Virtual Machine Monitor): programa que crea las VMs, reparte el hardware y aísla los guests (corre en modo supervisor; las instrucciones privilegiadas del guest generan trap). Tipo 1 (bare-metal): corre directo sobre el hardware (ESXi, KVM, Xen), para servidores. Tipo 2 (hosted): corre sobre un SO host como una aplicación (VMware Workstation).

**¿El SO guest tiene acceso directo y completo al hardware real, sin intermediación? (V/F)**
Falso. El hypervisor (VMM) intermedia siempre: crea hardware virtual, controla los recursos e intercepta/emula las instrucciones privilegiadas. El guest ve hardware virtual, no el real directo.

**En un hypervisor tipo 2, ¿el SO host se ejecuta directamente sobre el hardware físico y gestiona los drivers reales? (V/F)**
Verdadero. En tipo 2 el SO host corre sobre el hardware y maneja los drivers reales; el hypervisor es una aplicación que corre sobre ese host. En tipo 1 el hypervisor está directo sobre el hardware.

**¿En cuál técnica se debe modificar el kernel del guest para mejorar el rendimiento?**
En la paravirtualización. El SO guest está modificado para "saber que está virtualizado" y hablar con el hypervisor vía su API (hypercalls), evitando el costo de atrapar y emular. Gana performance pero soporta pocos SO.

**¿Qué implica la técnica binary translation? ¿Y trap-and-emulate?**
Trap-and-emulate: el guest corre en modo usuario; sus instrucciones privilegiadas generan un trap que el VMM emula y devuelve. Binary translation: el hypervisor escanea y reescribe en runtime las instrucciones sensibles que en x86 no generaban trap, reemplazándolas por llamadas seguras al VMM.

---

## Containers y Docker

**¿Qué es una imagen? ¿Y un contenedor? ¿Cómo se relacionan?**
La imagen es un template de solo lectura (app + dependencias + instrucciones): el molde. El contenedor es una instancia en ejecución de una imagen. Relación tipo clase/objeto: de una imagen se pueden crear muchos contenedores. Diferencia central: imagen = estática; contenedor = corriendo.

**¿Qué características del kernel usa Docker para proveer containers?**
Namespaces (aíslan la vista: PID, net, mount, uts), cgroups (limitan recursos) y chroot / union file systems (aíslan el filesystem). No usa hypervisor ni un kernel propio.

**¿Cada container instala/utiliza su propio kernel, diferente al del SO base? (V/F)**
Falso. Los containers comparten el kernel del host. Por eso no se puede correr un container con un kernel distinto (por ejemplo Windows sobre Linux). Es su diferencia clave con las VMs.

**¿Qué es un Union File System y cómo lo usa Docker?**
Es un mecanismo de montajes que apila varios directorios (capas) mostrándolos como uno solo. Docker arma la imagen como capas (cada una son diferencias con la anterior), todas de solo lectura menos la última (la del contenedor, R/W). Las capas de solo lectura se reutilizan entre imágenes.

**Al remover un archivo dentro de un Dockerfile con `RUN rm`, ¿se elimina definitivamente y reduce el tamaño de la imagen? (V/F)**
Falso. Como la imagen son capas apiladas, la capa donde estaba el archivo ya quedó fija; el `RUN rm` agrega una nueva capa que lo oculta, pero el archivo sigue ocupando en la capa anterior. El tamaño total no se reduce.

**¿Docker usa arquitectura cliente-servidor donde dockerd es el servidor que crea/ejecuta/monitorea los contenedores? (V/F)**
Verdadero. `dockerd` es el servidor (crea, ejecuta y monitorea contenedores e imágenes); la CLI es el cliente y se comunica vía la API REST. Docker no captura las syscalls: eso lo hace el kernel.

**Un mismo proceso muestra distinto PID visto desde el contenedor y desde el host. ¿Por qué?**
Por el PID namespace: le da al contenedor su propia numeración de PIDs. Es el mismo proceso con dos IDs: dentro del contenedor arranca como PID 1 (su init), y en el host tiene su PID real entre todos los procesos. El host ve los procesos del contenedor; al revés no.

**¿Dos formas de persistir datos en Docker y su diferencia?**
Volumes: los gestiona Docker (en `/var/lib/docker/volumes`); recomendados, más portables. Bind mounts: montan una ruta cualquiera del host (elegida por vos), accesible también por procesos ajenos a Docker. Diferencia: quién administra la ubicación y la portabilidad.

**¿Qué es el archivo compose y en qué se diferencia de un Dockerfile?**
El compose (YAML) declara una aplicación multi-contenedor (servicios, redes, volúmenes) y se levanta con un comando. El Dockerfile describe los pasos para construir UNA imagen. Uno arma la pieza, el otro orquesta el conjunto; se complementan (compose puede usar un Dockerfile con `build:`).

---

## Threads

**¿Un hilo (thread) es la unidad básica de utilización de CPU en los SO modernos? (V/F)**
Verdadero. El hilo es la unidad de ejecución/planificación (uso de CPU); el proceso es la unidad de propiedad de recursos (y contiene uno o más hilos).

**¿Cuál es la diferencia fundamental entre proceso y thread?**
Los hilos de un proceso comparten el espacio de direcciones y los recursos (código, datos, heap, archivos), mientras que cada proceso tiene su espacio aislado. Cada hilo sí tiene su propio stack, registros, PC y estado.

**¿Quién planifica los ULT? ¿Y los KLT? ¿Cómo afecta al multinúcleo?**
ULT: los planifica la biblioteca en espacio de usuario; el kernel ve un solo proceso, por lo que no hay paralelismo real (no aprovechan varios cores) y un bloqueo frena a todos. KLT: los planifica el kernel, hilo por hilo, por lo que sí hay paralelismo (los reparte en distintos cores).

**¿Un ULT en el modelo M:1 puede aprovechar directamente múltiples procesadores físicos sin ningún mecanismo adicional? (V/F)**
Falso. En M:1 muchos ULT mapean a un solo KLT: el kernel ve una única entidad ejecutable, por lo que no hay paralelismo real en varios cores. Para eso se necesita 1:1 o M:N (KLT).

**Si un proceso crea N ULT, ¿con strace se observa que invoca N veces clone3? (V/F)**
Falso. Los ULT se crean en espacio de usuario, sin pedirle hilos al kernel, por lo que no hay `clone3` por hilo. `clone`/`clone3` aparece con procesos (fork) y con KLT (pthread_create), no con ULT.

**¿Qué características tendrá el proceso creado si se ejecuta fork() pero NO exec()?**
El hijo es una copia (clon) del padre que ejecuta el mismo programa (no se reemplaza). Tiene PID propio, su memoria es copia del padre vía Copy-on-Write (se duplica al escribir), hereda recursos, y padre/hijo se distinguen por el valor de retorno de fork (0 en el hijo, PID del hijo en el padre).

**¿Qué es el GIL y por qué en CPython se usan procesos para CPU-bound?**
El Global Interpreter Lock permite que solo un hilo ejecute bytecode a la vez en CPython/MRI. Por eso los hilos no logran paralelismo real en tareas CPU-bound. Solución: procesos (multiprocessing), porque cada proceso tiene su propio intérprete y GIL, logrando paralelismo real. En IO-bound el GIL se libera durante la espera.

---

## Multiprocesadores y Seguridad

**¿En qué CPU/s corre el SO en maestro-esclavo vs SMP?**
Maestro-esclavo: el SO corre en una única CPU (la maestra); todas las syscalls se redirigen a ella (cuello de botella con muchas CPU). SMP: el SO corre en cualquier CPU (la que invocó la syscall), sin maestro, pero requiere sincronizar el acceso concurrente al kernel.

**En SMP, ¿qué puede ocurrir si el kernel accede en paralelo a una estructura compartida? ¿Qué mecanismo lo maneja?**
Puede haber una condición de carrera, dejando la estructura en estado inconsistente (por ejemplo dos CPU eligen el mismo proceso o la misma página libre). Se maneja con locks/mutex (exclusión mutua): lock global o, mejor, lock por estructura.

**En SMP, ¿hay impacto negativo por migrar un hilo de una CPU a otra?**
Sí: se pierde el aprovechamiento de la caché (afinidad). En la CPU nueva sus datos no están cacheados, por lo que hay cache misses, relecturas desde memoria y tráfico de coherencia. Por eso el SO prefiere mantener cada hilo en su CPU y solo migra para balancear carga.

**En gang scheduling, ¿todos los hilos de un proceso se programan para ejecutarse simultáneamente en distintas CPU en el mismo intervalo? (V/F)**
Verdadero. En gang scheduling (planificación por pandillas) los hilos relacionados forman una pandilla que se ejecuta en simultáneo en distintas CPU e inician/terminan sus intervalos juntos. Mejora el trabajo en paralelo (hilos que se comunican no se esperan).

**En un sistema distribuido, ¿todos los nodos deben ejecutar el mismo SO y tener el mismo hardware para la interoperabilidad? (V/F)**
Falso. Los sistemas distribuidos conectan computadoras completas heterogéneas (distinto SO y hardware) a través de una red, comunicándose por pasaje de mensajes. No requieren SO ni hardware idénticos.

**¿Qué es ASLR? ¿Se puede activar/desactivar sin recompilar el kernel?**
Address Space Layout Randomization: coloca en direcciones aleatorias el stack, heap, librerías (y código si es PIE) en cada ejecución, para dificultar exploits (buffer overflow) que dependen de direcciones fijas. Sí se activa/desactiva sin recompilar, con `/proc/sys/kernel/randomize_va_space` (0 desactivado, 2 completo).

**¿Un dominio de protección es un conjunto de pares (objeto, derecho) que especifica qué operaciones puede hacer un proceso sobre cada objeto? (V/F)**
Verdadero. Un dominio es un conjunto de pares (objeto, derecho). Un proceso en ese dominio puede hacer sobre cada objeto solo las operaciones autorizadas (right). En UNIX el dominio lo define el par (UID, GID).

**¿Un sistema con muchas características y funcionalidades tiende a ser más seguro porque ofrece más herramientas de defensa? (V/F)**
Falso. Más funcionalidades significan mayor superficie de ataque (más código, más bugs potenciales). La seguridad se favorece con el mínimo privilegio (POLA) y quitando lo que no se usa, no acumulando features.
