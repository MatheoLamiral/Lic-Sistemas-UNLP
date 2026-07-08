# Taller Docker

## Ejercicio 1:​ Instale Docker CE (Community Edition) en su sistema operativo.

Ayuda: seguir las instrucciones de la página de Docker. La instalación más simple para distribuciones de GNU/Linux basadas en Debian es usando los repositorios.

## Ejercicio 2:​ Asegúrese de agregar el usuario con el que trabajará al grupo docker, por ejemplo en la VM, luego de esta operación deberá cerrar la sesión del usuario so en la terminal y volver a loguearse:

```bash
~# adduser so docker
```

## Ejercicio 3:​ Luego de volver a loguearse verifique que el usuario pertenece al grupo docker:

```bash
~$ groups
so cdrom floppy audio dip video plugdev users netdev bluetooth docker
```

## Ejercicio 4:​ Usando las herramientas (comandos) provistas por Docker realice las siguientes tareas:

### a. Obtener una imagen de la última versión de Ubuntu disponible. ¿Cuál es el tamaño en disco de la imagen obtenida? ¿Ya puede ser considerada un contenedor? ¿Qué significa lo siguiente: *Using default tag: latest*?

- Para obtener la imagen de ubuntu ejecutamos `docker pull ubuntu`
- Para listar las imagenes y poder ver el tamaño en disco de las mismas ejecutamos `docker images`
  - En particular nos interesa la siguiente línea:
    ```
    ubuntu:latest              b7f48194d4d8        158MB         45.3MB        
    ```
    - Las columnas son IMAGE, ID, DISK USAGE, CONTENT SIZE y EXTRA (en este caso vacía)
    - Podemos observar entonces, que **la imagen de ubuntu tiene un tamaño en disco de 45.3 MB** (CONTENT SIZE), el DISK USAGE incluye el overhead de las capas
- "Using default tag: latest", significa que, si no le especificamos ninguna version al comando `docker pull`, **por defecto nos traerá la última versión**

No puede ser considerada un contenedor, **solo descargamos la imagen** (el molde). **Un contenedor es una instancia en ejecución de esa imagen**, que recién se creará cuando ejecutemos `docker run`

### b. De la imagen obtenida en el punto anterior iniciar un contenedor que simplemente ejecute el comando ls -l.

```bash
matheolamiral@fedora ~ > docker run ubuntu ls -l
total 16
lrwxrwxrwx+                   1 root root   7 Apr 20 08:46 bin -> usr/bin
drwxr-xr-x+                   1 root root   0 Apr 20 08:46 boot
drwxr-xr-x+                   5 root root 340 Jul  7 20:56 dev
drwxr-xr-x+                   1 root root  56 Jul  7 20:56 etc
drwxr-xr-x+                   1 root root  12 Jun 27 04:18 home
lrwxrwxrwx+                   1 root root   7 Apr 20 08:46 lib -> usr/lib
lrwxrwxrwx+                   1 root root   9 Apr 20 08:46 lib64 -> usr/lib64
drwxr-xr-x+                   1 root root   0 Jun 27 02:06 media
drwxr-xr-x+                   1 root root   0 Jun 27 02:06 mnt
drwxr-xr-x+                   1 root root   0 Jun 27 02:06 opt
dr-xr-xr-x+                 545 root root   0 Jul  7 20:56 proc
drwx------+                   1 root root  30 Jun 27 04:18 root
drwxr-xr-x+                   1 root root  22 Jun 27 04:18 run
lrwxrwxrwx+                   1 root root   8 Apr 20 08:46 sbin -> usr/sbin
drwxr-xr-x+                   1 root root   0 Jun 27 02:06 srv
dr-xr-xr-x+                  13 root root   0 Jul  6 22:24 sys
drwxrwxrwt+                   1 root root   0 Jun 27 02:07 tmp
drwxr-xr-x+                   1 root root  94 Jun 27 04:18 usr
drwxr-xr-x+                   1 root root  90 Jun 27 04:18 var
```

