# Infograma de Repaso: Multiprocesadores

## Origen y motivación

- La industria siempre buscó **más poder de cómputo**. La solución histórica: subir la **velocidad de reloj**.
- Hoy subir el clock es físicamente complejo:
  - Ninguna señal va más rápido que la **luz** (~20 cm/nseg en cobre/fibra).
  - **Disipación de calor** (problema fundamental) y **consumo eléctrico**.
- **Solución actual:** cómputo **paralelo y/o distribuido** → varias CPU a velocidad "normal" que en conjunto dan la potencia. → **más cores**, no más Hz.

---

## Esquemas de arquitectura (mayor → menor acoplamiento)

| Esquema | Memoria | Comunicación | Retardo |
|---|---|---|---|
| **Multiprocesador (memoria COMPARTIDA)** | Un único espacio de direcciones, por **BUS** | A través de la memoria compartida | **2–10 nseg** |
| **Multicomputadora (memoria DISTRIBUIDA)** | Cada CPU tiene memoria local | **Pasaje de mensajes** (interconexión alta velocidad) | **10–50 μseg** |
| **Sistema distribuido** | Cada nodo es una PC completa | Pasaje de mensajes por **red** | **10–100 mseg** |

- **Multicomputadoras (clusters):** fáciles de fabricar, difíciles de programar. **Fuertemente acopladas** (una tarea empieza y termina en la misma CPU).
- **Sistemas distribuidos:** computadoras completas y heterogéneas (distinto SO/HW) conectadas por red.
- **Salto clave:** de nseg (compartida) a mseg (distribuido) → factor de **millones**.

---

## Memoria compartida: UMA vs NUMA

A nivel HW cada procesador direcciona toda la memoria. Según la **velocidad de acceso**:

| | **UMA** (Uniform Memory Access) | **NUMA** (Non-Uniform Memory Access) |
|---|---|---|
| **Tiempo de acceso** | **Igual** para todas las CPU | **Depende**: local rápido / remoto lento |
| **Espacio de direcciones** | Único | Único (visible a todas) |
| **Acceso remoto** | — | Con **LOAD/STORE**, requiere bus compartido |
| **Escalabilidad** | Baja (caro, poco escalable) | Alta (escala en n° de CPU) |
| **Rendimiento/costo** | Mayor rendimiento, más caro | Menor rendimiento a igual clock, más barato |
| **Ejemplo típico** | **SMP por bus** | Grandes sistemas multi-nodo |

### UMA en detalle
- **Basado en bus:** un único bus; al sumar CPU el **ancho de banda del bus** es el cuello de botella → CPU ociosa.
- **Con cache:** reduce accesos al bus. Bloque **RO** en varias caches; bloque **RW** en una sola. Necesita **protocolo de coherencia de cache**.
- **Cache + memoria local:** memoria privada por bus dedicado; la compartida solo para variables compartidas (requiere ayuda del **compilador**).
- **Escalar más allá del bus** (límite ~16–32 CPU):
  - **Crossbar (barras cruzadas):** n CPU × n bancos, hasta n conexiones; **contención** si 2 CPU van al mismo módulo; muchos switches (caro).
  - **Redes multietapa:** menos switches, pero **más bloqueos**. Mensaje = Módulo + Dirección + CódigoOp(READ/WRITE) + Valor.

### NUMA en detalle
- **NC-NUMA:** sin cache. **CC-NUMA:** con cache (clave mantener coherencia).
- **CC-NUMA grande → multiprocesador basado en directorios:** BD en HW que indica dónde está cada línea y su estado (limpia/sucia). Dirección = **nodo + línea + desplazamiento**.

### Coherencia de cache (problema central)
- Dato cacheado en varias CPU → al escribir, una CPU manda mensaje al bus:
  - Copias **limpias** en otras caches → se **descartan**.
  - Copia **sucia** → se escribe a memoria e informa antes de modificar.

---

## Chips multinúcleo
Más transistores por chip → opciones: más cache (poca mejora), más clock (sigue 1 solo hilo), o **más cores** (comparten cache/memoria → **paralelismo real**). El SW debe diseñarse según el HW.

---

## Tipos de SO multiprocesador

1. **Cada CPU con su SO** (poco usado): memoria dividida estáticamente; procesos atados a 1 CPU. Problemas: **desbalance**, no comparte páginas, cache de disco **inconsistente**.
2. **Maestro–Esclavo:** 1 sola copia del SO; todas las syscalls van a la CPU **maestra**. Resuelve balanceo/páginas, pero el maestro es **cuello de botella** con muchas CPU.
3. **SMP (Multiprocesadores Simétricos):** 1 copia del SO, **cualquier CPU** lo ejecuta; la syscall la corre la CPU que la invocó. Sin cuello de botella. Problema: varias CPU en el SO a la vez / eligen mismo proceso o página.

