# Control Groups

## Preparación

Actualmente Debian y la mayoría de las distribuciones usan CGroups 2 por defecto, pero para esta práctica usaremos CGroups 1. Para esto es necesario cambiar un parámetro de arranque del sistema en grub:

1. Editar /etc/default/grub:

    ```
    # Cambiar:
    GRUB_CMDLINE_LINUX="quiet"
    # Por:
    GRUB_CMDLINE_LINUX="quiet systemd.unified_cgroup_hierarchy=0"
    ```

2. Actualizar la configuración de GRUB:

    ```bash
    sudo update-grub
    ```

3. Reiniciar la máquina.

4. Verificar que se esté usando CGroups 1. Para esto basta con hacer `ls /sys/fs/cgroup/`. Se deberían ver varios subdirectorios como cpu, memory, blkio, etc. (en vez de todo montado de forma unificada).

> A continuación se probará el uso de cgroups. Para eso se crearán dos procesos que compartirán una misma CPU y cada uno la tendrá asignada un tiempo determinado.
>
> Nota: es posible que para ejecutar xterm tenga que instalar un gestor de ventanas. Esto puede hacer con `apt-get install xterm`.

## Ejercicio 1:​ ¿Dónde se encuentran montados los cgroups? ¿Qué versiones están disponibles?

Los `cgroups` están montados en `/sys/fs/cgroup/`. Están disponibles las versiones **v1** y **v2**, pero el sistema está configurado para usar v1, cada controlador se monta por separado en su subdirectorio (cpu, memory, blkio, pids, cpuset, etc.). Se verifica con `ls /sys/fs/cgroup/`. 

## Ejercicio 2:​ ¿Existe algún controlador disponible en cgroups v2? ¿Cómo puede determinarlo?

Se determina leyendo el archivo `cgroup.controllers` de la jerarquía v2 en `/sys/fs/cgroup/unified/`. Como la configuración que tenemos es para v1, está vacío, es decir, no hay controladores disponibles en v2 (todos estan asignados a v1).
- `cat /sys/fs/cgroup/unified/cgroup.controllers` no imprime nada

## Ejercicio 3:​ Analice qué sucede si se remueve un controlador de cgroups v1 (por ej. Umount /sys/fs/cgroup/rdma).

El `umount` **desmontó el filesystem** del controlador `rdma`, pero el directorio `/sys/fs/cgroup/rdma` **sigue existiendo** (vacío) como punto de montaje "huérfano". Entonces, el controlador `rdma` **ya no está disponible para usarse**, **no vamos a poder crear nuevos cgroups bajo ese controlador**.  

## Ejercicio 4:​ Crear dos cgroups dentro del subsistema cpu llamados cpualta y cpubaja. Controlar que se hayan creado tales directorios y ver si tienen algún contenido.

- Creamos los cgroups:
```bash
    root@so:~# mkdir /sys/fs/cgroup/cpu/cpualta
    root@so:~# mkdir /sys/fs/cgroup/cpu/cpubaja
```
- Controlamos que se hayan creado:
```bash
    root@so:~# ls /sys/fs/cgroup/cpu/cpualta
    cgroup.clone_children  cpuacct.usage_percpu_sys   cpu.cfs_quota_us
    cgroup.procs           cpuacct.usage_percpu_user  cpu.idle
    cpuacct.stat           cpuacct.usage_sys          cpu.shares
    cpuacct.usage          cpuacct.usage_user         cpu.stat
    cpuacct.usage_all      cpu.cfs_burst_us           notify_on_release
    cpuacct.usage_percpu   cpu.cfs_period_us          tasks
    root@so:~# ls /sys/fs/cgroup/cpu/cpubaja
    cgroup.clone_children  cpuacct.usage_percpu_sys   cpu.cfs_quota_us
    cgroup.procs           cpuacct.usage_percpu_user  cpu.idle
    cpuacct.stat           cpuacct.usage_sys          cpu.shares
    cpuacct.usage          cpuacct.usage_user         cpu.stat
    cpuacct.usage_all      cpu.cfs_burst_us           notify_on_release
    cpuacct.usage_percpu   cpu.cfs_period_us          tasks
```