### c. ¿Qué sucede si ejecuta el comando docker [container] run ubuntu /bin/bash? ¿Puede utilizar la shell Bash del contenedor?

Al ejecutar `docker run ubuntu /bin/bash` (sin flags), el contenedor arranca y termina inmediatamente, sin darnos acceso a la shell. No podemos usar bash, porque necesita una terminal interactiva conectada a STDIN (Standard Input), y sin ella no tiene de dónde leer comandos, por lo que finaliza al instante (y el contenedor se detiene con él).

#### i. Modifique el comando utilizado para que el contenedor se inicie con una terminal interactiva y ejecutarlo. ¿Ahora puede utilizar la shell Bash del contenedor? ¿Por qué?

- `docker run -it ubuntu /bin/bash`
  - `-i` (interactive): mantiene STIDN abierto y conectado (el teclado llega al bash)
  - `-t` (tty): le asigna una pseudo-terminal, bash se comporta como una consola real

El prompt cambia a `root@<id>:/#`, indicando que estamos dentro del contenedor. 

#### ii. ¿Cuál es el PID del proceso bash en el contenedor? ¿Y fuera de éste?

- Al ejecutar `echo $$` dentro del contenedor, vemos qe el PID es 1 
- Al ejecutar `docker top 019f56c80184` (el texto final es el nombre del contenedor), vemos que el PID es 65339
  - `docker top` muestra todos los procesos del contenedor con su PID visto desde el host
    >[!NOTE]    
    > También podríamos haber usado `ps aux | grep /bin/bash`, pero `docker top` es más directo


Es el mismo proceso con dos PIDs distintos debido al **PID namespace** que docker crea para aislar el contenedor. **Dentro del contenedor ve su propia numeración, mientras que en el host tiene su PID real** entre todos los procesos del sistema

#### iii. Ejecutar el comando lsns. ¿Qué puede decir de los namespace?

- Dentro del contenedor:
```bash
root@019f56c80184:/# lsns
        NS TYPE   NPROCS PID USER COMMAND
4026531834 time        2   1 root /bin/bash
4026531837 user        2   1 root /bin/bash
4026534224 mnt         2   1 root /bin/bash
4026534225 uts         2   1 root /bin/bash
4026534226 ipc         2   1 root /bin/bash
4026534227 pid         2   1 root /bin/bash
4026534228 cgroup      2   1 root /bin/bash
4026534229 net         2   1 root /bin/bash
```

El contenedor tiene su **propio conjunto de namespaces** con **IDs distintos a los del host** para mnt, uts, ipc, pid, cgroup y net. En cambio time y user coinciden con los del host (por defecto docker no los aisla, los comparte). Docker los crea para aislar el contenedor 

#### iv. Dentro del contenedor cree un archivo con nombre sistemas-operativos en el directorio raíz del filesystem y luego salga del contenedor (finalice la sesión de Bash utilizando las teclas Ctrl + D o el comando exit).

- `cd /`
- `touch sistemas-operativos`
- `exit` 

#### v. Corrobore si el archivo creado existe en el directorio raíz del sistema operativo anfitrión (host). ¿Existe? ¿Por qué?

El archivo no existe en el `/` del host. Esto se debe a que el **contenedor tiene su propio filesystem aislado** (la imagen de solo lectura, más una capa de escritura propia, aislada mediante el mount namespace que vimos en el `lsns`). El archivo se creó dentro de esa capa del contenedor, así que el **host, que tiene su propio sistema de archivos, no lo ve**.

### d. Vuelva a iniciar el contenedor anterior utilizando el mismo comando (con una terminal interactiva). ¿Existe el archivo creado en el contenedor? ¿Por qué?

Al ejecutar de, el archivo `sistemas-operativos` **NO existe**. Esto se debe a que `docker run` **crea un contenedor nuevo a partir de la imagen de Ubuntu, con su propia capa de escritura vacía**. El archivo que creamos antes quedó en la capa de escritura del contenedor anterior, no en la imagen, por lo que este contenedor nuevo empieza limpio y no lo tiene.

