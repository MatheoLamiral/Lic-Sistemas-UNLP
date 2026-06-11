## Ejercicio 1:​ ¿Cómo se denomina en GNU/Linux a la porción de código que se agrega al kernel en tiempo de ejecución? ¿Es necesario reiniciar el sistema al cargarlo? Si no se pudiera utilizar esto. ¿Cómo deberíamos hacer para proveer la misma funcionalidad en Gnu/Linux?

En GNU/Linux, la porción de código que se agrega al kernel en tiempo de ejecución se denomina **módulo del kernel** (LKM, *Loadable Kernel Module*). Se trata de un archivo objeto con extensión `.ko` (*kernel object*) que puede cargarse y descargarse dinámicamente mediante comandos como `insmod`, `modprobe` y `rmmod`.

**No es necesario reiniciar el sistema** al cargarlo, esa es justamente su principal ventaja, ya que el módulo se integra al kernel en ejecución sin interrumpir el funcionamiento del sistema.

Si no se pudieran utilizar módulos, para proveer la misma funcionalidad habría que **compilar el código directamente dentro de la imagen del kernel** (kernel monolítico estático). Esto implicaría:
- Modificar el código fuente del kernel para incluir la nueva funcionalidad.
- Recompilar el kernel completo.
- Instalar la nueva imagen y **reiniciar el sistema** para que los cambios tengan efecto.

Esto haría al kernel más grande, menos flexible y obligaría a reiniciar cada vez que se quisiera agregar, modificar o quitar funcionalidad.

## Ejercicio 2:​ ¿Qué es un driver? ¿Para qué se utiliza?

Un **driver** (o **controlador de dispositivo**) es una porción de código del kernel que actúa como **intermediario entre el sistema operativo y un dispositivo de hardware** específico. Su función es traducir las operaciones genéricas que el SO quiere realizar (leer, escribir, abrir, cerrar, configurar) a las instrucciones concretas que ese hardware en particular entiende.

**Se utiliza para:**
- **Abstraer el hardware**: el SO y las aplicaciones no necesitan conocer los detalles del dispositivo.
- **Comunicar al kernel con el dispositivo**: el driver le indica al kernel **qué hacer** cuando se lee o escribe sobre el device file. Esto se implementa mediante la estructura `struct file_operations`, que asocia cada operación (read, write, open, release) con una función específica del driver.
- **Registrar el dispositivo** en el kernel (por ejemplo, con `register_chrdev` para dispositivos de caracter) asociándolo a un *major number* que lo identifica.

En GNU/Linux, los drivers se implementan típicamente como **módulos de carga dinámica** (`.ko`), lo que permite cargarlos y descargarlos en tiempo de ejecución sin recompilar ni reiniciar el kernel. De hecho, los drivers representan aproximadamente el **68.8% del código** del kernel Linux y se ejecutan en **modo privilegiado** (modo kernel), por lo que un bug en un driver puede afectar la estabilidad de todo el sistema.

## Ejercicio 3:​ ¿Por qué es necesario escribir drivers?

Es necesario escribir drivers porque **cada dispositivo de hardware tiene su propio protocolo, registros e interfaz de comunicación**, y el kernel no puede conocer de antemano cómo interactuar con cada uno. Las razones principales son:

- **Diversidad de hardware**: existen miles de dispositivos distintos (tarjetas de red, discos, GPUs, sensores, impresoras, etc.) y cada fabricante puede implementar su propio protocolo. Sin un driver, el SO no sabría cómo comunicarse con ese hardware.
- **Abstracción del hardware**: el driver expone una interfaz uniforme (operaciones de archivo: `read`, `write`, `open`, etc.) que permite que las aplicaciones y el resto del kernel trabajen sin conocer los detalles del dispositivo.
- **Hardware nuevo**: cuando aparece un dispositivo que el kernel no soporta, hay que escribir un driver que sepa hablar con él.
- **Mantener el kernel modular y portable**: en GNU/Linux los drivers conforman el ~68.8% del código del kernel; escribirlos como módulos permite que el kernel base no necesite conocer todo el hardware posible.

## Ejercicio 4:​ ¿Cuál es la relación entre módulo y driver en GNU/Linux?

En GNU/Linux **los drivers se implementan típicamente como módulos del kernel** (LKM). Es decir:

- Un **módulo** es un mecanismo genérico para extender la funcionalidad del kernel en caliente (cargarlo/descargarlo sin reiniciar). Puede contener cualquier tipo de código: drivers, sistemas de archivos, módulos de seguridad, protocolos de red, etc.
- Un **driver** es código que controla un dispositivo de hardware específico.

