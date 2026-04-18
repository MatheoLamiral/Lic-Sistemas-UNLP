# Compilación del kernel Linux

>[!NOTE]
> LA compilación se llevó a cabo utilizando la VM provista por la cátedra

1. nos posicionamos en el directorio del kernel 
    ```zsh
        cd kernel/
    ```
2. Descomprimimos el código fuente 
    ```zsh
        tar xvf linux-6.13.tar.xz
    ```
3. Aplicamos el parche para actualizar de 6.13 a 6.13.7
    ```zsh
        cd linux-6.13
        xzcat ../patch-6.13.7.xz | patch -p1
    ```
    >[!NOTE]
    > - `xzcat ../patch-6.13.7.xz` descomprime el parche y lo manda por stdout (sin crear un archivo intermedio) 
    > - `patch -p1` aplica el parche. El `-p1` le dice que ignore el primer nivel de directorio de los paths que vienen en el parche (los parches del kernel vienen con paths tipo `a/kernel/sched.c` y `b/kernel/sched.c`, el `-p1` saca ese `a/` o `b/`).
4. Copiamos la configuración del kernel actual como base
    ```zsh
        cp /boot/config-$(uname -r) ~/kernel/linux-6.13/.config
    ```
    >[!NOTE]
    > - `uname -r` devuelve la versión del kernel que está corriendo ahora mismo (el de la VM)
    > - `/boot/config-<version>` es el archivo de configuración con el que se compiló ese kernel actual
    > - Lo copiamos como `.config` (con el punto al inicio, queda oculto) dentro del source tree del kernel nuevo

5. Actualizamos la configuración con `olddefconfig`
    ```zsh
        cd ~/kernel/linux-6.13
        make olddefconfig
    ```
    >[!NOTE]
    > Toma el `.config` viejo (el del kernel actual de la VM) y lo adapta al nuevo: para cualquier opción de configuración nueva que no existía antes, usa el valor por defecto automáticamente sin preguntar. En nuestro caso devolvió `No change to .config`, lo que significa que no había opciones nuevas por resolver.

6. Adaptamos la configuración a los módulos realmente cargados con `localmodconfig`
    ```zsh
        make localmodconfig
    ```
    >[!NOTE]
    > - Revisa qué módulos están cargados en este momento en la VM (equivalente a `lsmod`) y deshabilita del `.config` todos los demás.
    > - El resultado es un kernel mucho más chico y rápido de compilar, a medida del hardware de esta VM.
    > - Durante la ejecución hizo preguntas sobre opciones nuevas marcadas como `(NEW)`. En cada una se presionó `Enter` para aceptar el valor por defecto.

7. Configuración personalizada del kernel con `menuconfig`
    ```zsh
        make menuconfig
    ```
    Desde la interfaz de texto se habilitaron las siguientes opciones (requeridas por la parte C de la práctica):
    - `File systems` → `Btrfs filesystem support` → como módulo (`<M>`)
    - `Device Drivers` → `Block devices` → `Loopback device support` → como módulo (`<M>`)

    Y se deshabilitaron las siguientes para reducir el tamaño del kernel y el tiempo de compilación:
    - `General setup` → `Configure standard kernel features (expert users)`
    - `Kernel hacking` → `Kernel debugging`

    >[!NOTE]
    > La barra espaciadora cicla entre tres estados: `<*>` (compilado dentro del kernel), `<M>` (como módulo) y `< >` (deshabilitado). Dentro de `menuconfig` se puede usar `/` para buscar opciones por nombre (por ejemplo `BTRFS_FS` o `BLK_DEV_LOOP`).

    Al salir, se guardaron los cambios en el `.config`.

8. Verificación de que las opciones quedaron aplicadas en el `.config`
    ```zsh
        grep -E "CONFIG_BTRFS_FS|CONFIG_BLK_DEV_LOOP" .config
        grep "CONFIG_DEBUG_KERNEL" .config
    ```
    >[!NOTE]
    > Se verificó que `CONFIG_BTRFS_FS=m` y `CONFIG_BLK_DEV_LOOP=m` estén presentes, y que `CONFIG_DEBUG_KERNEL` aparezca como `# CONFIG_DEBUG_KERNEL is not set`.

9. Compilación del kernel
    ```zsh
        make -j$(nproc)
    ```
    >[!NOTE]
    > - `-j$(nproc)` lanza tantos jobs de compilación en paralelo como CPUs tenga la VM, acelerando mucho el proceso.
    > - `nproc` devuelve la cantidad de procesadores disponibles, y `$( )` hace que bash lo reemplace por ese número.
    > - La compilación puede durar varios minutos u horas dependiendo del hardware.
    > - Al terminar se verifica que no haya errores y que aparezca el mensaje `Kernel: arch/x86/boot/bzImage is ready`.

10. Verificación de la compilación
    ```zsh
        ls -lh arch/x86/boot/bzImage
        find . -name "btrfs.ko" -o -name "loop.ko"
    ```
    >[!NOTE]
    > - Se comprobó que `arch/x86/boot/bzImage` existe (aproximadamente 7,7 MB).
    > - Se comprobó que los módulos `./fs/btrfs/btrfs.ko` y `./drivers/block/loop.ko` fueron generados correctamente.

11. Instalación de los módulos (requiere privilegios de root)
    ```zsh
        su -
        cd /home/so/kernel/linux-6.13
        make modules_install
    ```
    >[!NOTE]
    > Copia todos los módulos `.ko` a `/lib/modules/6.13.7/`, que es donde el kernel los busca al arrancar y cuando se usa `modprobe`. Al finalizar ejecuta `depmod` para generar los metadatos de dependencias entre módulos (`modules.dep`).

12. Instalación del kernel
    ```zsh
        make install
    ```
    >[!NOTE]
    > En distribuciones basadas en Debian este comando automáticamente:
    > 1. Copia `bzImage` a `/boot/vmlinuz-6.13.7`
    > 2. Copia `System.map` a `/boot/System.map-6.13.7`
    > 3. Copia el `.config` a `/boot/config-6.13.7`
    > 4. Genera la imagen initramfs en `/boot/initrd.img-6.13.7` mediante `initramfs-tools`
    > 5. Actualiza la configuración de GRUB con `update-grub`, agregando una nueva entrada para el kernel 6.13.7 sin eliminar las anteriores.

13. Reiniciar el sistema para probar el nuevo kernel
    ```zsh
        su - -c reboot
    ```
    >[!NOTE]
    > - Se usa `su - -c reboot` (con el guion) para que se cargue el entorno completo de root e incluya `/sbin` en el `PATH`. Sin el guion el comando `reboot` no se encuentra porque está en `/sbin/`.
    > - En el menú de GRUB aparecen tanto el nuevo kernel 6.13.7 como los originales de Debian (6.1.0-31 y 6.1.0-29), lo que permite volver atrás en caso de que el nuevo kernel no arranque.

14. Verificación del kernel en ejecución
    ```zsh
        uname -r
    ```
    >[!NOTE]
    > El comando devolvió `6.13.7`, confirmando que el sistema está ejecutando el kernel compilado en esta práctica.