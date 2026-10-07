# Primera fecha 2023

## Ejercicio 1:​ ¿Qué es el kernel de GNU/Linux? ¿Cuáles son sus funciones principales dentro del Sistema Operativo?

El kernel de GNU/Linux es el núcleo del sistema operativo. Es una porción de código que reside en memoria principal, se ejecuta en modo privilegiado y actúa como intermediario entre el hardware y las aplicaciones, a las que ofrece una interfaz controlada mediante system calls. De hecho, en un sentido estricto, el kernel es el Sistema Operativo en sí mismo.

- Sus funciones principales son:
  - Administración de la memoria principal
  - Manejo del uso de la CPU
  - Administración de procesos
  - Gestión de E/S
  - Comunicación y concurrencia

## Ejercicio 2:​ Explique brevemente qué es un módulo del kernel de Linux y qué ventaja/s provee compilar una funcionalidad como módulo respecto a compilarla como built-in.

Es un fragmento de código que puede cargarse o descargarse en el kernel bajo demanda, en tiempo de ejecución (con `insmod`/`rmmod`), sin necesidad de recompilar ni reiniciar.

- Ventajas respecto a built-in:
- Uso de memoria: una funcionalidad built-in que no se usa nunca ocupa espacio igual. Como módulo se carga solo cuando se necesita.
- Sin reiniciar: para cambiar/actualizar algo built-in hay que recompilar el kernel y reiniciar el sistema. Un módulo se actualiza "en vuelo".
- Desarrollo más ágil: probar un driver es cargar/descargar un .ko, sin recompilar todo el kernel.

## Ejercicio 3:​ ¿Qué tipos de archivos se encuentran en /dev? ¿Qué representan estos archivos?

En `/dev` se encuentran los device files, que representan los dispositivos del sistema y son el punto de acceso desde el espacio de usuario. Se tratan como archivos (`open`/`read`/`write`) y el kernel redirige esas operaciones al driver correspondiente.
- Hay dos tipos:
  - De caracter (c): acceso byte a byte, secuencial. Ej: teclado, mouse, /dev/tty.
  - De bloque (b): datos en bloques de tamaño fijo con acceso aleatorio. Ej: discos, pendrives (/dev/sda).

## Ejercicio 4:​ ¿Cuál de las siguientes sentencias es verdadera?

### a. Libc es el componente del kernel donde se definen las system calls.

Falso, las syscalls se definen en el código del kernel. libc es la biblioteca de usuario que solo las "envuelve"

### b. Las system calls se definen en módulos del kernel que se pueden administrar con insmod, modprobe, rmmod y modinfo.

Falso, las syscalls son parte del kernel base, no se cargan/descargan como módulos.

### c. Las system calls se ejecutan en modo privilegiado y se identifican a través de un número.

Verdadero

### d. Cada driver implementa una system call.

Falso, un driver no implementa una syscall, implementa las operaciones del dispositivo (`read`/`write`/`open` vía `file_operations`). Las usa, no las define.

## Ejercicio 5:​ Indique si es verdadero o falso y justifique su respuesta:

"RAID 1 provee stripping y paridad distribuida"

## Ejercicio 6:​ En el contexto de los filesystems defina brevemente inodo, bloque y extent.

## Ejercicio 7:​ Suponga que un usuario desea limitar el uso de CPU de un proceso para que no sea mayor al 80%. ¿Qué mecanismo provisto por el kernel Linux podría utilizar?

El mecanismo que podría utilizar, es `cgroups`. Tendría que crear un cgroup en el subsistema/controlador de CPU, poner un límite de CPU (cuota) del 80% y agregar el proceso a ese cgroup (metiendo su PID en el group)

## Ejercicio 8:​ En el contexto de Docker ¿Qué es una imagen? ¿Y un contenedor? ¿Cuál es la principal diferencia entre ambos?

Una imagen en docker, es el template/molde de solo lectura que contiene la app + dependencias/librerías y las instrucciones para construir el contenedor, y el contenedor es la instancia en ejecución de esa imagen. La diferencia principal, es que la imagen no se ejecuta y el contenedor sí. De una misma imagen se pueden crear varios contenedores

## Ejercicio 9:​ ¿Qué características del kernel Linux utiliza docker para proveer containers?

Las características del kernel de linux que utiliza docker para proveer containers son:
- chroot para cambiar la raíz del contenedor
- Namespaces para darle al contenedor su "vista" aislada de los recursos (PID, Net, Mount, UTS, IPC, User)
- Cgroups para limitar y controlar los recursos que consume 

## Ejercicio 10:​ ¿Qué es el archivo compose y cuál es su función? ¿En qué sentido es diferente de un Dockerfile?

Es archivo de configuración para definir aplicaciones compuestas de varios contenedores. Su función es servir de definición declarativa de la aplicación, Docker compose lo lee y a partir de él crea y orquesta toda la aplicación.

Se diferencia de un Dockerfile en su propósito. Mientras que Dockerfile describe los pasos para construir una sola imagen, el compose define cómo levantar y orquestar una aplicación de varios contenedores. No son excluyentes, el compose puede incluso usar un Dockerfile con el bloque `build:`, uno arma la pieza y el otro orquesta el conjunto 