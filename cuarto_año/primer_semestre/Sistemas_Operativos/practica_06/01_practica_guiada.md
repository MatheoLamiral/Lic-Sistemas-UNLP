# Práctica guiada

>[!NOTE]
> La práctica requiere ejecutar los programas affinity y affinity_half_and_half provistos en el repositorio de la cátedra. En cada caso si el programa tarda demasiado o muy poco ajuste la macro ITERATIONS y/o la macro THREADS para disminuir o aumentar la carga del sistema.

## Ejercicio 1:​ Utilice lscpu para determinar cuántos cores lógicos tiene su computadora (si usa una máquina virtual asegúrese de configurar al menos 2 CPUs para llevar a cabo el resto de la práctica).

En mi caso, se puede observar `CPU(s): 16`

## Ejercicio 2:​ Analice el código y comentarios del programa affinity.c.

El programa crea 100 hilos (constante `THREADS`) con `pthread_create` y espera a que terminen con `pthread_join`. Cada hilo ejecuta la función `worker`, que usa `sched_getcpu()` para **obtener en qué core está corriendo** e imprime "Worker thread X, running on CPU Y". Luego entra en un bucle largo (`ITERATIONS`) que **simula trabajo** y, en cada vuelta, vuelve a llamar a `sched_getcpu()` para **detectar si el scheduler migró el hilo a otro core**, en cuyo caso imprime "moved from CPU A to CPU B". Las impresiones se hacen con `printf_sync`, un `printf` **thread-safe que usa un mutex para que las salidas de los 100 hilos no se mezclen**. 
En síntesis, el programa **permite observar en qué core arranca cada hilo y si el kernel lo mantiene ahí o lo migra durante la ejecución**.

## Ejercicio 3:​ Compile los programas provistos en practica6 con el comando make.

Se compila con `make`, que usa el `Makefile` provisto para compilar `affinity.c` y `affinity_half_and_half.c` con gcc, generando los ejecutables `affinity` y `affinity_half_and_half`.

## Ejercicio 4:​ Ejecute ./affinity y conteste:

### a. ¿Qué información muestra el programa?

**Muestra, por cada uno de los 100 hilos (worker), en qué core (CPU) se ejecuta**, la línea "Worker thread X, running on CPU Y" indica el core donde arrancó cada hilo. Y si durante la ejecución el scheduler migra un hilo a otro core, imprime "Worker thread X moved from CPU A to CPU B". En mi caso, los hilos se distribuyeron en los 16 cores (CPU 0-15). El **scheduler repartió la carga entre todos los cores disponibles** (balanceo).

### b. ¿Los hilos se ejecutan siempre en el mismo core desde su creación?

No, los hilos **no se ejecutan siempre en el mismo core** desde su creación, aparecen muchas líneas "moved", es decir, el **scheduler los migra entre cores durante la ejecución**. Esto ocurre porque **hay muchos más hilos (100) que cores (16)**, el scheduler debe repartir el tiempo de CPU y rebalancear la carga, migrando hilos entre cores. Aunque el scheduler prefiere mantener la afinidad (para aprovechar la caché), con esta relación hilos/cores prioriza el balanceo.

### c. Para más claridad puede elegir un hilo y seguir su ejecución con grep:

```bash
./affinity | grep "thread 4[, ]"
```

- Estos son algunos ejemplos:
```bash
matheolamiral@fedora ~/D/L/4/S/p/c/practica6 > ./affinity | grep "thread 4[, ]"
Worker thread 4, running on CPU 2
Worker thread 4 moved from CPU 2 to CPU 3
Worker thread 4 moved from CPU 3 to CPU 13
Worker thread 4 moved from CPU 13 to CPU 12
Worker thread 4 moved from CPU 12 to CPU 13
Worker thread 4 moved from CPU 13 to CPU 12
matheolamiral@fedora ~/D/L/4/S/p/c/practica6 > ./affinity | grep "thread 1[, ]"
Worker thread 1, running on CPU 8
matheolamiral@fedora ~/D/L/4/S/p/c/practica6 > ./affinity | grep "thread 3[, ]"
Worker thread 3, running on CPU 14
Worker thread 3 moved from CPU 14 to CPU 15
Worker thread 3 moved from CPU 15 to CPU 14
Worker thread 3 moved from CPU 14 to CPU 15
Worker thread 3 moved from CPU 15 to CPU 14
Worker thread 3 moved from CPU 14 to CPU 6
Worker thread 3 moved from CPU 6 to CPU 7
```

