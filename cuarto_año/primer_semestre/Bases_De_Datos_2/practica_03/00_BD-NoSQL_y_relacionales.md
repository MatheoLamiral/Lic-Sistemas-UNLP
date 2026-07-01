# Bases de datos NoSQL y relacionales

### Ejercicio 1: ¿Cuales de los siguientes conceptos de RDBMS existen en MongoDB? En caso de no existir, ¿hay alguna alternativa? ¿Cual es? Base de Datos, Tabla / Relacion, Fila / Tupla, Columna

**Base de Datos**: existe en MongoDB con la misma idea conceptual que en un RDBMS, es un contenedor lógico que agrupa colecciones relacionadas y aísla los datos de otras bases. Se selecciona o crea con `use <nombre>` y administra usuarios y permisos por separado.

**Tabla / Relación**: **no existe como tal**. Su equivalente es la **colección (collection)**, un conjunto de documentos que comparten un propósito. 

>[!NOTE]
> La diferencia clave es que una colección **no exige un esquema fijo**, distintos documentos pueden tener campos diferentes, mientras que una tabla obliga a todas las filas a respetar las mismas columnas. Esto se conoce como **schemaless** (aunque puede aplicarse validación de esquema opcional).

**Fila / Tupla**: **no existe como tal**. Su equivalente es el **documento (document)**, almacenado en formato **BSON** (Binary JSON). Cada documento es una estructura jerárquica de pares clave-valor que puede contener arrays, subdocumentos anidados y tipos heterogéneos. A diferencia de una fila, **no tiene una forma predefinida** ni necesita coincidir con la de los demás documentos de la colección.

**Columna**: **no existe como tal**. Su equivalente es el **campo (field)** dentro de un documento. Mientras una columna se define a nivel de tabla y aplica a todas sus filas, un campo se define **por documento**, puede aparecer en unos y no en otros, contener tipos distintos en distintos documentos y anidar arrays u objetos arbitrarios.

**Correspondencia conceptual:**

| RDBMS              | MongoDB        |
| ------------------ | -------------- |
| Base de Datos      | Base de Datos  |
| Tabla / Relación   | Colección      |
| Fila / Tupla       | Documento      |
| Columna            | Campo          |

>[!NOTE]
> La diferencia de fondo es que en un RDBMS la **estructura** está definida a nivel de tabla y se respeta uniformemente, mientras que en MongoDB la estructura vive **dentro de cada documento** y puede variar entre uno y otro de la misma colección.

### Ejercicio 2: ¿Existen claves foraneas en MongoDB? ¿Que diferencias existen con las bases de datos de tipo relacional?

**No existen claves foráneas en MongoDB.** Lo más cercano es guardar dentro de un documento el `_id` de otro documento (eventualmente envuelto en un `DBRef`), pero MongoDB **no valida ni mantiene** automáticamente esa relación.

**Diferencias con un RDBMS:**

- **Integridad referencial**: en un RDBMS, una `FOREIGN KEY` es una **restricción a nivel del motor**. En MongoDB, **el motor no chequea nada**, se puede guardar un `route_id` que no exista, y borrar ese `route` no afecta a los documentos que lo referenciaban. Toda la integridad queda en manos de la aplicación.

- **Esquemas de datos**: los RDBMS poseen un **esquema fijo y rígido**, mientras que mongo es **sin esquema** (schemaless). Los documentos dentro de una misma colección pueden tener estructuras diferentes y se pueden agregar nuevos campos sobre la marcha sin afectar a los registros existentes  

- **Forma de modelar la relación**: en un RDBMS la única forma de relacionar dos entidades es por FK. En MongoDB hay **dos enfoques**, decididos por el diseñador:
  - **Documentos embebidos**: la entidad relacionada se guarda anidada dentro del documento padre. No hay FK porque no hay entidad separada.
  - **Referencias**: se guarda el `_id` del documento relacionado en otra colección. Es lo más parecido a una FK pero sin validación automática.

- **Joins y navegación**: un RDBMS resuelve la relación con `JOIN` en una sola consulta SQL. En MongoDB, para resolver una referencia hay que usar el operador **`$lookup`** del Aggregation Framework, o hacer dos consultas separadas desde la aplicación. Esto suele ser más costoso, por eso embeber es preferible cuando los datos relacionados se consultan siempre juntos.

