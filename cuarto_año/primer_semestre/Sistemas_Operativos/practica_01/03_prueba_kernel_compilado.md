# Poner a prueba el kernel compilado

>[!NOTE]
> El objetivo de esta parte es verificar que las funcionalidades habilitadas durante la compilación (soporte para el filesystem BTRFS y soporte para dispositivos loopback) estén efectivamente operativas en el kernel 6.13.7 recién instalado.

>[!NOTE]
> Se debe estar ejecutando el kernel 6.13.7 compilado en la parte anterior. Verificar con `uname -r`.

1. Nos posicionamos en el directorio donde está la imagen
    ```zsh
        cd ~/kernel
    ```

2. Descomprimimos el filesystem
    ```zsh
        unxz btrfs.image.xz
    ```
    >[!NOTE]
    > - `unxz` descomprime el archivo `.xz` y deja el archivo original `btrfs.image` (sin la extensión `.xz`).
    > - Por defecto **reemplaza** el archivo: el `.xz` desaparece. Para conservar el original se puede usar `unxz -k btrfs.image.xz` (la `-k` de "keep").
    > - El archivo resultante tiene aproximadamente 110 MiB.

3. Nos convertimos en root (los siguientes pasos requieren privilegios)
    ```zsh
        su -
    ```
    >[!NOTE]
    > El comando `mount` requiere privilegios de root para montar filesystems. La contraseña de root en la VM es `toor`.

4. Creamos el punto de montaje
    ```zsh
        mkdir -p /mnt/btrfs
    ```
    >[!NOTE]
    > - El punto de montaje es un directorio vacío donde el sistema "enchufa" el filesystem.
    > - La opción `-p` evita errores si el directorio ya existe.

5. Montamos la imagen usando el driver loopback
    ```zsh
        mount -t btrfs -o loop /home/so/kernel/btrfs.image /mnt/btrfs/
    ```
    >[!NOTE]
    > Desglose del comando:
    > - `mount` → comando para montar filesystems.
    > - `-t btrfs` → indica que el filesystem es de tipo BTRFS (el soporte que habilitamos en `menuconfig`). Sin él, el comando fallaría con `unknown filesystem type 'btrfs'`.
    > - `-o loop` → le dice a `mount` que use un dispositivo loopback, es decir, que trate al archivo como si fuera un disco de bloques. El kernel usa `/dev/loop0`, `/dev/loop1`, etc. Solo funciona porque habilitamos `Loopback device support`.
    > - `/home/so/kernel/btrfs.image` → archivo a montar (se usa path absoluto porque root está parado en `/root`).
    > - `/mnt/btrfs/` → punto de montaje.
    >
    > Si todo sale bien no se muestra ninguna salida; en Linux el silencio significa éxito.

6. Verificamos el montaje
    ```zsh
        mount | grep btrfs
    ```
    En nuestro caso la salida fue:
    ```
    /home/so/kernel/btrfs.image on /mnt/btrfs type btrfs (rw,relatime,discard=async,noacl,space_cache=v2,subvolid=5,subvol=/)
    ```
    >[!NOTE]
    > - Se confirma que el filesystem está montado en `/mnt/btrfs` como tipo `btrfs`.
    > - Las opciones `discard=async`, `space_cache=v2` y `subvolid=5` son características típicas de BTRFS, confirmando que el driver está funcionando correctamente.

7. Listamos el contenido y leemos el README
    ```zsh
        ls /mnt/btrfs
        cat /mnt/btrfs/README
    ```
    >[!NOTE]
    > El archivo se llama `README` (sin extensión `.md` como indica la guía). Se recomienda leerlo con `cat` porque contiene códigos de escape ANSI que otros comandos (como `less` o editores de texto) pueden no interpretar correctamente.

8. Desmontamos el filesystem (al terminar)
    ```zsh
        umount /mnt/btrfs
    ```
    >[!NOTE]
    > Es buena práctica desmontar el filesystem cuando ya no se necesita, especialmente antes de apagar el sistema o de volver a comprimir la imagen.

## Resultado

La prueba confirmó que ambas funcionalidades compiladas en el kernel 6.13.7 están operativas:

- **Soporte para BTRFS**: se pudo montar y leer el contenido de una imagen con ese filesystem.
- **Soporte para dispositivos loopback**: se pudo tratar el archivo `btrfs.image` como un dispositivo de bloques mediante la opción `-o loop` del comando `mount`.