### e. Obtenga el identificador del contenedor (container_id) donde se creó el archivo y utilícelo para iniciar con el comando docker start -ia container_id el contenedor en el cual se creó el archivo.

- `docker start -ia 019f56c80184`
  - `-i` interactivo
  - `-a` attach, conecta nuestra terminal a la salida del contenedor

#### i. ¿Cómo obtuvo el container_id para este comando?

- `docker ps -a`

#### ii. Chequee nuevamente si el archivo creado anteriormente existe. ¿Cuál es el resultado en este caso? ¿Puede encontrar el archivo creado?

- Ahora si vemos el archivo `sistemas-operativos` ya que no creamos un contenedor nuevo, sino que reiniciamos el mismo con `docker start`. Este contenedor conserva su capa de escritura

>[!IMPORTANT]
> `docker run` crea un contenedor NUEVO con capa de escritura vacía, en cambio, `docker start` reinicia el MISMO contenedor y conserva su capa de escritura.

### f. ¿Cuántos contenedores están actualmente en ejecución? ¿En qué estado se encuentra cada uno de los que se han ejecutado hasta el momento?

- En ejecución (`docker ps`): 1 → 019f56c80184 (recursing_ptolemy), estado `Up`
- Los que se han ejecutado hasta el momento se encuentran en estado `Exited (0)`, es decir, terminados sin error

### g. Elimine todos los contenedores creados hasta el momento. Indique el o los comandos utilizados.

- `docker rm -f $(docker ps -aq)` elimina absolutamente todos los contenedores
- `docker rm -f <id_1> <id_2> ...` elimina los contenedores que le indiquemos 

## Ejercicio 5:​ Creación de una imagen a partir de un contenedor. Siguiendo los pasos indicados a continuación genere una imagen de Docker a partir de un contenedor:

### a. Inicie un contenedor a partir de la imagen de Ubuntu descargada anteriormente ejecutando una consola interactiva de Bash.

- `docker run -it ubuntu /bin/bash`

### b. Instale el servidor web Nginx (https://nginx.org/en/) en el contenedor utilizando los siguientes comandos:

```bash
export DEBIAN_FRONTEND=noninteractive
export TZ=America/Buenos_Aires
apt update -qq
apt install -y --no-install-recommends nginx
```

> [!NOTE]
> Los dos primeros comandos exportan dos variables de ambiente para que la instalación de una de las dependencias de nginx (el paquete tzdata) no requiera que interactivamente se respondan preguntas sobre la ubicación geográfica a utilizar.

### c. Salga del contenedor y genere una imagen Docker a partir de éste. ¿Con qué nombre se genera si no se especifica uno?

1. `exit`
2. `docker commit c4b6d534315b` (id del contenedor)

Si no se especifica un nombre, la imagen queda sin etiquetar(`<none>:<none>`/`<untagged>`), identificada únicamente por su **IMAGE ID**

>[!NOTE]
>  `commit` toma el estado actual del contenedor (imagen base de Ubuntu + la capa de escritura con nginx) y lo "congela" en una imagen nueva

### d. Cambie el nombre de la imagen creada de manera que en la columna Repository aparezca nginx-so y en la columna Tag aparezca v1.

- `docker tag 63f74741f8b9 nginx-so:v1`

### e. Ejecute un contenedor a partir de la imagen nginx-so:v1 que corra el servidor web nginx atendiendo conexiones en el puerto 8080 del host, y sirviendo una página web para corroborar su correcto funcionamiento. Para esto:

#### I. En el Sistema Operativo anfitrión (host) sobre el cual se ejecuta Docker crear un directorio que se utilizará para este taller. Éste puede ser el directorio nginx-so dentro de su directorio personal o cualquier otro directorio - para los fines de este enunciado haremos referencia a éste como /home/so/nginx-so, por lo que en los lugares donde se mencione esta ruta usted deberá reemplazarla por la ruta absoluta al directorio que haya decidido crear en este paso.