- **Filosofía del modelo**: el RDBMS asume **normalización**, separar entidades y vincularlas por FK. MongoDB favorece la **desnormalización**, agrupar la información que se consulta junta en un mismo documento, evitando relaciones cuando es posible.

### Ejercicio 3: Para acelerar las consultas, MongoDB tiene soporte para indices. ¿Que tipos de indices soporta?

Un **índice** en MongoDB es una estructura auxiliar que **mantiene los valores de uno o más campos ordenados para evitar escanear toda la colección al ejecutar una consulta**. Por defecto, toda colección tiene un índice único sobre `_id`. Los principales tipos de índices que MongoDB soporta son:

- **Single Field**: el más simple, indexa **un único campo** de la colección. Se crea con `db.coleccion.createIndex({ campo: 1 })` (`1` ascendente, `-1` descendente). Sirve para acelerar búsquedas por igualdad o rango sobre ese campo.

- **Compound Index**: indexa **múltiples campos** en un solo índice. Es útil para consultas que filtran por varios criterios a la vez, por ejemplo `{ nombre: 1, precio: -1 }`.

- **Geospatial Index**: optimiza consultas sobre **datos geográficos** (coordenadas). Hay dos variantes, **2dsphere** (geometrías sobre una esfera, útil para coordenadas terrestres) y **2d** (geometrías sobre un plano). Soportan operadores como `$near`, `$geoWithin` y `$geoIntersects`.

- **Multikey Index**: se aplica cuando el **campo indexado es un array**. MongoDB crea automáticamente una entrada de índice por cada elemento del array, lo que permite buscar eficientemente elementos dentro de él (por ejemplo, `db.recorridos.find({ stops: "San Telmo" })`).

- **Text Index**: permite búsquedas de **texto completo** sobre campos de tipo string. Soporta tokenización, stemming y stop words por idioma. Se usa con el operador `$text`.

- **Hashed Index**: indexa el **hash** del valor del campo en lugar del valor mismo. Sirve para distribuir documentos de forma uniforme entre shards (sharding por hash), pero no soporta consultas por rango.

- **Wildcard Index**: indexa **todos los campos** (o un subconjunto dinámico) de un documento, útil cuando el esquema es muy variable y no se sabe de antemano por qué campos se va a consultar.

**Propiedades adicionales** que se pueden combinar con cualquiera de los tipos anteriores:

- **Unique**: garantiza que no haya valores duplicados en el campo indexado (equivalente a un `UNIQUE` de SQL).
- **Sparse**: solo indexa los documentos que **tienen el campo definido**, ignorando los que no lo poseen.
- **Partial**: solo indexa los documentos que cumplen una condición específica (`partialFilterExpression`).
- **TTL (Time To Live)**: elimina automáticamente los documentos después de cierto tiempo, útil para sesiones, logs o caché.

>[!NOTE]
> Un índice acelera lecturas pero **encarece las escrituras** (cada `insert`/`update` debe mantenerlo) y ocupa espacio adicional. Por eso conviene crear índices solo sobre los campos que efectivamente se usan en filtros, ordenamientos o joins.

### Ejercicio 4:​ En MongoDB existen dos tipos de vistas. Explicar brevemente cuales son y que diferencias existen entre ellas. Ademas, mencionar algunos casos donde podria utilizarlas.

**1. Vistas estándar (dinámicas).**

Son **vistas virtuales**, no almacenan datos físicamente. Cada vez que se consulta la vista, MongoDB ejecuta el **pipeline de aggregation en tiempo real sobre la colección fuente y devuelve el resultado**. Se crean con:

```javascript
db.createView("rutas_caras", "recorridos", [
    { $match: { precio: { $gt: 50000 } } },
    { $project: { nombre: 1, precio: 1 } }
])
```

Son **siempre consistentes** con los datos actuales (no quedan desactualizadas), pero **cada consulta paga el costo de ejecutar el pipeline** completo.

**2. Vistas materializadas on-demand.**

Son **vistas físicas**, los resultados del pipeline se **guardan como una colección real** en disco usando los operadores `$merge` o `$out` al final del pipeline:

```javascript
db.recorridos.aggregate([
    { $match: { precio: { $gt: 50000 } } },
    { $project: { nombre: 1, precio: 1 } },
    { $merge: { into: "rutas_caras_materializada" } }
])
```

