# Segunda fecha 2023

## Ejercicio 1:​ ¿Qué contiene el initramfs? ¿Qué funcionalidad/es provee?

El initramfs (initial RAM filesystem) es un sistema de archivos temporal que se carga en RAM y se monta durante el arranque, antes de que el kernel pueda montar el filesystem raíz (/) real del disco. Una vez completado el arranque, se desmonta.

Contiene los ejecutables, drivers y módulos mínimos para iniciar el sistema. Principalmente los drivers/módulos que el kernel necesita para acceder al disco donde está el root, más un init temporal y utilidades básicas.

Funcionalidad:el problema que resuelve, es que el kernel necesita drivers para montar el root, pero si esos drivers son módulos, están dentro del propio root que todavía no puede montar. El initramfs aporta esos drivers en RAM, el kernel monta el root real y luego le cede el control al init definitivo.

## Ejercicio 2:​ Describa los motivos que puede tener un usuario de Linux para compilar un kernel.

Los principales motivos son:
- Soportar nuevos dispositivos
  - Agregar drivers para hardware que el kernel actual no reconoce
- Agregar mayor funcionalidad
  - Incorporar soporte para nuevos sistemas de archivos, protocolos u opciones que no venias habilitadas
- Optimizar
  - optimizar el funcionamiento de acuerdo al sistema donde corre
- Adaptarlo
  - quitar el soporte de hardware o funcionalidades que no se usan, dejando un kernel mas liviano y eficiente
- Corrección de bugs
  - aplicar parches por problemas de seguridad o errores de programación

## Ejercicio 3:​ Indique si la siguiente afirmación es verdadera o falsa y justifique en cualquier caso:

"Los drivers acceden a las funcionalidades del kernel a través de system calls"

Falso. Los drivers se ejecutan en espacio de kernel / modo privilegiado, no en espacio de usuario. Por lo tanto no necesitan system calls para acceder a las funcionalidades del kernel, las invocan directamente a través de la API interna del kernel (funciones como `kmalloc`, `printk`, `register_chrdev`, etc.). Las system calls son el mecanismo que usa el código de espacio de usuario para pedirle servicios al kernel 

## Ejercicio 4:​ Describa en sus palabras para qué se usa la función register_chrdev(). ¿Se puede usar en espacio de usuario, espacio de kernel o en ambos?

`register_chrdev()` registra un dispositivo de caracter (character device) en el kernel. Es la función con la que un driver le dice al kernel que se encargará de este dispositivo. Al llamarla se asocia:
- Un major number (que identifica al driver)
- Una tabla de operaciones que indica qué función del driver ejecutar ante cada operación 

A partir de ese registro, cuando un proceso opera sobre el device file en `/dev`(cuyo major coincide), el kernel sabe que debe redirigir esas operaciones a las funciones de ese driver

Solo se puede usar en espacio de kernel. `register_chrdev()` es una función interna de la API del kernel, así que únicamente puede ser invocada por código que corre dentro del kernel, es decir, por drivers/módulos del kernel. 

## Ejercicio 5:​ ¿Qué es un link simbólico? ¿En qué se diferencia de un hard-link? ¿Cuál/es consumen un i-nodo al crearse?

## Ejercicio 6:​ Describa la forma en que BTRFS usa Copy-on-Write.

## Ejercicio 7:​ Describa RAID 5 y responda ¿cuántos discos pueden fallar en RAID 5 sin que haya pérdida de datos?

## Ejercicio 8:​ Suponga que un usuario ejecuta los siguientes comandos:

```
$ docker start 8fef5232d77d
$ docker exec 8fef5232d77d ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  0.0  0.0   4188  3188 pts/0    Ss+  21:23   0:00 mi_proceso
...
```

Luego ejecuta el siguiente comando:

```
$ ps aux
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
...
root      423548  0.0  0.0   4188  3188 pts/0    Ss+  18:23   0:00 mi_proceso
...
```

### Explique por qué el proceso "mi_proceso" tiene distinto PID en cada cuadro (siendo que es exactamente el mismo proceso). ¿Qué mecanismo específico del kernel de Linux hace que eso suceda?

"mi_proceso" tiene distinto PID debido a los namespaces de PID, la característica del kernel que Docker usa para aislar los contenedores. Un PID namespace le da al contenedor su propia vista aislada de los identificadores de proceso, independiente de la del host. Por eso el mismo proceso (existe una sola vez) tiene dos IDs, uno dentro del contenedor que se ve como PID 1 (es el primer proceso de su namespace, su "init"), y en el host tiene su PID real (423548) entre todos los procesos del sistema.

## Ejercicio 9:​ ¿Qué es un Union Filesystem? ¿Cómo lo utiliza Docker?

Es un mecanismo de montajes que permite que varios directorios se monten en el mismo punto y aparezcan como un único filesystem. Las capas inferiores son solo de lectura y la capa superior es de escritura. El uso que le da docker es, que cada imagen está formada por varias capas pailadas, donde cada capa es un conjunto de diferencias respecto de la anterior (cada capa no guarda el sistema de archivos completo, sino solo lo que cambió respecto de la capa de abajo). Todas son de solo lectura. Al ejecutar un contenedor, docker arma el union-filesystem apilando esas capas y le agrega encima una capa escibible propia del contenedor, usando chroot para fijar eso union-filesystem como raíz del contenedor

## Ejercicio 10:​ ¿De qué manera puede lograrse que los datos sean persistentes en Docker? ¿Qué dos maneras hay de hacerlo? ¿Cuáles son las diferencias entre ellas?

Para hacer que los datos sean persistentes en docker hay que almacenarlos en el host. Hay dos formas de hacerlo:
- Volumes (Volúmenes): Almacenados en una zona del filesystem gestionada por docker (`/var/lib/docker/volumes`), es la opción recomendada ya que ofrece mayor portabilidad
- Bind mounts: Mapean cualquier ruta del host (es elegible por el usuario) y pueden ser modificados por procesos ajenos a Docker

Las diferencias son que, con volumes la ubicación es gestionada por docker, mientras que con bind mounts puede ser cualquier ruta del host. En cuanto a portabilidad volumes es mejor ya que está desacoplado del host, mientras que bind mounts está atado a una ruta concreta. Los volumes estan pensados para docker, mientras que bind mount tambien puede ser manipulado por otros procesos del host
