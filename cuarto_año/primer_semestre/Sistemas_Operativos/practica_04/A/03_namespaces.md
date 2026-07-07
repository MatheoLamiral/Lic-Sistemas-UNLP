# Namespaces

## Ejercicio 1:​ Explique el concepto de namespaces.

Namespace permite **abstraer un recurso global del sistema** para que los procesos dentro de ese namespace piensen que tienen su propia instancia aislada de ese recurso global. son la **base del aislamiento de los contenedores**
- **Limitan** lo que un proceso puede **ver**, y en consecuencia, lo que puede **usar**
- Cualquier **modificación** a un recurso queda **contenida dentro del namespace**


>[!NOTE]
> Un namespace es automáticamente eliminado cuando el último proceso en él finaliza o lo abandona

## Ejercicio 2:​ ¿Cuáles son los posibles namespaces disponibles?


|Namespace|Qué aísla|
|---------|---------|
| **IPC**     | System V IPC, cola de mensajes POSIX |
| **Network** | Dispositivos de red|
| **Mount**   | Puntos de montaje|
| **PID**     | IDs de procesos|
| **User**    | IDs de usuarios y grupos|
| **UTS**     | Hostname y nombre de dominio|
| **Cgroup**  | cgroup root directory|
| **Time**    | Distintos offsets al clock del sistema por namespace|


## Ejercicio 3:​ ¿Cuáles son los namespaces de tipo Net, IPC y UTS una vez que inicie el sistema (los que se iniciaron al ejecutar la VM de la cátedra)?

- `lsns` lista los namespaces y `-t ` se utiliza para filtrar por tipo: 
```bash
root@so:~# lsns -t net
        NS TYPE NPROCS PID USER    NETNSID NSFS COMMAND
4026531840 net      85   1 root unassigned      /sbin/init
root@so:~# lsns -t ipc
        NS TYPE NPROCS PID USER COMMAND
4026531839 ipc      85   1 root /sbin/init
root@so:~# lsns -t uts
        NS TYPE NPROCS   PID USER             COMMAND
4026531838 uts      82     1 root             /sbin/init
4026532166 uts       1   240 root             ├─/lib/systemd/systemd-udevd
4026532188 uts       1   282 systemd-timesync ├─/lib/systemd/systemd-timesyn
4026532256 uts       1   433 root             └─/lib/systemd/systemd-logind
```

## Ejercicio 4:​ ¿Cuáles son los namespaces del proceso cron? Compare los namespaces net, ipc y uts con los del punto anterior, ¿son iguales o diferentes?

```bash
so@so:~$ pgrep cron
426
# ahora como root
root@so:~# lsns -p 426
        NS TYPE   NPROCS PID USER COMMAND
4026531834 time       85   1 root /sbin/init
4026531835 cgroup     85   1 root /sbin/init
4026531836 pid        85   1 root /sbin/init
4026531837 user       85   1 root /sbin/init
4026531838 uts        82   1 root /sbin/init
4026531839 ipc        85   1 root /sbin/init
4026531840 net        85   1 root /sbin/init
4026531841 mnt        81   1 root /sbin/init
```

`net`, `ipc` y `uts` son idénticos a los del ejercicio 3. Esto se debe a que `cron` es un servicio del sistema que no crea sus propios namespaces, **corre en los mismos namespaces globales/iniciales que el resto de los procesos**. **Por defecto todos los procesos comparten esos namespaces**, el aislamiento recién aparece al crear uno nuevo con `unshare`.

## Ejercicio 5:​ Usando el comando unshare crear un nuevo namespace de tipo UTS.

### a. unshare --uts sh (son dos (--) guiones juntos antes de uts)

- Crea el namespace y abre la linea de comandos del mismo:
```bash
root@so:~# unshare --uts sh
# 
```
### b. ¿Cuál es el nombre del host en el nuevo namespace? (comando hostname)

