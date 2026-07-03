# Aggregation Framework

## Configuracion

### Ejercicio 29: Crear una nueva base de datos llamada "tours2". Guardar el archivo "generador1.js" adjunto a esta practica y ejecutarlo con: `load(<ruta del archivo 'generador1.js'>)`. Si se utiliza un cliente que lo permita (por ejemplo Robo3T o MongoDB Compass), se puede ejecutar directamente en el espacio de consultas. Examinar las colecciones generadas antes de continuar.

Se crea la base `tours2` y se ejecuta el script `generator1.js`, que genera las colecciones de datos de prueba.

**Cómo se ejecuta el script:**

El script `generator1.js` no fija el nombre de la base internamente: usa `db.stop` y `db.route`, que apuntan a **la base activa en ese momento**. Por eso el orden importa: primero hay que seleccionar `tours2` y recién después cargar el script.

- Desde **mongosh** (la carpeta `material` está montada en el contenedor como `/material`):
    ```javascript
    use tours2
    load("/material/generator1.js")
    ```
- Desde **Studio 3T / Compass:** seleccionar (o crear) la base `tours2`, abrir el IntelliShell sobre ella y ejecutar el `load(...)`, o pegar el contenido del script directamente en la consola.

**Qué genera el script:**

| Colección | Documentos | Estructura |
|---|---|---|
| `stop` | 119 | `{ name, code, desciprion }` |
| `route` | 50.000 | `{ name, price, totalKm, stops: [...] }` |

```javascript
// ejemplo de stop
{ _id: ObjectId("..."), name: "Diagonal Norte", code: 0, desciprion: "Stop number 0" }

// ejemplo de route
{ _id: ObjectId("..."), name: "route1", price: 502, totalKm: 17.92, stops: [45, 85, 79, 53, 105] }
```

>[!NOTE]
> - **La relación `route` ↔ `stop` es por `code`, no por `_id`.** El array `route.stops` contiene **números** (ej. `[45, 85, 79]`) que se corresponden con el campo `code` de `stop` (rango 0–118). Al hacer `$lookup` hay que vincular `route.stops` con `stop.code`, **no** con `stop._id`.
> - **El campo de `stop` está mal escrito: `desciprion`** (no `description`). Hay que proyectarlo con el nombre tal cual.
> - **`route.stops` es un array de entre 2 y 5 índices** (cantidad aleatoria por ruta).

> [!NOTE]
> El script usa `db.route.insert(...)`, una forma **deprecada** (mongosh sugiere `insertOne`/`insertMany`). Funciona igual, solo emite un warning.

## Consultas con Aggregation Framework

### Ejercicio 30: ​Obtener una muestra de 5 rutas aleatorias de la coleccion.

```javascript
    db.route.aggregate([
        {$sample: {size: 5}}
    ])
```

### Ejercicio 31: ​Extender la consulta anterior para incluir en el resultado toda la informacion de cada una de las stops. Tener en cuenta que pueden ligarse por su codigo.

```javascript
    db.route.aggregate([
        {$sample: {size: 5}},
        {$lookup: {
            from: "stop",
            localField: "stops",
            foreignField: "code",
            as: "stopsInfo"
        }}
    ])
```

>[!IMPORTANT]
> **$lookup** es una etapa del pipeline que trae todos los documentos de la colección A y les pega la información coincidente de la colección B.
> - `from`: colección externa de donde queremos sacar los datos
> - `localField`: campo del documento actual que contiene el valor de referencia (puede ser un arreglo, Mongo busca cada valor automáticamente)
> - `foreignField`: campo en la otra colección que debe coincidir con nuestro valor local
> - `as`: define el nombre del nuevo campo que se creará en nuestro documento


### Ejercicio 32: ​Obtener la informacion de las rutas (incluyendo la de sus stops) que tengan un precio mayor o igual a $90.000.

```javascript
    db.route.aggregate([
        {$match: {price: {$gte: 90000}}},
        {$lookup: {
            from: "stop",
            localField: "stops",
            foreignField: "code",
            as: "stopsInfo"
        }}
    ])
```

### Ejercicio 33: ​Obtener la informacion de las rutas que tengan 5 stops o mas.

```javascript
    db.route.aggregate([
        {$match: {$expr: {$gte: [{$size: "$stops"}, 5]}}}
    ])
```

### Ejercicio 34: ​Obtener la informacion de las rutas que tengan incluido en su nombre el string "111".

```javascript
    db.route.aggregate([
        {$match: {name: /111/}}
    ])
```

### Ejercicio 35: ​Obtener solo las stops de la ruta con nombre "Route100".

```javascript
    db.route.aggregate([
        {$match: {name: "route100"}},
        {$lookup: {
            from: "stop",
            localField: "stops",
            foreignField: "code",
            as: "stopsInfo"
        }},
        {$project: {stopsInfo: 1, _id: 0}}
    ])
```
### Ejercicio 36: ​Obtener la informacion del stop que mas apariciones tiene en rutas.

```javascript
    db.route.aggregate([
        {
            $unwind: "$stops"
        },
        {
            $group:{
                _id: "$stops",
                cantidadRutas: {$sum: 1}
            }
        },
        {
            $sort: {
                cantidadRutas: -1
            }
        },
        {
            $limit: 1 
        },
        {
            $lookup:{
                from: "stop",
                localField: "_id",
                foreignField: "code",
                as: "stopsInfo"
            }
        },
        {
            $project: {stopsInfo: 1}
        }
    ])
```

### Ejercicio 37: ​Obtener las rutas con precio inferior a $15.000. Agregar a cada una una nueva propiedad que especifique la cantidad de stops que posee. Crear una nueva coleccion llamada "rutas_economicas" y almacenar estos elementos.

```javascript
    db.route.aggregate([
        {
            $match: {
                price: {
                    $lt: 15000
                }
            }
        },
        {
            $addFields:{
                cantidadStops: {$size: "$stops"}
            }
        },
        {
            $out: "rutas_economicas"
        }
    ])
```

### Ejercicio 38: ​Por cada stop existente en la coleccion, calcular el precio promedio de las rutas que la incluyen.

```javascript
    db.route.aggregate([
        {
            $unwind: "$stops"
        },
        {
            $group:{
                _id: "$stops",
                precioPromedio: {$avg: "$price"}
            }
        }
    ])
```