Las consultas posteriores se hacen directamente contra la colección resultante (rápidas, indexables), pero los datos **no se actualizan automáticamente**, hay que re-ejecutar el pipeline (manualmente o con un job programado) cada vez que se quiera refrescar la vista.

**Principales diferencias:**

| Aspecto              | Vista estándar                      | Vista materializada                          |
| -------------------- | ----------------------------------- | -------------------------------------------- |
| Almacenamiento       | No persistente, se computa al vuelo | Persistente, se guarda como colección        |
| Consistencia         | Siempre actualizada                 | Hay que refrescar manualmente                |
| Performance lectura  | Más lenta (recalcula cada vez)      | Más rápida (lee de la colección ya calculada) |
| Soporta índices propios | No                               | Sí, se le pueden crear índices               |
| Costo de escritura   | Cero                                | Costo del pipeline al refrescar              |

**Casos típicos de uso:**

- **Vista estándar**: 
  - Se requiere **encapsulamiento**: ocultar al cliente si los datos son base o derivados sin preocuparse por la frescura.
  - Los **datos base cambian con mucha frecuencia** y las **lecturas no son masivas**.
- **Vista materializada**:
  - **Análisis y estadística**: para calcular promedios, sumas o conteos complejos mediante procesos de **map-reduce**. 
  - **Alto volumen de lectura**: cuando la aplicación necesita consultar datos derivados constantemente y no puede permitirse el costo de calcularlos cada vez.
  - **Reorganización de datos**: cuando se necesita ver la información organizada de una forma totalmente distinta a como se guardó originalment en los agregadoss 

>[!NOTE]
> La elección suele resumirse en un trade-off entre **frescura de los datos** y **performance de lectura**. La materializada acepta perder consistencia para ganar velocidad, yla estándar acepta perder velocidad para ganar consistencia.


### Ejercicio 5:​ Los documentos de una coleccion pueden diferir en la cantidad y tipos de campos. ¿Existen algunas formas de validar los elementos a insertar en una coleccion para evitar esta disparidad?

Aunque **MongoDB es schemaless por defecto**, ofrece un mecanismo de **validación de esquema** (Schema Validation) que permite **imponer reglas sobre la estructura, los tipos y los valores de los documentos al insertarlos o actualizarlos**. Esto se configura **a nivel de colección** mediante el atributo `validator`.

**Cómo se aplica:**

Al crear la colección (`db.createCollection(...)`) o modificarla (`db.runCommand({ collMod: ... })`) se le pasa un **objeto `validator` que define las reglas**. Hay dos formas principales de expresarlo:


**1. Usando `$jsonSchema` (recomendado).**

Es la **forma estándar y más expresiva**. Permite declarar un esquema completo con campos requeridos, tipos, valores permitidos, rangos y patrones, **basado en la especificación JSON Schema**:

```javascript
db.createCollection("recorridos", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["nombre", "precio", "stops"],
         properties: {
            nombre:  { bsonType: "string", description: "obligatorio, string" },
            precio:  { bsonType: "number", minimum: 0, description: "número no negativo" },
            totalKm: { bsonType: "number", minimum: 0 },
            stops:   { bsonType: "array", items: { bsonType: "string" }, minItems: 1 }
         }
      }
   }
})
```

**2. Usando operadores de consulta (`$expr`, `$type`, `$eq`, etc.).**

**Forma más libre**, equivalente a escribir un `find` que el documento debe satisfacer. Útil para reglas dinámicas o que dependen de varios campos:

```javascript
db.createCollection("recorridos", {
   validator: {
      $and: [
         { precio: { $type: "number", $gte: 0 } },
         { stops: { $type: "array" } }
      ]
   }
})
```

**Modos de validación (cómo se aplica la regla):**

- `validationLevel`:
  - `strict` (default): valida **todos** los inserts y updates.
  - `moderate`: valida los inserts y los updates **solo si el documento ya cumplía** las reglas previamente (útil al introducir validación sobre datos legacy).
  - `off`: desactiva la validación.
- `validationAction`:
  - `error` (default): rechaza la operación si no cumple las reglas.
  - `warn`: la operación se ejecuta pero queda registrada en el log.

**Otras formas complementarias de "validar":**