El comando `hostname`, muestra la salida `so`

### c. Ejecutar el comando lsns. ¿Qué puede ver con respecto a los namespaces?

```bash
# lsns
        NS TYPE   NPROCS   PID USER             COMMAND
4026531834 time       93     1 root             /sbin/init
4026531835 cgroup     93     1 root             /sbin/init
4026531836 pid        93     1 root             /sbin/init
4026531837 user       93     1 root             /sbin/init
4026531838 uts        88     1 root             /sbin/init
4026531839 ipc        93     1 root             /sbin/init
4026531840 net        93     1 root             /sbin/init
4026531841 mnt        89     1 root             /sbin/init
4026532165 mnt         1   248 root             ├─/lib/systemd/systemd-udevd
4026532166 uts         1   248 root             ├─/lib/systemd/systemd-udevd
4026532167 mnt         1   278 systemd-timesync ├─/lib/systemd/systemd-times
4026532196 uts         1   278 systemd-timesync ├─/lib/systemd/systemd-times
4026532255 mnt         1   440 root             ├─/lib/systemd/systemd-login
4026532266 uts         1   440 root             └─/lib/systemd/systemd-login
4026531862 mnt         1    26 root             kdevtmpfs
4026532233 uts         2   654 root             sh
```

Vemos que en la última línea se agrega nuestro namespace UTS nuevo, con ID 4026532233 y que el proceso sh (PID 654) lo está utilizando.

### d. Modificar el nombre del host en el nuevo hostname.

- Cambia el nombre del hostname, en este caso "aislado"
```bash
# hostname aislado
```
### e. Abrir otra sesión, ¿cuál es el nombre del host anfitrión?

Al abrir otra sesión y ejecutar `hostname`, vemos que el host es **so**

### f. Salir del namespace (exit). ¿Qué sucedió con el nombre del host anfitrión?

Al salir del namespace (exit), el hostname del anfitrión sigue siendo so (nunca dejó de serlo). El cambio de hostname de so a "aislado" estuvo **contenido dentro del namespace y nunca afectó al sistema real**, además, al terminar la shell sh, ese UTS namespace se destruyó (junto con su hostname "aislado").

## Ejercicio 6:​ Usando el comando unshare crear un nuevo namespace de tipo Net.

### a. unshare --pid sh

- Crea un nuevo PID namespace y lanza sh adentro. 

### b. ¿Cuál es el PID del proceso sh en el namespace? ¿Y en el host anfitrión?

- Dentro del namespace `echo $$` retorna 736
- Fuera del namespace `ps aux | grep sh` retorna una lista, pero particularmente nos interesa la siguiente fila:
```bash
root         736  0.0  0.0   2576   908 pts/1    S+   16:07   0:00 sh
```

El proceso `sh` del namespace **tiene el mismo PID** (736) visto desde adentro (`echo $$`) que desde afuera (`ps aux`). El aislamiento existe pero todavía no es visible, porque **sin un `/proc` propio la shell sigue leyendo los PIDs del host**.

### c. Ayuda: los PIDs son iguales. Esto se debe a que en el nuevo namespace se sigue viendo el comando ps sigue viendo el /proc del host anfitrión. Para evitar esto (y lograr un comportamiento como los contenedores), ejecutar:

```bash
unshare --pid --fork --mount-proc
```

### d. En el nuevo namespace ejecutar ps -ef. ¿Qué sucede ahora?

Se ven solo dos procesos, la shell con PID 1 y el propio ps con PID 4. Ya no se ven los procesos del host. Esto ocurre porque `--fork` hace que la shell sea el PID 1 del nuevo namespace, y `--mount-proc` monta un `/proc` propio, del cual `ps` lee la información

>[!NOTE]
> Es el comportamiento de aislamiento de un contenedor, numeración de PIDs propia empezando en 1, y solo los procesos del namespace visibles

### e. Salir del namespace

Salimos del namespace con `exit`
