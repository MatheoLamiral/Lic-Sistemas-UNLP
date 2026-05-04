# System calls


## Ejercicio 1: ¿Qué es una System Call? ¿Para qué se utiliza?

Una System Call (llamada al sistema) es el mecanismo que utiliza un proceso de usuario para solicitar un servicio al Sistema Operativo. Es un llamado al kernel para ejecutar una función específica que controla un dispositivo o ejecuta una instrucción privilegiada. 

Los procesos corren en modo usuario, limitados a su espacio de direcciones, sin acceso directo al hardware. Cuando necesitan una operación privilegiada (leer un archivo, crear un proceso, etc.), deben pedírsela al SO, que corre en modo kernel. La syscall es el puente entre ambos, se ejecuta en modo kernel pero en contexto del proceso que la invocó.  

Se utilizan para:
- **Controlar el hardware** (disco, red, mouse) que el proceso no puede tocar directamente.
- **Ejecutar instrucciones privilegiadas** reservadas al kernel.
- **Proveer una interfaz común y portable** (estandarizada por POSIX).

Una System Call se invoca de la siguiente manera:

1. La libc carga el número de syscall y los parámetros en registros (máx. 6 parámetros).
2. Ejecuta un trap: int 0x80 (x86), syscall (x86_64), svc (ARM).
3. Se cambia a modo kernel; el dispatcher busca el número en la syscall table y ejecuta el handler.
4. Retorna el control al proceso con el valor de retorno.

El programador normalmente no invoca syscalls directamente: usa los wrappers de libc (definidos por POSIX para garantizar portabilidad).

>[!NOTE] libc
> Librería estándar de C que en UNIX/Linux funciona como API principal del SO. Provee wrappers sobre las system calls, exponiendo funciones de alto nivel (printf, open, read) que internamente invocan al kernel. Es la interfaz entre las aplicaciones de usuario y las syscalls.

>[!NOTE] POSIX
> Estándar que define la interfaz común de los sistemas UNIX (funciones de libc, syscalls, shell, utilidades). Su propósito es garantizar portabilidad: un programa escrito contra POSIX corre en cualquier SO compatible sin tocar el código.

## Ejercicio 2: ¿Para qué sirve la macro syscall? Describa el propósito de cada uno de sus parámetros.

`syscall()` es una función de libc (declarada en `unistd.h`) que permite invocar explícitamente una system call por su número, sin pasar por el wrapper específico de libc. Se usa cuando:

- La syscall es nueva y libc todavía no provee un wrapper.
- Se quiere invocar una syscall propia (como en esta práctica).
- Se necesita testear o estudiar el mecanismo de invocación directa.

- Firma
  - `long int syscall(long int sysno, ...);`
- Parámetros
  - `sysno`: número de la system call a invocar.
  - `...`: lista de parámetros para la system call, según su firma (máx. 6 parámetros).
- Valor de retorno 
  - Devuelve un long con el valor que retorna la syscall. Ante error, devuelve -1 y setea errno.

## Ejercicio 3: Ejecute el siguiente comando e identifique el propósito de cada uno de los archivos que encuentra `ls -lh /boot | grep vmlinuz`

```bash
    matheolamiral:licenciatura_en_sistemas/ (main*) $ ls -lh /boot | grep vmlinuz

    -rwxr-xr-x. 1 root root  17M Jan 11 00:15 vmlinuz-0-rescue-f6a2e2a13ec044a0991e43e64d8f0d71
    -rwxr-xr-x. 1 root root  17M Oct  5  2025 vmlinuz-6.17.1-300.fc43.x86_64
    -rwxr-xr-x. 1 root root  18M Mar 24 21:00 vmlinuz-6.19.10-200.fc43.x86_64
    -rwxr-xr-x. 1 root root  18M Apr 17 21:00 vmlinuz-6.19.13-200.fc43.x86_64
``` 

Los archivos vmlinuz son imágenes comprimidas y booteables del kernel Linux ubicadas en /boot. El nombre viene de:
- vm: virtual memory (el kernel soporta memoria virtual)
- linuz: Linux (el sistema operativo)
- z: comprimido (gzip, bzip2, xz, etc.)

Es el archivo que el bootloader (GRUB) carga en memoria al arrancar el sistema para iniciar el kernel.

En cuanto a la salida del comando:  
- `vmlinuz-0-rescue-f6a2e2a13ec044a0991e43e64d8f0d71`: kernel de rescate. Sirve para bootear en modo recuperación si los kernels normales fallan.
- `vmlinuz-6.17.1-300.fc43.x86_64`: kernel principal de la versión 6.17.1.
- `vmlinuz-6.19.10-200.fc43.x86_64`: Kernel 6.19.10 instalado por una actualización previa.
- `vmlinuz-6.19.13-200.fc43.x86_64`: Kernel 6.19.13, el más reciente instalado.

