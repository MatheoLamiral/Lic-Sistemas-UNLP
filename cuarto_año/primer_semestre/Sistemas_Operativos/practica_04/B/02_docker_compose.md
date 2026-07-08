# Docker compose

## Ejercicio 1:​ Utilizando sus palabras describa, ¿qué es docker compose?

Docker Compose es una herramienta para definir y ejecutar aplicaciones de varios contenedores mediante un único archivo de configuración (docker-compose.yaml).

En vez de levantar cada contenedor a mano con muchos docker run, se declara toda la app (frontend, backend, base de datos, etc.) en un solo archivo y se la maneja con un comando: `docker compose up` la levanta entera y `docker compose down` la baja. Compose se encarga de crear los contenedores, conectarlos en una red común y configurar puertos, volúmenes y variables.

>[!NOTE]
> La ventaja es la reproducibilidad (todo queda en un archivo versionable) y simplicidad (un comando orquesta toda la aplicación multi-contenedor).

## Ejercicio 2:​ ¿Qué es el archivo compose y cuál es su función? ¿Cuál es el "lenguaje" del archivo?

El archivo compose (`docker-compose.yaml` o `compose.yaml`) es el archivo de configuración donde se **declara toda la aplicación multi-contenedor**: qué servicios la componen, qué imagen usa cada uno, sus puertos, volúmenes, redes, variables de entorno, dependencias, etc.

Su función es servir de **definición declarativa de la aplicación**. Docker Compose lo lee y, a partir de él, **crea y orquesta todos los contenedores** con un solo comando (`docker compose up`). Es lo que hace que el entorno sea reproducible y versionable.

