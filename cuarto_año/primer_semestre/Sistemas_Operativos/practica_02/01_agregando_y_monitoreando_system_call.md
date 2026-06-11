# Agregando una System Call

## Ejercicio 1:​ Añadiremos el siguiente archivo con el código de nuestra system call -> kernel/my_sys_call.c

- Dentro de la VM nos posicionamos en `/home/so/kernel/linux-6.13`
- Creamos el archivo con `nano kernel/my_sys_call.c`
- Copiamos el siguiente código dentro del mismo:

```c
#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/sched.h>
#include <linux/uaccess.h>
#include <linux/sched/signal.h>
#include <linux/slab.h>          // Para kmalloc y kfree

SYSCALL_DEFINE1(my_sys_call, int, arg) {
    printk(KERN_INFO "My syscall called with arg: %d\n", arg);
    return 0;
}

SYSCALL_DEFINE2(get_task_info, char __user *, buffer, size_t, length) {
    struct task_struct *task;
    char kbuffer[1024];           // Buffer en el espacio del kernel
    int offset = 0;

    for_each_process(task) {
        offset += snprintf(kbuffer + offset, sizeof(kbuffer) - offset,
                           "PID: %d | Nombre: %s | Estado: %d \n",
                           task->pid, task->comm, task_state_index(task));

        if (offset >= sizeof(kbuffer))   // Evita sobrepasar el tamaño del buffer
            break;

        printk(KERN_INFO "PID: %d | Nombre: %s\n", task->pid, task->comm);
    }

    // Copia la información al espacio de usuario
    if (copy_to_user(buffer, kbuffer, min(length, (size_t)offset)))
        return -EFAULT;

    return min(length, (size_t)offset);
}

SYSCALL_DEFINE2(get_threads_info, char __user *, buffer, size_t, length) {
    struct task_struct *task, *thread;
    char *kbuffer;
    int offset = 0;

    // Asignar memoria dinámica para el buffer
    kbuffer = kmalloc(2048, GFP_KERNEL);
    if (!kbuffer)
        return -ENOMEM;

    for_each_process(task) {
        offset += snprintf(kbuffer + offset, 2048 - offset,
                           "Proceso: %s (PID: %d)\n",
                           task->comm, task->pid);

        for_each_thread(task, thread) {
            offset += snprintf(kbuffer + offset, 2048 - offset,
                               "    ├── Hilo: %s (TID: %d)\n",
                               thread->comm, thread->pid);

            if (offset >= 2048)
                break;
        }

        if (offset >= 2048)
            break;
    }

    if (copy_to_user(buffer, kbuffer, min(length, (size_t)offset))) {
        kfree(kbuffer);
        return -EFAULT;
    }

    kfree(kbuffer);
    return min(length, (size_t)offset);
}
```

### ¿Para qué sirven los macros `SYS_CALL_DEFINE`?

Son macros del kernel que declaran y definen una system call correctamente, ocultando la complejidad de la convención de llamada del kernel. El número al final indica cuántos parámetros recibe la syscall (máx. 6)

- Sintaxis: `SYSCALL_DEFINEn(nombre, tipo1, nombre1, tipo2, nombre2, ...)`

Sin estos macros habría que escribir manualmente la función con `asmlinkage`, los wrappers por arquitectura y registrarla en la syscall table. son una abstracción que estandariza todo eso.

### ¿Para que se utilizan la macros `for_each_process` y `for_each_thread`?

Son marcos del kernel para iterar sobre la lista de procesos y threads del sistema. Acceden a la lista enlazada de `task_struct` que mantiene el scheduler.

- `for_each_process(task)` itera sobre todos los procesos del sistema (cada uno representado por su `task_struct` líder de grupo).
- `for_each_thread(task, thread)` itera sobre los threads pertenecientes a un proceso dado (recorre el thread group de ese proceso). Se usa anidada dentro de `for_each_process`

>[!NOTE]
> En Linux, cada thread es un `task_struct`. El "proceso" es simplemente el thread líder del grupo (`task->tgid == task->pid`),

### ¿Para que se utiliza la función `copy_to_user`?