- `mkdir -p ~/nginx-so`
- `cd ~/nginx-so`

#### II. Dentro de ese directorio, cree un archivo llamado index.html que contenga el código HTML de este gist de GitHub: https://gist.github.com/ncuesta/5b959fce1c7d2ed4e5a06e84e5a7efc8.

- `curl -L https://gist.githubusercontent.com/ncuesta 5b959fce1c7d2ed4e5a06e84e5a7efc8/raw -o index.html`

#### III. Cree un contenedor a partir de la imagen nginx-so:v1 montando el directorio del host (/home/so/nginx-so) sobre el directorio /var/www/html del contenedor, mapeando el puerto 80 del contenedor al puerto 8080 del host, y ejecutando el servidor nginx en primer plano. Indique el comando utilizado. Para iniciar el servidor nginx en primer plano utilice el comando `nginx -g 'daemon off;'`

- Parados en el directorio donde está el `index.html` ejecutamos `docker run --rm -p 8080:80 -v tu_ruta/nginx-so:/var/www/html:Z nginx-so:v1 nginx -g 'daemon off;'`
  - `-p 8080:80` → mapea el puerto 80 del contenedor al 8080 del host.
  - `v <ruta>:/var/www/html:Z` → monta el directorio del host con el `index.html`. El `:Z` es necesario en Fedora porque SELinux (MAC) bloquea el acceso del contenedor a los archivos montados, `:Z` los reetiqueta para permitirlo.
  - `nginx -g 'daemon off;'` → ejecuta nginx en primer plano.

### f. Verifique que el contenedor esté ejecutándose correctamente abriendo un navegador web y visitando la URL http://localhost:8080.

### g. Modifique el archivo index.html agregándole un párrafo con su nombre y número de alumno. ¿Es necesario reiniciar el contenedor para ver los cambios?

**No es necesario reiniciar el contenedor**. Al agregar el párrafo al `index.html` y recargar http://localhost:8080, el cambio aparece de inmediato. Esto se debe a que el archivo está en el host y se monta con -v (volumen/bind mount). El **contenedor lee el archivo del host en tiempo real**, por eso las modificaciones se reflejan al instante sin reiniciar.

### h. Analice: ¿por qué es necesario que el proceso nginx se ejecute en primer plano? ¿Qué ocurre si lo ejecuta sin -g 'daemon off;'?

Es necesario que nginx corra en primer plano, ya que un **contenedor vive solo mientras su proceso principal (PID 1) esté en ejecución**. Por defecto, nginx arranca como daemon, se bifurca a segundo plano y el proceso original termina. Si eso pasa dentro del contenedor, Docker interpreta que el proceso principal finalizó y detiene el contenedor (nginx se apaga con él). Al usar` nginx -g 'daemon off;'`, se **fuerza a nginx a quedarse en primer plano**, sin `-g daemon off;` el **contenedor arranca y se detiene inmediatamente**.

## Ejercicio 6:​ Creación de una imagen Docker a partir de un archivo Dockerfile. Siguiendo los pasos indicados a continuación, genere una nueva imagen a partir de los pasos descritos en un Dockerfile. Ayuda: las instrucciones necesarias para definir los pasos en el Dockerfile son FROM, EXPOSE, RUN, COPY y CMD.

### a. En el directorio del host creado en el punto anterior (/home/so/nginx-so), cree un archivo Dockerfile que realice los siguientes pasos:

#### i. Comenzar en base a la imagen oficial de Ubuntu.

```Dockerfile
FROM ubuntu
```

#### ii. Exponer el puerto 80 del contenedor.

```Dockerfile
EXPOSE 80
```

#### iii. Instalar el servidor web nginx.

```Dockerfile
RUN export DEBIAN_FRONTEND=noninteractive && \
export TZ=America/Buenos_Aires && \
apt update -qq && \
apt install -y --no-install-recommends nginx
``` 

