# Desarrollando un Driver

## Ejercicio 1:​ Modifique el archivo memory.c para que tenga el siguiente código: https://gitlab.com/unlp-so/codigo-para-practicas/-/blob/main/practica2/crear_driver/1_memory.c

1. `nano memory.c`
2. reemplazamos el contenido con este códgio:
    ```c
        #include <linux/init.h>
        #include <linux/module.h>
        #include <linux/kernel.h> /* printk() */
        #include <linux/slab.h> /* kmalloc() */
        #include <linux/fs.h> /* everything... */
        #include <linux/errno.h> /* error codes */
        #include <linux/types.h> /* size_t */
        #include <linux/proc_fs.h>
        #include <linux/fcntl.h> /* O_ACCMODE */
        #include <linux/uaccess.h> /* copy_from/to_user */

        MODULE_LICENSE("Dual BSD/GPL");

        int memory_open(struct inode *inode, struct file *filp);
        int memory_release(struct inode *inode, struct file *filp);
        ssize_t memory_read(struct file *filp, char *buf, size_t count, loff_t *
                f_pos);
        ssize_t memory_write(struct file *filp, const char *buf, size_t count,
                loff_t *f_pos);
        void memory_exit(void);
        int memory_init(void);

        /* Structure that declares the usual file */
        /* access functions */
        struct file_operations memory_fops = {
        read: memory_read,
            write: memory_write,
            open: memory_open,
            release: memory_release
        };

        /* Declaration of the init and exit functions */
        module_init(memory_init);
        module_exit(memory_exit);

        /* Global variables of the driver */
        /* Major number */
        int memory_major = 60;
        /* Buffer to store data */
        char *memory_buffer;

        int memory_init(void) {
            int result;
            /* Registering device */
            result = register_chrdev(memory_major, "memory", &memory_fops);
            if (result < 0) {
                printk("<1>memory: cannot obtain major number %d\n", memory_major);
                return result;
            }
            /* Allocating memory for the buffer */
            memory_buffer = kmalloc(1, GFP_KERNEL);
            if (!memory_buffer) {
                result = -ENOMEM;
                goto fail;
            }
            memset(memory_buffer, 0, 1);
            printk("<1>Inserting memory module\n");
            return 0;
        fail:
            memory_exit();
            return result;
        }

        void memory_exit(void) {
            /* Freeing the major number */
            unregister_chrdev(memory_major, "memory");

            /* Freeing buffer memory */
            if (memory_buffer) {
                kfree(memory_buffer);
            }
            printk("<1>Removing memory module\n");
        }

        int memory_open(struct inode *inode, struct file *filp) {
            /* Success */
            return 0;
        }

        int memory_release(struct inode *inode, struct file *filp) {
            /* Success */
            return 0;
        }

        ssize_t memory_read(struct file *filp, char *buf,
                size_t count, loff_t *f_pos) {
            printk("memory_read()\n");
            /* Transfering data to user space */
            if (copy_to_user(buf,memory_buffer,1)) {
                // return 0 if copy_to_user fails
                return 0;
            }
            /* Changing reading position as best suits */
            if (*f_pos == 0) {
                *f_pos+=1;
                return 1;
            } else {
                return 0;
            }
        }

        ssize_t memory_write( struct file *filp, const char *buf,
                size_t count, loff_t *f_pos) {
            const char *tmp;
            tmp=buf+count-1;
            printk("memory_write()\n");
            if (copy_from_user(memory_buffer,tmp,1)) {
                // return 0 if copy_from_user fails
                return 0;
            }
            return 1;
        }
    ```
 3. Recompilamos con `make -C /home/so/kernel/linux-6.13 M=$(pwd) modules`

## Ejercicio 2:​ Responda lo siguiente:

### a. ¿Para qué sirve la estructura ssize_t y memory_fops? ¿Y las funciones register_chrdev y unregister_chrdev?

