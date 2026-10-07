## 1. Kernel de Linux y compilación

### Qué es el kernel

El **kernel** es la porción de código que reside en **memoria principal** y actúa como **intermediario entre el hardware y las aplicaciones**. Se ejecuta en modo privilegiado, ofrece a los procesos de usuario una interfaz controlada a través de **system calls** y es, en sentido estricto, el sistema operativo en sí mismo. El resto de piezas —shell, utilidades, librerías como `libc`— forman parte del "SO en sentido amplio" (Linux + GNU = GNU/Linux), pero el núcleo, lo mínimo indispensable, es el kernel.

Sus **cinco funciones principales** son la administración de la **memoria principal**, el manejo del uso de la **CPU** (scheduling), la administración de **procesos**, la gestión de **entrada/salida** y la coordinación de **comunicación y concurrencia** entre procesos. Ningún proceso de usuario puede acceder al hardware ni salirse de su propio espacio de direcciones sin pedírselo al kernel a través de una syscall.

### Modos de ejecución

El hardware provee al menos dos **modos de ejecución**, señalizados por un **bit de modo** en la CPU:

- **Modo supervisor / kernel / privilegiado:** habilita el conjunto completo de instrucciones, incluyendo las privilegiadas (acceso a HW, cambio de tablas de páginas, deshabilitar interrupciones, etc.). Solo se ejecutan acá.
- **Modo usuario:** el proceso ve únicamente su propio espacio de direcciones y un subconjunto reducido de instrucciones.

La CPU arranca en modo supervisor y desciende a modo usuario cuando le cede el control a un proceso. La **única** forma de volver a modo kernel es a través de un **trap o interrupción** (una syscall es exactamente eso: una interrupción de software controlada). Un proceso no puede "decidir" cambiar de modo por su cuenta.

<div class="diagram">
<svg viewBox="0 0 620 220" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="11"><rect x="20" y="20" width="580" height="70" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="30" y="40" fill="#1e40af" font-weight="700">Modo usuario (Ring 3)</text><text xml:space="preserve" x="30" y="58" fill="#1e3a8a" font-size="10">- proceso solo accede a su espacio de direcciones</text><text xml:space="preserve" x="30" y="72" fill="#1e3a8a" font-size="10">- subconjunto reducido de instrucciones</text><line x1="20" y1="100" x2="600" y2="100" stroke="#f97316" stroke-width="2" stroke-dasharray="6,3"/><rect x="230" y="90" width="160" height="20" fill="#fff7ed" stroke="#f97316"/><text xml:space="preserve" x="310" y="104" text-anchor="middle" fill="#9a3412" font-size="10" font-weight="700">TRAP / INTERRUPCIÓN</text><rect x="20" y="120" width="580" height="80" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="30" y="140" fill="#7f1d1d" font-weight="700">Modo supervisor / kernel (Ring 0)</text><text xml:space="preserve" x="30" y="158" fill="#7f1d1d" font-size="10">- conjunto completo de instrucciones (incl. privilegiadas)</text><text xml:space="preserve" x="30" y="172" fill="#7f1d1d" font-size="10">- acceso al HW, tablas de páginas, deshabilitar interrupciones</text><text xml:space="preserve" x="30" y="186" fill="#7f1d1d" font-size="10">- syscalls, drivers, módulos, planificador</text><path d="M 470 90 L 470 60" stroke="#22c55e" stroke-width="2" fill="none" marker-end="url(#ar-up)"/><text xml:space="preserve" x="490" y="70" font-size="9" fill="#166534">return</text><path d="M 500 60 L 500 110" stroke="#0284c7" stroke-width="2" fill="none" marker-end="url(#ar-dn)"/><text xml:space="preserve" x="510" y="90" font-size="9" fill="#0369a1">syscall</text><defs><marker id="ar-up" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M 0 10 L 5 0 L 10 10 z" fill="#22c55e"/></marker><marker id="ar-dn" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto"><path d="M 0 0 L 5 10 L 10 0 z" fill="#0284c7"/></marker></defs></svg>
<div class="caption">Fig. 1.2 — El bit de modo divide el mundo en dos. La barrera se cruza <strong>solo</strong> vía trap/interrupción.</div>
</div>

### Tipos de kernel

Hay tres arquitecturas clásicas:

- **Monolítico** (Unix, FreeBSD): toda la funcionalidad linkeada en una única imagen, todo corre en modo supervisor. Máxima eficiencia (no hay cambios de modo internos entre subsistemas) pero un bug en cualquier parte cae todo.
- **Microkernel** (Minix, QNX): en modo supervisor solo lo mínimo (procesos, memoria, IPC básica). Los drivers, filesystem, red, etc. corren en **espacio de usuario** como servicios. Da aislamiento y robustez a costa de rendimiento (más cambios de modo).
- **Monolítico híbrido** (GNU/Linux, Windows NT, macOS/XNU): es monolítico pero admite **cargar y descargar módulos en tiempo de ejecución**, sin recompilar ni reiniciar. Es el modelo de Linux.

Que Linux sea "**monolítico híbrido**" quiere decir que su base es una única imagen monolítica y sus módulos se cargan en caliente. Cuidado con la trampa: aunque el módulo se cargue dinámicamente, una vez cargado **corre en modo kernel** exactamente igual que el resto — un bug en un módulo puede provocar un Kernel Panic.

<div class="diagram">
<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="11"><g transform="translate(0,0)"><text xml:space="preserve" x="110" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">Monolítico</text><rect x="10" y="30" width="200" height="30" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="110" y="49" text-anchor="middle" fill="#1e40af">Aplicaciones (modo usuario)</text><rect x="10" y="75" width="200" height="150" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="110" y="95" text-anchor="middle" fill="#7f1d1d" font-weight="600">Modo kernel</text><text xml:space="preserve" x="110" y="115" text-anchor="middle" fill="#7f1d1d" font-size="9">Scheduler · Memoria · FS</text><text xml:space="preserve" x="110" y="130" text-anchor="middle" fill="#7f1d1d" font-size="9">Drivers · Red · IPC</text><text xml:space="preserve" x="110" y="145" text-anchor="middle" fill="#7f1d1d" font-size="9">— todo linkeado —</text><text xml:space="preserve" x="110" y="180" text-anchor="middle" fill="#7f1d1d" font-size="9" font-style="italic">1 sola imagen</text><text xml:space="preserve" x="110" y="245" text-anchor="middle" font-size="9" fill="#475569">Unix, FreeBSD</text></g><g transform="translate(240,0)"><text xml:space="preserve" x="110" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">Microkernel</text><rect x="10" y="30" width="200" height="80" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="110" y="48" text-anchor="middle" fill="#1e40af" font-size="9">Aplicaciones + servicios (modo usuario)</text><rect x="20" y="55" width="55" height="18" fill="#bfdbfe" stroke="#1e40af"/><text xml:space="preserve" x="47.5" y="67" text-anchor="middle" font-size="8" fill="#1e40af">Drivers</text><rect x="82" y="55" width="55" height="18" fill="#bfdbfe" stroke="#1e40af"/><text xml:space="preserve" x="109.5" y="67" text-anchor="middle" font-size="8" fill="#1e40af">FS</text><rect x="144" y="55" width="55" height="18" fill="#bfdbfe" stroke="#1e40af"/><text xml:space="preserve" x="171.5" y="67" text-anchor="middle" font-size="8" fill="#1e40af">Red</text><rect x="20" y="80" width="80" height="18" fill="#bfdbfe" stroke="#1e40af"/><text xml:space="preserve" x="60" y="92" text-anchor="middle" font-size="8" fill="#1e40af">Otros servicios</text><rect x="10" y="130" width="200" height="60" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="110" y="150" text-anchor="middle" fill="#7f1d1d" font-weight="600" font-size="10">Modo kernel (mínimo)</text><text xml:space="preserve" x="110" y="168" text-anchor="middle" fill="#7f1d1d" font-size="9">IPC · scheduling básico</text><text xml:space="preserve" x="110" y="183" text-anchor="middle" fill="#7f1d1d" font-size="9">memoria básica</text><text xml:space="preserve" x="110" y="245" text-anchor="middle" font-size="9" fill="#475569">Minix, QNX</text></g><g transform="translate(480,0)"><text xml:space="preserve" x="110" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">Monolítico híbrido</text><rect x="10" y="30" width="200" height="30" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="110" y="49" text-anchor="middle" fill="#1e40af">Aplicaciones (modo usuario)</text><rect x="10" y="75" width="200" height="150" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="110" y="95" text-anchor="middle" fill="#7f1d1d" font-weight="600">Modo kernel</text><text xml:space="preserve" x="110" y="115" text-anchor="middle" fill="#7f1d1d" font-size="9">Scheduler · Memoria · FS</text><text xml:space="preserve" x="110" y="130" text-anchor="middle" fill="#7f1d1d" font-size="9">Red · IPC · Drivers built-in</text><rect x="30" y="150" width="45" height="22" fill="#fde68a" stroke="#b45309" stroke-dasharray="2,2"/><text xml:space="preserve" x="52.5" y="164" text-anchor="middle" font-size="8" fill="#78350f">.ko</text><rect x="85" y="150" width="45" height="22" fill="#fde68a" stroke="#b45309" stroke-dasharray="2,2"/><text xml:space="preserve" x="107.5" y="164" text-anchor="middle" font-size="8" fill="#78350f">.ko</text><rect x="140" y="150" width="45" height="22" fill="#fde68a" stroke="#b45309" stroke-dasharray="2,2"/><text xml:space="preserve" x="162.5" y="164" text-anchor="middle" font-size="8" fill="#78350f">.ko</text><text xml:space="preserve" x="110" y="192" text-anchor="middle" font-size="9" fill="#78350f" font-style="italic">módulos (runtime)</text><text xml:space="preserve" x="110" y="207" text-anchor="middle" font-size="9" fill="#7f1d1d">↕ carga/descarga en caliente</text><text xml:space="preserve" x="110" y="245" text-anchor="middle" font-size="9" fill="#475569" font-weight="700">GNU/Linux, WinNT, XNU</text></g></svg>
<div class="caption">Fig. 1.1 — Los tres tipos de kernel. Linux es monolítico híbrido: base linkeada + módulos <code>.ko</code> cargables en caliente, pero todo ejecuta en modo supervisor.</div>
</div>

### Portabilidad

Linux es **altamente portable**: una misma estructura de código fuente soporta muchas arquitecturas de CPU (x86, ARM, RISC-V, PowerPC, etc.). Esto es posible porque está escrito **mayormente en C** —fácilmente adaptable/recompilable a cualquier arquitectura— reservando **Assembler solo para lo específico de bajo nivel** de cada plataforma. Desde la versión 6.1 también admite Rust, sobre todo para módulos.

Detalle importante: la portabilidad **no significa** que el **mismo binario** corra en cualquier arquitectura. Significa que el **código fuente** se adapta y se recompila. El binario de x86 no arranca en ARM.

### Por qué recompilar el kernel

Los motivos típicos son: **soportar nuevos dispositivos** (drivers de hardware nuevo), **agregar funcionalidad** (soporte para nuevos filesystems, protocolos), **optimizar** el rendimiento según el HW donde corre, **adaptar/limpiar** quitando soporte no usado (kernel más liviano) y **corregir bugs** de seguridad o programación. Cosas como "agregar nuevos usuarios" no tienen nada que ver con recompilar el kernel.

### Los siete pasos de la compilación (en orden)

<div class="diagram">
<svg viewBox="0 0 720 130" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><defs><marker id="flow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M 0 0 L 8 4 L 0 8 z" fill="#0f172a"/></marker></defs><g><circle cx="45" cy="50" r="22" fill="#22d3ee" stroke="#0e7490" stroke-width="2"/><text xml:space="preserve" x="45" y="55" text-anchor="middle" font-weight="700" fill="#0f172a">1</text><text xml:space="preserve" x="45" y="90" text-anchor="middle" font-size="9" fill="#334155">Fuente</text><text xml:space="preserve" x="45" y="102" text-anchor="middle" font-size="8" fill="#64748b">kernel.org</text><line x1="70" y1="50" x2="90" y2="50" stroke="#0f172a" stroke-width="1.5" marker-end="url(#flow)"/><circle cx="115" cy="50" r="22" fill="#22d3ee" stroke="#0e7490" stroke-width="2"/><text xml:space="preserve" x="115" y="55" text-anchor="middle" font-weight="700" fill="#0f172a">2</text><text xml:space="preserve" x="115" y="90" text-anchor="middle" font-size="9" fill="#334155">Preparar</text><text xml:space="preserve" x="115" y="102" text-anchor="middle" font-size="8" fill="#64748b">patch</text><line x1="140" y1="50" x2="160" y2="50" stroke="#0f172a" stroke-width="1.5" marker-end="url(#flow)"/><circle cx="185" cy="50" r="22" fill="#22d3ee" stroke="#0e7490" stroke-width="2"/><text xml:space="preserve" x="185" y="55" text-anchor="middle" font-weight="700" fill="#0f172a">3</text><text xml:space="preserve" x="185" y="90" text-anchor="middle" font-size="9" fill="#334155">Configurar</text><text xml:space="preserve" x="185" y="102" text-anchor="middle" font-size="8" fill="#64748b">.config</text><line x1="210" y1="50" x2="230" y2="50" stroke="#0f172a" stroke-width="1.5" marker-end="url(#flow)"/><circle cx="255" cy="50" r="22" fill="#facc15" stroke="#a16207" stroke-width="2"/><text xml:space="preserve" x="255" y="55" text-anchor="middle" font-weight="700" fill="#0f172a">4</text><text xml:space="preserve" x="255" y="90" text-anchor="middle" font-size="9" fill="#334155">Compilar</text><text xml:space="preserve" x="255" y="102" text-anchor="middle" font-size="8" fill="#64748b">make + modules</text><line x1="280" y1="50" x2="300" y2="50" stroke="#0f172a" stroke-width="1.5" marker-end="url(#flow)"/><circle cx="335" cy="50" r="22" fill="#facc15" stroke="#a16207" stroke-width="2"/><text xml:space="preserve" x="335" y="55" text-anchor="middle" font-weight="700" fill="#0f172a">5</text><text xml:space="preserve" x="335" y="90" text-anchor="middle" font-size="9" fill="#334155">Reubicar</text><text xml:space="preserve" x="335" y="102" text-anchor="middle" font-size="8" fill="#64748b">/boot + initrd</text><line x1="360" y1="50" x2="380" y2="50" stroke="#0f172a" stroke-width="1.5" marker-end="url(#flow)"/><circle cx="415" cy="50" r="22" fill="#a3e635" stroke="#3f6212" stroke-width="2"/><text xml:space="preserve" x="415" y="55" text-anchor="middle" font-weight="700" fill="#0f172a">6</text><text xml:space="preserve" x="415" y="90" text-anchor="middle" font-size="9" fill="#334155">GRUB</text><text xml:space="preserve" x="415" y="102" text-anchor="middle" font-size="8" fill="#64748b">update-grub</text><line x1="440" y1="50" x2="460" y2="50" stroke="#0f172a" stroke-width="1.5" marker-end="url(#flow)"/><circle cx="495" cy="50" r="22" fill="#a3e635" stroke="#3f6212" stroke-width="2"/><text xml:space="preserve" x="495" y="55" text-anchor="middle" font-weight="700" fill="#0f172a">7</text><text xml:space="preserve" x="495" y="90" text-anchor="middle" font-size="9" fill="#334155">Reboot</text><text xml:space="preserve" x="495" y="102" text-anchor="middle" font-size="8" fill="#64748b">y probar</text><rect x="545" y="30" width="160" height="40" fill="#f0fdf4" stroke="#166534" stroke-dasharray="3,2"/><text xml:space="preserve" x="625" y="46" text-anchor="middle" font-size="9" fill="#166534" font-weight="700">Artefactos</text><text xml:space="preserve" x="625" y="60" text-anchor="middle" font-size="8" fill="#166534">/boot/vmlinuz · /boot/initrd</text></g></svg>
<div class="caption">Fig. 1.3 — Flujo canónico de compilación e instalación de un kernel Linux.</div>
</div>

1. **Obtener el código fuente** (típicamente desde `kernel.org`).
2. **Preparar el árbol de archivos** (descomprimir, aplicar parches).
3. **Configurar el kernel** (generar el `.config`).
4. **Construir el kernel e instalar los módulos** (`make && make modules_install`).
5. **Reubicar el kernel y crear el initrd/initramfs** (`make install` lo automatiza en muchas distros).
6. **Configurar el gestor de arranque** (GRUB / LILO) para que reconozca el nuevo kernel.
7. **Reiniciar y probar** el nuevo kernel.

Al hacer `make modules_install && make install`, los **módulos** se copian a `/lib/modules/<versión>/` y la **imagen del kernel** (`vmlinuz`/`bzImage`), el `System.map`, el `.config` y el initramfs se copian a `/boot/`. Después hay que actualizar GRUB.

**Herramientas** que se usan: `gcc` (compilador), `make` (ejecuta las directivas de los Makefiles), `binutils` (assembler/linker), `libc`, `ncurses` (solo si usás `menuconfig`) y `initrd-tools`. `make` compara la fecha de modificación de cada target con sus dependencias y solo recompila lo desactualizado; se le puede pasar `-j$(nproc)` para paralelizar.

**Configuración (`make config`)**: la variante `menuconfig` es la más usada (menús en terminal, no requiere entorno gráfico, ideal por SSH); `config` es texto secuencial y `xconfig` es GUI. En `menuconfig`, la barra espaciadora cicla entre `<*>` (built-in, va dentro de la imagen), `<M>` (módulo cargable) y `< >` (deshabilitado).

**Parches**: un parche es un archivo de `diff` con los cambios respecto a una versión base. Se aplica con el comando `patch`, típicamente por pipe: `xzcat ../patch-6.13.7.xz | patch -p1` (el `-p1` ignora el primer nivel `a/`/`b/`). Pueden ser incrementales (uno sobre otro) o no incrementales (sobre el mainline). `patch --dry-run` simula sin modificar.

### Por qué hay que reconfigurar el gestor de arranque

Una vez compilado e instalado el nuevo kernel, GRUB **no lo detecta automáticamente**. Hay que ejecutar `update-grub` (o equivalente) para **actualizar el menú de arranque** incorporando el nuevo kernel en `grub.cfg`. Es fundamental entender que esto **no reinstala el binario del gestor**: solo actualiza el archivo de configuración con las rutas de la nueva imagen y su initramfs. Por eso podés tener varios kernels compilados en la misma máquina y elegir cuál arrancar desde el menú de GRUB.

### initramfs / initrd

Es un **sistema de archivos temporal en RAM** que se monta durante el arranque, **antes** de montar el filesystem raíz real. Contiene los **módulos, drivers y programas mínimos** que el kernel necesita para poder llegar al root definitivo (drivers del controlador de disco, del filesystem del root, LVM/RAID/cifrado si aplica, un shell mínimo tipo `busybox`, `udev` y el init temporal). Una vez que el kernel monta el root real, el initramfs se desmonta y le cede el control al init definitivo.

**Puede no ser necesario** si todos esos drivers y filesystems críticos están compilados **built-in** (`<*>`) dentro del kernel: entonces el kernel monta el root directamente sin ayuda. En un desktop común esto no es habitual porque el kernel genérico de la distro trae casi todo como módulo para ser universal.

### Built-in vs módulo

Cuando configurás una funcionalidad en el `.config`, tenés tres opciones:

- **Built-in (`<*>`):** compilada dentro de la imagen del kernel. Acceso directo, sin carga en runtime, pero ocupa memoria aunque no la uses y para modificarla tenés que recompilar y reiniciar.
- **Módulo (`<M>`):** archivo `.ko` cargable en caliente. Solo consume memoria cuando se necesita, se puede actualizar sin reiniciar (`insmod`/`rmmod`) y facilita el desarrollo. Contra: corre en modo kernel igual que el resto — un bug puede colgar el sistema.
- **Deshabilitada (`< >`):** no está.

