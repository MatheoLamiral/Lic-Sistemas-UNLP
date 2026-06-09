# TP4 - Bases de Datos NoSQL con Redis

## Servicios

El [docker-compose.yml](docker-compose.yml) levanta **Redis Stack**, que incluye:

| Servicio | Puerto | Descripción |
|---|---|---|
| Redis | `6379` | Servidor Redis (acceso por `redis-cli` o clientes) |
| RedisInsight | `8001` | Interfaz web visual ([http://localhost:8001](http://localhost:8001)) |

- **Persistencia:** AOF habilitada + volumen `redis-tp4-data` 

## Comandos de Docker

### Levantar el entorno

```bash
docker compose up -d
```
Descarga la imagen (la primera vez) y arranca Redis en segundo plano (`-d` = detached).

### Apagar el entorno

```bash
docker compose down
```
Detiene y elimina el contenedor. **Los datos se conservan** en el volumen.

```bash
docker compose down -v
```
Igual que el anterior pero **borra también el volumen** (se pierden todos los datos). 

### Ver el estado

```bash
docker compose ps          # contenedores del compose
docker ps                  # todos los contenedores corriendo
```

### Ver logs

```bash
docker compose logs -f redis    # logs en vivo (Ctrl+C para salir)
```

### Reiniciar

```bash
docker compose restart
```

## Cómo ejecutar las consultas

### Opción A — Consola `redis-cli` (recomendada para el TP)

```bash
docker exec -it redis-tp4 redis-cli
```
Abre la consola interactiva de Redis. Ahí se escriben los comandos directamente. Para salir: `exit` o `Ctrl+D`.

> `docker exec -it redis-tp4 redis-cli` ejecuta `redis-cli` **dentro** del contenedor `redis-tp4`.
> `-it` mantiene la sesión interactiva.

### Ejecutar un comando suelto (sin entrar a la consola)

```bash
docker exec redis-tp4 redis-cli SET package "Bariloche 3 days"
docker exec redis-tp4 redis-cli GET package
```

### Opción B — RedisInsight (interfaz visual)

1. Abrir [http://localhost:8001](http://localhost:8001) en el navegador.
2. Conectar a `localhost:6379` (sin usuario ni contraseña).
3. Usar el **Workbench** para correr comandos y el **Browser** para ver las claves.