La relación es que todo driver puede ser un módulo, pero no todo módulo es un driver. En la práctica, los drivers se distribuyen como módulos (`.ko`) y se cargan dinámicamente con `insmod` o `modprobe`. También pueden compilarse directamente dentro del binario del kernel (*built-in*), pero al hacerlo se pierde la posibilidad de cargarlos/descargarlos en tiempo de ejecución.

## Ejercicio 5:​ ¿Qué implicancias puede tener un bug en un driver o módulo?

Las implicancias son **graves** porque tanto módulos como drivers se ejecutan en **modo Kernel (privilegiado)** y comparten el mismo espacio de direcciones que el resto del kernel. Un bug puede:

- **Colgar todo el sistema operativo** (no solo un proceso). En UNIX/Linux esto se manifiesta como un **Kernel Panic**, en Windows como una **BSOD (Blue Screen of Death)**.
- **Corromper memoria del kernel** o de otros subsistemas, ya que no existe aislamiento entre módulos: todos viven en el mismo espacio de memoria.
- **Comprometer la seguridad del sistema**: al ejecutarse con máximos privilegios, un bug puede ser explotado para escalar privilegios o acceder a recursos protegidos.
- **Acceder a hardware sin restricciones**, pudiendo dañar el estado del dispositivo o dejarlo en un estado inconsistente.

>[!NOTE]
> Esto es una consecuencia del diseño del kernel monolítico de Linux. **La tasa de errores en drivers es 7 veces mayor que en el resto del kernel**, y los drivers representan el 68.8% del código, lo que los convierte en la principal fuente de inestabilidad. En un microkernel, en cambio, los drivers corren en espacio de usuario y un fallo no comprometería todo el SO.

## Ejercicio 6:​ ¿Qué tipos de drivers existen en GNU/Linux?

En GNU/Linux los drivers se clasifican según el tipo de dispositivo que controlan:

### Drivers de dispositivos de bloque (*block devices*)
- Acceden a los datos en **bloques de tamaño fijo** (generalmente 1024 bytes o múltiplos).
- Permiten **acceso aleatorio** (se puede leer/escribir cualquier bloque).
- Suelen estar bufereados por el kernel.
- Ejemplos: discos rígidos, SSD, pendrives, particiones (`/dev/sda`, `/dev/nvme0n1`).

### Drivers de dispositivos de caracter (*character devices*)
- Acceden a los datos **byte a byte** de forma **secuencial** (cada byte solo puede leerse una vez).
- No permiten acceso aleatorio.
- Ejemplos: mouse, teclado, puerto serie, tarjeta de sonido, terminales (`/dev/tty`, `/dev/random`).

### Drivers de red (*network devices*)
- Manejan dispositivos de red (interfaces Ethernet, WiFi, etc.).
- **No se representan como archivos**, sino que se manejan a través de la API de sockets y se identifican por nombre de interfaz (`eth0`, `wlan0`).
- Trabajan con paquetes en lugar de flujos de bytes o bloques.

A cada tipo de dispositivo se le asigna un **major number** que lo identifica (por ejemplo, discos SCSI = major 8), y un **minor number** que distingue instancias dentro del mismo tipo.

## Ejercicio 7:​ ¿Qué hay en el directorio `/dev`? ¿Qué tipos de archivo encontramos en esa ubicación?

El directorio `/dev` contiene los **device files** (archivos de dispositivo), que son la representación como archivos de cada dispositivo de hardware del sistema. Esta es una abstracción característica de UNIX. Cada dispositivo se trata como un archivo sobre el cual se pueden hacer operaciones (`read`, `write`, `open`, `close`), y el driver correspondiente traduce esas operaciones a las instrucciones reales del hardware.

Los device files no contienen datos en sí mismos, sino que son **puntos de acceso al driver**. Se crean mediante el comando:

```bash
mknod [-m <mode>] <file-name> [b|c] <major-number> <minor-number>
```

### Tipos de archivo que se encuentran en `/dev`

| Tipo | Identificación (`ls -l`) | Descripción |
|---|---|---|
| **Archivos de bloque** | `b` al inicio (ej: `brw-rw----`) | Representan dispositivos de bloque (discos, particiones). Ejemplo: `/dev/sda`, `/dev/sda1` |
| **Archivos de caracter** | `c` al inicio (ej: `crw-rw----`) | Representan dispositivos de caracter (mouse, terminal, sonido). Ejemplo: `/dev/tty`, `/dev/null` |

Cada device file está identificado por dos números:
- **Major number**: identifica el tipo de dispositivo / driver asociado.
- **Minor number**: identifica la instancia particular dentro de ese tipo.