<div class="callout warning">
<div class="callout-title">⚠ Trampas típicas del parcial</div>

- "Linux es monolítico híbrido **porque** permite cargar/descargar funcionalidades vía módulos" → <span class="tag v">V</span>.
- "Linux es portable porque su código puede modificarse fácilmente para distintas arquitecturas" → <span class="tag v">V</span>. NO es porque el mismo binario corra en cualquier arquitectura.
- "Reconfigurar el gestor de arranque = reinstalar GRUB" → <span class="tag f">F</span>. Solo actualiza el menú.
- "El initramfs siempre es imprescindible" → <span class="tag f">F</span>: si todo lo necesario para montar el root está built-in, no hace falta.
- "El kernel de Linux es un SO en sentido estricto porque contiene todo lo necesario para gestionar HW y procesos" → <span class="tag f">F</span>: es el núcleo; el SO completo agrega utilidades, bibliotecas, shell, etc.
- "En un microkernel los drivers corren en modo kernel para mejorar rendimiento" → <span class="tag f">F</span>: corren en espacio de usuario. Correr todo en modo kernel es lo del monolítico.
- "Se puede tener más de un kernel compilado en la misma máquina" → <span class="tag v">V</span>: GRUB los lista, permite volver atrás si el nuevo no arranca.

</div>

---

## 2. Módulos, drivers, /dev, /proc y System Calls

### Módulos (LKM — Loadable Kernel Modules)

Un **módulo del kernel** es un fragmento de código (archivo `.ko`, *kernel object*) que puede **cargarse y descargarse en tiempo de ejecución sin recompilar ni reiniciar** el kernel. Se instala en `/lib/modules/<versión>/`, comparte el espacio de direcciones del kernel y **se ejecuta en modo supervisor** (privilegiado). Por eso, un bug en un módulo puede llevarse todo el sistema por delante (Kernel Panic en Linux / BSOD en Windows), no solo el proceso que lo invocó.

Todo módulo define una **función de inicialización** (`module_init`, se corre al cargar; devuelve 0 si todo salió bien) y una **función de cleanup** (`module_exit`, se corre al descargar). Los módulos pueden registrar entradas en `/proc` (no es exclusivo de los built-in) y también podés compilar la misma funcionalidad **built-in** dentro de la imagen — en ese caso ya no podés descargarla en caliente.

Los **comandos** clave son:

| Comando | Función |
|---|---|
| `insmod <archivo.ko>` | Carga UN módulo por ruta; no resuelve dependencias, falla si faltan símbolos. |
| `modprobe <nombre>` | Carga por nombre desde `/lib/modules`, resuelve automáticamente dependencias usando `modules.dep`. |
| `rmmod <nombre>` | Descarga el módulo (solo si su contador de uso está en 0). |
| `lsmod` | Lista módulos cargados (es una vista "linda" de `/proc/modules`). |
| `modinfo <nombre>` | Muestra metadatos del módulo (autor, licencia, descripción, params). |

El archivo **`/lib/modules/<versión>/modules.dep`** es el mapa de dependencias entre módulos. Lo genera automáticamente `depmod -a` y lo consulta `modprobe` para cargar en el orden correcto todo lo que un módulo necesita. `insmod`, en cambio, no consulta este archivo y falla si le faltan dependencias.

### Drivers

Un **driver** es código que actúa de **intermediario entre el kernel y un dispositivo de hardware**. Traduce operaciones genéricas (`open`, `read`, `write`, `close`, `ioctl`) a las instrucciones concretas del hardware particular. En Linux la **forma correcta** de implementar un driver es **como un módulo** (no como servicio, no como syscall, no como kthread) — aunque también podés compilarlo built-in. **Todo driver puede ser un módulo, pero no todo módulo es un driver**: los módulos son un mecanismo genérico de extensión, y los drivers son un uso particular de ese mecanismo.

Los drivers representan aproximadamente el **68.8% del código** del kernel Linux y tienen una tasa de errores unas **7× mayor** que el resto del kernel, lo cual —sumado a que corren en modo privilegiado— los convierte en la principal fuente de inestabilidad.

**Muy importante:** los drivers **no acceden a las funcionalidades del kernel a través de syscalls**. Corren en espacio de kernel, así que invocan **directamente la API interna del kernel** (`kmalloc`, `printk`, `register_chrdev`, `copy_to_user`, `copy_from_user`, etc.). Las syscalls son el mecanismo del espacio de usuario para pedir servicios al kernel.

La función **`register_chrdev(major, "nombre", &fops)`** registra un dispositivo de caracter en el kernel, asociando un **major number** con una **tabla de operaciones** (`struct file_operations`). Solo puede invocarse desde **espacio de kernel** (código del driver o módulo). La `struct file_operations` es una tabla que indica al kernel qué función del driver ejecutar ante cada operación: `read` → `memory_read`, `write` → `memory_write`, etc. Su inverso es `unregister_chrdev`.

### Major y minor number

Cada device file tiene dos números asociados:

- **Major number:** identifica el **driver** asociado a un **tipo** de dispositivo. Le dice al kernel a qué driver derivar la operación.
- **Minor number:** identifica el **dispositivo concreto o instancia** dentro de ese driver. Por ejemplo, `/dev/sda1` y `/dev/sda2` comparten major (mismo driver de disco SCSI) pero difieren en minor (particiones distintas).

### /dev — device files

`/dev` contiene los **device files**: archivos que representan dispositivos y son el **punto de acceso desde espacio de usuario** al driver. Encajan con la filosofía UNIX de "todo es un archivo": los abrís, leés, escribís y cerrás como cualquier archivo, y el kernel se encarga de redirigir esas operaciones al driver adecuado usando el major number.

Los device files **no contienen datos**; son "punteros" al driver. Se crean con `mknod [-m <mode>] <ruta> [b|c] <major> <minor>`. En un `ls -l` aparecen con un prefijo especial:

| Tipo | Marca | Acceso | Ejemplos |
|---|---|---|---|
| **Carácter** | `c` (`crw-...`) | Byte a byte, secuencial | teclado, mouse, tty, `/dev/null`, `/dev/random` |
| **Bloque** | `b` (`brw-...`) | Bloques de tamaño fijo, acceso aleatorio | discos: `/dev/sda`, `/dev/nvme0n1` |

Los **dispositivos de red** NO se representan como archivos en `/dev`. Se acceden a través de la API de sockets y se identifican por nombre de interfaz (`eth0`, `wlan0`). En `/dev` también podés encontrar enlaces simbólicos (`/dev/stdin` → `/proc/self/fd/0`) y sockets/pipes especiales.

### /proc — pseudo-filesystem

`/proc` es un **filesystem virtual** que expone las **estructuras internas del kernel** como archivos. **No ocupa espacio en disco**: la mayoría de sus archivos tienen tamaño 0 y su contenido se **genera al vuelo** al leerlo (se ejecuta una función del kernel que devuelve la información). Contiene datos de cada proceso (`/proc/<pid>/`), información del sistema y también configuración escribible.

Un módulo cargable (no solo los built-in) **puede registrar entradas en `/proc`**. Es un mito frecuente en el parcial pensar que solo los built-in pueden.

### System Calls

Una **system call** es la **API que expone el kernel al espacio de usuario** para pedirle servicios que requieren modo privilegiado (acceder a archivos, dispositivos, red, crear procesos, etc.). Es el puente controlado usuario → kernel. El mecanismo es una **interrupción de software (TRAP)**: `int 0x80` en x86 de 32 bits o la instrucción `syscall` en x86-64. Todas las syscalls usan la misma interrupción; se distinguen entre sí por el **número** cargado en el registro `EAX`/`RAX`, y admiten hasta 6 parámetros en registros. Al recibir el trap, el **dispatcher** busca el número en la **tabla de syscalls** (`syscall_64.tbl` en x86-64) y ejecuta el handler correspondiente.

<div class="diagram">
<svg viewBox="0 0 720 280" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><defs><marker id="sar" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#0f172a"/></marker></defs><text xml:space="preserve" x="360" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">Mecanismo de una system call (x86-64)</text><rect x="20" y="30" width="680" height="80" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="35" y="48" font-weight="700" fill="#1e3a8a">Modo usuario</text><rect x="45" y="58" width="130" height="42" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="110" y="76" text-anchor="middle" font-size="9" fill="#0f172a">programa (main)</text><text xml:space="preserve" x="110" y="90" text-anchor="middle" font-size="8" font-family="monospace" fill="#475569">printf("hola")</text><rect x="220" y="58" width="130" height="42" fill="#fde68a" stroke="#b45309"/><text xml:space="preserve" x="285" y="76" text-anchor="middle" font-size="9" fill="#78350f" font-weight="700">libc (wrapper)</text><text xml:space="preserve" x="285" y="90" text-anchor="middle" font-size="8" font-family="monospace" fill="#78350f">RAX=1, RDI=1, ...</text><rect x="395" y="58" width="120" height="42" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="455" y="76" text-anchor="middle" font-size="9" fill="#7f1d1d" font-weight="700">syscall (instr)</text><text xml:space="preserve" x="455" y="90" text-anchor="middle" font-size="8" fill="#7f1d1d">TRAP</text><line x1="175" y1="79" x2="220" y2="79" stroke="#0f172a" marker-end="url(#sar)"/><line x1="350" y1="79" x2="395" y2="79" stroke="#0f172a" marker-end="url(#sar)"/><line x1="20" y1="115" x2="700" y2="115" stroke="#f97316" stroke-width="2" stroke-dasharray="6,3"/><rect x="20" y="125" width="680" height="140" fill="#fef2f2" stroke="#991b1b"/><text xml:space="preserve" x="35" y="143" font-weight="700" fill="#7f1d1d">Modo kernel (Ring 0)</text><rect x="45" y="155" width="130" height="45" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="110" y="173" text-anchor="middle" font-size="9" fill="#7f1d1d" font-weight="700">dispatcher</text><text xml:space="preserve" x="110" y="188" text-anchor="middle" font-size="8" fill="#7f1d1d">lee RAX, indexa tabla</text><rect x="220" y="155" width="180" height="90" fill="#ffe4e6" stroke="#9f1239"/><text xml:space="preserve" x="310" y="172" text-anchor="middle" font-size="9" font-weight="700" fill="#881337">syscall_64.tbl</text><line x1="230" y1="180" x2="390" y2="180" stroke="#9f1239"/><text xml:space="preserve" x="230" y="196" font-size="8" font-family="monospace" fill="#881337">0 read sys_read</text><text xml:space="preserve" x="230" y="210" font-size="8" font-family="monospace" fill="#881337">1 write sys_write ←</text><text xml:space="preserve" x="230" y="224" font-size="8" font-family="monospace" fill="#881337">2 open sys_open</text><text xml:space="preserve" x="230" y="238" font-size="8" font-family="monospace" fill="#881337">...</text><rect x="445" y="155" width="130" height="45" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="510" y="173" text-anchor="middle" font-size="9" fill="#7f1d1d" font-weight="700">sys_write()</text><text xml:space="preserve" x="510" y="188" text-anchor="middle" font-size="8" fill="#7f1d1d">handler en kernel</text><rect x="600" y="155" width="90" height="45" fill="#fbbf24" stroke="#78350f"/><text xml:space="preserve" x="645" y="173" text-anchor="middle" font-size="9" fill="#78350f" font-weight="700">driver TTY</text><text xml:space="preserve" x="645" y="188" text-anchor="middle" font-size="8" fill="#78350f">file_operations</text><line x1="175" y1="177" x2="220" y2="177" stroke="#0f172a" marker-end="url(#sar)"/><line x1="400" y1="177" x2="445" y2="177" stroke="#0f172a" marker-end="url(#sar)"/><line x1="575" y1="177" x2="600" y2="177" stroke="#0f172a" marker-end="url(#sar)"/><text xml:space="preserve" x="360" y="255" text-anchor="middle" font-size="8" fill="#7c2d12" font-style="italic">Cada syscall se identifica por un número único (registro RAX) y máx. 6 parámetros. Todas usan la misma instrucción TRAP.</text></svg>
<div class="caption">Fig. 2.1 — Ciclo de una syscall: programa → wrapper de libc → instrucción <code>syscall</code> (trap) → dispatcher del kernel → tabla → handler → (opcionalmente) driver.</div>
</div>

Puntos que suelen confundir:

- Las syscalls **se definen en el código del kernel**, no en `libc` ni en módulos.
- Se **adjuntan estáticamente en tiempo de compilación** del kernel.
- Para **agregar una nueva** hay que (a) declararla en la tabla (`syscall_32.tbl` / `syscall_64.tbl`) con un **número único**, (b) implementar el handler en espacio de kernel y (c) recompilar. No alcanza con reiniciar.
- **`libc` es una biblioteca de usuario** que provee wrappers: acomoda los argumentos, carga el número de syscall y dispara el trap. NO implementa la syscall en sí. La función `syscall()` de la propia libc permite invocar una syscall por número **sin** wrapper específico.
- **POSIX** es un estándar de interfaz que busca la portabilidad de aplicaciones entre Unix; libc respeta POSIX. No toda función de libc es una syscall (muchas son puramente de biblioteca), y técnicamente se puede invocar una syscall sin libc (assembler directo).
- Para monitorear qué syscalls invoca un proceso en runtime se usa **`strace`**; para mapear nombre ↔ número estáticamente, **`ausyscall`**.
- Manejo cuidadoso de punteros de usuario: hay que validar con `get_user`/`put_user`/`copy_from_user`/`copy_to_user`. Un puntero mal usado puede provocar Kernel Panic o fugar memoria del kernel.

Todo proceso arranca con **tres file descriptors abiertos**: `0` = stdin (entrada), `1` = stdout (salida), `2` = stderr (errores). Por eso un `printf` termina en un `write(1, ...)`.

<div class="callout warning">
<div class="callout-title">⚠ Trampas típicas del parcial</div>

- "`libc` es el componente del kernel donde se definen las syscalls" → <span class="tag f">F</span>. `libc` es wrapper de usuario.
- "Las syscalls se implementan como módulos del kernel administrables con `insmod`/`rmmod`" → <span class="tag f">F</span>. Son parte del kernel base, estáticas.
- "Las syscalls se ejecutan en modo privilegiado y se identifican por un número" → <span class="tag v">V</span>.
- "Cada driver implementa una system call" → <span class="tag f">F</span>. Implementa `file_operations`, no una syscall.
- "Los drivers acceden a las funcionalidades del kernel a través de syscalls" → <span class="tag f">F</span>. Acceso directo por API interna.
- "`register_chrdev` puede invocarse desde espacio de usuario" → <span class="tag f">F</span>. Solo espacio de kernel.
- "Los módulos se ejecutan en espacio de usuario" → <span class="tag f">F</span>. Modo supervisor.
- "Un módulo permite implementar syscalls dinámicas" → <span class="tag f">F</span>.
- "Solo los módulos built-in pueden crear entradas en /proc" → <span class="tag f">F</span>. También los cargables.
- Sobre el output `brw-rw---- 1 root root 240, 0 weird`: la `b` inicial indica dispositivo de bloques y **240** es el **major** (identifica al driver, NO son 240 bytes de tamaño). Escribir con `echo "hola" > weird` no incrementa el tamaño porque no es un archivo regular, es un punto de acceso al driver.

</div>
---

## 3. Threads (hilos)

### Proceso vs hilo

Un **hilo** (o *lightweight process*) es la **unidad básica de ejecución** dentro de un proceso. En los SO modernos, el hilo es la unidad de utilización de CPU / planificación, mientras que el **proceso** es la unidad de **propiedad de recursos**: un proceso es una colección de uno o más hilos que comparten el mismo espacio de direcciones y los mismos recursos.

Los hilos de un mismo proceso **comparten**:

- El espacio de direcciones completo: **código (TEXT), datos, heap**.
- Los recursos del proceso: **archivos abiertos, señales, sockets**.
- El **PID** del proceso.
- El único **PCB** (Process Control Block).

Y cada hilo tiene lo suyo:

- **Stack propio**.
- **Registros y Program Counter (PC)** propios.
- **Estado de ejecución** y contexto del procesador.
- Su propio **TCB** (Thread Control Block) con un **TID** único.

Por eso los hilos son "más baratos": crear/destruir un hilo solo requiere un TCB + stack + registros, y el cambio de contexto entre hilos del mismo proceso no cambia el espacio de direcciones (solo cambia registros y PC). En cambio, un proceso nuevo obliga al SO a crear un espacio de direcciones aislado, un PCB, etc. La contrapartida es que como los hilos comparten memoria, la **protección entre hilos es responsabilidad del programador** (mutex, semáforos, etc.), no del SO.

<div class="diagram">
<svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><g transform="translate(0,0)"><text xml:space="preserve" x="140" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">Proceso con 1 hilo</text><rect x="20" y="30" width="240" height="200" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="30" y="46" fill="#64748b" font-size="8">PID único · PCB único</text><rect x="35" y="55" width="210" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="140" y="72" text-anchor="middle" fill="#1e3a8a" font-size="9">TEXT (código)</text><rect x="35" y="84" width="210" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="140" y="101" text-anchor="middle" fill="#1e3a8a" font-size="9">DATA (datos globales)</text><rect x="35" y="113" width="210" height="42" fill="#e0e7ff" stroke="#4338ca"/><text xml:space="preserve" x="140" y="130" text-anchor="middle" fill="#3730a3" font-size="9">HEAP</text><text xml:space="preserve" x="140" y="145" text-anchor="middle" fill="#4338ca" font-size="8" font-style="italic">memoria dinámica</text><rect x="35" y="160" width="210" height="42" fill="#fef3c7" stroke="#b45309"/><text xml:space="preserve" x="140" y="177" text-anchor="middle" fill="#78350f" font-size="9">STACK</text><text xml:space="preserve" x="140" y="192" text-anchor="middle" fill="#78350f" font-size="8" font-style="italic">variables locales, retornos</text><rect x="35" y="207" width="210" height="18" fill="#f0abfc" stroke="#a21caf"/><text xml:space="preserve" x="140" y="220" text-anchor="middle" fill="#701a75" font-size="9">Recursos: FDs, señales, sockets</text></g><g transform="translate(320,0)"><text xml:space="preserve" x="140" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">Proceso con 3 hilos</text><rect x="20" y="30" width="280" height="200" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="30" y="46" fill="#64748b" font-size="8">PID único · PCB único · TIDs: T1, T2, T3</text><rect x="35" y="55" width="250" height="20" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="160" y="70" text-anchor="middle" fill="#1e3a8a" font-size="9">TEXT (compartido)</text><rect x="35" y="78" width="250" height="20" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="160" y="93" text-anchor="middle" fill="#1e3a8a" font-size="9">DATA (compartido)</text><rect x="35" y="101" width="250" height="30" fill="#e0e7ff" stroke="#4338ca"/><text xml:space="preserve" x="160" y="121" text-anchor="middle" fill="#3730a3" font-size="9">HEAP (compartido)</text><text xml:space="preserve" x="35" y="145" fill="#78350f" font-size="8">Stacks propios (uno por hilo):</text><rect x="35" y="150" width="78" height="55" fill="#fef3c7" stroke="#b45309"/><text xml:space="preserve" x="74" y="167" text-anchor="middle" fill="#78350f" font-size="9" font-weight="700">Stack T1</text><text xml:space="preserve" x="74" y="182" text-anchor="middle" fill="#78350f" font-size="8">registros</text><text xml:space="preserve" x="74" y="194" text-anchor="middle" fill="#78350f" font-size="8">PC · TCB</text><rect x="121" y="150" width="78" height="55" fill="#fef3c7" stroke="#b45309"/><text xml:space="preserve" x="160" y="167" text-anchor="middle" fill="#78350f" font-size="9" font-weight="700">Stack T2</text><text xml:space="preserve" x="160" y="182" text-anchor="middle" fill="#78350f" font-size="8">registros</text><text xml:space="preserve" x="160" y="194" text-anchor="middle" fill="#78350f" font-size="8">PC · TCB</text><rect x="207" y="150" width="78" height="55" fill="#fef3c7" stroke="#b45309"/><text xml:space="preserve" x="246" y="167" text-anchor="middle" fill="#78350f" font-size="9" font-weight="700">Stack T3</text><text xml:space="preserve" x="246" y="182" text-anchor="middle" fill="#78350f" font-size="8">registros</text><text xml:space="preserve" x="246" y="194" text-anchor="middle" fill="#78350f" font-size="8">PC · TCB</text><rect x="35" y="210" width="250" height="15" fill="#f0abfc" stroke="#a21caf"/><text xml:space="preserve" x="160" y="221" text-anchor="middle" fill="#701a75" font-size="9">Recursos: FDs, señales, sockets (compartidos)</text></g></svg>
<div class="caption">Fig. 3.1 — Qué comparten y qué es propio. TEXT/DATA/HEAP y recursos son del proceso; stack, registros, PC y TCB son de cada hilo.</div>
</div>

