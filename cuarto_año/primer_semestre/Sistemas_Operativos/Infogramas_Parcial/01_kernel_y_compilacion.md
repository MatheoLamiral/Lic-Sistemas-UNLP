# Infograma de Repaso: Kernel de Linux y Compilación

> Repaso denso para parcial de Sistemas Operativos (UNLP). Leé la sección de **Trampas** al final.

---

## 1. ¿Qué es el Kernel?

- **Porción de código** que reside en **memoria principal** y administra los recursos. Actúa como **API/intermediario entre el hardware y las aplicaciones**.
- Es **"el encargado de que el software y el hardware trabajen juntos"**.
- En **sentido estricto, el Kernel ES el Sistema Operativo** (el resto —shell, herramientas— son componentes del SO, no el SO en sí).
- Provee acceso seguro al HW vía **system calls**. Un proceso de usuario no puede hacer nada fuera de su espacio de direcciones sin pedírselo al kernel.

### Las 5 funciones principales
1. **Administración de memoria principal** (asigna, gestiona y protege).
2. **Manejo del uso de la CPU** (planificación / scheduling).
3. **Administración de procesos** (ciclo de vida completo).
4. **Gestión de E/S** (acceso a dispositivos y periféricos).
5. **Comunicación y Concurrencia** (IPC, sincronización segura).

### Modos de ejecución (los provee el HW)
- **Modo Supervisor / Kernel / privilegiado**: acceso al **conjunto completo de instrucciones** (HW, memoria, CPU). Instrucciones privilegiadas **solo** acá.
- **Modo Usuario**: el proceso accede solo a **su propio espacio**, con instrucciones reducidas.
- El **bit de modo** en la CPU indica el modo actual. Arranca en **supervisor**; al ceder control a un proceso se pone en **usuario**. La **única** forma de volver a modo kernel es vía **trap o interrupción** (no lo decide el proceso de usuario).

---

## 2. Tipos de Kernel

| Tipo | Idea clave | Dónde corren los servicios | Ejemplos |
|---|---|---|---|
| **Monolítico** | Toda la funcionalidad en **un solo bloque** linkeado | Todo en **modo supervisor** | Unix, FreeBSD |
| **Microkernel** | **Mínimo** código en modo supervisor (procesos, memoria, E/S básica) | El resto en **modo usuario** | Minix, QNX |
| **Monolítico HÍBRIDO** | Monolítico **+** capacidad de cargar/descargar **módulos** en runtime | Núcleo y módulos en **modo kernel** | **GNU/Linux**, Windows NT, macOS (XNU) |

### ¿Por qué Linux es monolítico-híbrido?
- **Monolítico**: toda la funcionalidad del SO está **linkeada en una sola imagen** que corre en modo privilegiado (máxima eficiencia, sin cambios de modo internos).
- **Híbrido**: permite **cargar y descargar funcionalidad en runtime mediante módulos** (sin reiniciar). Ojo: el módulo, una vez cargado, **también corre en modo kernel** (un bug puede colgar todo el sistema).

---

## 3. Portabilidad

- Linux es **altamente portable**: una **misma estructura de código fuente da soporte a TODAS las arquitecturas**.
- Esto se logra porque está escrito **mayoritariamente en C** (fácilmente modificable/recompilable para distintas arquitecturas de CPU), reservando **Assembler solo para instrucciones especiales y de bajo nivel**. (Rust desde v6.1, sobre todo para módulos).
- **CLAVE:** la portabilidad NO significa que el **mismo binario** corra en cualquier arquitectura, sino que el **código** se adapta/recompila fácilmente para cada una.

---

## 4. ¿Por qué (re)compilar el kernel?

- **Soportar nuevos dispositivos** (ej.: placa de video).
- **Agregar funcionalidad** (nuevos filesystems, protocolos de red).
- **Optimizar** el rendimiento según el HW donde corre.
- **Adaptar / limpiar**: quitar soporte de hardware que no se usa → kernel más chico.
- **Corregir bugs** (errores de programación o vulnerabilidades de seguridad).

---

## 5. Los 7 PASOS de Compilación (EN ORDEN)

1. **Obtener el código fuente** (desde `kernel.org`).
2. **Preparar el árbol de archivos** del código fuente (descomprimir, aplicar parches).
3. **Configurar el código fuente** (generar el `.config`).
4. **Construir el kernel** a partir del código fuente **e instalar los módulos**.
5. **Reubicar el kernel** y **crear el disco RAM inicial (initrd/initramfs)**.
6. **Configurar y ejecutar el gestor de arranque** (GRUB/LILO).
7. **Reiniciar y probar** el nuevo kernel.