>[!NOTE]
> Los `export` de `DEBIAN_FRONTEND` y `TZ` van **dentro del mismo `RUN`** (con `&&`), porque cada `RUN` es una capa independiente, en un `RUN` aparte no valdrían para el `apt install`.

#### iv. Copiar el archivo index.html del mismo directorio del host al directorio /var/www/html de la imagen.

```Dockerfile
COPY index.html /var/www/html/index.html
```

#### v. Indicar el comando que se utilizará cuando se inicie un contenedor a partir de esta imagen para ejecutar el servidor nginx en primer plano: nginx -g 'daemon off;'. Use la forma exec para definir el comando, de manera que todas las señales que reciba el contenedor sean enviadas directamente al proceso de nginx. 

```Dockerfile
CMD ["nginx", "-g", "daemon off;"]
```

>[!IMPORTANT]
> El `CMD` se escribe en **forma exec** (`["nginx","-g","daemon off;"]`) y no en forma shell. Así nginx corre como **PID 1 directo** y recibe las señales del contenedor (ej. el SIGTERM de `docker stop`) directamente, permitiendo un frenado limpio.

### b. Utilizando el Dockerfile que generó en el punto anterior construya una nueva imagen Docker guardándola localmente con el nombre nginx-so:v2.

`docker build -t nginx-so:v2 .`

### c. Ejecute un contenedor a partir de la nueva imagen creada con las opciones adecuadas para que pueda acceder desde su navegador web a la página a través del puerto 8090 del host. Verifique que puede visualizar correctamente la página accediendo a http://localhost:8090.

`docker run --rm -p 8090:80 nginx-so:v2`
- `-p 8090:80` → puerto 80 del contenedor → 8090 del host.
- Sin `-v` → el index.html viene incluido en la imagen (no hace falta montarlo).
- Sin `nginx -g 'daemon off;'` → ya está en el CMD del Dockerfile.

### d. Modifique el archivo index.html del host agregando un párrafo con la fecha actual y recargue la página en su navegador web. ¿Se ven reflejados los cambios que hizo en el archivo? ¿Por qué?

**No, los cambios no se reflejan**. A diferencia del ejercicio 5, donde el html se montaba como volumen y se leía del host en vivo, acá el `index.html` se **copió dentro de la imagen con COPY durante el docker build**. El contenedor sirve esa copia interna, que quedó "congelada" al momento de construir la imagen. **Modificar el archivo del host no cambia la copia que está dentro de la imagen**.

### e. Termine el contenedor iniciado antes y cree uno nuevo utilizando el mismo comando. Recargue la página en su navegador web. ¿Se ven ahora reflejados los cambios realizados en el archivo HTML? ¿Por qué?

1. `Ctrl + c`
2. `docker run --rm -p 8090:80 nginx-so:v2`

No, los **cambios siguen sin reflejarse**, aunque el contenedor sea nuevo. Esto se debe a que el **contenedor se crea a partir de la misma imagen nginx-so:v2**, que todavía contiene la copia vieja del `index.html` (la que se copió con COPY durante el docker build). **Crear un contenedor nuevo (`docker run`) no reconstruye la imagen, solo la instancia tal cual está**. **Para incorporar el cambio** habría que **reconstruir la imagen** con `docker build`.

### f. Vuelva a construir una imagen Docker a partir del Dockerfile creado anteriormente, pero esta vez dándole el nombre nginx-so:v3. Cree un contenedor a partir de ésta y acceda a la página en su navegador web. ¿Se ven reflejados los cambios realizados en el archivo HTML? ¿Por qué?

1. `docker build -t nginx-so:v3 .`
2. `docker run --rm -p 8090:80 nginx-so:v3`

Sí, **ahora los cambios se reflejan**. Al reconstruir la imagen, la instrucción `COPY index.html` se ejecutó de nuevo y copió la versión actualizada del html dentro de la nueva imagen. El contenedor de `nginx-so:v3` sirve esa copia nueva.

>[!IMPORTANT]
> Cuando el contenido está dentro de la imagen (vía `COPY`), la única forma de actualizarlo es reconstruir la imagen.