### Concurrencia vs paralelismo

- **Concurrencia:** múltiples tareas **progresan intercaladas** en el tiempo. Puede darse con un único core (multiplexación temporal): da la ilusión de simultaneidad.
- **Paralelismo:** múltiples tareas se ejecutan **realmente al mismo tiempo** en **múltiples cores**.

Todo paralelismo implica concurrencia, pero no toda concurrencia es paralelismo. Un programa concurrente puede correr sin paralelismo en un uniprocesador.

### ULT vs KLT

Hay dos tipos de hilos según quién los gestiona:

- **ULT (User Level Threads):** la **biblioteca de hilos en espacio de usuario** los crea, gestiona y planifica (por ejemplo GNU Pth, versiones de Pthreads sin soporte de kernel). El **kernel no sabe que existen**: ve un único proceso con un único flujo de ejecución.
- **KLT (Kernel Level Threads):** los **conoce y planifica el kernel**, hilo por hilo. En Linux se crean con la syscall `clone()`/`clone3()` con los flags `CLONE_VM` + `CLONE_THREAD`.

La comparación clave:

| Criterio | **ULT** | **KLT** |
|---|---|---|
| ¿Quién planifica? | La biblioteca (espacio de usuario) | El kernel |
| Visibilidad al kernel | Invisible: ve 1 solo proceso | Cada hilo es entidad planificable |
| Paralelismo en multicore | **NO** (no puede repartirlos en núcleos) | **SÍ** (paralelismo real) |
| Costo de cambio de contexto | **Barato** (sin pasar a modo kernel) | **Caro** (cada operación es syscall) |
| Bloqueo por syscall | Bloquea **TODO el proceso** | Solo bloquea al hilo llamador |
| Portabilidad | Alta (funcionan sin soporte del kernel) | Dependen del soporte del SO |

El trade-off es claro: los **KLT** ganan en paralelismo real y en robustez ante bloqueos (si un hilo hace una syscall bloqueante, solo se bloquea él, los demás siguen), pero pagan **overhead** por operar en modo kernel. Los **ULT** son rápidos y portables (corren incluso sin soporte del SO) pero **no aprovechan múltiples núcleos** y un bloqueo de un hilo bloquea a todos.

Regla práctica de rendimiento: **KLT / procesos** son mejores para tareas **CPU-bound** (necesitan paralelismo real). **ULT** brillan en **IO-bound**: las esperas se solapan haciendo yields dentro de la biblioteca, sin overhead de kernel.

### Modelos de mapeo ULT ↔ KLT

Los ULT no pueden ejecutarse directamente: necesitan mapearse sobre un KLT para obtener CPU. Hay tres modelos:

- **N:1 (Muchos a Uno):** varios ULT sobre un solo KLT. Sin paralelismo real; si un hilo se bloquea, todos se bloquean. Típico de bibliotecas de threads sin soporte del kernel.
- **1:1 (Uno a Uno):** cada ULT tiene su KLT propio. Es el modelo de **Linux, Windows NT y Solaris moderno**. Paralelismo máximo pero costo alto (1 KLT por hilo).
- **M:N (Muchos a Muchos):** M ULT sobre N KLT, con N ajustable. Balance entre paralelismo y costo (Solaris con LWP, TRIX).

<div class="diagram">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><g transform="translate(0,0)"><text xml:space="preserve" x="110" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">N:1 (Muchos a Uno)</text><text xml:space="preserve" x="110" y="34" text-anchor="middle" font-size="8" fill="#64748b">sin paralelismo real</text><circle cx="45" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="45" y="74" text-anchor="middle" font-size="9">U1</text><circle cx="90" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="90" y="74" text-anchor="middle" font-size="9">U2</text><circle cx="135" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="135" y="74" text-anchor="middle" font-size="9">U3</text><circle cx="180" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="180" y="74" text-anchor="middle" font-size="9">U4</text><rect x="30" y="100" width="165" height="22" fill="#fde68a" stroke="#b45309"/><text xml:space="preserve" x="112" y="115" text-anchor="middle" font-size="9" fill="#78350f">biblioteca de hilos</text><line x1="45" y1="84" x2="112" y2="100" stroke="#0f172a"/><line x1="90" y1="84" x2="112" y2="100" stroke="#0f172a"/><line x1="135" y1="84" x2="112" y2="100" stroke="#0f172a"/><line x1="180" y1="84" x2="112" y2="100" stroke="#0f172a"/><circle cx="112" cy="150" r="16" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="112" y="154" text-anchor="middle" font-size="9">K</text><line x1="112" y1="122" x2="112" y2="134" stroke="#0f172a"/><rect x="20" y="190" width="185" height="26" fill="#e2e8f0" stroke="#334155"/><text xml:space="preserve" x="112" y="207" text-anchor="middle" font-size="9" fill="#0f172a">Kernel + CPUs</text><line x1="112" y1="166" x2="112" y2="190" stroke="#0f172a"/><text xml:space="preserve" x="112" y="236" text-anchor="middle" font-size="8" fill="#475569">1 solo hilo corre a la vez</text></g><g transform="translate(240,0)"><text xml:space="preserve" x="110" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">1:1 (Uno a Uno)</text><text xml:space="preserve" x="110" y="34" text-anchor="middle" font-size="8" fill="#64748b">Linux, WinNT — paralelismo real</text><circle cx="45" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="45" y="74" text-anchor="middle" font-size="9">U1</text><circle cx="90" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="90" y="74" text-anchor="middle" font-size="9">U2</text><circle cx="135" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="135" y="74" text-anchor="middle" font-size="9">U3</text><circle cx="180" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="180" y="74" text-anchor="middle" font-size="9">U4</text><line x1="45" y1="84" x2="45" y2="134" stroke="#0f172a"/><line x1="90" y1="84" x2="90" y2="134" stroke="#0f172a"/><line x1="135" y1="84" x2="135" y2="134" stroke="#0f172a"/><line x1="180" y1="84" x2="180" y2="134" stroke="#0f172a"/><circle cx="45" cy="150" r="14" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="45" y="154" text-anchor="middle" font-size="9">K1</text><circle cx="90" cy="150" r="14" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="90" y="154" text-anchor="middle" font-size="9">K2</text><circle cx="135" cy="150" r="14" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="135" y="154" text-anchor="middle" font-size="9">K3</text><circle cx="180" cy="150" r="14" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="180" y="154" text-anchor="middle" font-size="9">K4</text><rect x="20" y="190" width="185" height="26" fill="#e2e8f0" stroke="#334155"/><text xml:space="preserve" x="112" y="207" text-anchor="middle" font-size="9" fill="#0f172a">Kernel + CPUs</text><line x1="45" y1="164" x2="45" y2="190" stroke="#0f172a"/><line x1="90" y1="164" x2="90" y2="190" stroke="#0f172a"/><line x1="135" y1="164" x2="135" y2="190" stroke="#0f172a"/><line x1="180" y1="164" x2="180" y2="190" stroke="#0f172a"/><text xml:space="preserve" x="112" y="236" text-anchor="middle" font-size="8" fill="#475569">1 KLT por hilo — costo alto</text></g><g transform="translate(480,0)"><text xml:space="preserve" x="110" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">M:N (Muchos a Muchos)</text><text xml:space="preserve" x="110" y="34" text-anchor="middle" font-size="8" fill="#64748b">balance (Solaris LWP)</text><circle cx="45" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="45" y="74" text-anchor="middle" font-size="9">U1</text><circle cx="90" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="90" y="74" text-anchor="middle" font-size="9">U2</text><circle cx="135" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="135" y="74" text-anchor="middle" font-size="9">U3</text><circle cx="180" cy="70" r="14" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="180" y="74" text-anchor="middle" font-size="9">U4</text><line x1="45" y1="84" x2="70" y2="134" stroke="#0f172a"/><line x1="90" y1="84" x2="70" y2="134" stroke="#0f172a"/><line x1="135" y1="84" x2="155" y2="134" stroke="#0f172a"/><line x1="180" y1="84" x2="155" y2="134" stroke="#0f172a"/><circle cx="70" cy="150" r="14" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="70" y="154" text-anchor="middle" font-size="9">K1</text><circle cx="155" cy="150" r="14" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="155" y="154" text-anchor="middle" font-size="9">K2</text><rect x="20" y="190" width="185" height="26" fill="#e2e8f0" stroke="#334155"/><text xml:space="preserve" x="112" y="207" text-anchor="middle" font-size="9" fill="#0f172a">Kernel + CPUs</text><line x1="70" y1="164" x2="70" y2="190" stroke="#0f172a"/><line x1="155" y1="164" x2="155" y2="190" stroke="#0f172a"/><text xml:space="preserve" x="112" y="236" text-anchor="middle" font-size="8" fill="#475569">M ULT sobre N KLT</text></g></svg>
<div class="caption">Fig. 3.2 — Modelos de mapeo ULT↔KLT. Solo 1:1 y M:N logran paralelismo real en varios núcleos.</div>
</div>

### fork() y exec()

- **`fork()`** crea un **proceso hijo**, copia (casi) idéntica del padre. Usa **Copy-On-Write**: padre e hijo comparten las páginas en solo lectura y se copian recién cuando alguna de las partes escribe. Es **`fork()` el que asigna el nuevo PID** al hijo.
- **`exec()`** **reemplaza la imagen del proceso** por otro programa. NO crea proceso ni cambia el PID.
- El patrón clásico de la shell para lanzar un comando externo es **`fork()` + `exec()`**: el padre crea un hijo, y el hijo reemplaza su código por el del programa a ejecutar.

**`fork()` sin `exec()` — cae mucho en parcial.** El hijo es una copia (casi) idéntica del padre:

- Ejecuta el **mismo programa/código, mismos datos** que el padre (no se reemplaza).
- **Hereda los descriptores de archivo abiertos**, señales, cwd, etc.
- Tiene **PID propio** (distinto del padre) y su **PPID** apunta al padre.
- Se diferencian por el **valor de retorno de `fork()`**: `0` en el hijo, PID del hijo en el padre. Cada uno usa esa diferencia para tomar un camino distinto en el código.

En Linux, tanto `fork()` como `pthread_create()` terminan invocando la syscall **`clone()`**. Lo que cambia son los flags: `fork()` da espacio aislado (COW); `pthread_create()` pasa `CLONE_VM` + `CLONE_THREAD` para compartir espacio de direcciones y recursos con el padre. Por eso `pthread_create` sí aparece en `strace` como un `clone3`, pero **crear ULT no lo hace**: la biblioteca los gestiona internamente sin llamar al kernel.

### Detalle: GIL en Python

En CPython el **Global Interpreter Lock (GIL)** permite que solo un hilo ejecute bytecode a la vez, incluso si hay varios cores disponibles. Por eso los hilos no logran paralelismo real en tareas CPU-bound; la solución típica es usar **procesos** (`multiprocessing`), porque cada proceso tiene su propio intérprete y su propio GIL. En tareas IO-bound el GIL se libera durante la espera, así que los hilos sí ayudan.

<div class="callout warning">
<div class="callout-title">⚠ Trampas típicas del parcial</div>

- "¿Quién planifica los ULT?" → **La biblioteca en espacio de usuario**. "¿Y los KLT?" → **El kernel**.
- "Los ULT en modelo M:1 pueden aprovechar directamente múltiples procesadores físicos" → <span class="tag f">F</span>. Sin mecanismo adicional (KLT), no.
- "Si un proceso crea N ULT, con `strace` se ven N `clone3`" → <span class="tag f">F</span>. Los ULT no invocan al kernel; `clone3` aparece con procesos y con KLT (pthread_create), no con ULT.
- "`fork()` sin `exec()`" → hijo es copia del padre, mismo programa, distinto PID, hereda descriptores.
- "¿Quién asigna el PID nuevo?" → **`fork()`**, no `exec()` (`exec()` conserva el PID).
- Hilo principal: `gettid() == getpid()`. En ULT (GNU Pth) todos comparten el mismo `gettid()` porque el kernel ve una sola entidad; solo `pth_self()` los distingue.
- "Un hilo es la unidad básica de utilización de CPU en los SO modernos" → <span class="tag v">V</span>.

</div>
---

## 4. Virtualización

### Qué es virtualizar y para qué

Virtualizar es una técnica de **abstracción de recursos**: una capa de software desacopla el hardware físico del software que corre encima, oculta detalles y permite que **una única máquina haga el trabajo de varias**, compartiendo el hardware entre múltiples entornos aislados.

Los motivos para virtualizar son variados: **consolidación** (servidores subutilizados que pasan de ~10-18% de uso a ~70%), **aislamiento** (probar apps inseguras o correr software legacy sin contaminar el sistema principal), **aprovechamiento del HW** (varios SO distintos en simultáneo, ahorro energético) y **flexibilidad** (las VMs se encapsulan en archivos, así que backup, copia y migración entre servidores son triviales).

Se distinguen dos actores: el **host** (SO anfitrión + capa de virtualización) y el **guest** (lo que se está simulando: un SO completo).

### Hypervisor / VMM

El **hypervisor** o **VMM (Virtual Machine Monitor)** es el programa que implementa las máquinas virtuales, gestiona el reparto de recursos y planifica la ejecución de los guests. Corre en modo supervisor y los guests corren en modo usuario. Cuando el guest intenta ejecutar una instrucción privilegiada, se genera un **trap al VMM**, que la interpreta o emula.

Hay dos tipos:

| | **Tipo 1 (bare-metal)** | **Tipo 2 (hosted)** |
|---|---|---|
| Dónde corre | **Directo sobre el hardware** | Como aplicación **sobre un SO anfitrión** |
| ¿SO anfitrión? | **No** (el hypervisor es "el SO base") | **Sí** |
| Rendimiento | Mayor | Menor (capa extra) |
| Uso típico | Servidores, data center | Escritorio, pruebas |
| Ejemplos | **ESXi, Xen, Hyper-V, KVM** | **VirtualBox, VMware Workstation** |

La diferencia clave es que el **tipo 1 no necesita SO anfitrión** (corre sobre el bare-metal directamente); el **tipo 2 sí requiere un host** que gestiona los drivers reales del hardware.

<div class="diagram">
<svg viewBox="0 0 720 260" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="9"><g transform="translate(0,0)"><text xml:space="preserve" x="115" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">Hypervisor Tipo 1</text><text xml:space="preserve" x="115" y="30" text-anchor="middle" font-size="8" fill="#64748b">bare-metal (ESXi, Xen, KVM)</text><rect x="10" y="40" width="70" height="55" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="45" y="58" text-anchor="middle" font-size="8" fill="#1e3a8a">App</text><line x1="10" y1="65" x2="80" y2="65" stroke="#1e40af"/><text xml:space="preserve" x="45" y="82" text-anchor="middle" font-size="8" fill="#1e3a8a">SO guest</text><rect x="85" y="40" width="70" height="55" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="120" y="58" text-anchor="middle" font-size="8" fill="#1e3a8a">App</text><line x1="85" y1="65" x2="155" y2="65" stroke="#1e40af"/><text xml:space="preserve" x="120" y="82" text-anchor="middle" font-size="8" fill="#1e3a8a">SO guest</text><rect x="160" y="40" width="70" height="55" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="195" y="58" text-anchor="middle" font-size="8" fill="#1e3a8a">App</text><line x1="160" y1="65" x2="230" y2="65" stroke="#1e40af"/><text xml:space="preserve" x="195" y="82" text-anchor="middle" font-size="8" fill="#1e3a8a">SO guest</text><rect x="10" y="100" width="220" height="30" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="120" y="119" text-anchor="middle" font-size="10" font-weight="700" fill="#7f1d1d">Hypervisor (VMM)</text><rect x="10" y="135" width="220" height="30" fill="#e5e7eb" stroke="#374151"/><text xml:space="preserve" x="120" y="154" text-anchor="middle" font-size="10" font-weight="700" fill="#111827">HARDWARE</text><text xml:space="preserve" x="120" y="200" text-anchor="middle" font-size="8" fill="#475569">no hay SO anfitrión</text><text xml:space="preserve" x="120" y="215" text-anchor="middle" font-size="8" fill="#475569">mejor rendimiento</text></g><g transform="translate(250,0)"><text xml:space="preserve" x="115" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">Hypervisor Tipo 2</text><text xml:space="preserve" x="115" y="30" text-anchor="middle" font-size="8" fill="#64748b">hosted (VirtualBox, VMware)</text><rect x="10" y="40" width="70" height="55" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="45" y="58" text-anchor="middle" font-size="8" fill="#1e3a8a">App</text><line x1="10" y1="65" x2="80" y2="65" stroke="#1e40af"/><text xml:space="preserve" x="45" y="82" text-anchor="middle" font-size="8" fill="#1e3a8a">SO guest</text><rect x="85" y="40" width="70" height="55" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="120" y="58" text-anchor="middle" font-size="8" fill="#1e3a8a">App</text><line x1="85" y1="65" x2="155" y2="65" stroke="#1e40af"/><text xml:space="preserve" x="120" y="82" text-anchor="middle" font-size="8" fill="#1e3a8a">SO guest</text><rect x="160" y="40" width="70" height="55" fill="#fef3c7" stroke="#b45309"/><text xml:space="preserve" x="195" y="70" text-anchor="middle" font-size="8" fill="#78350f">Otras apps</text><text xml:space="preserve" x="195" y="82" text-anchor="middle" font-size="8" fill="#78350f">del host</text><rect x="10" y="100" width="145" height="30" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="82" y="119" text-anchor="middle" font-size="10" font-weight="700" fill="#7f1d1d">Hypervisor</text><rect x="10" y="135" width="220" height="30" fill="#fde68a" stroke="#b45309"/><text xml:space="preserve" x="120" y="154" text-anchor="middle" font-size="10" font-weight="700" fill="#78350f">SO anfitrión (host)</text><rect x="10" y="170" width="220" height="26" fill="#e5e7eb" stroke="#374151"/><text xml:space="preserve" x="120" y="187" text-anchor="middle" font-size="10" font-weight="700" fill="#111827">HARDWARE</text><text xml:space="preserve" x="120" y="215" text-anchor="middle" font-size="8" fill="#475569">host maneja drivers reales</text></g><g transform="translate(490,0)"><text xml:space="preserve" x="115" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">Containers (Docker/LXC)</text><text xml:space="preserve" x="115" y="30" text-anchor="middle" font-size="8" fill="#64748b">virtualización a nivel SO</text><rect x="10" y="40" width="65" height="50" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="42" y="60" text-anchor="middle" font-size="8" fill="#064e3b">App</text><text xml:space="preserve" x="42" y="74" text-anchor="middle" font-size="7" fill="#064e3b">+ libs</text><rect x="80" y="40" width="65" height="50" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="112" y="60" text-anchor="middle" font-size="8" fill="#064e3b">App</text><text xml:space="preserve" x="112" y="74" text-anchor="middle" font-size="7" fill="#064e3b">+ libs</text><rect x="150" y="40" width="65" height="50" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="182" y="60" text-anchor="middle" font-size="8" fill="#064e3b">App</text><text xml:space="preserve" x="182" y="74" text-anchor="middle" font-size="7" fill="#064e3b">+ libs</text><text xml:space="preserve" x="42" y="105" text-anchor="middle" font-size="7" fill="#065f46" font-style="italic">container</text><text xml:space="preserve" x="112" y="105" text-anchor="middle" font-size="7" fill="#065f46" font-style="italic">container</text><text xml:space="preserve" x="182" y="105" text-anchor="middle" font-size="7" fill="#065f46" font-style="italic">container</text><rect x="10" y="115" width="215" height="24" fill="#e0e7ff" stroke="#4338ca"/><text xml:space="preserve" x="117" y="131" text-anchor="middle" font-size="9" fill="#3730a3">Docker daemon · runc</text><rect x="10" y="142" width="215" height="30" fill="#fecaca" stroke="#991b1b"/><text xml:space="preserve" x="117" y="161" text-anchor="middle" font-size="10" font-weight="700" fill="#7f1d1d">KERNEL (host)</text><text xml:space="preserve" x="117" y="171" text-anchor="middle" font-size="7" fill="#7f1d1d">namespaces + cgroups + chroot</text><rect x="10" y="176" width="215" height="22" fill="#e5e7eb" stroke="#374151"/><text xml:space="preserve" x="117" y="191" text-anchor="middle" font-size="9" font-weight="700" fill="#111827">HARDWARE</text><text xml:space="preserve" x="117" y="215" text-anchor="middle" font-size="8" fill="#475569">mismo kernel · sin hypervisor</text></g></svg>
<div class="caption">Fig. 4.1 — Tipo 1 vs Tipo 2 vs Containers. Los containers comparten el kernel del host y no usan hypervisor.</div>
</div>