Sirve para copiar datos desde el espacio del kernel al espacio de usuario de forma segura. Es la API oficial para mover datos a través de la frontera kernel/usuario.

- `copy_to_user(buffer, kbuffer, min(length, (size_t)offset))`
  - **buffer (destino, en user space)**: puntero `char __user *` provisto por el proceso que invocó la syscall.
  - **kbuffer (origen, en kernel space)**: donde el kernel armó la información.
  - **Tercer argumento**: cantidad de bytes a copiar.

>[!NOTE] Por qué no usar memcpy directamente?
> Porque los punteros provenientes del usuario no son confiables
> - Pueden apuntar a memoria del kernel
> - Pueden ser inválidos
> - Pueden no estar paginados todavía  
> 
> `copy_to_user` valida que la dirección esté dentro del espacio de usuario del proceso invocante y maneja page faults correctamente. Retorna 0 si copió todo, o el número de bytes que no pudo copiar (por eso el código retorna `-EFAULT` cuando el resultado es distinto de cero).

### ¿Para qué se utiliza la función `printk`, ¿porque no la típica `printf`?

`printk` es la función del kernel para escribir mensajes al log del kernel (`dmesg`, `/var/log/kern.log`, etc.). Es la equivalente a `printf` pero usable desde el kernel.

No se usa `printf` porque **no existe en el kernel**, esa función es parte de la biblioteca estándar de C (libc) que solo está disponible en espacio de usuario.

>[!NOTE]
> El kernel es un binario standalone que no enlaza con libc, así que cualquier función de la stdlib (`printf`, `malloc`, `fopen`, etc.) simplemente no está disponible. Por eso el kernel provee sus propias versiones: `printk`, `kmalloc`, etc.

- Niveles de printk 
  - `KERN_*` indican la severidad del mensaje y permiten filtrar la salida

    |Prefijo|Uso|
    |-------|---|
    |`KERN_EMERG`|Emergencia, el sistema está inutilizable|
    |`KERN_ALERT`|Alerta, se requiere acción inmediata|
    |`KERN_CRIT`|Crítico, condiciones críticas|
    |`KERN_ERR`|Error, condiciones de error|
    |`KERN_WARNING`|Advertencia, condiciones potencialmente problemáticas|
    |`KERN_NOTICE`|Notificación, condiciones normales pero relevantes|
    |`KERN_INFO`|Información, mensajes informativos|
    |`KERN_DEBUG`|Depuración, mensajes de depuración|

  - Para ver los mensajes que escribieron las syscalls del código:
    - `dmesg | tail`
    - o en vivo `sudo dmesg -w`

### Podría explicar que hacen las sytem call que hemos incluido?

#### my_sys_call(int arg)

Recibe un único parámetro entero `arg` y lo imprime al log del kernel con `printk`

- La idea es verificar que el mecanismo completo de agregar una syscall funciona de punto a punto. Se valida ejecutando la syscall y luego mirando `dmesg` para ver el mensaje

#### get_task_info(char __user *buffer, size_t length)

Devuelve la lista de procesos del sistema al espacio de usuario

1. Declara un buffer estático de 1024 bytes en el stack del kernel (`kbuffers`)
2. Recorre todos los procesos con `for_each_process(task)`
3. Por cada proceso, escribe en `kbuffer` con `snprintf`:
   1. PID (task->pid)
   2. Nombre (task->comm)
   3. Estado (task_state_index(task))
4. Si el buffer se llena, corta el loop con un break
5. Copia el buffer al espacio de usuario con `copy_to_user`. Si falla, retorna `-EFAULT`
6. Retorna la cantidad de bytes efectivamente copiados

>[!NOTE]
> Tiene una limitación, y es que en un sistema con muchos procesos, al tener un `kbuffer` estático de 1024 bytes, la información se trunca

#### get_threads_info(char __user *buffer, size_t length)

Devuelve la lista de procesos con sus threads en formato jerárquico (árbol)

1. Reserva memoria dinámica con kmalloc(2048, GFP_KERNEL). Si falla retorna `-ENOMEM`.
   - `GFP_KERNEL` indica que la asignación puede dormir (aceptable en contexto de proceso).
