# Operaciones CRUD básicas

## Configuración inicial e incerciones 

### Ejercicio 9: Crear una nueva base de datos llamada "tours" y una coleccion llamada "recorridos".

1. Levantamos el entorno con `docker compose up -d`
2. Abrimos la shell de MongoDB con `docker compose exec mongo mongosh`
3. Creamos la base de datos con `use tours`
   - Esto selecciona la base `tours`. Si no existe, MongoDB la crea automáticamente al insertar el primer documento.
4. Creamos la colección `recorridos` con `db.createCollection("recorridos")`
5. Verificamos que la base y la colección se hayan creado correctamente con `show dbs` y `show collections`

> [!NOTE]
> Si solo se haace use tours y nada más, la base no aparece en `show dbs` hasta que tenga al menos una colección con datos.

### Ejercicio 10: En la nueva coleccion, utilizando el comando correspondiente, insertar el siguiente documento: `{ "nombre": "City Tour", "precio": 200, "stops": ["Diagonal Norte", "Avenida de Mayo", "Plaza del Congreso"], "totalKm": 5 }`

- Una vez que estamos en la base `tours` ejecutamos:
    ```javascript
        db.recorridos.insertOne({ 
            nombre: "City Tour", 
            precio: 200, 
            stops: ["Diagonal Norte", "Avenida de Mayo", "Plaza del Congreso"],
            totalKm: 5 
        })
    ```
- Deberíamos recibir una respuesta similar a:
    ```json
    {
      "acknowledged": true,
      "insertedId": ObjectId("...") // ID generado automáticamente
    }
    ```

### Ejercicio 11: Recuperar la informacion insertada usando db.recorridos.find() (puede agregarse .pretty() al final para ver los datos indentados). ¿Que diferencia se observa entre el documento insertado y el documento recuperado?

La diferencia es que el documento recuperado contiene un campo adicional `_id` de tipo `ObjectId` que no estaba en el documento insertado. MongoDB **agrega ese campo automáticamente a cualquier documento que se inserte sin un `_id` explícito**, ya que cumple el rol de **clave primaria** de la colección, garantizando que cada documento pueda identificarse de forma única.

### Ejercicio 12: Agregar a la coleccion, utilizando un solo comando, los documentos especificados en el archivo "material_adicional_1.json" adjunto a esta practica.

- Tenemos dos opciones para realizar esta tarea:
  - `mongoimport` desde el host:
    ```bash
    docker compose exec mongo mongoimport \
        --db tours \
        --collection recorridos \
        --file /material/material_adicional_1.json \
        --jsonArray
    ```
    > [!NOTE]
    > El flag `--jsonArray` es necesario porque el archivo contiene un array de documentos. Sin este flag, `mongoimport` intentaría interpretar el archivo como un documento JSONL.
  - `insertMany` + `cat` desde adentro de `mongosh`:
    ```bash
    docker compose exec mongo mongosh tours
    db.recorridos.insertMany(JSON.parse(cat("/material/material_adicional_1.json")))
    ```
    - `cat("/material/...")` lee el archivo del filesystem y devuelve el string. `cat` es una función de mongosh, no del shell del sistema.
    - `JSON.parse(...)` lo convierte en un array de objetos JavaScript.
    - `db.recorridos.insertMany([...])` los inserta todos en la colección.

## Operaciones de actualizacion y eliminacion

### Ejercicio 13: ​Actualizar el recorrido "Cultural Odyssey" para que su total de kilometros sea 12.

```javascript
    db.recorridos.updateOne(
        { nombre: "Cultural Odyssey" }, // filtro
        { $set: { totalKm: 12 } } // asigna 12 al campo totalKm, independientemente del valor anterior
    )
```

> [!NOTE]
> Se usa `$set` porque la consigna pide **dejar el valor en 12**, no incrementarlo. `$set` asigna un valor absoluto y es robusto frente a cambios en el estado previo del documento (no depende de saber cuál era el `totalKm` original).

### Ejercicio 14: ​Actualizar el listado de stops del recorrido "Delta Tour" para agregar "Tigre".

```javascript
    db.recorridos.updateOne(
        { nombre: "Delta Tour" }, // filtro
        { $push: { stops: "Tigre" } } // agrega "Tigre" al array de stops
    )
```

### Ejercicio 15: ​Aumentar un 10% el precio de todos los recorridos.

```javascript
    db.recorridos.updateMany(
        {}, // filtro vacío para seleccionar todos los documentos
        { $mul: { precio: 1.10 } } // multiplica el campo precio por 1.10 para aumentar un 10%
    )
```