### Herramientas y comandos clave
- **`gcc`** (compilador C), **`make`** (ejecuta directivas de los **Makefiles**), **`binutils`** (assembler/linker), **`libc6`**, **`ncurses`** (solo para `menuconfig`), **`initrd-tools`**.
- **`make`** compara la **fecha de modificación** de cada target con sus dependencias: solo recompila lo desactualizado.
- **`make -j$(nproc)`**: compila en paralelo según cantidad de CPUs.
- **`make modules_install`**: copia los `.ko` a `/lib/modules/<versión>`.
- **`make install`**: copia `bzImage` → `/boot/vmlinuz-<v>`, `System.map`, `.config`, genera el initramfs y actualiza GRUB.

### Configuración del kernel (`.config`)
- **`make config`**: texto secuencial, pregunta opción por opción (tedioso, sin dependencias extra).
- **`make menuconfig`**: menús navegables en terminal (requiere **ncurses**). El más usado, ideal en servidores/SSH.
- **`make xconfig`**: GUI gráfica (requiere entorno X).
- En `menuconfig`, la barra espaciadora cicla: **`<*>` built-in**, **`<M>` módulo**, **`< >` deshabilitado**.

### Parches
- **Parche** = archivo de **diff** que indica qué código agregar/quitar sobre una versión base.
- Se aplican con el comando **`patch`**, frecuentemente vía pipe: `xzcat ../patch-6.13.7.xz | patch -p1` (el `-p1` ignora el primer nivel de directorio `a/` o `b/`).
- Pueden ser **incrementales** (sobre la versión inmediatamente anterior) o **no incrementales** (sobre el mainline). `--dry-run` simula sin modificar.

---

## 6. Gestor de arranque: ¿por qué reconfigurarlo?

- Tras compilar e instalar, el GRUB **NO detecta el nuevo kernel automáticamente**.
- Reconfigurarlo (ej.: **`update-grub`/`update-grub2`**) **actualiza el menú de arranque incorporando el nuevo kernel en la configuración** (`grub.cfg`).
- **NO reinstala el binario del gestor**: solo actualiza su archivo de configuración con las rutas de la nueva imagen y su initramfs.

---

## 7. initramfs / initrd

- **Sistema de archivos temporal en RAM**, montado en el arranque **ANTES de montar el root real**.
- Contiene los **módulos, drivers y programas mínimos** que el kernel necesita para poder **montar el filesystem raíz** definitivo. Una vez montado el root, se desmonta.
- **PUEDE NO SER NECESARIO**: si todos los drivers y FS críticos para montar el root están compilados **built-in (`<*>`)** dentro del kernel, el initramfs deja de ser un requisito estricto.

---

## 8. Módulo vs Built-in

- **Built-in (`<*>`)**: compilado dentro de la imagen del kernel. Más eficiente (acceso directo, no se carga en memoria aparte), pero fijo.
- **Módulo (`<M>`)** — ventajas:
  - **Memoria**: solo se carga cuando se necesita (`/lib/modules/<versión>`).
  - **Sin reiniciar**: se carga/descarga **en caliente** (`modprobe`, `lsmod`).
  - **Desarrollo ágil**: facilita el desarrollo y mantenimiento modular.
  - Contra: corre en **modo kernel**, un bug puede comprometer todo el sistema.

---

## ⚠️ Trampas típicas de parcial

- **"Linux es monolítico-híbrido PORQUE permite cargar/descargar funcionalidades vía módulos"** → **VERDADERO**.
- **"Linux es portable porque su código puede modificarse fácilmente para distintas arquitecturas de CPU"** → **VERDADERO**. (NO es porque el mismo **binario** corra en cualquier arquitectura).
- **Reconfigurar el gestor de arranque = actualizar el menú con el nuevo kernel** (opción correcta). NO reinstala el binario del gestor.
- **initramfs**:
  - "Aloja módulos del kernel y programas útiles para el arranque" → **V**.
  - "No siempre es necesario" → **V** (si todo está built-in).
  - **NO** inicializa la RAM con ceros → eso es FALSO.
- **El kernel**:
  - "Es el encargado de que SW y HW trabajen juntos" → **V**.
  - "Administra memoria principal y uso de CPU" → **V**.
  - **Puedo tener más de un kernel compilado en la misma máquina** → **V** (GRUB lista varios; permite volver atrás si el nuevo no arranca).
