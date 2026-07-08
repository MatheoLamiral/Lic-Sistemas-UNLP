# Ejercicio guiado - Instanciando un Wordpress y una Base de Datos

## Ejercicio guiado

Dado el siguiente código de archivo compose:

```yaml
version: "3.9"

services:
  db:
    image: mysql:5.7
    networks:
      - wordpress
    volumes:
      - db_data:/var/lib/mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: somewordpress
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
  wordpress:
    depends_on:
      - db
    image: wordpress:latest
    networks:
      - wordpress
    volumes:
      - ${PWD}:/data
      - wordpress_data:/var/www/html
    ports:
      - "127.0.0.1:8000:80"
    restart: always
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
      WORDPRESS_DB_NAME: wordpress
volumes:
  db_data: {}
  wordpress_data: {}
networks:
  wordpress:
```

## Preguntas

Intente analizar el código ANTES de correrlo y responda:

## Ejercicio 1:​ ¿Cuántos contenedores se instancian?

Se instancian **dos contenedores**, uno llamado `db` y otro llamado `wordpress`

## Ejercicio 2:​ ¿Por qué no se necesitan Dockerfiles?

Porque los **servicios usan imágenes ya construidas y publicadas en Docker Hub** (`image: mysql:5.7` y `image: wordpress:latest`). No hay ningún bloque `build`, así que Docker descarga esas imágenes directamente en vez de construirlas. Un **Dockerfile solo haría falta si necesitáramos una imagen propia/a medida**.

## Ejercicio 3:​ ¿Por qué el servicio identificado como "wordpress" tiene la siguiente línea?

```yaml
depends_on:
  - db
```

Esto indica, que para que se pueda crear el contenedor `wordpress`, **debe haberse creado** correctamente el contenedor `db`.

>[!IMPORTANT]
> `depends_on` solo espera a que el contenedor de `db` arranque, no a que la base esté lista para aceptar conexiones (para eso haría falta un `healtcheck`)

## Ejercicio 4:​ ¿Qué volúmenes y de qué tipo tendrá asociado cada contenedor?

`db` tiene un **named volume** (`db_data`). `wordpress` tiene dos volúmenes, un **bind mount** (`${PWD}:/data`) y un **named volume** (`wordpress_data`).

## Ejercicio 5:​ ¿Por qué uso el volumen nombrado de la siguiente manera para el servicio db en lugar de dejar que se instancie un volumen anónimo con el contenedor?

```yaml
volumes:
  - db_data:/var/lib/mysql
```

Usamos un named volume, porque de esa forma se crea un volumen persisente y reutilizable con nombre (`db_data`) que Docker puede identificar y conservar, incluso si eliminamos o recreamos el contenedor (a menos que se utilice `-v`). **Si no lo nombramos, Docker crea un volumen anónimo**, como `/var/lib/docker/volumes/2dwe2342dewd.../_data` que **no tiene nombre, se pierde fácilmente y es difícil de reutilizar o gestionar**. En una base de datos, perder el volumen significa perder todos los datos de la base. Por eso es crítico usar un volumen nombrado y no dejarlo al azar de un anónimo.

## Ejercicio 6:​ ¿Qué genera la siguiente línea en la definición de wordpress?

```yaml
volumes:
  - ${PWD}:/data
```

Es un bind mount, **monta el directorio actual del host** (`${PWD}` = present working directory, desde donde se ejecuta `docker compose`) sobre `/data` **dentro del contenedor**. Así el **contenido de la carpeta del proyecto** (donde está el `docker-compose.yml`)** queda accesible en** `/data`, y los **cambios se reflejan en ambas direcciones** (rw), permitiendo compartir archivos con el contenedor y guardar archivos generados por wordpress en el host.

## Ejercicio 7:​ ¿Qué representa la información que estoy definiendo en el bloque environment de cada servicio? ¿Cómo se "mapean" al instanciar los contenedores?

Son **variables de entorno que se le pasan a cada contenedor al instanciarlo**, con su configuración, credenciales y nombre de la base (`MYSQL_*` en `db`), y datos de conexión a la base (`WORDPRESS_DB_*` en `wordpress`). Al instanciar, Docker Compose **inyecta esas variables dentro del contenedor como variables de entorno**, y la **aplicación las lee para configurarse** (ej. MySQL crea la base MYSQL_DATABASE con ese usuario/contraseña y WordPress usa WORDPRESS_DB_* para conectarse a ella).

## Ejercicio 8:​ ¿Qué sucede si cambio los valores de alguna de las variables definidas en bloque "environment" en solo uno de los contenedores y hago que sean diferentes? (Por ej: cambio SOLO en la definición de wordpress la variable WORDPRESS_DB_NAME)

Se **rompe la conexión**, WordPress intentaría conectarse a una base con ese nombre nuevo, pero MySQL creó la base con el nombre de `MYSQL_DATABASE` (wordpress). **Al no coincidir, WordPress no encuentra su base de datos**

## Ejercicio 9:​ ¿Cómo sabe comunicarse el contenedor "wordpress" con el contenedor "db" si nunca doy información de direccionamiento?