>[!IMPORTANT]
> `/sys/fs/cgroup/cpu/` es un **filesystem cgroup**, cuando se crea un directorio ahí, el **kernel automáticamente lo convierte en un cgroup y le rellena adentro los archivos de control** (`cpu.shares`, `cpu.procs`, etc.), no es una carpeta común.

## Ejercicio 5:​ En base a lo realizado, ¿qué versión de cgroup se está utilizando?

La versión que se está utilizando es **cgroups v1**. Podemos darnos cuenta de esto, debido a la existencia de múltiples subdirectorios dentro de `/sys/fs/cgroup/`, donde cada **controlador tiene su propio punto de montaje por separado**.

## Ejercicio 6:​ Indicar a cada uno de los cgroups creados en el paso anterior el porcentaje máximo de CPU que cada uno puede utilizar. El valor de cpu.shares en cada cgroup es 1024. El cgroup cpualta recibirá el 70 % de CPU y cpubaja el 30 %.

El archivo `cpu.shares` define el **peso relativo de CPU de cada cgroup**. Por defecto es 1024. Para repartir 70/30 se calcula proporcionalmente sobre ~1024:
- 70% → 717 (≈ 0.70 × 1024)
- 30% → 307 (≈ 0.30 × 1024)

```bash
root@so:~# echo 717 > /sys/fs/cgroup/cpu/cpualta/cpu.shares
root@so:~# echo 307 > /sys/fs/cgroup/cpu/cpubaja/cpu.shares
```

>[!NOTE]
> `cpu.shares` es un **peso relativo y solo actúa cuando hay competencia por la CPU**. Es decir, el 70/30 recién se nota cuando ambos cgroups pelean por el mismo core al mismo tiempo. Si solo uno usa la CPU, se lleva el 100% aunque tenga 307 o 717

## Ejercicio 7:​ Iniciar dos sesiones por ssh a la VM. (Se necesitan dos terminales, por lo cual, también podría ser realizado con dos terminales en un entorno gráfico). Referenciaremos a una terminal como termalta y a la otra, termbaja.

## Ejercicio 8:​ Usando el comando taskset, que permite ligar un proceso a un core en particular, se iniciará el siguiente proceso en background. Uno en cada terminal. Observar el PID asignado al proceso que es el valor de la columna 2 de la salida del comando.

```bash
# taskset -c 0 md5sum /dev/urandom &
```

- En mi caso las salidas:
  - `[1] 835` → PID 835 en termalta
  - `[1] 841` → PID 841 en termbaja

>[!NOTE]
> `md5sum /dev/urandom` lee bytes aleatorios infinitamente y calcula su hash. Es una tarea CPU-bound que consume 100% de CPU. Al ligarlas ambas al core 0, las dos pelean por el mismo núcleo.

## Ejercicio 9:​ Observar el uso de la CPU por cada uno de los procesos generados (con el comando top en otra terminal). ¿Qué porcentaje de CPU obtiene cada uno aproximadamente?

Ejecutando `top`, vemos que los dos procesos rondan el 50% de uso de CPU. Esto, porque como **no los metimos en ningún cgroup**, el scheduler los trata por igual

## Ejercicio 10:​ En cada una de las terminales agregar el proceso generado en el paso anterior a uno de los cgroup (termalta agregarla en el cgroup cpualta, termbaja en cpubaja. El process_pid es el que obtuvieron después de ejecutar el comando taskset).

- En termalta:
```bash
    root@so:~# echo 835 > /sys/fs/cgroup/cpu/cpualta/cgroup.procs
```
- En termbaja:
```bash
    root@so:~# echo 841 > /sys/fs/cgroup/cpu/cpubaja/cgroup.procs
```