- Convención de nombres
  - `vmlinuz-<versión>-<release>.<distro>.<arquitectura>`
    - `<versión>`: versión del kernel Linux
    - `<release>`: número de build de la distribución
    - `<distro>`: identificador (`fc43` para Fedora 43 en este caso)
    - `<arquitectura>`: arquitectura de CPU (x86_64 para 64 bits en este caso)
- Por qué hay varios kernels
  - El sistema conserva los kernels anteriores tras cada actualización para poder bootear una versión previa desde el menú de GRUB si el kernel nuevo presenta problemas (regresiones, drivers rotos, etc.).

## Ejercicio 4:  Acceda al codigo fuente de GNU Linux, sea visitando https://kernel.org/ o bien trayendo el código del kernel(cuidado, como todo software monolítico son unos cuantos gigas) `git clone https://github.com/torvalds/linux.git`

## Ejercicio 5: Para que sirve el archivo ` arch/x86/entry/syscalls/syscall_64.tbl`

Es la tabla de system calls para la arquitectura x86_64. Define el mapeo entre el número de syscall y la función handler del kernel que la implementa.

- Cada línea tienee el formato `<number>  <abi>     <name>          <entry point>`
  - `number`: número único de syscall
  - `abi`: interfaz binaria, `64` solo para x86_64, `32` para x32, `common` para ambas
  - `name`: nombre simbólico de la syscall (el que usa el espacio de usuario)
  - `entry point`: función del kernel que implementa la syscall 

- Se usa para:
  - Durante la compilación del kernel, este archivo se procesa para generar la syscall table (un array de punteros a funciones, indexado por número de syscall).
  - Cuando un proceso emite la instrucción `syscall`, el dispatcher del kernel:
    - Toma el número que está en `RAX`.
    - Busca esa entrada en la tabla generada a partir de `syscall_64.tbl`.
    - Invoca el handler correspondiente.

>[!NOTE] RAX
> Registro de propósito general de 64 bits en la arquitectura x86_64 (extensión del EAX de 32 bits y del AX de 16 bits). En el contexto de las system calls cumple dos roles:
> - Antes de la syscall, contiene el número de syscall a invocar 
> - Después de la syscall, contiene el valor de retorno de la syscall

## Ejercicio 6: ¿Para qué sirve la herramienta `strace`? ¿Cómo se usa?

`strace` es una herramienta de diagnóstico que traza las system calls invocadas por un proceso y las señales que recibe. Permite ver el "diálogo" entre un programa y el kernel: qué syscalls llama, con qué parámetros y qué retorna cada una.

- Se usa para:
  - Debuggear programas sin tener su código fuente.
  - Detectar fallos en accesos a archivos, permisos, conexiones de red, etc.
  - Analizar performance: ver qué syscalls son lentas o se invocan demasiado.
  - Aprender cómo un programa interactúa con el SO.
  - Investigar comportamientos sospechosos (seguridad, malware básico).

- Uso básico:
  - `strace <programa> [argumentos]`
- Ejemplo:
    ```bash
        $ strace a.out > /dev/null

        execve("./syscall.o", ["./syscall.o"], [/* 19 vars */]) = 0
        mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f12ea552000
        write(1, "hola mundo!", 11) = 11
    ```
    - Cada línea muestra: `nombre_syscall(parámetros) = valor_retorno`.


## Ejercicio 7: ¿Para qué sirve la herramienta ausyscall? ¿Cómo se usa?

`ausyscall` es una herramienta del paquete audit (auditd) que permite convertir entre nombres y números de system calls para una arquitectura dada. Es útil porque los números de syscall dependen de la arquitectura (no son los mismos en x86, x86_64, ARM, etc.).

-  Se usa para:
   -  Saber qué número corresponde a una syscall en cierta arquitectura. 
   -  Saber qué nombre tiene una syscall a partir de su número (útil al leer logs de auditoría o salidas crudas).
   -  Listar todas las syscalls disponibles en una arquitectura.
   -  Verificar el número asignado a una syscall propia recién agregada.

- Uso básico:
  - `ausyscall [arquitectura] <nombre_o_número>` 
  - Si se omite la arquitectura, usa la del sistema actual.

>[!NOTE] comparación con `strace`
> `strace` traza en runtime las syscalls que invoca un prooceso, mientras que `ausyscall` consulta estáticamente el mapeo entre nombres y números sin ejecutar nada

>[!NOTE] auditd
> Audit Daemon es el demonio de auditoría del sistema en Linux. Forma parte del Linux Audit Framework, un subsistema del kernel que permite registrar eventos de seguridad en el sistema.






