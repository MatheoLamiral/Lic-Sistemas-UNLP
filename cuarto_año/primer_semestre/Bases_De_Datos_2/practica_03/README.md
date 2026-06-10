# Práctica 3 — Bases de Datos NoSQL con MongoDB

## Estructura

```
practica_03/
├── docker-compose.yml      # define los servicios (mongo + mongo-express)
├── material/               # archivos provistos por la cátedra (JSON y JS)
├── ...
```

## Qué levanta el `docker-compose.yml`

- **`mongo`** — Servidor MongoDB (última versión oficial) escuchando en el puerto `27017` del host. Inicializa con la base `tours` por defecto.
- **`mongo-express`** — Interfaz web liviana para explorar bases/colecciones/documentos sin instalar Compass ni Robo3T. Disponible en [http://localhost:8081](http://localhost:8081).
- **Volumen `mongo-tp3-data`** — Persistencia, los datos sobreviven a reinicios del contenedor.
- **Bind mount `./material:/material:ro`** — Monta la carpeta local `material/` dentro del contenedor en modo solo lectura, para poder usar `mongoimport` y `load(...)` sobre los archivos del TP sin copiarlos manualmente.

## Comandos

Todos los comandos se ejecutan desde esta carpeta (`practica_03/`).

### Ciclo de vida del entorno

```bash
docker compose up -d        # levantar (la primera vez descarga las imágenes)
docker compose ps           # ver estado de los contenedores
docker compose logs -f mongo  # ver logs en vivo
docker compose stop         # parar (conserva datos)
docker compose start        # arrancar de nuevo
docker compose down         # eliminar contenedores (conserva el volumen)
docker compose down -v      # eliminar contenedores Y los datos
```

### Cliente Mongo (`mongosh`)

```bash
docker compose exec mongo mongosh           # abre el prompt
docker compose exec mongo mongosh tours     # entra directamente a la base 'tours'
```

Una vez dentro del prompt:

```javascript
use tours
db.createCollection("recorridos")
db.recorridos.insertOne({ nombre: "City Tour", precio: 200 })
db.recorridos.find().pretty()
```

### Cargar archivos del TP

**Ejercicio 12 — importar `material_adicional_1.json` a la colección `recorridos`:**

```bash
docker compose exec mongo mongoimport \
    --db tours \
    --collection recorridos \
    --file /material/material_adicional_1.json \
    --jsonArray
```

**Ejercicio 29 — ejecutar `generador1.js` sobre la base `tours2`:**

```bash
docker compose exec mongo mongosh tours2 --eval "load('/material/generador1.js')"
```

O abriendo la shell e invocando `load(...)` desde adentro:

```bash
docker compose exec mongo mongosh
> use tours2
> load('/material/generador1.js')
```

### GUI web — Mongo Express

Abrir [http://localhost:8081](http://localhost:8081) en el navegador. Permite ver bases, colecciones, ejecutar consultas y editar documentos visualmente.

> Si no te interesa esta interfaz, podés eliminar el bloque `mongo-express` del `docker-compose.yml` sin afectar al servidor de MongoDB.

## Notas

- El servidor escucha en `mongodb://localhost:27017` desde el host, así que también podés conectarte con **MongoDB Compass**, **Robo3T** u otra herramienta externa.
- El volumen `mongo-tp3-data` es nombrado, lo gestiona Docker. Para inspeccionarlo: `docker volume inspect practica_03_mongo-tp3-data`.
- La carpeta `material/` está montada como **read-only** dentro del contenedor (`:ro`), MongoDB puede leer los archivos pero no escribirlos, así evitamos modificarlos accidentalmente.