## Ejercicio 5:​ Utilice taskset para ejecutar todos los hilos del programa affinity en el core 0.

- `taskset -c 0 ./affinity`

### a. ¿Cuánto tiempo tardó la ejecución comparativamente con invocar ./affinity sin taskset? Puede usar el comando time y sumar los 3 valores que devuelve para obtener un valor preciso.

```bash
# Libre (usando los 16 cores)
matheolamiral@fedora ~/D/L/4/S/p/c/practica6 > time ./affinity > /dev/null


________________________________________________________
Executed in    1.15 secs    fish           external
   usr time   17.87 secs    0.23 millis   17.87 secs
   sys time    0.01 secs    1.21 millis    0.01 secs

# Todos en el core 0
matheolamiral@fedora ~/D/L/4/S/p/c/practica6 > time taskset -c 0 ./affinity > /dev/null


________________________________________________________
Executed in   10.11 secs    fish           external
   usr time   10.02 secs    1.50 millis   10.02 secs
   sys time    0.02 secs    0.54 millis    0.02 secs

```

- `time` te devuelve 3 valores:
  - `real` → tiempo total transcurrido. Este es el que importa para comparar.
  - `user` → tiempo de CPU en modo usuario (sumado de todos los cores).
  - `sys` → tiempo de CPU en modo kernel.

Con todos los cores, el tiempo real fue 1.15 s, forzando todo al core 0, el real fue 10.11 s → ~8.8× más lento en un solo core. En el libre, user (17.87 s) es mucho mayor que real (1.15 s), porque ~16 cores trabajaron en paralelo (17.87 / 1.15 ≈ 15.5 ≈ 16 cores). El trabajo total se repartió entre los núcleos, por eso terminó rápido en tiempo de reloj. En cambio, cuando usamos solo el core 0 no hay paralelismo, el tiempo de CPU coincide con el tiempo transcurrido, los 100 hilos se serializan en un núcleo.
En conclusión, el **paralelismo real de SMP acelera drásticamente. Serializar todo en un core desperdicia los demás núcleos.**

>[!NOTE]
> El `> /dev/null` manda toda la salida de los hilos al vacío, para que la impresión de miles de líneas no ensucie ni distorsione la medición del tiempo.

## Ejercicio 6:​ Analice el código y comentarios de affinity_half_and_half.c.

### a. ¿En qué core se ejecutarán los procesos con rank < THREADS / 2?

Los hilos con `rank < THREADS/2` (es decir, los 50 primeros, rank 0 a 49) se ejecutarán en el CPU 0. El código les fija la afinidad a la CPU 0 con `CPU_SET(0, &cpuset)` y `sched_setaffinity()`. Los otros 50 (rank ≥ 50) van al CPU 1.

### b. Ejecute ./affinity_half_and_half y observe la asignación de cores de forma similar al punto 4. De nuevo puede filtrar un hilo con grep para más claridad.

Cada hilo primero imprime el core donde arrancó ("running on CPU X", un core cualquiera de los 16 que le asignó el scheduler), y luego una única línea "moved from CPU X to CPU Y" que lo lleva a su core asignado.

- Los hilos 0 a 49 (`rank < THREADS/2`) terminan todos en CPU 0 ("moved ... to CPU 0").
- Los hilos 50 a 99 (`rank ≥ THREADS/2`) terminan todos en CPU 1 ("moved ... to CPU 1").  

Es decir, aunque tengo 16 cores, el programa fuerza a que la mitad de los hilos corra en CPU 0 y la otra mitad en CPU 1, mediante `sched_setaffinity()`.

### c. ¿Los hilos que arrancan un core dado siguen toda su ejecución en el mismo core? ¿Por qué?

**Sí. Después de la migración inicial hacia su core asignado (CPU 0 o CPU 1), cada hilo permanece en ese core toda su ejecución**, no aparece ninguna otra línea "moved" para él (migra una sola vez y se queda). Esto se debe a que el programa fija manualmente la afinidad de cada hilo con `sched_setaffinity()`. **Al establecer la afinidad, el kernel queda impedido de migrar el hilo a otro core**, incluso si quisiera balancear la carga.

>[!NOTE]
> En el ejercicio 4 (`affinity.c`), el scheduler decidía y migraba libremente los hilos por balanceo (afinidad blanda/automática), acá el programador impone la afinidad (afinidad dura/forzada), y los hilos quedan clavados en su core.