- **Índices `unique`**: garantizan unicidad en uno o varios campos (equivalente a `UNIQUE` de SQL).
- **Validación en la capa de aplicación**: si se usa un ODM como **Mongoose** (Node.js) o **Spring Data MongoDB** (Java), los esquemas/entidades definidos en código actúan como una capa de validación adicional antes de llegar a la base.

>[!NOTE]
> La validación de esquema en MongoDB **no es obligatoria por defecto**, hay que activarla explícitamente. Esto refleja la filosofía del motor, dar la flexibilidad por default y permitir restringirla solo cuando el dominio lo amerita.

### Ejercicio 6:​ MongoDB tiene soporte para transacciones, pero no es igual que el de los RDBMS. ¿Cual es el alcance de una transaccion en MongoDB?

MongoDB **NO soporta transacciones ACID**, lo unico que nos garantiza es que, cualquier operación que modifique **un solo documento** es **atómica por defecto**. Esta es la razón por la que embeber reduce el uso explícito de transacciones, en el caso de transacciones entre diferentes documetnos es distinto, ahi hay que bloquear la colección e iniciar y finalizar la transacción explícitamente. El alcance es a nivel documento o nivel colección.

>[!NOTE]
> En resumen, el "alcance" de una transacción en MongoDB puede ir desde una sola operación sobre un documento (atómica por default) hasta múltiples operaciones sobre múltiples colecciones y bases. La diferencia con un RDBMS es que en MongoDB las **transacciones multi-documento son la excepción**, no la regla, y el motor favorece resolver la atomicidad con un buen diseño de documentos.

### Ejercicio 7:​ Las relaciones entre documentos en MongoDB pueden establecerse mediante documentos embebidos o referencias. Investigar como se implementa cada una y analizar las ventajas y desventajas de cada una, comparandola con la forma estandar de establecer relaciones en una base de datos relacional.

**1. Documentos embebidos (*embedded documents*).**

La entidad relacionada se guarda **anidada dentro del documento padre**, como un subdocumento (o un array de subdocumentos). No existe como entidad independiente en otra colección.

```javascript
{
    nombre: "City Tour",
    precio: 200,
    stops: [
        { nombre: "Diagonal Norte", descripcion: "..." },
        { nombre: "Avenida de Mayo", descripcion: "..." }
    ]
}
```

**Ventajas:**

- **Lectura en una sola consulta**: toda la información viaja junta.
- **Atomicidad implícita**: una actualización al documento padre y a sus embebidos es **atómica** sin transacciones.
- **Localidad de datos**: el motor lee la información de un mismo documento en bloque, lo que aprovecha mejor la caché y el disco.

**Desventajas:**

- **Duplicación**: si la misma entidad se embebe en varios padres y cambia, hay que actualizarla en cada copia.
- **Tamaño limitado**: un documento en MongoDB tiene un **máximo de 16 MB**. Si la cantidad de embebidos crece sin tope, el documento puede chocar contra ese límite.
- **Imposibilidad de consultar el embebido como entidad independiente**: por ejemplo, "todos los `stops` ordenados por nombre" requiere un pipeline con `$unwind`, mientras que en una entidad separada sería un `find` directo.

**2. Referencias (*manual references* o *DBRefs*).**

El documento guarda solo el `_id` (o un identificador equivalente) de otro documento que vive en otra colección. La aplicación o un `$lookup` resuelve la relación cuando hace falta.

```javascript
// Colección "stops"
{ _id: 1, nombre: "Diagonal Norte", descripcion: "..." }

// Colección "recorridos"
{
    nombre: "City Tour",
    precio: 200,
    stops: [1, 2, 3]      // ids referenciados
}
```

**Ventajas:**

- **Normalización**: cada entidad existe una sola vez, los cambios en un `Stop` se reflejan automáticamente en todas las rutas que lo referencian.
- **Sin límite de tamaño**: el documento padre se mantiene pequeño aunque tenga miles de referencias.
- **Acceso independiente**: la entidad relacionada puede consultarse, indexarse y actualizarse por sí misma.

**Desventajas:**