2. Recorre los procesos con `for_each_process`.
3. Por cada proceso, escribe `"Proceso: <nombre> (PID: <pid>)"`.
4. Loop anidado con `for_each_thread(task, thread)`: por cada thread del proceso, escribe `" ├── Hilo: <nombre> (TID: <tid>)"`.
5. Verifica overflow del buffer en ambos niveles del loop.
6. Copia al usuario con `copy_to_user`.
7. Libera la memoria con `kfree(kbuffer)` tanto en éxito como en error (importante para no leakear).
8. Retorna la cantidad de bytes copiados.

## Ejercicio 2: Modificaremos uno de los archivos Makefile del código del Kernel para indicar la compilación de nuestro código agregado en el paso anterior

El archivo `kernel/Makefile` controla qué archivos `.c` del directorio `kernel/` se compilan e integran al binario del kernel. Hay que agregar `my_sys_call.o` a la lista.

1. abrimos el archivo con `nano kernel/Makefile`
2. ubicamos la línea que dice `obj-y =` y al final agregamos `my_sys_call.o` al final, quedando algo así:

```makefile
    obj-y     = fork.o exec_domain.o panic.o \
                cpu.o exit.o softirq.o resource.o \
                sysctl.o capability.o ptrace.o user.o \
                signal.o sys.o umh.o workqueue.o pid.o task_work.o \
                extable.o params.o \
                kthread.o sys_ni.o nsproxy.o \
                notifier.o ksysfs.o cred.o reboot.o \
                async.o range.o smpboot.o ucount.o regset.o ksyms_common.o \
                my_sys_call.o
```

## Ejercicio 3: Añadir una entrada al final de la tabla que contiene todas las System Calls, la syscall table. En nuestro caso, vamos a dar soporte para nuestra syscall a la arquitectura arm64., si fue x86_64, la sys call table se encuentra en arch/x86/entry/syscalls/syscall_64.tbl

>[!IMPORTANT]
>- El archivo donde añadiremos la entrada para la system call está estructurado en columnas de la siguiente forma: `<number> <abi> <name> <entry point>`
>- Buscaremos la última entrada cuya ABI sea “common” y luego agregaremos una línea para nuestra system call.
>- Debemos asignar un número único a nuestra system call, de modo que aumentaremos en 1 el número de la última.

1. Abrimos el archivo con `nano arch/x86/entry/syscalls/syscall_64.tbl`
2. Ubicamos la ultima línea con ABI `common` y agregamos estas líneas después de la última entrada:

```
    467   common   my_sys_call        sys_my_sys_call
    468   common   get_task_info      sys_get_task_info
    469   common   get_threads_info   sys_get_threads_info
```

3. Abrimos el archivo con `nano include/uapi/asm-generic/unistd.h` y agregamos estas líneas al final de la tabla:

```c
    #define __NR_my_sys_call 466
    __SYSCALL(__NR_my_sys_call, sys_my_sys_call)
    #define __NR_get_task_info 467
    __SYSCALL(__NR_get_task_info, sys_get_task_info)
    #define __NR_get_threads_info 468
    __SYSCALL(__NR_get_threads_info, sys_get_threads_info)
```

4. Después, modificamos la línea `#define __NR_syscalls` y la actualizamos a 470 en este caso

```c
    #define __NR_syscall_max 470
```

## Ejercicio 4: Lo próximo que debemos realizar es compilar el Kernel con nuestros cambios. Una vez seguidos todos los pasos de la compilación como lo vimos en el trabajo práctico 1, acomodamos la imagen generada y arrancamos el sistema con el nuevo kernel.

1. Primero, es recomendable tomar un snapshot de la VM antes de compilar el kernel, para poder volver a un estado limpio si algo sale mal.
2. Compilamos el kernel con `make -j$(nproc)`. 

3. Una vez finalizada la compilación sin errores, instalamos los módulos del kernel. Este comando requiere privilegios de root porque escribe en `/lib/modules/`:

```bash
sudo make modules_install
```

>[!IMPORTANT]
> En Debian, si durante la instalación se asignó contraseña a root, `sudo` no viene instalado por defecto. Se puede usar `su -` para convertirse en root y ejecutar los comandos sin el prefijo `sudo`, o instalar `sudo` con `apt install sudo` y agregar el usuario al grupo `sudo` con `usermod -aG sudo <usuario>`.