> [!NOTE] 
> En `/dev` también pueden encontrarse **enlaces simbólicos** (ej: `/dev/stdin` → `/proc/self/fd/0`) y **sockets/pipes** especiales, aunque no son device files propiamente dichos.

## Ejercicio 8:​ ¿Para qué sirven el archivo `/lib/modules/<version> modules.dep` utilizado por el comando modprobe?

El archivo `/lib/modules/<version>/modules.dep` contiene la **información de dependencias entre módulos** del kernel. Es decir, indica qué módulos dependen de otros para funcionar correctamente.

- Es **generado automáticamente** por el comando `depmod` (por defecto `depmod -a` lo escribe en `/lib/modules/<version>/modules.dep`).
- Lo utiliza el comando **`modprobe`** para cargar módulos de forma "inteligente": cuando se quiere cargar un módulo que depende de otros, `modprobe` consulta este archivo y **carga primero todas sus dependencias** en el orden correcto, evitando errores de símbolos no resueltos.
- A diferencia de `insmod`, que carga un único módulo y falla si faltan dependencias, `modprobe` resuelve la cadena completa de forma automática gracias a `modules.dep`.

En síntesis: **`modules.dep` es el "mapa de dependencias" que permite que `modprobe` cargue módulos junto con todo lo que necesitan para operar.**

## Ejercicio 9:​ ¿En qué momento/s se genera o actualiza un initramfs?

Un **initramfs** (*initial RAM filesystem*) es un sistema de archivos temporal que se monta durante el arranque del sistema y contiene los **ejecutables, drivers y módulos necesarios para iniciar el sistema** (por ejemplo, los drivers del disco donde está el rootfs real). Luego del arranque se desmonta.

Se genera o actualiza en los siguientes momentos:

1. **Al compilar e instalar un kernel nuevo**: una vez instalado el kernel y sus módulos (`make modules_install`), se crea el initramfs asociado a esa versión con `mkinitramfs`:
    ```bash
        # mkinitramfs -o /boot/initrd.img-6.13.7 6.13.7
    ```
2. **Al instalar o actualizar el paquete del kernel** vía el gestor de paquetes (`apt`, `dnf`, etc.). El postinst del paquete ejecuta automáticamente `update-initramfs` para regenerarlo.
3. **Al agregar/quitar/actualizar módulos** que deben estar disponibles durante el arranque temprano (por ejemplo, instalando drivers de almacenamiento o cambiando el sistema de archivos raíz). Se regenera manualmente con:
    ```bash
        # update-initramfs -u
    ```
4. **Al modificar la configuración de initramfs-tools** (archivos en `/etc/initramfs-tools/`), por ejemplo para agregar scripts o módulos forzados.

## Ejercicio 10:​ ¿Qué módulos y drivers deberá tener un initramfs mínimamente para cumplir su objetivo?

El objetivo del initramfs es permitir al kernel **acceder y montar el sistema de archivos raíz (rootfs) real** para continuar el arranque. Por lo tanto, debe contener mínimamente los módulos y drivers necesarios para llegar hasta ese sistema de archivos.

### Drivers/módulos mínimos requeridos

1. **Drivers del controlador de almacenamiento** donde reside el rootfs:
   - SATA/AHCI (`ahci`, `libata`)
   - NVMe (`nvme`)
   - SCSI / RAID (`sd_mod`, `mpt3sas`, `megaraid_sas`)
   - USB Mass Storage si el rootfs está en USB (`usb_storage`, `xhci_hcd`)
   - Virtio si es una VM (`virtio_blk`, `virtio_scsi`)

2. **Driver del sistema de archivos** del rootfs:
   - `ext4`, `xfs`, `btrfs`, `f2fs`, etc. (según corresponda)

3. **Módulos de mapeo de bloques**, si el rootfs lo requiere:
   - LVM (`dm_mod`, `dm_thin_pool`)
   - RAID por software (`md`, `raid1`, `raid5`)
   - Cifrado de disco (`dm_crypt`, `aes`)

4. **Módulos de red**, solo si el rootfs es remoto (NFS, iSCSI):
   - Driver de la tarjeta de red correspondiente
   - Soporte del protocolo (`nfs`, `iscsi_tcp`)

5. **Herramientas y binarios mínimos en userspace**:
   - Un shell mínimo (típicamente `busybox`)
   - `udev` para detectar dispositivos
   - El script `init` del initramfs que monta el rootfs y hace el `switch_root`

>[!NOTE]
> En resumen, **todo lo necesario para llegar a montar el rootfs**. Drivers del hardware que aloja el rootfs + driver del filesystem + (si aplica) capas de mapeo (LVM/RAID/cripto) + utilidades para realizar el montaje.