A través de la **red interna definida** (`networks: wordpress`). Docker Compose **crea esa red virtual interna y provee un DNS interno para que los contenedores se comuniquen**, **cada servicio es accesible por su nombre de servicio** como si fuera un **hostname**. Por eso wordpress usa `WORDPRESS_DB_HOST: db`, el nombre `db` se resuelve automáticamente a la IP del contenedor de la base dentro de esa red. No hace falta dar IPs, Compose maneja la resolución por nombre.

## Ejercicio 10:​ ¿Qué puertos expone cada contenedor según su Dockerfile? (pista: navegue el sitio https://hub.docker.com/_/wordpress y https://hub.docker.com/_/mysql para acceder a los Dockerfiles que generaron esas imágenes y responder esta pregunta.)

- `mysql:5.7` expone el puerto `3306/TCP` (MySQL).
- `wordpress:latest` expone el puerto `80/TCP` (corre sobre Apache).

>[!NOTE]
> `expose` en el Dockerfile solo documenta los puertos que usa el servicio, es distinto de publicarlos (`ports:`), que los mapea al host.

## Ejercicio 11:​ ¿Qué servicio se "publica" para ser accedido desde el exterior y en qué puerto? ¿Es necesario publicar el otro servicio? ¿Por qué?

Se publica el servicio wordpress, con `ports: "127.0.0.1:8000:80"`, de esta forma el **puerto `80` del contenedor queda accesible en `127.0.0.1:8000` del host**. El servicio `db` **NO se publica** (no tiene bloque `ports`), y **no es necesario**, ya que **la base solo necesita ser accedida por el contenedor de wordpress**, que está en la misma red interna de Compose. Publicar `db` al host sería **innecesario e inseguro** (expondría la base de datos al exterior).

## Instanciando

Cree un directorio llamado docker-compose-ej-1 donde prefiera, ubíquese dentro de éste y cree un archivo denominado docker-compose.yml pegando dentro el código anterior. La herramienta docker-compose, por defecto, espera encontrar en el directorio desde donde se la invoca un archivo docker-compose.yml (por eso lo creamos con ese nombre). Si existe, lee este archivo compose y realiza el despliegue de los recursos allí definidos.

Ahora, desde ese directorio ejecute el comando `docker compose up`, lo que resulta en el comienzo del despliegue de nuestros servicios. Como es la primera vez que lo corremos y si no tenemos las imágenes en la caché local de nuestro dispositivo, se descargan las imágenes de los servicios que estamos iniciando (recordar lo visto en la práctica anterior).

```bash
~$ docker compose up
```

En este punto, quedará la consola conectada a los servicios y estaremos viendo los logs exportados de los servicios. Si cerramos la consola o detenemos el proceso con ctrl+c, los servicios se darán de baja porque iniciamos los servicios en modo *foreground*. Para no quedar "pegados" a la consola podemos iniciar los servicios en modo *detached* de modo que queden corriendo en segundo plano (*background*), igual que como se hace con el comando `docker run -d IMAGE`:

```bash
~$ docker compose up -d
```

De esta manera veremos sólo información de que los servicios se inician y su nombre, pero la consola quedará "libre".

Si quisiéramos conectarnos a alguno de los contenedores que docker-compose inició, por ejemplo el contenedor de wordpress, podemos hacerlo de la manera tradicional que se vio en la práctica de Docker (`docker exec [OPTIONS] CONTAINER COMMAND [ARG...]`) utilizando el identificador apropiado para el contenedor, o mediante el comando que docker-compose también brinda para hacerlo y usar su nombre de servicio ("wordpress" en este caso):

```bash
~$ docker compose exec wordpress /bin/bash
```

Una vez dentro del contenedor, podemos navegar sus directorios normalmente. Si nos dirigimos al directorio /data, veremos dentro el contenido de nuestro directorio "docker-compose-ej-1" (solo tenemos el archivo docker-compose.yml) ya que montamos ese directorio como un volumen. Si creamos algún archivo dentro de este directorio, lo vemos también reflejado afuera del contenedor (el volumen montado como rw funciona en ambas direcciones).

Para listar los servicios que iniciamos:

```bash
~$ docker compose ps
```

Se puede observar que el servicio wordpress está exponiendo el puerto 80 del contenedor en la dirección 127.0.0.1 puerto 8000 de nuestro dispositivo host. Esto quiere decir que si ingresamos desde un navegador a la dirección "127.0.0.1:8000" veremos la página de inicio de la aplicación Wordpress.

De este modo, hemos realizado el despliegue de una aplicación wordpress y de su base de datos mediante el uso de contenedores y la herramienta docker-compose. Desde este punto, solo queda continuar con la instalación de wordpress desde el browser.

Si queremos detener los servicios podemos ejecutar el comando:

```bash
~$ docker-compose stop
```

y para eliminarlos:

```bash
~$ docker compose down
```

Pero atención, esto elimina los contenedores pero no SUS VOLÚMENES DE DATOS, por lo que si volvemos a levantar los servicios por más que hayamos eliminado los contenedores, veremos que todas las modificaciones que hayamos realizado en la instalación de wordpress y datos agregados a la base de datos aún están presentes. Si queremos eliminar todo rastro de un despliegue previo, tendremos que eliminar los contenedores y también los volúmenes asociados utilizando el flag -v en docker-compose down:

```bash
~$ docker-compose down -v
```

De esta manera, hemos eliminado todo lo instanciado por el docker compose. Solo quedan las imágenes Docker descargadas en la caché local del dispositivo, las cuales deben eliminar por su cuenta.