### Ejercicio 16: ​Eliminar el recorrido con nombre "Temporal Route".

```javascript
    db.recorridos.deleteOne({ nombre: "Temporal Route" })
```

### Ejercicio 17: ​Crear el array de etiquetas (tags) para la ruta "Urban Exploration" y agregar el elemento "Gastronomia" a dicho arreglo.

```javascript
    db.recorridos.updateOne(
        { nombre: "Urban Exploration" }, // filtro
        { $push: { tags: "Gastronomia" } } // agrega "Gastronomia" al array tags; si el campo no existe, lo crea como un array con ese único elemento
    )
```

> [!NOTE]
> Se elige `$push` en lugar de `$set` porque expresa la intención correcta (**agregar un elemento a una lista**) y, además, MongoDB crea el campo `tags` automáticamente como un array si no existía previamente. No hace falta inicializarlo a `[]` en un paso anterior.

> [!IMPORTANT]
>  El valor pasado a `$push` es **el elemento a agregar**, no un array contenedor. Si se escribiera `{ $push: { tags: ["Gastronomia"] } }`, el resultado sería `tags: [["Gastronomia"]]` (un array anidado).

## Consultas con `find()`

### Ejercicio 18: Obtener la ruta con nombre "Museum Tour".

```javascript
    db.recorridos.find({ nombre: "Museum Tour" })
```

### Ejercicio 19: ​Las rutas con precio superior a $60.000.

```javascript
    db.recorridos.find({ precio: { $gt: 60000 } })
```

### Ejercicio 20: ​Las rutas con precio superior a $50.000 y con un total de kilometros mayor a 10.

```javascript
    db.recorridos.find({ precio: { $gt: 50000 }, totalKm: { $gt: 10 } })
```
### Ejercicio 21: ​Las rutas que incluyan el stop "San Telmo".

```javascript
    db.recorridos.find({ stops: "San Telmo" })
```

### Ejercicio 22: ​Las rutas que incluyan el stop "Recoleta" y no el stop "Plaza Italia".

```javascript
    db.recorridos.find({
        $and: [
            {stops: "Recoleta" }, 
            {stops: {$ne: "Plaza Italia"}}
        ]
    })
```

O podemos escribirlo sin `$and` ya que el filtro por defecto es una conjunción:

```javascript
    db.recorridos.find({
        stops: {$eq: "Recoleta", $ne: "Plaza Italia"}
    })
```

### Ejercicio 23: ​El nombre y el total de km (si es que posee) de las rutas que incluyan el stop "Delta" y tengan un precio menor a $50.000.

```javascript
    db.recorridos.find({
        $and:[
            {stops: "Delta"},
            {precio: {$lt: 50000}}
        ]
    },
    {nombre: 1, totalKm: 1})
```

O podemos escribirlo sin `$and` ya que el filtro por defecto es una conjunción:

```javascript
    db.recorridos.find(
        {stops: "Delta", precio: {$lt: 50000}},
        {nombre: 1, totalKm: 1, _id: 0}
        )
```

### Ejercicio 24: ​Las rutas que incluyen tanto "San Telmo" como "Recoleta" y "Avenida de Mayo" entre sus stops.

```javascript
    db.recorridos.find({
        stops: {$all: ["San Telmo", "Recoleta", "Avenida de Mayo"]}
    })
```

### Ejercicio 25: ​Solo el nombre de las rutas que dispongan de mas de 5 stops.

```javascript
    db.recorridos.find({
        $expr: {
            $gt: [{ $size: "$stops"}, 5]
        }
    })
```

### Ejercicio 26: ​Las rutas que no tengan definido el total de sus kilometros.

```javascript
    db.recorridos.find({
        totalKm: { $exists: false}
    })
```

### Ejercicio 27: ​Los nombres y el listado de stops de aquellas rutas que incluyen algun museo en sus recorridos.

```javascript
    db.recorridos.find({
        stops: { $regex: /Museo/}
    },{nombre: 1, stops: 1, _id: 0})
```

También podríamos evitar usar `$regex` de la siguiente manera

```javascript
    db.recorridos.find({stops: /Museo/},{nombre: 1, stops: 1, _id: 0})
```

Además si quisieramos hacerlo case-insensitive (mayus. y minus.) usamos el flag `i`

```javascript
    db.recorridos.find({ stops: /museo/i }, { nombre: 1, stops: 1, _id: 0 })
```

### Ejercicio 28: ​La cantidad total de elementos que posee la coleccion.

```javascript
    db.recorridos.countDocuments({})
```