- **`ssize_t`**: no es una estructura, es un **tipo de dato** (*signed size_t*) que representa un tamaño con signo. Se usa como tipo de retorno de las funciones `read` y `write` porque permite devolver tanto la **cantidad de bytes** efectivamente leídos/escritos (valor positivo) como un **código de error** (valor negativo, ej. `-EFAULT`). `size_t` (sin signo) no podría representar errores.

- **`memory_fops`** (de tipo `struct file_operations`): es la estructura que **asocia cada operación de archivo con la función del driver** que la implementa. En el código:
    ```c
    struct file_operations memory_fops = {
        read:    memory_read,
        write:   memory_write,
        open:    memory_open,
        release: memory_release
    };
    ```
  Es decir, cuando se haga un `read` sobre el dispositivo, el kernel llamará a `memory_read`; ante un `write`, a `memory_write`, etc. Es el "puente" entre las llamadas genéricas del SO y el código concreto del driver.

- **`register_chrdev(major, "memory", &memory_fops)`**: **registra el driver** como un dispositivo de **caracter** (*character device*) en el kernel, asociando un *major number* (60) al nombre `"memory"` y a la tabla de operaciones `memory_fops`. A partir de ese momento, el kernel sabe qué funciones invocar cuando se opera sobre un dispositivo con ese major.

- **`unregister_chrdev(major, "memory")`**: hace lo inverso, **libera/desregistra** ese major number cuando se descarga el módulo (se llama en `memory_exit`), dejando el número disponible nuevamente.

### b. ¿Cómo sabe el kernel que funciones del driver invocar para leer y escribir al dispositivo?

A través de la estructura **`struct file_operations`** (`memory_fops`). Al registrar el driver con `register_chrdev`, le pasamos un puntero a esa estructura, que contiene los punteros a nuestras funciones (`memory_read`, `memory_write`, `memory_open`, `memory_release`). Cuando un proceso de usuario hace `read()`, `write()`, `open()` o `close()` sobre el device file, el kernel busca en `file_operations` el puntero correspondiente y **invoca esa función del driver**. Así se logra que operaciones genéricas se traduzcan al código específico del dispositivo.

### c. ¿Cómo se accede desde el espacio de usuario a los dispositivos en Linux?

A través de los **device files** ubicados en `/dev`. En UNIX/Linux "todo es un archivo", por lo que un dispositivo se accede como si fuera un archivo común: se abre con `open()`, se lee con `read()`, se escribe con `write()` y se cierra con `close()` (o desde la shell con comandos como `echo`, `cat`, `more`, redirecciones `>`). El proceso de usuario nunca toca el hardware directamente: el kernel intercepta esas llamadas y, según el *major number* del device file, las redirige a las funciones del driver correspondiente.

### d. ¿Cómo se asocia el módulo que implementa nuestro driver con el dispositivo?

La asociación se hace mediante el **major number**. El módulo registra ese número con `register_chrdev(60, "memory", &memory_fops)`, y el device file se crea con el **mismo** major number usando `mknod /dev/memory c 60 0`. De esta forma, cuando alguien opera sobre `/dev/memory`, el kernel ve que su major es 60, lo relaciona con el driver que registró ese major y llama a las funciones de `memory_fops`. El **minor number** (0) sirve para distinguir instancias manejadas por el mismo driver.

### e. ¿Qué hacen las funciones copy_to_user y copy_from_user? (https://developer.ibm.com/technologies/linux/articles/l-kernel-memory-access/).

Transfieren datos de forma **segura** entre el espacio de usuario y el espacio del kernel, que son espacios de direcciones **separados** (el kernel no puede simplemente desreferenciar un puntero de usuario).

- **`copy_to_user(dest_usuario, src_kernel, n)`**: copia `n` bytes **desde el kernel hacia el espacio de usuario**. La usa `memory_read` para entregarle al proceso el contenido del buffer del driver.
- **`copy_from_user(dest_kernel, src_usuario, n)`**: copia `n` bytes **desde el espacio de usuario hacia el kernel**. La usa `memory_write` para traer al buffer del driver lo que el proceso quiere escribir.