4. Instalamos el kernel propiamente dicho con `sudo make install`. Este comando copia `vmlinuz-<version>` y `System.map-<version>` a `/boot/`, genera el `initramfs` correspondiente y actualiza el menú de GRUB.

5. Verificamos que los archivos del nuevo kernel quedaron en `/boot/`:

```bash
ls -lh /boot/vmlinuz* /boot/initrd* /boot/System.map*
```

Deberíamos ver el `vmlinuz-<version>`, el `initrd.img-<version>` y el `System.map-<version>` correspondientes a la versión recién compilada.

6. Reiniciamos el sistema con `sudo reboot` (o `/sbin/reboot` si el comando no se encuentra en el PATH del usuario actual).

7. En el menú de GRUB seleccionamos el kernel recién compilado. Si GRUB no muestra el menú al arrancar, mantenemos `Shift` apretado durante el boot para forzar su aparición.

8. Una vez logueados, verificamos que estamos corriendo el kernel nuevo:

```bash
uname -r
```

La salida debe coincidir con la versión que acabamos de compilar (por ejemplo, `6.13.7`).

## Ejercicio 5: Ahora vamos a verificar que nuestras system calls nuevas ya son parte del kernel

1. Buscamos el símbolo de nuestras system calls en el `System.map` del kernel recientemente compilado:

```bash
grep get_task_info /boot/System.map-$(uname -r)
grep my_sys_call /boot/System.map-$(uname -r)
grep get_threads_info /boot/System.map-$(uname -r)
```

2. Aquí deberíamos ver el mapa de símbolos correspondiente a cada system call. La salida tiene esta forma:

```
ffffffff8123abcd T __x64_sys_my_sys_call
ffffffff8123abcd T __ia32_sys_my_sys_call
ffffffff8123ef01 T __x64_sys_get_task_info
ffffffff8123ef01 T __ia32_sys_get_task_info
ffffffff8123ef34 T __x64_sys_get_threads_info
ffffffff8123ef34 T __ia32_sys_get_threads_info
```

>[!NOTE]
> - `__x64_sys_<nombre>` es el handler para llamadas desde procesos x86_64 nativos.
> - `__ia32_sys_<nombre>` es el handler para procesos x86 32-bit corriendo en modo de compatibilidad.
> - La columna `T` indica que el símbolo es de tipo *text* (función) y es global.
> - La dirección al principio (`ffffffff...`) indica la posición del código en el espacio de direcciones del kernel.

Si los símbolos aparecen, las system calls están registradas correctamente y son invocables desde user space.

## Ejercicio 6: Nuestro último paso es realizar un programa que llame a la System Call que recopila información sobre los hilos en ejecución.

1. Creamos un directorio de trabajo fuera del árbol del kernel y dentro creamos el archivo del programa de prueba:

```bash
mkdir ~/test_syscall && cd ~/test_syscall
nano get_threads_info.c
```

2. Pegamos el siguiente código:

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <string.h>

#define SYS_get_threads_info 469

void print_task_info(const char *info) {
    printf("\nInformación de los hilos en ejecución:\n");
    printf("----------------------------------------\n");
    printf("%s", info);
    printf("\n----------------------------------------\n");
}

int main() {
    char buffer[1024];          // Buffer donde se almacenará la información de las tareas
    long bytes_read;

    // Llamada al sistema para obtener la información de los hilos
    bytes_read = syscall(SYS_get_threads_info, buffer, sizeof(buffer));

    // Comprobamos si la llamada al sistema fue exitosa
    if (bytes_read < 0) {
        perror("Error al invocar la llamada al sistema");
        return 1;
    }

    // Mostrar la información obtenida de los procesos
    print_task_info(buffer);
    return 0;
}
```

>[!IMPORTANT]
> El valor de `SYS_get_threads_info` debe coincidir con el número que asignamos a la system call en `arch/x86/entry/syscalls/syscall_64.tbl` durante el Ejercicio 3. Si usamos otro número, ajustarlo en este `#define`.