## Ejercicio 11:​ Desde otra terminal observar cómo se comporta el uso de la CPU. ¿Qué porcentaje de CPU recibe cada uno de los procesos?

Ahora vemos que el proceso **835 ronda el 70%** de uso de la CPU, y el **841 ronda el 30%**. Esto debido a que, **835 está en el cgroup cpualta** (shares 717) y **841 está en el cgroup cpubaja** (shares 307), y el **kernel reparte la CPU proporcionalmente a los shares cuando ambos compiten** por el mismo core.

>[!IMPORTANT]
> Estos porcentajes, siempre y cuando estén compitiendo por la CPU, en caso de que solo uno de ellos lo intente, tomara el 100% de la misma

## Ejercicio 12:​ En termalta, eliminar el job creado (con el comando jobs ven los trabajos, con kill %1 lo eliminan. No se olviden del %.). ¿Qué sucede con el uso de la CPU?

- En termalta
```bash
    root@so:~# jobs # muestra los jobs en background
    [1]+  Ejecutando              taskset -c 0 md5sum /dev/urandom &
    root@so:~# kill %1 # elimina el job número 1
```

Luego de esto, observamos que el **proceso 841** (cgroup cpubaja) **ronda el 100% de uso de la CPU**, esto debido a que, como vinimos mencionando, el **peso relativo que el cgroup pone sobre la CPU solo aplica si el proceso está compitiendo por la misma**, y como matamos el proceso 835, 841 ya no tiene competencia.

## Ejercicio 13:​ Finalizar el otro proceso md5sum.

- En termbaja
```bash
    root@so:~# jobs # muestra los jobs en background
    [1]+  Ejecutando              taskset -c 0 md5sum /dev/urandom &
    root@so:~# kill %1 # elimina el job número 1
```

Luego de esto, observamos que el uso de la CPU baja a ≈ 0

## Ejercicio 14:​ En este paso se agregarán a los cgroups creados los PIDs de las terminales (Importante: si se tienen que agregar los PID desde afuera de la terminal ejecute el comando echo $$ dentro de la terminal para conocer el PID a agregar. Se debe agregar el PID del shell ejecutando en la terminal).

```bash
    # En termalta
    root@so:~# echo $$ > /sys/fs/cgroup/cpu/cpualta/cgroup.procs
    # En termbaja
    root@so:~# echo $$ > /sys/fs/cgroup/cpu/cpubaja/cgroup.procs
```

## Ejercicio 15:​ Ejecutar nuevamente el comando taskset -c 0 md5sum /dev/urandom & en cada una de las terminales. ¿Qué sucede con el uso de la CPU? ¿Por qué?

Los `md5sum` **nacen ya dentro de cpualta y cpubaja respectivamente**, ya que **heredaron el cgroup de su shell**, sin que tuvieramos que meter sus PIDs a mano, a diferencia del ejercicio 10. El reparto vuelve a ser ~70% / ~30% respectivamente.

## Ejercicio 16:​ Si en termbaja ejecuta el comando: taskset -c 0 md5sum /dev/urandom & (deben quedar 3 comandos md5 ejecutando a la vez, 2 en la termbaja). ¿Qué sucede con el uso de la CPU? ¿Por qué?

Al lanzar un tercer `md5sum` en termbaja, quedan 3 procesos compitiendo por el core 0, uno en cpualta y dos en cpubaja. El reparto entre cgroups se mantiene por los shares (cpualta ~70%, cpubaja ~30%), pero como cpubaja ahora tiene dos procesos, esos deben repartirse el 30%, ~15% cada uno, mientras que el de cpualta conserva el ~70% completo. Esto demuestra que los `cpu.shares` **distribuyen la CPU por cgroup, no por proceso, el porcentaje del cgroup se divide entre todos sus procesos**.