- **Lecturas más caras**: para recomponer el grafo hay que usar `$lookup` (similar a un `JOIN`) o varias consultas, lo que tiene overhead.
- **Sin integridad referencial automática**: a diferencia de un FK, MongoDB no impide que la referencia apunte a un `_id` inexistente (ver ejercicio 2).
- **Atomicidad cruzada cuesta más**: actualizar el padre y la entidad referenciada en una sola operación atómica requiere una **transacción multi-documento explícita**.

**Comparación con un RDBMS:**

| Aspecto              | RDBMS (FK)                  | Embebidos                       | Referencias en Mongo                 |
| -------------------- | --------------------------- | ------------------------------- | ------------------------------------ |
| Forma de modelar     | Tabla separada + FK         | Anidado en el documento padre   | `_id` del relacionado en el padre    |
| Integridad           | Garantizada por el motor    | N/A (no hay entidad separada)   | Manual, a cargo de la aplicación     |
| Lectura conjunta     | `JOIN`                      | Inmediata, ya viene todo        | `$lookup` o consultas separadas      |
| Duplicación          | No (normalizado)            | Sí                              | No                                   |
| Modelo dominante     | **Normalización** (3FN)     | **Desnormalización**            | Normalización moderada               |


>[!IMPORTANT]
> Regla práctica:**
> - **Embeber** cuando la entidad relacionada **no se accede por sí sola**, se actualiza junto con el padre y tiene tamaño acotado (relaciones 1-a-1 o 1-a-pocos).
> - **Referenciar** cuando la entidad **vive con identidad propia** (se busca, se actualiza, se comparte entre muchos padres), o cuando la relación crece sin tope (1-a-muchos / muchos-a-muchos).

>[!NOTE]
> En un RDBMS la decisión de cómo modelar está prácticamente cerrada por la normalización, en MongoDB es una **decisión de diseño explícita** que define el rendimiento y la facilidad de uso del modelo.

### Ejercicio 8:​ Tomando como referencia el modelo de los trabajos practicos anteriores y suponiendo que este podria mapearse a una base de datos en MongoDB, proponer algunos casos donde la relacion seria conveniente mapearla como referencia y otros como documentos embebidos. Justificar la eleccion. 

**Relaciones que conviene mapear por referencia**


- **`Route` ↔ `DriverUser` y `Route` ↔ `TourGuideUser`**: los choferes y guías son entidades con **identidad propia**, pueden participar en varias rutas distintas y se consultan por sí mismos. Embeberlos en cada `Route` los duplicaría y rncarece demasiado cualquier actualización sobre un conductor o guía.

- **`Route` ↔ `Stop`**: un `Stop` aparece en muchas rutas distintas. Si se embebiera, cualquier cambio en su descripción habría que propagarlo a todas las rutas. Como referencia se mantiene una sola "versión" de cada stop y se consulta con `$lookup`.

- **`User` ↔ `Purchase`**: un usuario puede tener cientos o miles de compras a lo largo del tiempo. Además, las compras suelen consultarse de forma independiente, conviene tenerlas como colección separada referenciando al `User` por `_id`.

- **`ItemService` → `Service`**: cada ítem referencia el servicio que se compró. El `Service` tiene vida propia (puede ser comprado en muchas compras distintas) y sus datos no deberían duplicarse.

- **`Supplier` ↔ `Service`** : cada `Service` es una entidad independiente y compartida. Embeberla duplicaría los datos y, además, ya se la referencia desde otros lados.

**Relaciones que conviene mapear como documentos embebidos**

- **`Purchase` ↔ `Review`**: cada `Review` está directamente asociada a una única `Purchase` y no tiene sentido que exista de forma independiente. Como además es opcional y única por compra, el tamaño no crece descontroladamente. Embeber permite leer la compra y su reseña en una sola operación.

- **`Purchase` ↔ `ItemService`**: los ítems de servicio de una compra viven y mueren con la compra, su cantidad típica es chica (no se compran cientos de servicios por viaje) y siempre se consultan junto con la compra. Embeberlos elimina un `$lookup` y mantiene la atomicidad al crear/actualizar la compra.


>[!NOTE]
> Una **regla práctica** para decidir, ante una relación, qué enfoque conviene en MongoDB:
> - Si la entidad "hija" **vive con identidad propia**, se consulta sola, es compartida por muchos padres, o crece sin tope → **referencia**.
> - Si la entidad "hija" **no tiene sentido fuera del padre**, se consulta siempre junto a él, y su tamaño está acotado → **embeber**.