>[!NOTE]
> Cuando utilizamos llamadas al sistema "tradicionales" (como `open()`, `read()`, `write()`, etc.), no es necesario invocarlas explícitamente con `syscall()`, ya que la librería `libc` provee funciones *wrapper* que las encapsulan. Como nuestra system call es nueva y no tiene wrapper en libc, debemos invocarla por su número con la función genérica `syscall()`.

3. Compilamos el programa:

```bash
gcc -o get_threads_info get_threads_info.c
```

4. Ejecutamos el programa para ver el resultado:

```bash
./get_threads_info
```

La salida debería listar todos los procesos del sistema junto a sus hilos en formato jerárquico:

```
Información de los hilos en ejecución:
----------------------------------------
Proceso: systemd (PID: 1)
    ├── Hilo: systemd (TID: 1)
Proceso: kthreadd (PID: 2)
    ├── Hilo: kthreadd (TID: 2)
...
----------------------------------------
```

### Construcción de un Makefile para automatizar la compilación

Con lo visto en la Práctica 1 sobre Makefiles, construya un Makefile de manera que si ejecuto:
- `make`, nuestro programa se compila get_task_info.c
- `make clean`, limpia el ejecutable y el código objeto generado
- `make run`, ejecuta el programa

```makefile
CC = gcc # Compilador
CFLAGS = -Wall # Flags del compilador
TARGET = get_threads_info # Nombre del ejecutable a generar
SRC = get_threads_info.c # Archivo fuente

all: $(TARGET)

# Para construír get_threads_info, necesitamos get_threads_info.c
$(TARGET): $(SRC) 
    # Expande a gcc -Wall -o get_threads_info get_threads_info.c
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) 
clean:
    # Elimina el ejecutable y cualquier archivo objeto generado
	rm -f $(TARGET) *.o


run: $(TARGET)
    # Antes de ejecutar, garantiza que el binario esté compilado. Si no lo está, dispara la regla de $(TARGET) primero.
	./$(TARGET)

.PHONY: all clean run
```

## Monitoreando System Calls

1. Ejecutamos el programa anteriormente compilado y observamos su salida:

```bash
./get_threads_info



Información de los hilos en ejecución:
----------------------------------------
Proceso: systemd (PID: 1)
    ├── Hilo: systemd (TID: 1)
Proceso: kthreadd (PID: 2)
    ├── Hilo: kthreadd (TID: 2)
Proceso: pool_workqueue_ (PID: 3)
    ├── Hilo: pool_workqueue_ (TID: 3)
Proceso: kworker/R-rcu_g (PID: 4)
    ├── Hilo: kworker/R-rcu_g (TID: 4)
Proceso: kworker/R-sync_ (PID: 5)
    ├── Hilo: kworker/R-sync_ (TID: 5)
Proceso: kworker/R-slub_ (PID: 6)
    ├── Hilo: kworker/R-slub_ (TID: 6)
Proceso: kworker/R-netns (PID: 7)
    ├── Hilo: kworker/R-netns (TID: 7)
Proceso: kworker/R-mm_pe (PID: 12)
    ├── Hilo: kworker/R-mm_pe (TID: 12)
Proceso: rcu_tasks_kthre (PID: 13)
    ├── Hilo: rcu_tasks_kthre (TID: 13)
Proceso: rcu_tasks_rude_ (PID: 14)
    ├── Hilo: rcu_tasks_rude_ (TID: 14)
Proceso: rcu_tasks_trace (PID: 15)
    ├── Hilo: rcu_tasks_trace (TID: 15)
Proceso: ksoftirqd/0 (PID: 16)
    ├── Hilo: ksoftirqd/0 (TID: 16)
Proceso: rcu_preempt (PID: 17)
    ├── Hilo: rcu_preempt (TID: 17)
Proceso: rcu_exp_par_gp_ (PID: 
----------------------------------------

```

2. Luego de ejecutar el programa, inspeccionamos el log del kernel con `dmesg`:

```bash
sudo dmesg | tail -30
```
```
    [  926.318139]  ? exc_invalid_op+0x13/0x60
    [  926.318144]  ? asm_exc_invalid_op+0x16/0x20
    [  926.318168]  ? vsnprintf+0x4b6/0x560
    [  926.318175]  ? vsnprintf+0x6d/0x560
    [  926.318183]  snprintf+0x51/0x70
    [  926.318192]  __x64_sys_get_threads_info+0x104/0x1a0
    [  926.318201]  do_syscall_64+0x7e/0x190
    [  926.318206]  ? srso_alias_return_thunk+0x5/0xfbef5
    [  926.318211]  ? __handle_mm_fault+0xb25/0xfe0
    [  926.318234]  ? srso_alias_return_thunk+0x5/0xfbef5
    [  926.318238]  ? __count_memcg_events+0x9d/0x130
    [  926.318245]  ? srso_alias_return_thunk+0x5/0xfbef5
    [  926.318249]  ? count_memcg_events.constprop.0+0x1a/0x30
    [  926.318255]  ? srso_alias_return_thunk+0x5/0xfbef5
    [  926.318259]  ? handle_mm_fault+0xaa/0x2d0
    [  926.318265]  ? srso_alias_return_thunk+0x5/0xfbef5
    [  926.318269]  ? do_user_addr_fault+0x375/0x670
    [  926.318276]  ? srso_alias_return_thunk+0x5/0xfbef5
    [  926.318291]  ? exc_page_fault+0x72/0x190
    [  926.318297]  entry_SYSCALL_64_after_hwframe+0x76/0x7e
    [  926.318304] RIP: 0033:0x7f5bffea9799
    [  926.318309] Code: 08 89 e8 5b 5d c3 66 2e 0f 1f 84 00 00 00 00 00 90 48 89 f8 48 89 f7 48 89 d6 48 89 ca 4d 89 c2 4d 89 c8 4c 8b 4c 24 08 0f 05 <48> 3d 01 f0 ff ff 73 01 c3 48 8b 0d 37 06 0d 00 f7 d8 64 89 01 48
    [  926.318313] RSP: 002b:00007fff45269138 EFLAGS: 00000202 ORIG_RAX: 00000000000001d5
    [  926.318319] RAX: ffffffffffffffda RBX: 00007fff45269668 RCX: 00007f5bffea9799
    [  926.318322] RDX: 0000559d92420dd8 RSI: 0000000000000400 RDI: 00007fff45269140
    [  926.318325] RBP: 00007fff45269550 R08: 00007f5bfff9b680 R09: 00007f5bfff8f4e8
    [  926.318328] R10: 0000000000000000 R11: 0000000000000202 R12: 0000000000000000
    [  926.318331] R13: 00007fff45269678 R14: 0000559d92420dd8 R15: 00007f5bfffc9020
    [  926.318351]  </TASK>
    [  926.318353] ---[ end trace 0000000000000000 ]---
```

>[!NOTE]
> En el log del kernel deberíamos ver los mensajes generados por las llamadas a `printk` que están dentro de nuestras system calls (por ejemplo, `PID: <n> | Nombre: <comando>` por cada proceso recorrido en `get_task_info`). Esto se debe a que `printk` escribe en el *ring buffer* del kernel, accesible vía `dmesg` o `/var/log/kern.log`. La diferencia con `printf` es que esta última escribe a `stdout` del proceso de usuario.

3. Ejecutamos el programa con la herramienta `strace` para ver las system calls que invoca:

```bash
strace ./get_threads_info
```

>[!NOTE]
> Si `strace` no está instalado en la VM, lo instalamos con `sudo apt install strace`.

4. En la salida de `strace` deberíamos ver una línea similar a la siguiente, donde nuestra system call aparece identificada por su número en hexadecimal:

```
syscall_0x1d5(0x7fff136e5140, 0x400, 0x55f507d64dd8, 0, 0x7faf5080b680, 0x7faf507ff4e8) = 0x400
```

5. Para confirmar que el número en hexadecimal corresponde a nuestra system call, lo convertimos a decimal:

```bash
echo $((0x1d5))
```

El valor que obtenemos debe coincidir con el número que asignamos en `syscall_64.tbl` (en este caso, 469). Esto confirma que `strace` interceptó la invocación de nuestra syscall personalizada y la reportó por su número, ya que aún no existe un nombre simbólico registrado en la base de datos de `strace`.

