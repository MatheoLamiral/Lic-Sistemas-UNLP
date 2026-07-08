# Conceptos teóricos

## Ejercicio 1:​ Explique las características principales y formas de comunicación entre procesos en:

### a. Multiprocesadores con memoria compartida

Dos o más CPU comparten el acceso a la RAM. Los programas se ejecutan en cualquier CPU y cada proceso ve un espacio normal de direcciones virtuales. Los procesos se comunican a través de la memoria compartida. Es el esquema de **mayor acoplamiento**, con comunicación muy rápida (~2-10 nseg).

### b. Multicomputadora con memoria independiente / pasaje de mensajes

Cada CPU tiene su memoria local y los procesos se comunican a través del pasaje de mensajes por interconexión de alta velocidad. **Fuertemente acopladas** (clusters), comunicación en el orden de µseg (10-50)

### c. Sistemas Distribuidos

Cada nodo es una PC completa con su memoria y los procesos se comunican a través del pasaje de mensajes por red. Es el esquema de **menor acoplamiento** y comunicación mucho más lenta (~10-100 mseg).

## Ejercicio 2:​ Indique en qué CPU/s se ejecuta el sistema operativo en sistemas de tipo:

### a. Maestro-esclavo

El **SO se ejecuta en una única CPU, la maestra**. Hay **una sola copia del SO, y todas las system calls se redirigen a esa CPU maestra**. Las CPU esclavas ejecutan los procesos de usuario y cuando necesitan un servicio del SO, se lo piden al maestro. La maestra, si le sobra tiempo, también puede ejecutar procesos.

>[!NOTE]
> Con muchas CPU el maestro es un cuello de botella

### b. SMP

Hay una sola copia del SO en memoria, y cualquier CPU puede ejecutarlo. La syscall la ejecuta la CPU que la invocó.

>[!NOTE]
> No tiene cuello de botella, pero dos o más CPU pueden estar ejecutando código del SO a la vez, o seleccionando el mismo proceso o misma página libre

## Ejercicio 3:​ ¿Qué puede ocurrir si el kernel S.O. quiere acceder en paralelo a una estructura de datos en la memoria compartida en un sistema SMP? ¿Qué mecanismo permite manejar esta situación?

Si dos o más CPU acceden en paralelo a la misma estructura de datos del kernel (una sin protección), se produce una **condición de carrera** (race condition), donde las **operaciones se entremezclan y pueden dejar la estructura en un estado inconsistente o corrupto**.

Existen dos soluciones a este problema:
- **Lock global**
  - **Todo el SO es una seccion crítica**, donde cualquier CPU lo ejecuta, pero solo una a la vez
  - Se comporta como maestro-esclavo, se usa muy poco debido a su **mala performance**
- **Lock por estructura**
  - Varias **secciones críticas independientes**, cada una con su propio mutex
  - Tiene un **mejor rendimiento** y es el esquema más usado. Sin embargo, existen **dificultades** para delimitar cada sección crítica. Estructuras en varias secciones pueden generar **deadlocks**

>[!NOTE]
> En uniprocesador bastaba con deshabilitar interrupciones para proteger una tabla crítica, pero en multiprocesador NO alcanza (se deshabilita las de una CPU, pero otra puede seguir accediendo), por eso hace falta un protocolo de mutex real

## Ejercicio 4:​ ¿En el caso de una arquitectura SMP puede haber un impacto negativo por migrar un hilo de una CPU a otra?

Si, hay un impacto negativo, y es que se **pierde el aprovechamiento de la caché**. **Un hilo que se ejecuta en una CPU va cargando sus datos e instrucciones en la caché de esa CPU**, si el hilo sigue en esa CPU tiene alta probabilidad de encontrar sus datos ya cacheados, esto se llama **planificación por afinidad**. **Al migrar el hilo a otra CPU pierde la afinidad de caché**, la nueva CPU no tiene sus datos cacheados, lo que provoca **cache misses, relecturas desde memoria y tráfico extra en el bus por el protocolo de coherencia (trashing)**.

>[!NOTE]
> Por eso el SO usa planificación de 2 niveles (cada CPU tiene su colección de hilos y solo se migran si una CPU queda ociosa), prioriza mantener la afinidad, migrando solo para balancear carga.