**Lenguaje**: está escrito en **YAML** (YAML Ain't Markup Language), un formato de texto plano para representar datos de forma estructurada, basado en **indentación** (sangría) y **pares "clave: valor"**. Es legible por humanos y muy usado para archivos de configuración.

## Ejercicio 3:​ ¿Cuáles son las versiones existentes del archivo docker-compose.yaml existentes y qué características aporta cada una? ¿Son compatibles entre sí? ¿Por qué?

Existieron principalmente tres formatos:

- **Versión 1 (legacy)**: la más antigua, sin la clave `version` ni el bloque `services` (los servicios iban en la raíz). No soportaba redes ni volúmenes nombrados. **Obsoleta**.
- **Versión 2** (`version: "2"`): agregó el bloque `services`, **redes y volúmenes nombrados**, `depends_on` y límites de recursos (`mem_limit`, `cpus`). Orientada a **un solo host**.
- **Versión 3** (`version: "3"`): pensada para **producción y Docker Swarm**. Incorporó el bloque **`deploy`** (réplicas, políticas de despliegue) y movió ahí los límites de recursos, quitando algunas opciones de la v2.

**Compatibilidad**: **no son totalmente compatibles entre sí**, porque cada versión agrega o quita claves (p. ej. los límites de recursos están como `mem_limit` en v2 pero bajo `deploy.resources` en v3). Además, cada formato requiere una versión de Docker/Compose que lo soporte.

>[!NOTE]
> Actualmente Docker unificó v2 y v3 en la **Compose Specification**, donde la clave `version` quedó opcional/deprecada.

## Ejercicio 4:​ Investigue y describa la estructura de un archivo compose. Desarrolle al menos sobre los siguientes bloques indicando para qué se usan:

Un archivo compose se organiza en bloques de alto nivel, siendo `services` el principal, más bloques opcionales como `volumes` y `networks` a nivel raíz.

### a. services
Bloque **principal**: define los **servicios (contenedores)** que componen la aplicación. Cada servicio tiene su propia configuración (imagen, puertos, etc.).

### b. build
Indica **cómo construir la imagen** del servicio a partir de un **Dockerfile** (ruta del contexto y/o del Dockerfile). Se usa cuando la imagen se arma localmente en vez de traerla de un registry.

### c. image
Especifica la **imagen a usar** para el servicio (de un registry, p. ej. `nginx:latest`). Es la alternativa a `build`.

### d. volumes
Monta **volúmenes** en el servicio para **persistir datos** o compartir archivos con el host. A nivel raíz, declara los **volúmenes nombrados** que gestiona Docker.

### e. restart
Define la **política de reinicio** del contenedor: `no`, `always`, `on-failure`, `unless-stopped`. Controla qué hace Docker si el contenedor se detiene o falla.

### f. depends_on
Establece **dependencias y orden de arranque** entre servicios (un servicio arranca después de aquellos de los que depende).

### g. environment
Define **variables de entorno** que recibe el contenedor (p. ej. credenciales, configuración).

### h. ports
**Publica puertos** del contenedor hacia el **host**, con el mapeo `host:contenedor` (p. ej. `8080:80`). Hace el servicio accesible desde afuera.

### i. expose
**Expone puertos solo a otros contenedores** de la misma red, **sin** publicarlos al host. Es comunicación interna entre servicios.

### j. networks
Define y asocia las **redes** a las que se conectan los servicios, permitiendo que se comuniquen entre sí (por nombre de servicio).

## Ejercicio 5:​ Conceptualmente: ¿Cómo se podrían usar los bloques "healthcheck" y "depends_on" para ejecutar una aplicación Web dónde el backend debería ejecutarse si y sólo si la base de datos ya está ejecutándose y lista?

La clave es que `depends_on` por defecto solo espera a que el contenedor de la DB **arranque**, no a que esté **lista** para aceptar conexiones. Para eso se combina con `healthcheck`:

- En el servicio **db** se define un **`healthcheck`**: un comando que verifica si la base ya acepta conexiones (p. ej. `pg_isready`), con `interval` y `retries`.
- En el servicio **backend** se usa **`depends_on`** con la condición **`condition: service_healthy`** apuntando a `db`. Así el backend arranca **solo cuando la DB pasó su healthcheck** (está realmente lista), no apenas se crea su contenedor.

```yaml
services:
  db:
    image: postgres
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "user"]
      interval: 5s
      retries: 5
  backend:
    build: ./backend
    depends_on:
      db:
        condition: service_healthy
```

## Ejercicio 6:​ Indique qué hacen y cuáles son las diferencias entre los siguientes comandos:

### a. docker compose create y docker compose up
- **`create`**: solo **crea** los contenedores (y redes/volúmenes) pero **no los arranca**.
- **`up`**: **crea y arranca** todos los servicios (construyendo imágenes si hace falta) y muestra sus logs (con `-d` corre en segundo plano).

### b. docker compose stop y docker compose down
- **`stop`**: **detiene** los contenedores pero **los conserva** (junto con redes y volúmenes); se pueden volver a iniciar.
- **`down`**: **detiene y elimina** los contenedores y las redes creadas (los volúmenes nombrados se conservan, salvo `-v`).

### c. docker compose run y docker compose exec
- **`run`**: arranca un **contenedor nuevo** (puntual/one-off) de un servicio para ejecutar un comando.
- **`exec`**: ejecuta un comando **dentro de un contenedor que ya está en ejecución**.

### d. docker compose ps
Lista los **contenedores del proyecto** Compose y su **estado** (corriendo, detenido, puertos).

### e. docker compose logs
Muestra los **logs** (salida) de los servicios del proyecto.

## Ejercicio 7:​ ¿Qué tipo de volúmenes puede utilizar con docker compose? ¿Cómo se declara cada tipo en el archivo compose?

- **Volúmenes nombrados** (gestionados por Docker, persistentes): se declaran a nivel raíz en `volumes:` y se referencian en el servicio.
    ```yaml
    services:
      db:
        volumes:
          - datos_db:/var/lib/postgresql/data
    volumes:
      datos_db:
    ```
- **Bind mounts** (una ruta del host): se mapea una carpeta del host directamente.
    ```yaml
    services:
      web:
        volumes:
          - ./html:/usr/share/nginx/html
    ```
- **Volúmenes anónimos** (sin nombre, gestionados por Docker pero sin referencia explícita):
    ```yaml
    volumes:
      - /var/lib/mysql
    ```

>[!NOTE]
> Diferencia: el **nombrado** lo administra Docker y es portable/persistente; el **bind mount** apunta a una ruta concreta del host y puede ser modificado por procesos ajenos a Docker.

## Ejercicio 8:​ ¿Qué sucede si en lugar de usar el comando "docker compose down" utilizo "docker compose down -v/--volumes"?

- **`docker compose down`**: detiene y elimina contenedores y redes, **pero conserva los volúmenes nombrados** → los datos persistidos **se mantienen**.
- **`docker compose down -v` / `--volumes`**: hace lo mismo y **además elimina los volúmenes nombrados** (declarados en el compose) y los anónimos → **se pierden los datos** guardados en ellos.

>[!NOTE]
> En resumen, el `-v` borra también la persistencia. Útil para "empezar de cero", peligroso si no querés perder los datos (p. ej. la base de datos).