**Cuidado:** el SO guest **nunca tiene acceso directo y completo al hardware real**. El VMM siempre intermedia: crea hardware virtual, controla los recursos e intercepta/emula las instrucciones privilegiadas. El guest ve hardware virtual, no el real.

### Técnicas de virtualización

- **Full virtualization con Binary Translation:** el hypervisor **escanea y reescribe en tiempo de ejecución** las instrucciones sensibles del guest (aquellas que en x86 no generaban trap correctamente), reemplazándolas por llamadas seguras al VMM. El **SO guest no se modifica** — no sabe que está virtualizado. Costo alto porque hay que emular todo el HW.
- **Paravirtualización:** el **kernel del SO guest SE MODIFICA** para reemplazar las instrucciones privilegiadas por **hypercalls** (llamadas a la API del hypervisor). **Mejor rendimiento**, pero solo sirve para SO cuyo código puede modificarse. **Windows cerrado NO se puede paravirtualizar.**
- **Virtualización asistida por hardware:** las extensiones **Intel VT-x / AMD-V** en la CPU dan soporte directo a la virtualización (require flag habilitado en BIOS para VMs). Reduce el overhead del binary translation.
- **Emulación:** simula por software un hardware o arquitectura completo, y **puede correr una arquitectura distinta** de la del host (por ejemplo ARM sobre x86). Es la más lenta (ej. QEMU sin aceleración).

Resumen comparativo:

| Técnica | ¿Modifica el guest? | Rendimiento | Nota |
|---|---|---|---|
| Binary translation | **No** | Medio | Reescribe instr. privilegiadas en runtime |
| Paravirtualización | **Sí (kernel modificado)** | Alto | Usa hypercalls; no sirve para SO cerrados |
| Emulación | No | Bajo | Puede simular otra arquitectura |

### Contenedores (virtualización a nivel SO)

**LXC / Docker** son "virtualización a nivel SO":

- **NO usan hypervisor.**
- **Usan el mismo kernel que el host** (no instalan su propio kernel) → mucho más livianos que una VM.
- El aislamiento del espacio de usuario lo dan **namespaces** (vista aislada de recursos) y **cgroups** (límites de consumo).
- **No pueden correr un SO con kernel distinto** al del host (no virtualizan Windows sobre Linux).
- A diferencia de las VMs, los **procesos del container aparecen como procesos en el host** (con distinto PID gracias al PID namespace).

<div class="callout warning">
<div class="callout-title">⚠ Trampas típicas del parcial</div>

- "En cuál técnica se debe modificar el kernel del guest" → **Paravirtualización**.
- "En paravirtualización el SO guest NO se modifica" → <span class="tag f">F</span>.
- "La paravirtualización permite virtualizar Windows sobre Linux" → <span class="tag f">F</span>.
- "Los containers usan el mismo kernel que el host" → <span class="tag v">V</span>. "Instalan su propio kernel" → <span class="tag f">F</span>.
- "Los containers necesitan habilitar el flag de virtualización en BIOS" → <span class="tag f">F</span>.
- "Docker/containers necesitan un hypervisor tipo 2" → <span class="tag f">F</span>.
- "El SO guest tiene acceso directo y completo al HW real" → <span class="tag f">F</span>: siempre intermedia el VMM.
- "En hypervisor tipo 2 el SO host se ejecuta directamente sobre el hardware y gestiona los drivers reales" → <span class="tag v">V</span>.
- "En VMs los PIDs del guest aparecen como procesos en el anfitrión" → <span class="tag f">F</span> (esto sí pasa con containers).

</div>
---

## 5. chroot, cgroups y namespaces

Estos son los **tres mecanismos del kernel de Linux** que, combinados, hacen posibles los contenedores. Individualmente:

- **`chroot`** aísla el **filesystem** (raíz aparente).
- **`namespaces`** aíslan la **vista** que un proceso tiene de recursos globales.
- **`cgroups`** **limitan y controlan** el consumo de recursos.

### chroot (Service Isolation)

Data de UNIX v7 (1979). **Cambia el directorio raíz (`/`) aparente** de un proceso y de todos sus hijos. Aislamiento básico del filesystem: el proceso no puede ver ni acceder a archivos o comandos **fuera** de ese nuevo directorio raíz. Al entorno resultante se lo llama **"jail chroot"**. Docker lo usa para fijar el **union-FS** como raíz del contenedor.

Sintaxis: `chroot /new-root-dir comando`

Por sí solo, `chroot` **no aísla procesos, red, PIDs, ni usuarios**: para eso se necesitan namespaces.

### cgroups (Control Groups)

Es una característica del kernel que organiza procesos en **grupos jerárquicos** con el fin de **limitar, priorizar, contabilizar y controlar** su uso de recursos (CPU, memoria, E/S, red, etc.). Son **cuatro funcionalidades**, no solo limitación:

- **Limitación (resource limiting):** un grupo no puede exceder el uso de un recurso.
- **Priorización:** un grupo obtiene prioridad sobre otros al competir por un recurso.
- **Accounting:** medición/estadísticas del uso (útil para billing).
- **Control:** freezar (congelar) y reiniciar un grupo de procesos.

Conceptos base:

- **Controlador o subsistema:** componente del kernel específico por recurso (`cpu`, `memory`, `blkio`/`io`, `cpuset`, `pids`, `net_cls`, `freezer`...).
- **Jerarquía:** árbol de cgroups, representado como directorios en el pseudo-filesystem cgroup montado (`/sys/fs/cgroup`).
- Un proceso **NO necesita ser modificado** para pertenecer a un cgroup; se lo agrega escribiendo su PID en `cgroup.procs`. Los procesos desconocen que hay límites.
- Un proceso creado por **`fork` queda en el MISMO cgroup del padre** (herencia).
- Los límites de un cgroup hijo **no pueden superar** los del padre.

**Ejercicio clásico: limitar la CPU de un proceso al 80%.** Se resuelve con cgroups (controlador `cpu`):

1. Crear un cgroup dentro del controlador `cpu`.
2. Escribir la **cuota** (`cpu.cfs_quota_us` / `cpu.cfs_period_us`, o `cpu.max` en v2) correspondiente al 80%.
3. Agregar el PID del proceso a `cgroup.procs`.

**cgroups v1 vs v2:**

| Aspecto | **v1** | **v2** |
|---|---|---|
| Jerarquías | **Múltiples** (una por controlador) | **Única / unificada** |
| Montar un controlador particular | Sí se puede | No (todo en la jerarquía única) |
| Pertenencia de un proceso | A un cgroup **por cada jerarquía** (varias a la vez) | A **un solo** cgroup en toda la jerarquía |
| ¿Procesos en cgroups internos? | Permitidos | Solo en **cgroups sin hijos (hojas)**, salvo el root ("no internal process constraint") |
| Desmontar un controlador | Solo si no tiene cgroups hijos | — |

Las dos versiones **pueden coexistir** en el mismo sistema; lo que **no se puede** es montar **el mismo controlador** en ambas simultáneamente.

<div class="diagram">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><g transform="translate(0,0)"><text xml:space="preserve" x="175" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">cgroups v1 — múltiples jerarquías</text><text xml:space="preserve" x="60" y="42" text-anchor="middle" font-size="9" fill="#475569">jerarquía cpu</text><rect x="20" y="48" width="80" height="20" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="60" y="62" text-anchor="middle" font-size="9">root</text><line x1="60" y1="68" x2="35" y2="85" stroke="#334155"/><line x1="60" y1="68" x2="85" y2="85" stroke="#334155"/><rect x="10" y="85" width="50" height="20" fill="#bfdbfe" stroke="#1e40af"/><text xml:space="preserve" x="35" y="99" text-anchor="middle" font-size="9">grpA</text><rect x="60" y="85" width="50" height="20" fill="#bfdbfe" stroke="#1e40af"/><text xml:space="preserve" x="85" y="99" text-anchor="middle" font-size="9">grpB</text><text xml:space="preserve" x="180" y="42" text-anchor="middle" font-size="9" fill="#475569">jerarquía memory</text><rect x="140" y="48" width="80" height="20" fill="#fef3c7" stroke="#b45309"/><text xml:space="preserve" x="180" y="62" text-anchor="middle" font-size="9">root</text><line x1="180" y1="68" x2="180" y2="85" stroke="#334155"/><rect x="155" y="85" width="50" height="20" fill="#fde68a" stroke="#b45309"/><text xml:space="preserve" x="180" y="99" text-anchor="middle" font-size="9">grpX</text><text xml:space="preserve" x="300" y="42" text-anchor="middle" font-size="9" fill="#475569">jerarquía io</text><rect x="260" y="48" width="80" height="20" fill="#dcfce7" stroke="#166534"/><text xml:space="preserve" x="300" y="62" text-anchor="middle" font-size="9">root</text><circle cx="180" cy="150" r="18" fill="#f472b6" stroke="#831843"/><text xml:space="preserve" x="180" y="154" text-anchor="middle" font-size="10" font-weight="700" fill="#fff">P</text><text xml:space="preserve" x="180" y="185" text-anchor="middle" font-size="8" fill="#334155">un proceso, un cgroup por jerarquía</text><line x1="180" y1="132" x2="35" y2="105" stroke="#831843" stroke-dasharray="2,2"/><line x1="180" y1="132" x2="180" y2="105" stroke="#831843" stroke-dasharray="2,2"/><line x1="180" y1="132" x2="300" y2="68" stroke="#831843" stroke-dasharray="2,2"/><text xml:space="preserve" x="175" y="215" text-anchor="middle" font-size="8" fill="#64748b">Se puede montar un controlador particular · el mismo controlador NO puede</text><text xml:space="preserve" x="175" y="228" text-anchor="middle" font-size="8" fill="#64748b">estar en v1 y v2 a la vez</text></g><g transform="translate(370,0)"><text xml:space="preserve" x="150" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">cgroups v2 — jerarquía única</text><text xml:space="preserve" x="150" y="42" text-anchor="middle" font-size="9" fill="#475569">jerarquía unificada (todos los controladores)</text><rect x="110" y="48" width="80" height="20" fill="#e0e7ff" stroke="#3730a3"/><text xml:space="preserve" x="150" y="62" text-anchor="middle" font-size="9">root</text><line x1="150" y1="68" x2="60" y2="90" stroke="#334155"/><line x1="150" y1="68" x2="150" y2="90" stroke="#334155"/><line x1="150" y1="68" x2="240" y2="90" stroke="#334155"/><rect x="35" y="90" width="55" height="22" fill="#c7d2fe" stroke="#3730a3"/><text xml:space="preserve" x="62" y="104" text-anchor="middle" font-size="9">webapp</text><rect x="122" y="90" width="55" height="22" fill="#c7d2fe" stroke="#3730a3"/><text xml:space="preserve" x="149" y="104" text-anchor="middle" font-size="9">db</text><rect x="210" y="90" width="55" height="22" fill="#c7d2fe" stroke="#3730a3"/><text xml:space="preserve" x="237" y="104" text-anchor="middle" font-size="9">batch</text><line x1="62" y1="112" x2="62" y2="130" stroke="#334155"/><line x1="149" y1="112" x2="149" y2="130" stroke="#334155"/><line x1="237" y1="112" x2="237" y2="130" stroke="#334155"/><circle cx="62" cy="145" r="12" fill="#f472b6" stroke="#831843"/><text xml:space="preserve" x="62" y="149" text-anchor="middle" font-size="9" font-weight="700" fill="#fff">P1</text><circle cx="149" cy="145" r="12" fill="#f472b6" stroke="#831843"/><text xml:space="preserve" x="149" y="149" text-anchor="middle" font-size="9" font-weight="700" fill="#fff">P2</text><circle cx="237" cy="145" r="12" fill="#f472b6" stroke="#831843"/><text xml:space="preserve" x="237" y="149" text-anchor="middle" font-size="9" font-weight="700" fill="#fff">P3</text><text xml:space="preserve" x="150" y="180" text-anchor="middle" font-size="8" fill="#334155">Procesos solo en HOJAS (salvo root)</text><text xml:space="preserve" x="150" y="200" text-anchor="middle" font-size="8" fill="#64748b">"no internal process constraint"</text><text xml:space="preserve" x="150" y="220" text-anchor="middle" font-size="8" fill="#64748b">1 proceso pertenece a un solo cgroup</text><text xml:space="preserve" x="150" y="232" text-anchor="middle" font-size="8" fill="#64748b">en toda la jerarquía</text></g></svg>
<div class="caption">Fig. 5.1 — cgroups v1 (una jerarquía por controlador) vs v2 (jerarquía única, procesos solo en hojas).</div>
</div>

### Namespaces

Un **namespace** da a un proceso una **vista aislada de un recurso global del sistema**: el proceso "cree" tener su propia instancia. Un proceso está en **un namespace de cada tipo** a la vez, y sus hijos **heredan** los del padre (salvo que se cambien explícitamente).

| Namespace | Flag `CLONE_*` | Qué aísla |
|---|---|---|
| **PID** | `CLONE_NEWPID` | Árbol de PIDs propio; el primer proceso es **PID 1 (init)** del namespace |
| **NET** | `CLONE_NEWNET` | Interfaces de red, pilas, IPs, puertos |
| **MNT / Mount** | `CLONE_NEWNS` | Puntos de montaje (tabla de montajes propia) |
| **UTS** | `CLONE_NEWUTS` | Hostname y nombre de dominio |
| **IPC** | `CLONE_NEWIPC` | System V IPC, colas de mensajes POSIX |
| **USER** | `CLONE_NEWUSER` | Mapeo de UIDs/GIDs — root dentro puede no ser root en el host |
| **Cgroup** | `CLONE_NEWCGROUP` | Vista del cgroup root |
| **Time** | `CLONE_NEWTIME` | Offset del reloj por namespace |

Las **syscalls** que los manipulan son `clone()` (crea proceso + namespace nuevo), `unshare()` (mueve el proceso actual a un namespace nuevo) y `setns()` (une el proceso a un namespace existente).

**Doble PID por PID namespace:** un proceso `mi_proceso` corriendo dentro de un contenedor tiene **PID 1** dentro (es el primer proceso de su namespace, su "init") y un **PID real más alto** en el host (por ejemplo 423548). Desde el host se ven **todos** los procesos de todos los contenedores; desde el contenedor **no** se ven los del host.

<div class="diagram">
<svg viewBox="0 0 600 240" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><text xml:space="preserve" x="300" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">PID namespace — mismo proceso, dos PIDs</text><rect x="30" y="30" width="540" height="80" fill="#fef2f2" stroke="#b91c1c"/><text xml:space="preserve" x="45" y="48" font-weight="700" fill="#991b1b">Vista desde el HOST</text><text xml:space="preserve" x="45" y="66" font-size="9" fill="#7f1d1d" font-family="monospace">$ ps aux | grep mi_proceso</text><text xml:space="preserve" x="45" y="82" font-size="9" fill="#7f1d1d" font-family="monospace">root 423548 ... mi_proceso</text><text xml:space="preserve" x="45" y="97" font-size="8" fill="#991b1b" font-style="italic">→ el host ve todos los procesos, con sus PIDs "reales"</text><rect x="180" y="130" width="240" height="80" fill="#eff6ff" stroke="#1e40af" stroke-dasharray="4,3"/><text xml:space="preserve" x="300" y="150" text-anchor="middle" font-weight="700" fill="#1e3a8a">CONTAINER (PID namespace)</text><text xml:space="preserve" x="195" y="168" font-size="9" fill="#1e3a8a" font-family="monospace">$ docker exec ... ps aux</text><text xml:space="preserve" x="195" y="184" font-size="9" fill="#1e3a8a" font-family="monospace">root 1 ... mi_proceso</text><text xml:space="preserve" x="195" y="200" font-size="8" fill="#1e3a8a" font-style="italic">→ mismo proceso, aparece como PID 1 (init)</text><line x1="220" y1="86" x2="270" y2="180" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4,3"/><text xml:space="preserve" x="235" y="140" font-size="9" fill="#b45309" font-weight="700">mismo proceso</text></svg>
<div class="caption">Fig. 5.2 — Un proceso dentro de un container tiene PID 1 en su namespace y un PID real más alto en el host.</div>
</div>

<div class="callout warning">
<div class="callout-title">⚠ Trampas típicas del parcial</div>

- "¿Qué mecanismo del kernel limita el uso de CPU al 80%?" → **cgroups** (controlador `cpu`, cuota).
- "cgroups proveen limitación pero NO priorización" → <span class="tag f">F</span>: proveen ambas.
- "Una vez agregado a un cgroup, un proceso no puede moverse a otro" → <span class="tag f">F</span>.
- "Los procesos deben ser modificados para incorporarse a un cgroup" → <span class="tag f">F</span>.
- "Un proceso creado por `fork` no pertenece al cgroup del padre" → <span class="tag f">F</span>: lo hereda.
- v1: "existe una sola jerarquía en todo el sistema" → <span class="tag f">F</span> (eso es v2).
- v1: "un proceso puede estar en varios cgroups a la vez dentro de una jerarquía" → <span class="tag f">F</span> (uno por jerarquía).
- v2: "los procesos deben agregarse a cgroups sin hijos, salvo el root" → <span class="tag v">V</span>.
- "No es posible tener las dos versiones de cgroups montadas simultáneamente" → <span class="tag f">F</span>: sí se puede; lo que no se puede es el mismo controlador en ambas.
- "Un proceso tiene distinto PID dentro del contenedor y en el host" → <span class="tag v">V</span> (PID namespace).

</div>
---

## 6. Docker y contenedores

Docker es una **plataforma open-source para empaquetar y ejecutar aplicaciones en contenedores livianos**. Trabaja a **nivel SO**, comparte el kernel del host y **NO usa hypervisor**.

### Imagen vs Contenedor

Es la distinción central del tema:

| | **Imagen** | **Contenedor** |
|---|---|---|
| Qué es | Template/molde de **solo lectura** | Instancia **en ejecución** de una imagen |
| Contenido | App + dependencias + librerías + instrucciones | Imagen + capa escribible propia |
| Ejecución | **NO se ejecuta** (es estática) | **SÍ se ejecuta** (proceso/s aislado/s) |
| Relación | De 1 imagen se crean **varios** contenedores | Cada uno autónomo y aislado |
| Analogía OOP | Clase | Objeto/instancia |

Una imagen puede **basarse en otras** (cadena de capas). Se puede generar una imagen a partir de un contenedor con `docker commit`. La diferencia clave es que la imagen es solo lectura y el contenedor le agrega encima una **capa escribible**.

### Qué usa Docker del kernel

Docker corre en **espacio de usuario (Ring 3)**. **No captura syscalls** — eso lo hace el kernel. Pero sí requiere funcionalidades del kernel para armar los contenedores:

- **chroot:** cambia el directorio raíz del contenedor.
- **Namespaces:** vista aislada (PID, Net, Mount, UTS, IPC, User).
- **Cgroups:** limitan y controlan recursos (CPU, memoria, etc.).
- **Union Filesystem:** apila capas de imagen como si fueran un único FS.

El contenedor tiene sus propios filesystem, librerías, red, nombre... **excepto su propio kernel** (lo comparte con el host).

Docker usa **arquitectura cliente-servidor**: `dockerd` es el **servidor / daemon** (crea, ejecuta y monitorea contenedores e imágenes) y la CLI (`docker`) es el **cliente** que se comunica con él vía la API REST.

### Union Filesystem y capas

Es un **mecanismo de montaje** (no un FS nuevo): varios directorios montados en **un mismo punto** aparecen como uno solo. Las capas **inferiores son de solo lectura**; la capa **superior es escribible**.

Cada imagen es un conjunto de capas apiladas, donde cada capa guarda **solo las diferencias** respecto de la anterior. **Todas las capas de una imagen son de solo lectura**, y esas capas se **reutilizan entre imágenes** (ahorra espacio y descargas).

**Al ejecutar un contenedor** (copy-on-write):

1. Docker apila las capas read-only de la imagen.
2. Con `chroot` establece ese union-FS como raíz del contenedor.
3. Agrega encima una **capa escribible propia del contenedor**.
4. Solo esa **última capa** puede modificarse → varios contenedores pueden correr sobre las mismas capas base compartidas.

Al eliminar el contenedor se pierde su capa escribible; las capas inferiores quedan intactas. Por eso todo lo escrito **dentro del contenedor** se pierde si no se guarda fuera; y por eso **`RUN rm archivo`** en un Dockerfile **no reduce el tamaño de la imagen**: la capa donde estaba el archivo ya quedó fija; el `RUN rm` solo agrega una nueva capa que oculta el archivo, pero el original sigue ocupando en la capa previa.

<div class="diagram">
<svg viewBox="0 0 640 280" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><text xml:space="preserve" x="320" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">Union Filesystem de Docker (capas apiladas)</text><rect x="120" y="35" width="400" height="30" fill="#fecaca" stroke="#991b1b" stroke-width="2"/><text xml:space="preserve" x="320" y="55" text-anchor="middle" font-size="10" fill="#7f1d1d" font-weight="700">Capa escribible del CONTAINER (R/W · copy-on-write)</text><rect x="120" y="70" width="400" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="320" y="87" text-anchor="middle" font-size="9" fill="#1e3a8a">Capa N (RO) — CMD ["nginx"]</text><rect x="120" y="98" width="400" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="320" y="115" text-anchor="middle" font-size="9" fill="#1e3a8a">Capa 3 (RO) — COPY app/ /var/www</text><rect x="120" y="126" width="400" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="320" y="143" text-anchor="middle" font-size="9" fill="#1e3a8a">Capa 2 (RO) — RUN apt install nginx</text><rect x="120" y="154" width="400" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="320" y="171" text-anchor="middle" font-size="9" fill="#1e3a8a">Capa 1 (RO) — FROM ubuntu:22.04</text><text xml:space="preserve" x="115" y="55" text-anchor="end" font-size="8" fill="#7f1d1d">container →</text><text xml:space="preserve" x="115" y="125" text-anchor="end" font-size="8" fill="#1e3a8a">imagen (RO) →</text><rect x="120" y="190" width="400" height="24" fill="#fde68a" stroke="#b45309"/><text xml:space="preserve" x="320" y="207" text-anchor="middle" font-size="10" fill="#78350f">chroot → establece este union-FS como / del container</text><rect x="120" y="220" width="400" height="30" fill="#e5e7eb" stroke="#374151"/><text xml:space="preserve" x="320" y="239" text-anchor="middle" font-size="10" font-weight="700" fill="#111827">KERNEL del host (namespaces · cgroups · union FS)</text><text xml:space="preserve" x="580" y="105" font-size="8" fill="#475569">Capas RO se</text><text xml:space="preserve" x="580" y="118" font-size="8" fill="#475569">reutilizan entre</text><text xml:space="preserve" x="580" y="131" font-size="8" fill="#475569">imágenes</text><text xml:space="preserve" x="10" y="265" font-size="8" fill="#7c2d12">Nota: <tspan font-family="monospace">RUN rm foo</tspan> genera una capa nueva que oculta el archivo pero NO libera espacio en las capas RO inferiores.</text></svg>
<div class="caption">Fig. 6.1 — Union FS: capas RO de la imagen + 1 capa escribible del container. Solo la última capa se modifica.</div>
</div>

### Containers vs VMs

| **Container** | **VM** |
|---|---|
| Comparte el kernel del host | SO guest completo + kernel propio |
| Liviano, arranque rápido | Pesada, arranque lento |
| Aislamiento a nivel de proceso | Aislamiento completo (HW virtual) |
| NO necesita hypervisor | Requiere hypervisor |

### Dockerfile vs docker-compose

| | **Dockerfile** | **docker-compose (compose.yaml)** |
|---|---|---|
| Qué hace | Instrucciones para **construir UNA imagen** paso a paso | Definición **declarativa** para levantar y orquestar una app de **varios contenedores** |
| Resultado | Una imagen (1 pieza) | Conjunto de contenedores + redes + volúmenes |
| Lenguaje | Instrucciones (`FROM`, `RUN`, `COPY`, `CMD`, ...) | **YAML** (indentación, clave: valor) |
| Comando | `docker build` | `docker compose up` / `down` |

**No son excluyentes**: compose puede usar `build:` apuntando a un Dockerfile. Cada instrucción del Dockerfile genera **una nueva capa** de la imagen.

### Persistencia de datos

Lo escrito en la capa del contenedor se pierde al destruirlo. Para persistir hay que guardarlo en el host y montarlo dentro:

| | **Volumes (recomendado)** | **Bind mounts** |
|---|---|---|
| Ubicación | Gestionada por Docker en `/var/lib/docker/volumes` | **Cualquier ruta del host** elegida por el usuario |
| Portabilidad | Más portables, desacoplados del host | Atados a una ruta concreta |
| Acceso externo | Manejados por Docker | Pueden ser modificados por procesos ajenos a Docker |

<div class="callout warning">
<div class="callout-title">⚠ Trampas típicas del parcial</div>

- "A partir de una imagen solo se puede generar un solo contenedor" → <span class="tag f">F</span> (varios).
- "Docker necesita un hypervisor para ejecutarse" → <span class="tag f">F</span> (trabaja a nivel SO).
- "Un Dockerfile crea un container" → <span class="tag f">F</span>: crea una **imagen**.
- "Cada imagen está compuesta por capas de las cuales solo la última puede modificarse" → <span class="tag v">V</span> (la última es la del container).
- "Docker usa namespaces, cgroups y union filesystems" → <span class="tag v">V</span>.
- "No es posible generar una imagen a partir de un container" → <span class="tag f">F</span>: `docker commit`.
- "Docker no requiere funcionalidades del kernel porque corre en modo usuario" → <span class="tag f">F</span>: requiere chroot, namespaces, cgroups.
- "Todo archivo agregado a un container automáticamente pasa a ser parte de la imagen" → <span class="tag f">F</span>: va a la capa escribible del container, no de la imagen.
- "`RUN rm` reduce el tamaño total de la imagen" → <span class="tag f">F</span> (el archivo queda en la capa anterior).
- "Docker daemon (dockerd) es el servidor que crea/ejecuta/monitorea los contenedores" → <span class="tag v">V</span>.

</div>
---

## 7. Protección, seguridad y permisos

### Protección vs seguridad

- **Protección:** son los **mecanismos internos** del SO que controlan el acceso de procesos y usuarios a los recursos del sistema. Es el "cómo técnico" (los candados).
- **Seguridad:** concepto más general, la **defensa frente a amenazas externas e internas**; mide cuánto se puede confiar en que el sistema y sus datos mantienen su integridad.

La **protección es una parte de la seguridad**.

Hay una distinción clave entre **políticas** y **mecanismos**:

- Las **políticas** definen **qué** se quiere hacer / qué está permitido. Decisión de alto nivel; rara vez incluyen configuraciones.
- Los **mecanismos** son las herramientas, configuraciones e implementaciones concretas que **cómo** hacen cumplir la política.

Primero se define la política, después el mecanismo. Una misma política admite varios mecanismos: eso da flexibilidad (cambiar el mecanismo sin tocar la política).

La seguridad se mide con la **tríada CIA**:

- **Confidencialidad:** evitar la lectura/intercepción no autorizada.
- **Integridad:** evitar la modificación no autorizada.
- **Disponibilidad:** evitar la interrupción del servicio/recursos.

**Cuidado con la falacia común:** un sistema con muchas features **no** es automáticamente más seguro; al contrario, agrega superficie de ataque (más código, más bugs potenciales). La seguridad se favorece con el **principio de mínimo privilegio (POLA)** y quitando lo que no se usa.

### Dominios de protección

Un **dominio de protección** es un conjunto de pares **(objeto, derecho)** que especifica qué operaciones puede realizar un proceso sobre cada objeto. Un proceso "vive" en un dominio y solo puede hacer sobre cada objeto las operaciones autorizadas por ese dominio. En UNIX el dominio de un proceso lo define el par **(UID, GID)**.

### Permisos UNIX (rwx)

Cada archivo/directorio tiene **tres conjuntos de permisos**, uno por categoría:

- **u** (user/owner): el dueño del archivo.
- **g** (group): el grupo del archivo.
- **o** (others): todos los demás.

Cada conjunto tiene **r** (read = 4), **w** (write = 2) y **x** (execute = 1). En **octal** se suma por categoría. Por ejemplo `rwxr-xr--` = 4+2+1 / 4+0+1 / 4+0+0 = **754**.

Comandos:

- `chmod` — cambia permisos (`chmod 754 f`, `chmod u+x f`).
- `chown` — cambia el dueño (`chown usuario f`).
- `chgrp` — cambia el grupo (`chgrp grupo f`).

### Permisos especiales: setuid, setgid, sticky

Se representan como un **cuarto dígito octal** que precede a los permisos normales (por ejemplo `chmod 4755`).

| Permiso | Octal | Sobre un **archivo ejecutable** | Sobre un **directorio** |
|---|---|---|---|
| **setuid (SUID)** | 4 | Corre con los privilegios del **DUEÑO del archivo**, no del que lo lanza (ej: `passwd` corre como root) | Generalmente sin efecto |
| **setgid (SGID)** | 2 | Corre con los privilegios del **GRUPO del archivo** | Los archivos nuevos **heredan el grupo del directorio** (no el del usuario que los crea) |
| **sticky bit** | 1 | Sin efecto relevante hoy | Solo el **DUEÑO del archivo** (o el dueño del directorio, o root) puede **renombrar/eliminar** sus archivos, aunque otros tengan permiso de escritura en el dir. Ejemplo típico: **`/tmp`** |

Setuid/setgid implementan el **cambio de dominio dinámico** en UNIX: el proceso pasa temporalmente al dominio del dueño/grupo del ejecutable, justo cuando necesita más privilegio. En `ls -l` aparecen como `s` (en lugar de `x`) o `t` (sticky).

### UMASK

Es la **máscara** que define los permisos por defecto al crear archivos y directorios. Funciona por **resta**: se quitan sus bits de los permisos base (**666** para archivos, **777** para directorios).

Ejemplo con `umask 022`: archivo nuevo → `666 - 022 = 644`; directorio nuevo → `777 - 022 = 755`.

### /etc/passwd vs /etc/shadow

| Archivo | Contiene | Permisos |
|---|---|---|
| **`/etc/passwd`** | Info de usuarios: login, UID, GID, home, shell | **Legible por todos** (la contraseña **NO** está acá) |
| **`/etc/shadow`** | **Hashes de contraseñas** y políticas de expiración | **Solo root** puede leerlo/modificarlo |

### ASLR (Address Space Layout Randomization)

Es un mecanismo que **aleatoriza las direcciones** de memoria de un proceso en cada ejecución: **stack, heap, librerías compartidas** y, si el binario es PIE (Position Independent Executable), también el **código**. El objetivo es **dificultar exploits de memoria** (buffer overflow, return-to-libc) que necesitan direcciones fijas conocidas para funcionar.

**Linux provee ASLR para procesos de usuario**: sí. **Para el kernel también**, mediante **KASLR** (Kernel ASLR), que aleatoriza la dirección base donde se carga el kernel al arrancar. Es un **mecanismo separado** del ASLR de usuario.

Se controla con `/proc/sys/kernel/randomize_va_space`, con tres valores:

- `0` = desactivado.
- `1` = parcial (stack, mmap/librerías, vdso).
- `2` = completo (+ heap/brk). Es el **valor por defecto**.

Se puede activar/desactivar **sin recompilar el kernel** (basta escribir en ese archivo).

### Buffer overflow y shellcode (contexto)

- **Buffer overflow:** se escribe más allá del área de memoria reservada. C **no chequea límites**, así que un `strcpy` en un buffer pequeño puede pisar valores adyacentes en la pila, incluyendo la dirección de retorno de la función.
- **Shellcode:** código malicioso preparado para obtener los privilegios del programa atacado (típicamente lanzar una shell).
- ASLR y el uso correcto de permisos especiales (mínimo privilegio) **mitigan** estos ataques.

<div class="callout warning">
<div class="callout-title">⚠ Trampas típicas del parcial</div>

- "ASLR es solo para procesos de usuario en Linux" → <span class="tag f">F</span>: también para el kernel (KASLR).
- "Con UMASK se indican los permisos por default al crear un archivo/directorio" → <span class="tag v">V</span>.
- "El sticky-bit en un directorio permite que solo el dueño del archivo (o dueño del dir o root) pueda renombrar/eliminar los archivos" → <span class="tag v">V</span>.
- "En Linux `/etc/shadow` solo puede ser modificado por root" → <span class="tag v">V</span>.
- "setuid, setgid y sticky son permisos especiales" → <span class="tag v">V</span>.
- "setuid usa privilegios del que ejecuta el archivo" → <span class="tag f">F</span>: del **dueño** del archivo.
- "La contraseña está en `/etc/passwd`" → <span class="tag f">F</span>: en `/etc/shadow` (hasheada).
- "Un sistema con muchas features es más seguro porque tiene más herramientas de defensa" → <span class="tag f">F</span>: más features = más superficie de ataque. POLA.
- "Un dominio de protección es un conjunto de pares (objeto, derecho) que especifica operaciones sobre cada objeto" → <span class="tag v">V</span>.

</div>
---

## 8. File Systems, RAID y LVM

Tema clave y muy preguntado. Nota: si el programa de tu año excluye RAID/LVM, saltealo, pero cubrilo por las dudas — históricamente cae.

### Conceptos base de File Systems

Un **file system** organiza cómo se almacenan, nombran y recuperan los datos en un dispositivo. Reglas fundamentales:

- Una partición **debe tener un FS definido** para poder ser accedida (montada). Sin FS no hay lectura/escritura.
- El FS administra el espacio con **bloques** y describe cada archivo con un **inodo**.
- **El nombre del archivo NO vive en el inodo**: vive en la **entrada de directorio**, que asocia `nombre → número de inodo`.

**Inodo:** estructura que guarda los **metadatos** del archivo:

- Permisos (rwx), dueño (UID) y grupo (GID).
- Tamaño del archivo.
- Fechas: `atime` (acceso), `mtime` (modificación), `ctime` (cambio de metadatos); en Ext4 también `crtime` (creación).
- Punteros a los bloques de datos (directos, indirectos, doble/triple indirecto).
- **Contador de hard links** (link count).

Se puede montar un FS con `noatime` para no actualizar la fecha de acceso en cada lectura (mejora rendimiento).

<div class="diagram">
<svg viewBox="0 0 700 240" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><defs><marker id="fsar" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#0f172a"/></marker></defs><text xml:space="preserve" x="350" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">Directorio → Inodo → Bloques de datos</text><rect x="10" y="35" width="180" height="150" fill="#fde68a" stroke="#b45309"/><text xml:space="preserve" x="100" y="52" text-anchor="middle" font-size="10" font-weight="700" fill="#78350f">Directorio /home/matheo</text><line x1="10" y1="60" x2="190" y2="60" stroke="#b45309"/><text xml:space="preserve" x="20" y="75" font-size="9" font-weight="700" fill="#78350f">nombre</text><text xml:space="preserve" x="130" y="75" font-size="9" font-weight="700" fill="#78350f">inodo</text><line x1="10" y1="80" x2="190" y2="80" stroke="#b45309" stroke-dasharray="2,2"/><text xml:space="preserve" x="20" y="95" font-size="9" font-family="monospace" fill="#78350f">.</text><text xml:space="preserve" x="130" y="95" font-size="9" font-family="monospace" fill="#78350f">42</text><text xml:space="preserve" x="20" y="110" font-size="9" font-family="monospace" fill="#78350f">..</text><text xml:space="preserve" x="130" y="110" font-size="9" font-family="monospace" fill="#78350f">1</text><text xml:space="preserve" x="20" y="125" font-size="9" font-family="monospace" fill="#78350f">tesis.pdf</text><text xml:space="preserve" x="130" y="125" font-size="9" font-family="monospace" fill="#78350f" font-weight="700">128</text><text xml:space="preserve" x="20" y="140" font-size="9" font-family="monospace" fill="#78350f">apuntes</text><text xml:space="preserve" x="130" y="140" font-size="9" font-family="monospace" fill="#78350f">129</text><text xml:space="preserve" x="20" y="155" font-size="9" font-family="monospace" fill="#78350f">link.pdf</text><text xml:space="preserve" x="130" y="155" font-size="9" font-family="monospace" fill="#78350f" font-weight="700">128</text><text xml:space="preserve" x="100" y="176" text-anchor="middle" font-size="8" fill="#78350f" font-style="italic">el NOMBRE vive acá</text><rect x="230" y="35" width="220" height="150" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="340" y="52" text-anchor="middle" font-size="10" font-weight="700" fill="#1e3a8a">Inodo #128 (metadatos)</text><line x1="230" y1="60" x2="450" y2="60" stroke="#1e40af"/><text xml:space="preserve" x="240" y="75" font-size="9" fill="#1e3a8a">tipo:</text><text xml:space="preserve" x="360" y="75" font-size="9" fill="#1e3a8a" font-family="monospace">-rw-r--r--</text><text xml:space="preserve" x="240" y="90" font-size="9" fill="#1e3a8a">UID / GID:</text><text xml:space="preserve" x="360" y="90" font-size="9" fill="#1e3a8a" font-family="monospace">1000 / 1000</text><text xml:space="preserve" x="240" y="105" font-size="9" fill="#1e3a8a">tamaño:</text><text xml:space="preserve" x="360" y="105" font-size="9" fill="#1e3a8a" font-family="monospace">42 KB</text><text xml:space="preserve" x="240" y="120" font-size="9" fill="#1e3a8a">atime/mtime/ctime</text><text xml:space="preserve" x="240" y="135" font-size="9" fill="#1e3a8a">link count:</text><text xml:space="preserve" x="360" y="135" font-size="9" fill="#1e3a8a" font-family="monospace" font-weight="700">2</text><text xml:space="preserve" x="240" y="150" font-size="9" fill="#1e3a8a">punteros bloques →</text><text xml:space="preserve" x="240" y="176" font-size="8" fill="#1e3a8a" font-style="italic">NO tiene el nombre del archivo</text><text xml:space="preserve" x="580" y="55" text-anchor="middle" font-size="9" fill="#475569">bloques de datos</text><rect x="500" y="60" width="45" height="30" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="522" y="80" text-anchor="middle" font-size="9">B7</text><rect x="555" y="60" width="45" height="30" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="577" y="80" text-anchor="middle" font-size="9">B8</text><rect x="610" y="60" width="45" height="30" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="632" y="80" text-anchor="middle" font-size="9">B12</text><rect x="500" y="100" width="45" height="30" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="522" y="120" text-anchor="middle" font-size="9">B13</text><rect x="555" y="100" width="45" height="30" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="577" y="120" text-anchor="middle" font-size="9">B20</text><line x1="180" y1="125" x2="230" y2="125" stroke="#0f172a" marker-end="url(#fsar)"/><line x1="180" y1="155" x2="230" y2="125" stroke="#0f172a" stroke-dasharray="2,2"/><text xml:space="preserve" x="204" y="118" font-size="7" fill="#334155">2 hard links</text><line x1="450" y1="150" x2="500" y2="80" stroke="#0f172a" marker-end="url(#fsar)"/><line x1="450" y1="150" x2="500" y2="115" stroke="#0f172a" marker-end="url(#fsar)"/><text xml:space="preserve" x="350" y="215" text-anchor="middle" font-size="9" fill="#475569" font-style="italic">Hard link = otra entrada de directorio apuntando al mismo inodo. Symlink = archivo aparte con su propio inodo cuyo contenido es una ruta.</text></svg>
<div class="caption">Fig. 8.3 — El directorio asocia nombre → inodo. El inodo tiene los metadatos + punteros a bloques. El nombre <strong>no</strong> vive en el inodo.</div>
</div>

