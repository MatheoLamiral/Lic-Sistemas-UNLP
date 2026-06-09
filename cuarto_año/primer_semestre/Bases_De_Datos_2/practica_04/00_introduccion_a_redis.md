# Introducción a Redis

### Ejercicio 1:​ ¿Qué tipo de base de datos es Redis? ¿En qué se diferencia de una base de datos relacional y de otras bases de datos NoSQL como MongoDB?

**Redis (REmote DIctionary Server)** es una base de datos **NoSQL** del tipo **clave-valor (key-value store)**, que funciona **en memoria (in-memory)**. Es decir, guarda los datos como un gran diccionario donde a cada **clave** (un string único) le corresponde un **valor**, y mantiene ese conjunto principalmente en la **RAM** en lugar de en disco.

Su rasgo distintivo frente a otros key-value es que los valores no son solo strings: Redis soporta **estructuras de datos** (listas, sets, hashes, sorted sets, etc.), por lo que suele describirse como un **"data structure server"** (servidor de estructuras de datos).

**Diferencias con una base de datos relacional (RDBMS):**

| Aspecto | Redis | Relacional (SQL) |
|---|---|---|
| Modelo de datos | Clave-valor, sin esquema fijo | Tablas con filas y columnas, esquema rígido |
| Almacenamiento | Principalmente en **memoria RAM** | Principalmente en **disco** |
| Consultas | Acceso directo por clave; sin `JOIN` ni SQL | Lenguaje SQL con `JOIN`, agregaciones, etc. |
| Relaciones | No hay relaciones ni integridad referencial | Claves foráneas, integridad referencial |
| Transacciones | Soporte limitado (sin rollback real) | Transacciones **ACID** completas |
| Velocidad | Muy alta (lecturas/escrituras en microsegundos) | Más lenta por el acceso a disco |

En resumen, una relacional prioriza **consistencia, relaciones y consultas complejas**; Redis prioriza **velocidad y simplicidad de acceso**.

**Diferencias con otras NoSQL como MongoDB:**

Tanto Redis como MongoDB son NoSQL, pero pertenecen a **familias distintas**:

| Aspecto | Redis | MongoDB |
|---|---|---|
| Tipo de NoSQL | **Clave-valor** (in-memory) | **Orientada a documentos** (BSON/JSON) |
| Dónde viven los datos | En **memoria** (con persistencia opcional) | En **disco** (con caché en memoria) |
| Unidad de dato | Valor asociado a una clave | Documento (objeto tipo JSON con campos) |
| Consultas | Por clave; no consulta "por contenido" del valor | Ricas: filtros por campos, índices, aggregation framework |
| Caso típico | Caché, sesiones, colas, rankings en tiempo real | Almacenar y consultar datos semiestructurados persistentes |

La diferencia de fondo: **MongoDB es una base de datos de propósito general** pensada para **persistir y consultar** grandes volúmenes de documentos por su contenido. **Redis es una base de datos en memoria** pensada para **acceso ultrarrápido por clave**, ideal como caché o para datos volátiles/efímeros, no para consultas complejas sobre el contenido de los valores.

> [!NOTE]
> En la práctica, Redis y MongoDB suelen **complementarse**, no competir: MongoDB (u otra base) actúa como almacenamiento principal persistente, y Redis se pone delante como **capa de caché** para acelerar los accesos más frecuentes.

### Ejercicio 2:​ ¿Dónde almacena los datos Redis? ¿Qué implicancias tiene esto en términos de velocidad y de persistencia?

Redis almacena los datos **en la memoria principal (RAM)**, no en disco. El disco lo usa solo de forma **secundaria**, para guardar copias que permitan recuperar el estado tras un reinicio (persistencia opcional).

**Implicancias en velocidad:**

- Acceder a RAM es **órdenes de magnitud más rápido** que acceder a disco. Por eso Redis logra latencias de **microsegundos** y altísimo throughput.
- Es lo que lo hace ideal para **caché, sesiones y datos en tiempo real**.

**Implicancias en persistencia:**

- La RAM es **volátil**: si el proceso se cae o se reinicia sin haber respaldado, los datos **se pierden**.
  - Para mitigarlo, Redis ofrece persistencia **opcional** a disco mediante dos mecanismos:
    - **RDB:** snapshots periódicos del dataset completo.
    - **AOF:** registro (log) de cada operación de escritura.
- El dataset **debe entrar en la RAM disponible**: esto que acota el tamaño máximo y encarece el escalado.

> [!NOTE]
> El trade-off central de Redis: gana **velocidad** por estar en memoria, pero a costa de **durabilidad** (riesgo de pérdida ante fallos) y de un **límite de capacidad** dado por la RAM. La persistencia a disco reduce el riesgo, pero no iguala las garantías de una base orientada a disco.

### Ejercicio 3:​ ¿Qué tipos de datos soporta Redis? Listar y describir brevemente cada uno.

En Redis la **clave** siempre es un string, pero el **valor** puede tener distintos tipos de estructura:

**Tipos fundamentales:**