| Solución SMP | Descripción | Valoración |
|---|---|---|
| **Lock global** | Todo el SO = 1 sección crítica, una CPU a la vez | Se comporta como maestro-esclavo; mala performance |
| **Lock por estructura** | Varias secciones críticas, cada una con su mutex | Mejor rendimiento, **el más usado**; riesgo de **deadlocks** |

---

## Sincronización en multiprocesador

- En **uniprocesador** basta con **deshabilitar interrupciones** para tocar tablas del kernel.
- En **multiprocesador NO alcanza**: otra CPU puede generar interrupciones → se necesita **protocolo de mutex**.
- **TSL (Test and Set Lock):** lee palabra y escribe 1 (lock). En multiprocesador **no es indivisible** → 2 CPU podrían leer 0 y entrar juntas. **Solución:** TSL **bloquea el bus** (requiere soporte HW); genera carga por **espera activa (spinlock)**.
- Mejoras: variable de lock propia en cache de cada CPU; CPU que no obtiene lock va a una **lista y espera en su propio lock**; agregar **delays** entre intentos de TSL.

---

## Planificación en multiprocesador

Se decide **qué** hilo y **en qué CPU**. Se analizan **KLT** (hilos de kernel).

### Hilos independientes (tiempo compartido)
- **Cola única de listos:** simple, eficiente, da **balanceo de carga**. Desventaja: **contención** sobre la estructura única.
- **Espera activa:** si un hilo con spinlock pierde el quantum antes de liberar, las otras CPU quedan ociosas → flag por proceso (no se expulsa, Zahorjan 1991).
- **Afinidad de CPU:** ejecutar el hilo en la CPU donde ya corrió (datos en cache). **Planificación de 2 niveles:** hilo asignado a una CPU al crearse; **cola por-CPU**; si una CPU queda ociosa se reparten. Minimiza contención (ya no hay cola única).

### Hilos que trabajan en conjunto
- Se planifican juntos en varias CPU. Si se multiprograman independientemente, no corren sincrónicos (ej: A0/A1 tardan 200 ms en vez de 100).
- **Gang scheduling (pandillas):** hilos relacionados = pandilla; corren **simultáneamente** en distintas CPU; inician/terminan el intervalo juntos → mensajes más rápidos.

---

## Multicomputadoras (clusters) y memoria distribuida

- CPU fuertemente acopladas, **sin memoria compartida**. PCs con interfaz de red de alto rendimiento.
- Red: **Ethernet** (10–400 Gbps), **Infiniband** (120 Gbps). **HBA** para storage (FibreChannel).
- Topologías: estrella, anillo, malla/mesh, hipercubo, **Full Mesh**.
- **Conmutación:** *store-and-forward* (buffer hasta armar paquete, latencia) vs *circuitos* (ruta fija, más rápida, sin control de flujo).
- **Problema: copiado excesivo de paquetes** RAM↔placa. Soluciones: interfaz en **espacio de usuario** (sin kernel) o **canales DMA / procesadores de red** (lo actual).
- **Comunicación:** `send`/`receive` (con bloqueo, sin bloqueo+copia, sin bloqueo+interrupción) o **RPC** (invoca procedimiento remoto, transparente).
- **Balanceo de carga:** cada nodo tiene sus procesos; enfoque por **grafo** (minimizar aristas/tráfico entre subgrafos) o **distribuido** (reubica si está sobrecargado).

---

## Sistemas distribuidos

- "Conjunto de computadoras independientes que el usuario ve como un único sistema coherente" (Tanenbaum).
- Como multicomputadora pero **menor acoplamiento**: nodos por todo el mundo, PCs completas, distinto SO/HW/FS.
- **Middleware:** capa **por encima del SO** que aporta uniformidad, resuelve heterogeneidad y da interfaz/servicios comunes.

---

## ⚠️ Conceptos clave / posibles preguntas

- **Definir UMA vs NUMA** (acceso uniforme vs dependiente de local/remoto) y **NC-NUMA vs CC-NUMA**.
- **Memoria COMPARTIDA vs DISTRIBUIDA**: comunicación (memoria vs mensajes), acoplamiento, retardos (nseg vs μseg/mseg).
- **SMP**: definición, ventaja (sin cuello de botella) vs maestro-esclavo, y solución lock global vs lock por estructura.
- **Coherencia de cache**: por qué surge y cómo se resuelve (RO/RW, copias limpias/sucias, directorios en CC-NUMA).
- **TSL/spinlock**: por qué deshabilitar interrupciones no alcanza en multiprocesador; bloqueo del bus.
- **Afinidad de CPU**, cola global vs **cola por-CPU**, **gang scheduling**.
- **Por qué se pasó a más cores** (límite de calor/clock, velocidad de la luz).
- **Middleware** en sistemas distribuidos.