**Bloque:** unidad **mínima de almacenamiento** de datos del FS. Su tamaño se elige al crear el FS (típicamente 1K, 2K, 4K) y **no puede cambiarse dinámicamente después**.

**Extent:** conjunto de **bloques contiguos** descriptos como un rango (`inicio + longitud`) en vez de bloque por bloque. Ventajas: menos metadatos y mejor rendimiento para archivos grandes. Lo usan Ext4, XFS y BTRFS.

### Tipos de File System

**EXT2 / EXT3 / EXT4:**

- Dividen el FS en **grupos de bloques** (block groups).
- El **superbloque** (info global del FS) está **replicado** en varios grupos de bloques como redundancia ante corrupción.
- **Ext2** no tiene journaling. **Ext3** lo agrega. **Ext4** agrega extents, journaling mejorado y guarda **fecha de creación** (crtime); soporta volúmenes y archivos más grandes.

**Journaling:** es un **log** donde se anotan las operaciones **antes** de aplicarlas al FS. Permite **recuperar el FS** a un estado consistente tras un corte de energía o caída. **Cuidado:** NO almacena "todas las operaciones sobre un archivo"; registra operaciones de metadatos / transacciones pendientes de aplicar, para recuperación.

**XFS:**

- Los **inodos se asignan dinámicamente** (no hay una tabla fija reservada al crear el FS).
- Alto rendimiento, usa extents y journaling.
- **NO se puede achicar** un FS XFS: solo se puede **crecer** (extender).

**BTRFS:**

- Usa **Copy-on-Write (CoW):** al modificar un dato, no sobrescribe el bloque original; escribe en un bloque nuevo y actualiza los punteros / árbol. Esto da consistencia ante cortes (nunca queda a medias) y **snapshots eficientes y baratos** (comparten bloques, solo se copia lo que cambia).
- Soporta **subvolúmenes**: raíces de árbol de archivos independientes dentro del mismo FS.
- En un subvolumen **no se puede definir un FS distinto a BTRFS** (el subvolumen es siempre BTRFS).
- Para **montar un subvolumen que ocupa más de una partición** basta con indicar **una sola** de esas particiones (BTRFS/LVM resuelven el resto).
- Soporta RAID interno, checksums y compresión.

### Links: hard vs simbólico

| Característica | HARD LINK | SYMLINK (soft) |
|---|---|---|
| Apunta a... | El **mismo inodo** que el original | Una **ruta / nombre** |
| ¿Consume inodo nuevo? | **NO** (comparte el inodo) | **SÍ** (tiene su propio inodo) |
| Si se borra el original | **Sigue funcionando** (los datos viven hasta que link count = 0) | **Queda roto** |
| ¿Cruza particiones / FS distintos? | **NO** | **SÍ** |

Clave del inodo: se elimina recién cuando su contador de links llega a 0. Por eso un hard link mantiene vivos los datos aunque borres el nombre original.

### RAID

**RAID (Redundant Array of Independent Disks)** combina varios discos físicos en una unidad lógica para mejorar velocidad, capacidad y/o redundancia. Conceptos base:

- **Striping:** reparte los datos en varios discos, en paralelo → velocidad.
- **Mirroring:** copia idéntica de los datos en otro disco → redundancia.
- **Paridad:** información calculada que permite **reconstruir** datos ante un fallo.

| Nivel | Striping | Paridad | Redundancia | Capacidad útil | Tolera fallo de |
|---|---|---|---|---|---|
| **RAID 0** | Sí | No | **No** | Suma de todos (100%) | **0 discos** |
| **RAID 1** | **No** | **No** | Sí (espejo) | La de **1 disco** (50% con 2) | 1 disco |
| **RAID 4** | Sí | **Dedicada** (1 disco) | Sí | N-1 discos | 1 disco |
| **RAID 5** | Sí | **Distribuida** entre todos | Sí | **N-1 discos** | **1 disco** |
| **RAID 6** | Sí | **Doble** distribuida | Sí | N-2 discos | **2 discos** |

<div class="diagram">
<svg viewBox="0 0 720 220" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><text xml:space="preserve" x="360" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">RAID 0 vs RAID 1 vs RAID 5</text><g transform="translate(0,30)"><text xml:space="preserve" x="110" y="14" text-anchor="middle" font-weight="700" fill="#1e40af">RAID 0 (striping)</text><rect x="20" y="25" width="60" height="130" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="50" y="42" text-anchor="middle" font-size="9" fill="#475569">Disco 1</text><rect x="90" y="25" width="60" height="130" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="120" y="42" text-anchor="middle" font-size="9" fill="#475569">Disco 2</text><rect x="160" y="25" width="60" height="130" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="190" y="42" text-anchor="middle" font-size="9" fill="#475569">Disco 3</text><rect x="25" y="55" width="50" height="20" fill="#93c5fd" stroke="#1e40af"/><text xml:space="preserve" x="50" y="69" text-anchor="middle" font-size="9">A1</text><rect x="95" y="55" width="50" height="20" fill="#93c5fd" stroke="#1e40af"/><text xml:space="preserve" x="120" y="69" text-anchor="middle" font-size="9">A2</text><rect x="165" y="55" width="50" height="20" fill="#93c5fd" stroke="#1e40af"/><text xml:space="preserve" x="190" y="69" text-anchor="middle" font-size="9">A3</text><rect x="25" y="80" width="50" height="20" fill="#93c5fd" stroke="#1e40af"/><text xml:space="preserve" x="50" y="94" text-anchor="middle" font-size="9">B1</text><rect x="95" y="80" width="50" height="20" fill="#93c5fd" stroke="#1e40af"/><text xml:space="preserve" x="120" y="94" text-anchor="middle" font-size="9">B2</text><rect x="165" y="80" width="50" height="20" fill="#93c5fd" stroke="#1e40af"/><text xml:space="preserve" x="190" y="94" text-anchor="middle" font-size="9">B3</text><rect x="25" y="105" width="50" height="20" fill="#93c5fd" stroke="#1e40af"/><text xml:space="preserve" x="50" y="119" text-anchor="middle" font-size="9">C1</text><rect x="95" y="105" width="50" height="20" fill="#93c5fd" stroke="#1e40af"/><text xml:space="preserve" x="120" y="119" text-anchor="middle" font-size="9">C2</text><rect x="165" y="105" width="50" height="20" fill="#93c5fd" stroke="#1e40af"/><text xml:space="preserve" x="190" y="119" text-anchor="middle" font-size="9">C3</text><text xml:space="preserve" x="120" y="145" text-anchor="middle" font-size="8" fill="#475569">A = A1+A2+A3 (repartido)</text><text xml:space="preserve" x="120" y="170" text-anchor="middle" font-size="8" fill="#7c2d12">Tolera fallo de 0 discos — pierdes TODO</text><text xml:space="preserve" x="120" y="182" text-anchor="middle" font-size="8" fill="#166534">Capacidad útil: 100%</text></g><g transform="translate(240,30)"><text xml:space="preserve" x="110" y="14" text-anchor="middle" font-weight="700" fill="#166534">RAID 1 (mirror)</text><rect x="45" y="25" width="60" height="130" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="75" y="42" text-anchor="middle" font-size="9" fill="#475569">Disco 1</text><rect x="115" y="25" width="60" height="130" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="145" y="42" text-anchor="middle" font-size="9" fill="#475569">Disco 2</text><rect x="50" y="55" width="50" height="20" fill="#86efac" stroke="#166534"/><text xml:space="preserve" x="75" y="69" text-anchor="middle" font-size="9">A</text><rect x="120" y="55" width="50" height="20" fill="#86efac" stroke="#166534"/><text xml:space="preserve" x="145" y="69" text-anchor="middle" font-size="9">A</text><rect x="50" y="80" width="50" height="20" fill="#86efac" stroke="#166534"/><text xml:space="preserve" x="75" y="94" text-anchor="middle" font-size="9">B</text><rect x="120" y="80" width="50" height="20" fill="#86efac" stroke="#166534"/><text xml:space="preserve" x="145" y="94" text-anchor="middle" font-size="9">B</text><rect x="50" y="105" width="50" height="20" fill="#86efac" stroke="#166534"/><text xml:space="preserve" x="75" y="119" text-anchor="middle" font-size="9">C</text><rect x="120" y="105" width="50" height="20" fill="#86efac" stroke="#166534"/><text xml:space="preserve" x="145" y="119" text-anchor="middle" font-size="9">C</text><text xml:space="preserve" x="110" y="145" text-anchor="middle" font-size="8" fill="#475569">Copia idéntica en ambos</text><text xml:space="preserve" x="110" y="170" text-anchor="middle" font-size="8" fill="#166534">Tolera fallo de 1 disco</text><text xml:space="preserve" x="110" y="182" text-anchor="middle" font-size="8" fill="#7c2d12">Capacidad útil: 50% (con 2 discos)</text></g><g transform="translate(480,30)"><text xml:space="preserve" x="110" y="14" text-anchor="middle" font-weight="700" fill="#7c2d12">RAID 5 (paridad distribuida)</text><rect x="20" y="25" width="60" height="130" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="50" y="42" text-anchor="middle" font-size="9" fill="#475569">Disco 1</text><rect x="90" y="25" width="60" height="130" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="120" y="42" text-anchor="middle" font-size="9" fill="#475569">Disco 2</text><rect x="160" y="25" width="60" height="130" fill="#f8fafc" stroke="#334155"/><text xml:space="preserve" x="190" y="42" text-anchor="middle" font-size="9" fill="#475569">Disco 3</text><rect x="25" y="55" width="50" height="20" fill="#fed7aa" stroke="#c2410c"/><text xml:space="preserve" x="50" y="69" text-anchor="middle" font-size="9">A1</text><rect x="95" y="55" width="50" height="20" fill="#fed7aa" stroke="#c2410c"/><text xml:space="preserve" x="120" y="69" text-anchor="middle" font-size="9">A2</text><rect x="165" y="55" width="50" height="20" fill="#fda4af" stroke="#9f1239"/><text xml:space="preserve" x="190" y="69" text-anchor="middle" font-size="9">Ap</text><rect x="25" y="80" width="50" height="20" fill="#fed7aa" stroke="#c2410c"/><text xml:space="preserve" x="50" y="94" text-anchor="middle" font-size="9">B1</text><rect x="95" y="80" width="50" height="20" fill="#fda4af" stroke="#9f1239"/><text xml:space="preserve" x="120" y="94" text-anchor="middle" font-size="9">Bp</text><rect x="165" y="80" width="50" height="20" fill="#fed7aa" stroke="#c2410c"/><text xml:space="preserve" x="190" y="94" text-anchor="middle" font-size="9">B2</text><rect x="25" y="105" width="50" height="20" fill="#fda4af" stroke="#9f1239"/><text xml:space="preserve" x="50" y="119" text-anchor="middle" font-size="9">Cp</text><rect x="95" y="105" width="50" height="20" fill="#fed7aa" stroke="#c2410c"/><text xml:space="preserve" x="120" y="119" text-anchor="middle" font-size="9">C1</text><rect x="165" y="105" width="50" height="20" fill="#fed7aa" stroke="#c2410c"/><text xml:space="preserve" x="190" y="119" text-anchor="middle" font-size="9">C2</text><text xml:space="preserve" x="120" y="145" text-anchor="middle" font-size="8" fill="#475569">Ap/Bp/Cp = paridad rotativa</text><text xml:space="preserve" x="120" y="170" text-anchor="middle" font-size="8" fill="#166534">Tolera fallo de 1 disco</text><text xml:space="preserve" x="120" y="182" text-anchor="middle" font-size="8" fill="#7c2d12">Capacidad útil: (N-1)/N</text></g></svg>
<div class="caption">Fig. 8.2 — Comparación visual de los niveles clásicos de RAID. En RAID 5 la paridad rota entre los discos (bloques P<sub>a</sub>, P<sub>b</sub>, P<sub>c</sub>).</div>
</div>

**Cálculos típicos del parcial:**

- RAID 5 con **5 discos de 1 TB** → capacidad útil = **(N-1) = 4 TB**. Tolera **1 disco caído**.
- Discos de distinto tamaño: el RAID se limita al **disco más chico**. Con 1, 2 y 3 GB → el array usa 3 × 1 GB efectivos; en RAID 5 la capacidad útil sería **2 GB**.

**Chunk size:** tamaño del bloque de striping (cuánto se escribe en un disco antes de pasar al siguiente). **No depende de la cantidad de discos.**

**DDP (Dynamic Disk Pool):** distribuye datos, paridad y spare sobre todos los discos de un pool, y la reconstrucción es más rápida. **No** funciona como "11 discos fijos reservando 2".

### LVM (Logical Volume Manager)

Capa de abstracción sobre los discos físicos que da **flexibilidad** frente al particionado clásico. Su gran ventaja: permite **extender un FS a través de diferentes particiones e incluso discos rígidos distintos**.

Jerarquía LVM:

<div class="diagram">
<svg viewBox="0 0 600 300" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><text xml:space="preserve" x="300" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">LVM stack — PV → VG → LV</text><text xml:space="preserve" x="70" y="42" font-size="9" fill="#475569">Discos / particiones físicas</text><rect x="20" y="48" width="90" height="30" fill="#e5e7eb" stroke="#374151"/><text xml:space="preserve" x="65" y="67" text-anchor="middle" font-size="9">/dev/sda1</text><rect x="120" y="48" width="90" height="30" fill="#e5e7eb" stroke="#374151"/><text xml:space="preserve" x="165" y="67" text-anchor="middle" font-size="9">/dev/sdb1</text><rect x="220" y="48" width="90" height="30" fill="#e5e7eb" stroke="#374151"/><text xml:space="preserve" x="265" y="67" text-anchor="middle" font-size="9">/dev/sdc1</text><line x1="65" y1="78" x2="65" y2="98" stroke="#0f172a" marker-end="url(#lvarrow)"/><line x1="165" y1="78" x2="165" y2="98" stroke="#0f172a" marker-end="url(#lvarrow)"/><line x1="265" y1="78" x2="265" y2="98" stroke="#0f172a" marker-end="url(#lvarrow)"/><text xml:space="preserve" x="360" y="115" font-size="9" fill="#475569">Physical Volumes</text><rect x="20" y="98" width="90" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="65" y="115" text-anchor="middle" font-size="9" font-weight="700" fill="#1e3a8a">PV1</text><rect x="120" y="98" width="90" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="165" y="115" text-anchor="middle" font-size="9" font-weight="700" fill="#1e3a8a">PV2</text><rect x="220" y="98" width="90" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="265" y="115" text-anchor="middle" font-size="9" font-weight="700" fill="#1e3a8a">PV3</text><line x1="65" y1="124" x2="165" y2="144" stroke="#0f172a"/><line x1="165" y1="124" x2="165" y2="144" stroke="#0f172a"/><line x1="265" y1="124" x2="165" y2="144" stroke="#0f172a"/><text xml:space="preserve" x="360" y="160" font-size="9" fill="#475569">Volume Group (pool)</text><rect x="20" y="144" width="290" height="34" fill="#fde68a" stroke="#b45309"/><text xml:space="preserve" x="165" y="163" text-anchor="middle" font-size="10" font-weight="700" fill="#78350f">VG "datos"</text><text xml:space="preserve" x="165" y="174" text-anchor="middle" font-size="8" fill="#78350f">extent size = 4 MiB</text><line x1="80" y1="178" x2="80" y2="198" stroke="#0f172a" marker-end="url(#lvarrow)"/><line x1="165" y1="178" x2="165" y2="198" stroke="#0f172a" marker-end="url(#lvarrow)"/><line x1="255" y1="178" x2="255" y2="198" stroke="#0f172a" marker-end="url(#lvarrow)"/><text xml:space="preserve" x="360" y="215" font-size="9" fill="#475569">Logical Volumes (tamaño = múltiplo de extent)</text><rect x="20" y="198" width="120" height="28" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="80" y="216" text-anchor="middle" font-size="9" font-weight="700" fill="#064e3b">LV /home</text><rect x="145" y="198" width="90" height="28" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="190" y="216" text-anchor="middle" font-size="9" font-weight="700" fill="#064e3b">LV /var</text><rect x="240" y="198" width="70" height="28" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="275" y="216" text-anchor="middle" font-size="9" font-weight="700" fill="#064e3b">LV logs</text><line x1="80" y1="226" x2="80" y2="246" stroke="#0f172a" marker-end="url(#lvarrow)"/><line x1="190" y1="226" x2="190" y2="246" stroke="#0f172a" marker-end="url(#lvarrow)"/><line x1="275" y1="226" x2="275" y2="246" stroke="#0f172a" marker-end="url(#lvarrow)"/><text xml:space="preserve" x="80" y="260" text-anchor="middle" font-size="9" fill="#334155">ext4</text><text xml:space="preserve" x="190" y="260" text-anchor="middle" font-size="9" fill="#334155">xfs</text><text xml:space="preserve" x="275" y="260" text-anchor="middle" font-size="9" fill="#334155">btrfs</text><text xml:space="preserve" x="165" y="285" text-anchor="middle" font-size="9" fill="#475569" font-style="italic">Filesystems (creados sobre los LV) — se montan</text><rect x="380" y="200" width="200" height="80" fill="#fff7ed" stroke="#f97316"/><text xml:space="preserve" x="480" y="218" text-anchor="middle" font-size="9" font-weight="700" fill="#9a3412">Orden importa</text><text xml:space="preserve" x="480" y="238" text-anchor="middle" font-size="8" fill="#7c2d12">Extender: LV → FS</text><text xml:space="preserve" x="480" y="252" text-anchor="middle" font-size="8" fill="#7c2d12">Achicar: FS → LV</text><text xml:space="preserve" x="480" y="272" text-anchor="middle" font-size="8" fill="#7c2d12">Snapshots = CoW; crecen con cambios</text><defs><marker id="lvarrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M 0 0 L 8 4 L 0 8 z" fill="#0f172a"/></marker></defs></svg>
<div class="caption">Fig. 8.1 — Stack LVM: los PV inicializan particiones para LVM, el VG los agrupa como pool con un extent size, y los LV se tallan del pool para montar FS encima.</div>
</div>