>[!NOTE]
> Ambas **validan que el puntero de usuario sea legítimo** (que la dirección pertenezca realmente al espacio de ese proceso) antes de copiar, evitando que un puntero inválido o malicioso corrompa el kernel. Devuelven la cantidad de bytes que **no** pudieron copiarse (`0` si la copia fue completa y exitosa); por eso en el código, si devuelven distinto de `0`, se considera fallo.

## Ejercicio 3:​ Ahora ejecutamos lo siguiente:

```bash
# mknod /dev/memory c 60 0
```

1. `su -`
2. `mknod /dev/memory c 60 0`

## Ejercicio 4:​ Y luego:

```bash
# insmod memory.ko
```

- Recordar que antes hay que recompilar el módulo con el nuevo código (`make ... modules`). Luego, como root:
  1. `su -`
  2. `cd /home/so/practica2`
  3. `insmod memory.ko`

### Responda lo siguiente:

#### i. ¿Para qué sirve el comando mknod? ¿qué especifican cada uno de sus parámetros?.

`mknod` (*make node*) sirve para **crear un device file** (archivo de dispositivo) en el sistema de archivos, normalmente dentro de `/dev`. Es el punto de acceso que usa el espacio de usuario para comunicarse con el driver.

Para el comando `mknod /dev/memory c 60 0`, cada parámetro especifica:

| Parámetro | Valor | Qué especifica |
|---|---|---|
| `<file-name>` | `/dev/memory` | Ruta y nombre del device file a crear. |
| `[b\|c]` | `c` | Tipo de dispositivo: **`c`** = de **caracter** (acceso byte a byte), **`b`** = de **bloque**. |
| `<major-number>` | `60` | **Major number**: identifica qué driver maneja el dispositivo (debe coincidir con el registrado por `register_chrdev`). |
| `<minor-number>` | `0` | **Minor number**: identifica la instancia particular dentro de ese driver. |

#### ii. ¿Qué son el "major" y el "minor" number? ¿Qué referencian cada uno?

Son los dos números que identifican a cada device file y permiten al kernel vincularlo con su driver:

- **Major number**: referencia **qué driver** está a cargo del dispositivo. Cuando se opera sobre el device file, el kernel usa el major para saber a qué driver redirigir la operación (en nuestro caso, el 60 que registramos con `register_chrdev`).
- **Minor number**: referencia **qué instancia concreta** dentro de ese driver. Un mismo driver (mismo major) puede manejar varios dispositivos, el minor los distingue (ej. `/dev/sda1`, `/dev/sda2` comparten major pero tienen distinto minor). El minor lo interpreta internamente el propio driver.

## Ejercicio 5:​ Ahora escribimos a nuestro dispositivo:

```bash
echo -n abcdef > /dev/memory
```

- Como usuario común da `Permiso denegado`, porque `/dev/memory` fue creado por root (`mknod`) y solo root tiene permiso de escritura por defecto. Por eso se ejecuta como root:
  1. `su -`
  2. `echo -n abcdef > /dev/memory`

>[!NOTE]
> Este `echo` realiza un `write()` sobre `/dev/memory`, que el kernel traduce a la función `memory_write()` del driver. Se puede verificar con `dmesg | tail` (aparecen líneas `memory_write()`).

## Ejercicio 6:​ Ahora leemos desde nuestro dispositivo:

```bash
more /dev/memory
```

- Como root:
  1. `su -`
  2. `more /dev/memory`

La salida es un único caracter:

```
f
```

>[!NOTE]
> El `more` hace `read()` sobre `/dev/memory`, que el kernel traduce a `memory_read()`. El driver devuelve **un solo byte** (el contenido del buffer de 1 byte) y luego retorna `0` (EOF), por eso se lee una única `f`. 

## Ejercicio 7:​ Responda lo siguiente:

### a. ¿Qué salida tiene el anterior comando?, ¿Porque? (ayuda: siga la ejecución de las funciones memory_read y memory_write y verifique con dmesg)

La salida es el caracter `f`. El motivo está en cómo funcionan las dos funciones del driver:

- Al escribir con `echo -n abcdef > /dev/memory`, se ejecuta `memory_write()`. Pero esta función **no guarda toda la cadena**: hace `tmp = buf + count - 1`, es decir apunta al **último byte** de lo escrito, y con `copy_from_user(memory_buffer, tmp, 1)` copia **solo ese byte** al buffer del driver (que es de 1 byte). Como lo último de `abcdef` es la `f`, en el buffer queda guardada únicamente la `f`.

Por eso la salida es una sola `f`. Esto se verifica con `dmesg`, donde se ven las líneas `memory_write()` y `memory_read()` impresas por los `printk`.

### b. ¿Cuántas invocaciones a memory_write se realizaron?

Una sola. Aunque la cadena `abcdef` tiene 6 caracteres, `echo` hace **un único `write()`** con los 6 bytes de golpe (no uno por caracter), por lo que `memory_write()` se invoca **una vez**. Esto se confirma en `dmesg`: aparece una única línea `memory_write()`. (La función igualmente ignora 5 de los 6 bytes y solo guarda el último).

### c. ¿Cuál es el efecto del comando anterior? ¿Por qué?

El efecto de `more /dev/memory` es **leer y mostrar el contenido del buffer del driver**, que es la única `f` guardada. Solo muestra un caracter (y no `abcdef`) porque:
1. En la escritura, el driver guardó únicamente el último byte (`f`).
2. En la lectura, el buffer es de 1 byte y `memory_read()` devuelve 1 byte la primera vez y `0` (EOF) después, así que no hay más datos para entregar.

### d. Hasta aquí hemos desarrollado un ejemplo de un driver muy simple pero de manera completa, en nuestro caso hemos escrito y leído desde un dispositivo que en este caso es la propia memoria de nuestro equipo.

>[!NOTE]
> Completamos el ciclo de un driver de dispositivo de caracter: registramos el dispositivo (`register_chrdev`), definimos sus operaciones (`file_operations`), creamos el device file (`mknod`), y escribimos/leímos desde el espacio de usuario (`echo`/`more`), comprobando que esas operaciones se traducen a nuestras funciones `memory_write()`/`memory_read()` mediante `copy_from_user`/`copy_to_user`. El "dispositivo" en este caso es simplemente un buffer en la memoria del kernel.

### e. En el caso de un driver que lee un dispositivo como puede ser un file system, un dispositivo usb, etc. ¿Qué otros aspectos deberíamos considerar que aquí hemos omitido? ayuda: semáforos, ioctl, inb, outb.

En un driver real de un dispositivo de hardware deberíamos considerar varios aspectos que este ejemplo omitió:

- **Sincronización / concurrencia (semáforos, mutexes, spinlocks)**: nuestro driver usa un buffer global sin ninguna protección. Si dos procesos lo accedieran a la vez habría *condiciones de carrera*. Un driver real debe serializar el acceso al recurso compartido con semáforos, mutexes o spinlocks.
- **`ioctl`**: muchas operaciones sobre un dispositivo no encajan en un simple `read`/`write` (configurar baud rate, expulsar un CD, consultar estado, etc.). Esas operaciones de control se implementan con la llamada `ioctl`, que aquí no definimos.
- **Acceso a puertos de E/S del hardware (`inb`, `outb`)**: para hablar con hardware real hay que leer/escribir los registros del dispositivo mediante puertos de E/S (`inb`, `outb`, `inw`, `outw`) o memoria mapeada (`ioremap`). Nuestro "dispositivo" es solo memoria RAM, así que no fue necesario.
- **Manejo de interrupciones (IRQ)**: los dispositivos reales avisan eventos mediante interrupciones; un driver debe registrar y atender manejadores de IRQ.
- **Buffering y bloqueo**: gestionar buffers más grandes, lecturas/escrituras bloqueantes y no bloqueantes, colas de espera (`wait queues`), manejo correcto del `count` y de la posición (`f_pos`), etc.
- **Gestión de errores y de múltiples minors**: validar permisos, manejar varias instancias del dispositivo (distintos minor numbers) y liberar recursos correctamente ante fallos.