- **String:** el tipo más simple. Texto, números o datos binarios (hasta 512 MB). Sirve para contadores, caché de valores simples, flags.
- **List:** lista ordenada de strings, indexada por posición. Permite insertar/quitar en ambos extremos (push/pop). Útil para **colas (FIFO)** y **pilas (LIFO)**.
- **Set:** colección **no ordenada** de strings **únicos** (sin duplicados). Soporta operaciones de conjunto (unión, intersección, diferencia). Útil para etiquetas, relaciones, "elementos únicos".
- **Hash:** mapa de **campo → valor** dentro de una sola clave (como un diccionario anidado). Ideal para representar **objetos** (ej. un usuario con sus atributos).
- **Sorted Set (ZSet):** como un Set, pero cada elemento tiene un **score** numérico que lo mantiene **ordenado**. Útil para **rankings, leaderboards y colas de prioridad**.

**Tipos especializados (avanzados):**

- **Bitmap:** opera sobre los bits de un string; eficiente para flags masivos (ej. usuarios activos por día).
- **HyperLogLog:** estima la **cardinalidad** (cantidad de elementos únicos) de un set enorme usando muy poca memoria, de forma aproximada.
- **Stream:** estructura tipo log de eventos (append-only), pensada para **mensajería** y procesamiento de eventos en orden temporal.
- **Geospatial:** almacena coordenadas y permite consultas por **distancia/proximidad** geográfica.

> [!NOTE]
> Los **cinco primeros** (String, List, Set, Hash, Sorted Set) son los tipos clásicos y los más usados; el resto son estructuras especializadas para casos puntuales.

### Ejercicio 4: ​ Enunciar las características principales de Redis.

- **En memoria (in-memory):** mantiene los datos en RAM → latencias de microsegundos y altísimo rendimiento.
- **Clave-valor con estructuras de datos:** no solo strings, sino listas, sets, hashes, sorted sets, etc. ("data structure server").
- **Persistencia opcional:** puede respaldar a disco con RDB (snapshots) y/o AOF (log de escrituras), sin perder su naturaleza in-memory.
- **Single-threaded para comandos:** procesa las operaciones de forma **secuencial en un solo hilo**, lo que las hace **atómicas** por construcción y evita condiciones de carrera.
- **TTL / expiración:** se puede asignar tiempo de vida a las claves para que **se borren solas** (clave para caché y sesiones).
- **Alta velocidad y throughput:** maneja decenas/cientos de miles de operaciones por segundo.
- **Replicación y alta disponibilidad:** soporta réplicas (master-replica), **Redis Sentinel** (failover automático) y **Redis Cluster** (sharding / escalado horizontal).
- **Transacciones básicas:** mediante `MULTI`/`EXEC` (ver ejercicio 6), con atomicidad pero sin rollback.
- **Pub/Sub:** sistema de mensajería de publicación/suscripción integrado.
- **Scripting:** ejecución de scripts **Lua** del lado del servidor de forma atómica.
- **Simple y multiplataforma:** protocolo sencillo, clientes para casi todos los lenguajes, open source.

### Ejercicio 5:​ Comparar Redis con los RDBMS: ¿en qué casos conviene usar Redis en lugar de una base de datos relacional y en cuáles no?

La elección depende del tipo de acceso y de las garantías que se necesiten: Redis prioriza **velocidad y acceso por clave**; los RDBMS, **consistencia, relaciones y consultas complejas**.

**Conviene usar Redis cuando:**

- Se necesita **latencia muy baja / alta velocidad** de lectura-escritura (tiempo real).
- El acceso es **por clave conocida**, sin consultas complejas sobre el contenido.
- Los datos son **volátiles o temporales** y/o admiten expiración (caché, sesiones, tokens).
- Casos típicos: **caché**, sesiones de usuario, **rankings/leaderboards**, colas de tareas, contadores, rate limiting, Pub/Sub.

**NO conviene usar Redis (mejor un RDBMS) cuando:**

- Se requieren **transacciones ACID** completas e integridad referencial (ej. sistemas bancarios, facturación).
- Hay **relaciones complejas** entre entidades y se necesitan `JOIN` o consultas con múltiples condiciones.
- El **volumen de datos supera la RAM** disponible (Redis exige que el dataset entre en memoria).
- La **durabilidad** es crítica y no se tolera ninguna pérdida de datos.
- Se necesitan **consultas variadas e imprevistas sobre el contenido** de los datos, reportes o agregaciones complejas.

> [!NOTE]
> No es "Redis vs RDBMS" de forma excluyente: lo habitual es **combinarlos**: el RDBMS como almacén principal (persistente, consistente) y Redis por delante como **capa de caché** para acelerar los accesos más frecuentes.

### Ejercicio 6:​ ¿Redis tiene soporte para transacciones? ¿Cómo funcionan? ¿Qué garantías ofrecen y qué limitaciones tienen respecto de las transacciones ACID?

Sí, Redis tiene **soporte básico de transacciones**, aunque más limitado que el de un RDBMS.

**Cómo funcionan:**

Se basan en cuatro comandos:

- **`MULTI`:** inicia la transacción. Los comandos que siguen **no se ejecutan**, se **encolan**.
- **`EXEC`:** ejecuta **todos** los comandos encolados, de forma **secuencial y atómica** (sin que se intercale ningún otro comando de otro cliente).
- **`DISCARD`:** cancela la transacción y descarta la cola.
- **`WATCH`:** vigila una o más claves; si alguna **cambia** antes del `EXEC`, la transacción se **aborta** (mecanismo de **bloqueo optimista**).

```redis
WATCH saldo
MULTI
DECRBY saldo 100
INCRBY ahorro 100
EXEC          # si "saldo" cambió desde el WATCH, no se ejecuta nada
```

**Garantías que ofrecen:**

- **Atomicidad parcial:** todos los comandos encolados se ejecutan juntos, sin intercalarse con otros clientes (gracias al modelo single-threaded).
- **Aislamiento:** ningún otro cliente ve un estado intermedio durante el `EXEC`.

**Limitaciones respecto de ACID:**

- **No hay rollback.** Si un comando falla en tiempo de ejecución (ej. operar un tipo de dato incorrecto), **el resto igual se ejecuta**: no se deshacen los cambios ya aplicados. Solo se detecta antes de `EXEC` un error de **sintaxis**.
- **Atomicidad incompleta:** se ejecutan todos los comandos, pero no se garantiza el "todo o nada" ante errores lógicos en runtime.
- **Consistencia limitada:** no hay constraints, claves foráneas ni validaciones de integridad como en un RDBMS.
- **Durabilidad condicionada:** depende de la configuración de persistencia (RDB/AOF); por defecto, un fallo puede perder operaciones recientes.

> [!NOTE]
> Diferencia clave con ACID: en un RDBMS, si algo falla a mitad de la transacción, **se revierte todo** (rollback). En Redis **no existe el rollback**: garantiza que los comandos se ejecuten juntos y aislados, pero no que se deshagan si uno falla.

### Ejercicio 7:​ ¿Redis tiene persistencia? Describir los mecanismos disponibles (RDB y AOF) e indicar las diferencias entre ellos.

Sí. Aunque Redis trabaja en memoria, ofrece **persistencia opcional a disco** para no perder los datos ante un reinicio o caída. Dispone de dos mecanismos, que pueden usarse por separado o **combinados**.

**RDB (Redis Database / snapshots):**

Toma **"fotos" (snapshots) del dataset completo** cada cierto tiempo o según una cantidad de cambios, y las guarda en un archivo binario (`dump.rdb`).

- Archivo compacto, ideal para **backups** y restauración rápida.
- Menor impacto en el rendimiento (no escribe en cada operación).
- Riesgo de **perder los datos** generados **entre snapshot y snapshot** (si se cae justo antes de la próxima foto).

**AOF (Append Only File):**

Lleva un **registro (log) de cada operación de escritura** que modifica los datos; al reiniciar, Redis **reejecuta** ese log para reconstruir el estado.

- Mucha **mayor durabilidad** (puede configurarse para escribir casi en cada operación).
- Menor ventana de pérdida de datos.
- Archivo **más grande** y, según la configuración, **algo más lento** que RDB.

**Diferencias principales:**

| Aspecto | RDB | AOF |
|---|---|---|
| Qué guarda | Snapshot del dataset completo | Log de cada escritura |
| Durabilidad | Menor (se pierde lo posterior al último snapshot) | Mayor (ventana de pérdida mínima) |
| Tamaño del archivo | Compacto | Más grande |
| Rendimiento | Mejor (escribe esporádicamente) | Algo peor (escribe seguido) |
| Recuperación | Rápida | Más lenta (reejecuta el log) |
| Uso típico | Backups, restauración rápida | Cuando importa minimizar pérdida de datos |

> [!NOTE]
> No son excluyentes: la práctica recomendada para producción suele ser **usar ambos** — RDB para backups eficientes y AOF para minimizar la pérdida de datos ante fallos.

### Ejercicio 8:​ ¿Cuáles son los principales casos de uso de Redis en aplicaciones reales?

- **Caché:** acelerar el acceso a datos frecuentes guardándolos en memoria, descargando a la base principal. Es su uso más extendido.
- **Sesiones de usuario:** almacenar sesiones de aplicaciones web (con expiración automática vía TTL).
- **Rankings / leaderboards:** usando Sorted Sets, mantener tablas de posiciones ordenadas por puntaje en tiempo real (juegos, etc.).
- **Colas de tareas / mensajería:** usando Lists o Streams para procesar trabajos en segundo plano (productor-consumidor).
- **Pub/Sub:** comunicación en tiempo real entre componentes (chats, notificaciones, eventos).
- **Contadores en tiempo real:** likes, vistas, métricas, gracias a operaciones atómicas como `INCR`.
- **Rate limiting:** limitar la cantidad de peticiones por usuario/tiempo (control de abuso de APIs).
- **Tokens y datos temporales:** códigos de verificación, tokens de autenticación, carritos de compra, aprovechando la expiración automática.
- **Datos geoespaciales:** búsquedas por proximidad (ej. "locales cercanos") con el tipo Geospatial.