Reglas clave:

- El **tamaño de un LV** es siempre **múltiplo del tamaño del EXTENT** definido en el VG.
- Un LV puede **abarcar varios discos**: no está limitado al espacio de un único disco físico.

**Orden de operaciones (mnemotecnia):**

- **Extender (agrandar):** primero el **LV**, después el **FS**.
- **Achicar (reducir):** primero el **FS**, después el **LV**.
- Regla: "para crecer, primero el contenedor; para achicar, primero el contenido" — así no se pierden datos.

**Snapshots LVM:**

- Usan **Copy-on-Write**.
- Al crear el snapshot **no se copian** los datos ni metadatos del LV original: se copian **a medida que el LV original se modifica**, y solo los bloques que cambian.
- El **espacio del snapshot crece** con las modificaciones del original.
- **No se eliminan solos**: hay que borrarlos manualmente (si se llena, se invalidan).

<div class="callout warning">
<div class="callout-title">⚠ Trampas típicas del parcial</div>

- "RAID 1 provee striping y paridad distribuida" → <span class="tag f">F</span>: RAID 1 es mirroring, sin striping ni paridad.
- "¿En qué nivel de RAID NO existe striping?" → **RAID 1**.
- "RAID 5 con 5 discos de 1 TB tiene capacidad útil de..." → **4 TB** (N-1).
- "¿Cuántos discos pueden fallar en RAID 5 sin pérdida?" → **1**.
- "El chunk size depende de la cantidad de discos" → <span class="tag f">F</span>.
- "El nombre del archivo está en el inodo" → <span class="tag f">F</span>: en el directorio.
- "Cada vez que se crea un hard link se usa un nuevo inodo" → <span class="tag f">F</span>: comparte inodo.
- "Si se elimina un symlink, se elimina el archivo apuntado" → <span class="tag f">F</span>.
- "Si se elimina el archivo original, el symlink queda roto" → <span class="tag v">V</span>.
- "En XFS los inodos se asignan dinámicamente pero no se puede reducir el FS" → <span class="tag v">V</span>.
- "¿En qué FS no se puede disminuir el tamaño?" → **XFS**.
- "El journaling almacena todas las operaciones sobre un archivo" → <span class="tag f">F</span>: es un log de operaciones pendientes de aplicar, para recuperación.
- "En BTRFS un subvolumen puede tener un FS distinto a BTRFS" → <span class="tag f">F</span>.
- "Para montar un subvolumen que ocupa más de una partición basta con indicar una sola" → <span class="tag v">V</span>.
- "El tamaño de un LV siempre es múltiplo del extent del VG" → <span class="tag v">V</span>.
- "Un LV solo se puede extender si hay espacio en el disco físico donde está definido" → <span class="tag f">F</span>: puede abarcar varios.
- "Para achicar un LV: primero el FS y después el LV" → <span class="tag v">V</span> (para extender, al revés).
- "Los snapshots LVM usan CoW y crecen con las modificaciones del LV original" → <span class="tag v">V</span>.
- "Al crear el snapshot se copian metadatos y datos del LV original" → <span class="tag f">F</span>.
- "Una partición debe tener un FS definido para poder ser accedida" → <span class="tag v">V</span>.

</div>
---

## 9. Multiprocesadores

### Por qué multiprocesadores

Históricamente la industria buscó más poder de cómputo subiendo la **velocidad de reloj**. Hoy eso choca con dos límites físicos: ninguna señal viaja más rápido que la luz (~20 cm/ns en cobre/fibra) y la **disipación de calor** y el consumo eléctrico crecen mucho más rápido que el rendimiento. La solución actual es **cómputo paralelo/distribuido**: varias CPU a velocidad "normal" que en conjunto dan la potencia. Más cores, no más Hz.

### Esquemas de arquitectura (mayor → menor acoplamiento)

| Esquema | Memoria | Comunicación | Retardo |
|---|---|---|---|
| **Multiprocesador (memoria COMPARTIDA)** | Un único espacio de direcciones, por **BUS** | A través de la memoria compartida | **2–10 ns** |
| **Multicomputadora (memoria DISTRIBUIDA)** | Cada CPU tiene su memoria local | **Pasaje de mensajes** por interconexión de alta velocidad | **10–50 µs** |
| **Sistema distribuido** | Cada nodo es una PC completa | Pasaje de mensajes por **red** | **10–100 ms** |

Las **multicomputadoras** (clusters) son fáciles de fabricar pero difíciles de programar; son **fuertemente acopladas** (una tarea empieza y termina en la misma CPU). Los **sistemas distribuidos** son PCs completas y heterogéneas (distintos SO/HW) conectadas por red. El salto de retardo de nseg a mseg es un factor de millones.

### Memoria compartida: UMA vs NUMA

A nivel HW, en un multiprocesador de memoria compartida cada procesador direcciona toda la memoria. Según la velocidad de acceso:

| | **UMA** | **NUMA** |
|---|---|---|
| Tiempo de acceso | **Igual** para todas las CPU | **Depende**: local rápido / remoto lento |
| Espacio de direcciones | Único | Único (visible a todas) |
| Acceso remoto | — | Con **LOAD/STORE**, requiere bus compartido |
| Escalabilidad | Baja (caro) | Alta |
| Ejemplo típico | **SMP por bus** | Grandes sistemas multi-nodo |

**UMA basado en bus:** un único bus, y al sumar CPU el **ancho de banda del bus** se vuelve cuello de botella (CPU ociosa esperando el bus). Se palia con **caches** (bloque RO en varias caches; RW en una sola, requiere protocolo de coherencia). Para escalar más allá del bus (~16-32 CPU) se usan crossbar (barras cruzadas) o redes multietapa, con distintos trade-offs de contención vs cantidad de switches.

<div class="diagram">
<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><g transform="translate(0,0)"><text xml:space="preserve" x="170" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">UMA (Uniform Memory Access)</text><text xml:space="preserve" x="170" y="34" text-anchor="middle" font-size="8" fill="#64748b">SMP por bus — acceso igual para todas las CPU</text><rect x="30" y="50" width="50" height="34" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="55" y="72" text-anchor="middle" font-size="9" fill="#1e3a8a">CPU1</text><rect x="100" y="50" width="50" height="34" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="125" y="72" text-anchor="middle" font-size="9" fill="#1e3a8a">CPU2</text><rect x="170" y="50" width="50" height="34" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="195" y="72" text-anchor="middle" font-size="9" fill="#1e3a8a">CPU3</text><rect x="240" y="50" width="50" height="34" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="265" y="72" text-anchor="middle" font-size="9" fill="#1e3a8a">CPU4</text><line x1="20" y1="105" x2="300" y2="105" stroke="#f97316" stroke-width="4"/><text xml:space="preserve" x="308" y="109" font-size="9" fill="#9a3412" font-weight="700">BUS</text><line x1="55" y1="84" x2="55" y2="105" stroke="#334155"/><line x1="125" y1="84" x2="125" y2="105" stroke="#334155"/><line x1="195" y1="84" x2="195" y2="105" stroke="#334155"/><line x1="265" y1="84" x2="265" y2="105" stroke="#334155"/><rect x="80" y="140" width="160" height="40" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="160" y="164" text-anchor="middle" font-size="10" font-weight="700" fill="#064e3b">MEMORIA GLOBAL</text><line x1="160" y1="105" x2="160" y2="140" stroke="#334155"/><text xml:space="preserve" x="160" y="210" text-anchor="middle" font-size="8" fill="#475569">Todas las CPUs acceden con la misma latencia</text><text xml:space="preserve" x="160" y="223" text-anchor="middle" font-size="8" fill="#7c2d12">Cuello de botella: ancho de banda del bus</text><text xml:space="preserve" x="160" y="240" text-anchor="middle" font-size="8" fill="#475569" font-style="italic">Escala hasta ~16-32 CPUs</text></g><g transform="translate(360,0)"><text xml:space="preserve" x="160" y="18" text-anchor="middle" font-weight="700" fill="#0f172a">NUMA (Non-Uniform Memory Access)</text><text xml:space="preserve" x="160" y="34" text-anchor="middle" font-size="8" fill="#64748b">Local rápido / remoto lento</text><rect x="10" y="50" width="140" height="130" fill="#eff6ff" stroke="#3b82f6" stroke-dasharray="3,3"/><text xml:space="preserve" x="80" y="66" text-anchor="middle" font-size="9" fill="#1e40af" font-weight="700">Nodo A</text><rect x="30" y="75" width="45" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="52" y="92" text-anchor="middle" font-size="8" fill="#1e3a8a">CPU1</text><rect x="85" y="75" width="45" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="107" y="92" text-anchor="middle" font-size="8" fill="#1e3a8a">CPU2</text><rect x="30" y="115" width="100" height="50" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="80" y="140" text-anchor="middle" font-size="8" fill="#064e3b">MEM local</text><text xml:space="preserve" x="80" y="152" text-anchor="middle" font-size="7" fill="#166534">acceso rápido</text><rect x="170" y="50" width="140" height="130" fill="#eff6ff" stroke="#3b82f6" stroke-dasharray="3,3"/><text xml:space="preserve" x="240" y="66" text-anchor="middle" font-size="9" fill="#1e40af" font-weight="700">Nodo B</text><rect x="190" y="75" width="45" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="212" y="92" text-anchor="middle" font-size="8" fill="#1e3a8a">CPU3</text><rect x="245" y="75" width="45" height="26" fill="#dbeafe" stroke="#1e40af"/><text xml:space="preserve" x="267" y="92" text-anchor="middle" font-size="8" fill="#1e3a8a">CPU4</text><rect x="190" y="115" width="100" height="50" fill="#a7f3d0" stroke="#065f46"/><text xml:space="preserve" x="240" y="140" text-anchor="middle" font-size="8" fill="#064e3b">MEM local</text><text xml:space="preserve" x="240" y="152" text-anchor="middle" font-size="7" fill="#166534">acceso rápido</text><path d="M 150 140 Q 160 100 170 140" stroke="#9a3412" stroke-width="2" fill="none"/><text xml:space="preserve" x="160" y="102" text-anchor="middle" font-size="7" fill="#9a3412" font-weight="700">interconexión</text><text xml:space="preserve" x="160" y="200" text-anchor="middle" font-size="8" fill="#475569">Un solo espacio de direcciones, visible a todas</text><text xml:space="preserve" x="160" y="215" text-anchor="middle" font-size="8" fill="#7c2d12">Acceso remoto es más lento (por interconexión)</text><text xml:space="preserve" x="160" y="240" text-anchor="middle" font-size="8" fill="#475569" font-style="italic">Escala mejor · CC-NUMA usa directorios en HW</text></g></svg>
<div class="caption">Fig. 9.1 — UMA (todas las CPU con el mismo tiempo de acceso, bus compartido) vs NUMA (memoria local rápida, remota lenta, un único espacio de direcciones).</div>
</div>

**NUMA:** hay dos variantes: **NC-NUMA** (sin cache) y **CC-NUMA** (con cache; lo importante es mantener coherencia). Los CC-NUMA grandes se implementan como multiprocesadores basados en **directorios**: una base de datos en HW que indica dónde está cada línea de memoria y su estado (limpia/sucia).

**Coherencia de cache:** el problema central de la memoria compartida con caches. Un mismo dato puede estar cacheado en varias CPU; al escribir, la CPU manda mensaje al bus para invalidar/descartar copias limpias en otras caches, o forzar el write-back de una copia sucia antes de modificar.

### Chips multinúcleo

Con más transistores por chip, las opciones son: más cache (poca mejora directa), más clock (sigue con un solo hilo, y el clock está topeado por calor), o **más cores** (comparten cache/memoria y dan paralelismo real). El software tiene que estar diseñado para aprovecharlos.

### Tipos de SO multiprocesador

1. **Cada CPU con su SO** (poco usado): memoria dividida estáticamente; procesos atados a una CPU. Problemas: **desbalance** de carga, no se comparten páginas, la cache de disco puede quedar **inconsistente** entre CPUs.
2. **Maestro-Esclavo:** una sola copia del SO; **todas las syscalls van a la CPU maestra**. Resuelve balanceo y páginas, pero el maestro es **cuello de botella** con muchas CPU.
3. **SMP (Symmetric Multi-Processing):** una copia del SO, **cualquier CPU** puede ejecutarla; la syscall la corre la CPU que la invocó. Sin cuello de botella. **Problema:** varias CPU pueden estar en el kernel a la vez y competir por las mismas estructuras (elegir el mismo proceso a planificar o la misma página libre → **race condition**).

Soluciones en SMP:

- **Lock global:** todo el kernel = una sola sección crítica, una CPU a la vez. Se comporta como maestro-esclavo, mala performance.
- **Lock por estructura:** varias secciones críticas con su propio mutex. Es el enfoque más usado; mejor rendimiento pero requiere cuidado (riesgo de **deadlocks**).

### Sincronización en multiprocesador

En un uniprocesador basta con **deshabilitar interrupciones** para tocar tablas del kernel; en multiprocesador **NO alcanza**: otra CPU puede generar interrupciones. Se necesita **protocolo de mutex**.

**TSL (Test and Set Lock):** lee una palabra y la escribe en 1 en una sola operación atómica. En multiprocesador la operación **no es indivisible** si dos CPU la ejecutan al mismo tiempo: podrían leer 0 y entrar juntas. **Solución:** TSL **bloquea el bus** (requiere soporte HW). Como está esperando activamente, es un **spinlock** y genera carga (espera activa). Mejoras: variable de lock propia en cache de cada CPU, listas de espera propias por CPU, delays entre reintentos.

### Planificación en multiprocesador

Se decide **qué** hilo (KLT) ejecutar y **en qué CPU**.

**Hilos independientes (tiempo compartido):**

- **Cola única de listos:** simple, eficiente, da **balanceo de carga**. Desventaja: **contención** sobre la estructura única.
- **Problema con espera activa:** si un hilo con spinlock pierde el quantum antes de liberar el lock, las otras CPU quedan girando ociosas. Se resuelve con un flag por proceso para no expulsarlo hasta que libere (Zahorjan 1991).
- **Afinidad de CPU:** ejecutar el hilo en la CPU donde ya corrió antes (sus datos ya están en cache). **Planificación de 2 niveles:** el hilo se asigna a una CPU al crearse; **cola por-CPU**; si una CPU queda ociosa, se reparten hilos. Minimiza la contención y el tráfico de coherencia; migrar un hilo entre CPUs implica cache misses.

**Hilos que trabajan en conjunto:**

- Si se planifican independientemente, no corren sincrónicos: un hilo A0 que espera A1 puede quedar en cola mientras A1 está corriendo, duplicando el tiempo total.
- **Gang scheduling (planificación por pandillas):** los hilos relacionados forman una pandilla; corren **simultáneamente** en distintas CPU e inician/terminan el intervalo juntos. Esto acelera la comunicación entre hilos que se sincronizan.

### Multicomputadoras (clusters)

- CPU fuertemente acopladas, **sin memoria compartida**. PCs con interfaz de red de alto rendimiento (Ethernet 10-400 Gbps, Infiniband 120 Gbps; HBA para storage FibreChannel).
- **Topologías:** estrella, anillo, malla/mesh, hipercubo, full mesh.
- **Conmutación:** store-and-forward (buffer hasta armar paquete, latencia) vs circuitos (ruta fija, más rápida, sin control de flujo).
- **Problema típico:** copiado excesivo de paquetes entre RAM y placa. Soluciones: interfaz en espacio de usuario (sin pasar por kernel) o canales DMA / procesadores de red (lo actual).
- **Comunicación:** `send`/`receive` (con bloqueo, sin bloqueo + copia, sin bloqueo + interrupción) o **RPC** (invoca procedimiento remoto, transparente al programador).
- **Balanceo de carga:** enfoque por **grafo** (minimizar aristas/tráfico entre subgrafos asignados a distintas máquinas) o **distribuido** (los nodos reubican procesos si están sobrecargados).

### Sistemas distribuidos

Tanenbaum los define como "un conjunto de computadoras independientes que el usuario ve como un único sistema coherente". A diferencia de las multicomputadoras, tienen **menor acoplamiento**: nodos distribuidos por todo el mundo, PCs completas, con **distinto SO, HW y FS**.

Se apoyan en una capa de **middleware** por encima del SO, que aporta uniformidad, resuelve la heterogeneidad y da interfaces/servicios comunes (por ejemplo un directorio global de recursos).

**Cuidado con la trampa:** en un sistema distribuido los nodos **no** necesitan ejecutar el mismo SO ni tener el mismo hardware para interoperar; justamente el middleware existe para resolver esa heterogeneidad.

### Conceptos clave

- **UMA vs NUMA** (uniforme vs dependiente de local/remoto), y **NC-NUMA vs CC-NUMA** (sin cache vs con cache).
- **Memoria compartida vs distribuida:** comunicación (memoria vs mensajes), acoplamiento, retardos (nseg vs µseg/mseg).
- **SMP:** definición, ventaja (sin cuello de botella) vs maestro-esclavo. Solución de sincronización: lock global vs lock por estructura.
- **Coherencia de cache:** por qué surge y cómo se resuelve (RO/RW, copias limpias/sucias, directorios en CC-NUMA).
- **TSL/spinlock:** por qué deshabilitar interrupciones no alcanza en multiprocesador; el HW debe permitir **bloquear el bus**.
- **Afinidad de CPU** y **cola por-CPU** vs cola global; **gang scheduling** para hilos que colaboran.
- Por qué se pasó a más cores (límite de calor/clock, velocidad de la luz).
- **Middleware** como diferenciador de los sistemas distribuidos.
- En SMP, migrar un hilo entre CPUs implica **cache misses** y tráfico de coherencia (por eso el SO prefiere afinidad).

---

## 10. Deadlocks

### Definición

Un conjunto de procesos está en **deadlock** cuando cada uno está **bloqueado**, reteniendo recursos y **esperando** un recurso que está retenido por otro proceso del mismo conjunto. Ninguno avanza ni libera lo suyo. El caso mínimo es el "abrazo mortal": A tiene lo que B pide y B tiene lo que A pide.

### Recursos

- **Físicos** (CPU, memoria, dispositivos) / **lógicos** (archivos, registros, semáforos).
- **Apropiables / preemptibles:** se pueden quitar sin daño (memoria, CPU).
- **No apropiables:** si se quitan a mitad de uso, el proceso falla (una escritura a un CD o impresora a medias).
- Un recurso `Rj` puede tener varias **instancias** idénticas (clase de recurso).

Secuencia de uso: **Solicitar → Usar → Liberar**. Si al solicitar no se concede, el proceso espera.

### Las 4 condiciones de Coffman (1971) ⭐

**Deben darse las cuatro simultáneamente.** Si falta una sola, no hay deadlock. Esta es la base de la prevención.

1. **Exclusión mutua:** el recurso no es compartible; solo un proceso lo usa a la vez.
2. **Retención y espera (hold and wait):** el proceso mantiene recursos asignados mientras espera otros.
3. **No apropiación (no preemption):** no se pueden quitar los recursos a quien los posee.
4. **Espera circular (circular wait):** existe una lista circular de procesos donde cada uno espera un recurso del siguiente.

<div class="diagram">
<svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><text xml:space="preserve" x="320" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">Las 4 condiciones de Coffman — deben darse las 4 a la vez</text><rect x="10" y="35" width="150" height="120" fill="#fecaca" stroke="#991b1b" stroke-width="2"/><text xml:space="preserve" x="85" y="55" text-anchor="middle" font-weight="700" fill="#7f1d1d">1. Exclusión mutua</text><line x1="10" y1="62" x2="160" y2="62" stroke="#991b1b"/><text xml:space="preserve" x="85" y="85" text-anchor="middle" font-size="9" fill="#7f1d1d">Recurso no compartible</text><text xml:space="preserve" x="85" y="100" text-anchor="middle" font-size="9" fill="#7f1d1d">1 proceso a la vez</text><text xml:space="preserve" x="85" y="125" text-anchor="middle" font-size="8" fill="#7c2d12" font-style="italic">"solo yo puedo tenerlo"</text><rect x="170" y="35" width="150" height="120" fill="#fed7aa" stroke="#c2410c" stroke-width="2"/><text xml:space="preserve" x="245" y="55" text-anchor="middle" font-weight="700" fill="#7c2d12">2. Retención y espera</text><line x1="170" y1="62" x2="320" y2="62" stroke="#c2410c"/><text xml:space="preserve" x="245" y="85" text-anchor="middle" font-size="9" fill="#7c2d12">Retiene lo que tiene</text><text xml:space="preserve" x="245" y="100" text-anchor="middle" font-size="9" fill="#7c2d12">y pide más</text><text xml:space="preserve" x="245" y="125" text-anchor="middle" font-size="8" fill="#7c2d12" font-style="italic">"tengo A, pido B"</text><rect x="330" y="35" width="150" height="120" fill="#fef3c7" stroke="#b45309" stroke-width="2"/><text xml:space="preserve" x="405" y="55" text-anchor="middle" font-weight="700" fill="#78350f">3. No apropiación</text><line x1="330" y1="62" x2="480" y2="62" stroke="#b45309"/><text xml:space="preserve" x="405" y="85" text-anchor="middle" font-size="9" fill="#78350f">Nadie le puede quitar</text><text xml:space="preserve" x="405" y="100" text-anchor="middle" font-size="9" fill="#78350f">el recurso</text><text xml:space="preserve" x="405" y="125" text-anchor="middle" font-size="8" fill="#7c2d12" font-style="italic">"solo yo lo libero"</text><rect x="490" y="35" width="140" height="120" fill="#e0e7ff" stroke="#3730a3" stroke-width="2"/><text xml:space="preserve" x="560" y="55" text-anchor="middle" font-weight="700" fill="#312e81">4. Espera circular</text><line x1="490" y1="62" x2="630" y2="62" stroke="#3730a3"/><text xml:space="preserve" x="560" y="85" text-anchor="middle" font-size="9" fill="#312e81">Ciclo P1→P2→...→P1</text><text xml:space="preserve" x="560" y="100" text-anchor="middle" font-size="9" fill="#312e81">esperándose entre sí</text><text xml:space="preserve" x="560" y="125" text-anchor="middle" font-size="8" fill="#312e81" font-style="italic">"todos se esperan"</text><text xml:space="preserve" x="320" y="185" text-anchor="middle" font-size="9" fill="#7c2d12" font-weight="700">Prevención = romper al menos UNA de estas condiciones.</text></svg>
<div class="caption">Fig. 10.2 — Las 4 condiciones de Coffman. Si falta una sola, no hay deadlock.</div>
</div>

### Grafo de asignación de recursos

Se representan procesos como círculos (`Pi`), recursos como rectángulos (`Rj`), y con puntos internos las instancias del recurso. Las **aristas dirigidas**:

- `Pi → Rj`: el proceso **solicita** una instancia.
- `Rj → Pi`: el recurso está **asignado** al proceso.

Interpretación:

| Estado del grafo | Resultado |
|---|---|
| **Sin ciclos** | No hay deadlock (seguro) |
| **Con ciclo + 1 instancia por recurso** | **Sí hay** deadlock (ciclo es condición necesaria **y suficiente**) |
| **Con ciclo + varias instancias** | **Posibilidad** de deadlock (necesario, NO suficiente) |

<div class="diagram">
<svg viewBox="0 0 620 240" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif" font-size="10"><defs><marker id="darr" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#0f172a"/></marker></defs><text xml:space="preserve" x="310" y="16" text-anchor="middle" font-weight="700" fill="#0f172a">Grafo de asignación de recursos con ciclo → deadlock</text><circle cx="120" cy="90" r="24" fill="#f0abfc" stroke="#701a75" stroke-width="2"/><text xml:space="preserve" x="120" y="94" text-anchor="middle" font-weight="700" fill="#4a044e">P1</text><circle cx="380" cy="90" r="24" fill="#f0abfc" stroke="#701a75" stroke-width="2"/><text xml:space="preserve" x="380" y="94" text-anchor="middle" font-weight="700" fill="#4a044e">P2</text><rect x="230" y="30" width="50" height="50" fill="#fef3c7" stroke="#b45309" stroke-width="2"/><circle cx="255" cy="55" r="3" fill="#78350f"/><text xml:space="preserve" x="255" y="98" text-anchor="middle" font-size="10" font-weight="700" fill="#78350f">R1</text><rect x="230" y="140" width="50" height="50" fill="#fef3c7" stroke="#b45309" stroke-width="2"/><circle cx="255" cy="165" r="3" fill="#78350f"/><text xml:space="preserve" x="255" y="208" text-anchor="middle" font-size="10" font-weight="700" fill="#78350f">R2</text><line x1="230" y1="55" x2="144" y2="82" stroke="#166534" stroke-width="2" marker-end="url(#darr)"/><text xml:space="preserve" x="175" y="60" font-size="8" fill="#166534" font-weight="700">asignado</text><line x1="140" y1="105" x2="230" y2="160" stroke="#c2410c" stroke-width="2" marker-end="url(#darr)"/><text xml:space="preserve" x="150" y="145" font-size="8" fill="#c2410c" font-weight="700">solicita</text><line x1="280" y1="165" x2="360" y2="105" stroke="#166534" stroke-width="2" marker-end="url(#darr)"/><text xml:space="preserve" x="325" y="150" font-size="8" fill="#166534" font-weight="700">asignado</text><line x1="360" y1="82" x2="280" y2="55" stroke="#c2410c" stroke-width="2" marker-end="url(#darr)"/><text xml:space="preserve" x="320" y="55" font-size="8" fill="#c2410c" font-weight="700">solicita</text><rect x="440" y="35" width="160" height="80" fill="#fff7ed" stroke="#f97316"/><text xml:space="preserve" x="520" y="52" text-anchor="middle" font-size="9" font-weight="700" fill="#9a3412">DEADLOCK</text><text xml:space="preserve" x="450" y="70" font-size="8" fill="#7c2d12">P1 tiene R1, pide R2</text><text xml:space="preserve" x="450" y="83" font-size="8" fill="#7c2d12">P2 tiene R2, pide R1</text><text xml:space="preserve" x="450" y="98" font-size="8" fill="#7c2d12">Ciclo + 1 instancia c/u:</text><text xml:space="preserve" x="450" y="110" font-size="8" fill="#7c2d12" font-weight="700">→ necesario Y suficiente</text><text xml:space="preserve" x="310" y="230" text-anchor="middle" font-size="8" fill="#475569" font-style="italic">Con varias instancias por recurso, el ciclo es solo condición necesaria (posibilidad).</text></svg>
<div class="caption">Fig. 10.1 — Grafo de asignación de recursos con abrazo mortal entre P1 y P2.</div>
</div>

### Estrategias de manejo

| Estrategia | Idea | Cómo |
|---|---|---|
| **Prevención** | Que **nunca** se cumpla una de las 4 condiciones | Restringe la forma de solicitar recursos |
| **Evitación (avoidance)** | Asignar con cuidado según el estado del sistema | **Algoritmo del Banquero** |
| **Detección y recuperación** | Permitir el deadlock y luego romperlo | Grafo wait-for; abortar procesos / expropiar (selección de víctima) |
| **Avestruz (ostrich)** | Ignorar el problema | Asumir que casi nunca ocurre (lo usan UNIX/Windows en la práctica) |

**Prevención — cómo atacar cada condición:**

- **Exclusión mutua:** hacer recursos compartibles / spooling (no siempre posible).
- **Retención y espera:** reservar TODOS los recursos al inicio, o solo pedir cuando no se tiene nada. Riesgo: starvation, baja utilización.
- **No apropiación:** virtualizar el recurso vía un demonio que encola las peticiones (spooler).
- **Espera circular:** ordenar los recursos con una función `F: R → N`; solo se puede pedir `Rj` si el mayor `Ri` que se tiene cumple `F(Ri) < F(Rj)`.

### Estado seguro vs inseguro ⭐

- **Estado seguro:** existe una **cadena segura** `<P0, ..., Pn>` con todos los procesos que pueden completar su ejecución con los recursos disponibles (en algún orden). Garantiza que **no hay deadlock**.
- **Estado inseguro:** no se puede construir esa cadena. **Posibilidad** de deadlock, no implica deadlock seguro.
- **Si hay deadlock, el estado es inseguro**; la recíproca **no vale**.

### Algoritmo del Banquero (múltiples instancias) ⭐

Cada proceso declara su **máximo** de instancias que puede necesitar. El SO solo asigna recursos si el estado resultante sigue siendo **seguro**.

Estructuras:

- `disponible` (vector `m`): instancias libres por recurso.
- `asignacion` (matriz `n × m`): lo que cada `Pi` ya tiene.
- `max` (matriz `n × m`): máximo que `Pi` necesitará.
- `need = max − asignacion`: lo que le falta a cada proceso.

El algoritmo busca una **secuencia segura**: intenta encontrar un `Pi` cuyo `need` sea ≤ `disponible`; si lo encuentra, simula que `Pi` termina, libera sus recursos, y busca otro. Si al final logró que todos terminen, el estado es seguro.

Para **1 instancia por recurso** no hace falta banquero: basta el grafo de asignación y verificar que no haya ciclos.

### Deadlock vs Starvation

| Deadlock | Starvation |
|---|---|
| Conjunto de procesos **bloqueados mutuamente**, ninguno progresa | Un proceso **nunca obtiene** el recurso (siempre pospuesto) |
| Espera **circular** entre ellos | No requiere ciclo; suele ser por planificación / prioridades |
| Se rompe matando/expropiando | Se evita con políticas justas (aging, FIFO) |

En la recuperación por selección de víctima, hay que evitar elegir siempre al mismo proceso para no generar starvation.

<div class="callout warning">
<div class="callout-title">⚠ Trampas típicas del parcial</div>

- Nombrar las **4 condiciones de Coffman** y saber que las 4 deben darse simultáneamente.
- Interpretar el grafo: ciclo + una instancia por recurso = deadlock (necesario y suficiente); ciclo + varias instancias = solo posibilidad.
- Diferencia entre las 4 estrategias, y cómo prevención ataca cada condición.
- Diferencia **estado seguro vs inseguro** (inseguro ≠ deadlock; deadlock ⇒ inseguro).
- Algoritmo del Banquero: reconocer las estructuras y saber construir/justificar una secuencia segura.
- **Deadlock ≠ starvation:** deadlock = bloqueo circular mutuo; starvation = postergación infinita, sin necesidad de ciclo.

</div>
---

## 11. Lo que más cae en el parcial

Basado en el análisis de parciales 2022, 2023 (1ra y 2da fecha), 2025 (1ra fecha) y 2026 (1ra fecha), estas son las preguntas y bloques temáticos que se repiten. Reservá los últimos días de estudio para revisar bien estos ítems.

### Preguntas conceptuales que aparecieron literales o casi literales

**Kernel y compilación:**

- "¿Qué es el kernel? ¿Cuáles son sus funciones principales?" (2023).
- "Explique la arquitectura del kernel Linux, tipo, modularidad y portabilidad" (2025).
- "¿Qué contiene el initramfs? ¿Bajo qué condiciones puede no ser necesario?" (2023 y 2025).
- "Motivos para compilar un kernel" (2023).
- "Al compilar con `make modules_install && make install`, ¿en qué directorios se instalan el kernel y los módulos?" (2026).
- V/F: "El kernel de Linux es un SO en sentido estricto porque contiene todo lo necesario para gestionar hardware y procesos" (2026) → **Falso**.
- V/F: "En un microkernel los drivers y servidores de FS se ejecutan en modo kernel para mejorar el rendimiento" (2026) → **Falso**.

**Módulos y drivers:**

- "¿Qué es un módulo y qué ventaja da compilar como módulo vs built-in?" (2023 y 2025).
- V/F: "Los drivers acceden a las funcionalidades del kernel a través de system calls" (2023) → **Falso** (acceso directo por API interna).
- "¿Para qué se usa `register_chrdev()`? ¿Se puede usar en espacio de usuario o de kernel?" (2023) → **Solo en espacio de kernel**.
- "¿Qué sucede cuando se carga un módulo con `insmod`?" — multiple choice, respuesta: el módulo se carga en espacio de kernel, se inicializa con `init_module` y puede registrar interfaces (2025).

**/dev y device files:**

- "¿Qué tipos de archivos hay en `/dev` y qué representan?" (2023).
- Interpretación del output `brw-rw---- 1 root root 240, 0 weird`: multiple choice → **dispositivo de bloques + major 240 identifica al driver**; no son "240 bytes" ni "escribir con echo aumenta el tamaño" (2026).

**System calls:**

- V/F múltiple: "libc es el componente del kernel donde se definen las syscalls" → **Falso**; "las syscalls son módulos administrables con insmod/rmmod" → **Falso**; "las syscalls se ejecutan en modo privilegiado e identificadas por un número" → **Verdadero**; "cada driver implementa una syscall" → **Falso** (2023).
- V/F: "libc implementa directamente las syscalls en modo kernel sin trap ni interrupción" (2026) → **Falso**.
- V/F: "La tabla de syscalls (`syscall_64.tbl`) permite que el dispatcher identifique qué función ejecutar según el número del registro" (2026) → **Verdadero**.
- "¿Qué es una syscall y cuál es su propósito principal? ¿Cómo se implementa una nueva?" (2025).

**Threads:**

- "¿Quién planifica los ULT y los KLT? ¿Cómo afecta al multinúcleo?" (2025).
- "¿Qué características tendrá el proceso creado si se ejecuta `fork()` pero no `exec()`?" (2025).
- V/F: "Un hilo es la unidad básica de utilización de CPU en los SO modernos" (2026) → **Verdadero**.
- V/F: "Un ULT en M:1 puede aprovechar directamente múltiples procesadores físicos sin ningún mecanismo adicional" (2026) → **Falso**.
- V/F: "Si un proceso crea N ULTs entonces con `strace` podemos observar que invoca N veces `clone3`" (2026) → **Falso** (los ULT no llegan al kernel).

**Virtualización:**

- "Diferencia entre Hypervisors tipo 1 y tipo 2" (2025).
- V/F: "El SO guest tiene acceso directo y completo al HW real sin intermediación" (2026) → **Falso**.
- V/F: "En hypervisor tipo 2 el SO host se ejecuta directamente sobre el HW físico y gestiona los drivers reales" (2026) → **Verdadero**.

**cgroups y namespaces:**

- "¿Qué mecanismo del kernel Linux permite limitar el uso de CPU de un proceso a un 80%?" (2023) → **cgroups**.
- "Describa brevemente las funcionalidades de CGroups y Namespaces" (2025).
- "¿Por qué `mi_proceso` tiene distinto PID visto desde el contenedor y desde el host?" (2023) → **PID namespace**.

**Docker:**

- "¿Qué es una imagen? ¿Y un contenedor? ¿Cómo se relacionan?" (2023, 2025, 2026).
- "¿Qué características del kernel usa Docker para proveer containers?" (2023).
- "¿Qué es un Union Filesystem? ¿Cómo lo usa Docker?" (2023 y 2025).
- "¿Qué es el archivo compose y en qué se diferencia de un Dockerfile?" (2023).
- "Dos formas de persistir datos en Docker (volumes vs bind mounts)" (2023).
- V/F: "Docker usa una arquitectura cliente-servidor donde `dockerd` es el servidor responsable de crear, ejecutar y monitorear los contenedores" (2026) → **Verdadero**.
- V/F: "Al remover un archivo dentro de un Dockerfile con `RUN rm`, el archivo se elimina definitivamente de la imagen reduciendo su tamaño total" (2026) → **Falso**.

**File Systems / RAID / LVM:**

- "Defina inodo, bloque y extent" (2023).
- "¿Qué es un link simbólico? ¿En qué se diferencia de un hard-link? ¿Cuál/es consumen un i-nodo?" (2023 2da fecha).
- "Describa cómo BTRFS usa CoW" (2023 2da fecha).
- "Describa RAID 5 y responda cuántos discos pueden fallar sin pérdida" (2023 2da fecha).
- V/F: "RAID 1 provee striping y paridad distribuida" (2023) → **Falso**.

**Seguridad:**

- "¿Qué es ASLR? ¿Linux lo provee para procesos de usuario? ¿Y para el kernel?" (2025 y 2026) → **Sí para ambos, KASLR aparte**. Puede activarse/desactivarse sin recompilar (con `/proc/sys/kernel/randomize_va_space`).
- V/F: "Un sistema con muchas features tiende a ser más seguro porque ofrece más herramientas de defensa" (2026) → **Falso** (más superficie de ataque).
- V/F: "Un dominio de protección es un conjunto de pares (objeto, derecho)" (2026) → **Verdadero**.

**Multiprocesadores y distribuidos:**

- V/F: "En gang scheduling todos los hilos de un proceso se programan simultáneamente en distintas CPUs durante el mismo intervalo" (2026) → **Verdadero**.
- V/F: "En un sistema distribuido todos los nodos deben ejecutar el mismo SO y disponer del mismo hardware para garantizar la interoperabilidad" (2026) → **Falso**.

### Bloques de contenido que casi siempre están

1. **Definición de kernel + funciones + tipo (monolítico híbrido) + portabilidad.** Aparece en 2 de las 3 primeras fechas relevadas.
2. **Módulos vs built-in + qué hace `insmod`.**
3. **Contenido y utilidad del initramfs.**
4. **Naturaleza de las syscalls y de libc.** Suele venir como multiple choice.
5. **ULT vs KLT + fork sin exec.**
6. **Imagen vs contenedor + qué usa Docker del kernel + Union FS.**
7. **cgroups (limitar CPU) + namespaces (doble PID).**
8. **ASLR (para usuario y para kernel).**
9. **File system básico (inodo/bloque/extent) + links + BTRFS + RAID 5.**
10. **Gang scheduling y sistemas distribuidos (interoperabilidad heterogénea).**

### Formato del parcial

Las preguntas son de tres tipos:

- **Conceptuales cortas** ("explique X en sus palabras").
- **Verdadero/falso con justificación breve** — pesan mucho; hay que justificar aunque parezca obvio.
- **Multiple choice** con opciones plausibles ("A y C", "todas", "ninguna"). Estudiá bien las opciones cercanas: el error típico es marcar la que parece "más verdadera" sin descartar las incorrectas.

<div class="callout success">
<div class="callout-title">🎯 Estrategia de últimos días</div>

1. **Día 1-2 (mientras leés esto en el iPad):** lectura corrida del resumen, tema por tema. No pares a memorizar todavía, dejá que el mapa mental se arme.
2. **Día 3-4:** re-lectura activa; para cada bloque, cerrá los ojos y trata de reproducir sus 5-10 puntos clave. Volvé a los "trampas típicas" al final de cada capítulo — son las que más caen.
3. **Día 5-6:** hacé de memoria los parciales viejos (2023 primera y segunda, 2025 primera, 2026). Anotá dónde te trabás y volvé al capítulo correspondiente. El 2026 tiene muchos V/F concentrados; ideal para simulacro rápido.
4. **Día 7-9:** repaso de "trampas típicas" y cheatsheet (`Infogramas_Parcial/00_INDICE_y_cheatsheet.md`). Enfocá en RAID/LVM y en las respuestas V/F contraintuitivas (paravirtualización modifica el guest; setuid usa privilegios del dueño no del que ejecuta; snapshots LVM no copian nada al crearse; etc.).
5. **Día 10 (víspera):** revisá solo esta sección 11 y las tablas comparativas. Descansá y llegá fresco.

</div>

<div class="end-marker">exit 0</div>
