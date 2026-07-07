# Docker

### Ejercicio 1:​ Utilizando sus palabras, describa qué es Docker y enumere al menos dos beneficios que encuentre para el concepto de contenedores.

Es una **plataforma open source que permite empaquetar y ejecutar aplicaciones en contenedores livianos**. Te deja meter una aplicación junto con **todo lo que necesita para funcionar** (bianrios, librearías y dependencias) en un contenedor, que después corre igual que en cualquier entorno que tenga Docker, sin importar la máquina

- Beneficios de Docker:
  - **Livianos y arranque rápido**: como comparten el kernel del host y no incluyen un SO guest completo (a diferencia de las VMs), ocupan menos espacio y arrancan mucho más rápido. Esto permite correr más servicios en un mismo equipo sin necesidad de VMs
  - **Portabilidad**: el contenedor es autocontenido (trae app + librerías + dependencias), así que se ejecuta de la misma forma en la máquina del desarrollador, en testing y en producción, evitando el clásico "en mi máquina funciona".

>[!NOTE]
> Otros beneficios que se pueden mencionar son, aislamiento entre contenedores (a nivel de proceso, vía namespaces+cgroups), facilidad de despliegue y escalado (deployment), e independencia (administrar o romper un contenedor no afecta a los demás)

### Ejercicio 2:​ ¿Qué es una imagen? ¿Y un contenedor? ¿Cuál es la principal diferencia entre ambos?

**Una imagen** es un **template (modelo) de solo lectura** que contiene **todas las instrucciones y archivos necesarios para construír un contenedor** (aplicación + binarios, librerías y dependencias). Es estática, no se ejecuta, es la "plantilla" a partir de la cual se crean los contenedores. Una imagen puede **basarse en otras** formando una cadena de capas

**Un contenedor** es una **instancia en ejecución de ina imagen**. Es lo que realmente corre, cuando arrancás una imagen, se crea un contenedor, que es un proceso (o conjunto de procesos) aislados ejecutándose sobre el host

La principal diferencia entre ambos, es que la **imagen es estática**, un template de solo lectura, mientras que el **contenedor** es una imagen **en ejecución**

>[!NOTE]
> La analogía de programación orientada a objetos: la imagen es como una clase y el contenedor es como un objeto/instancia de esa clase. De una misma clase (imagen) podés crear varios objetos (contenedores), cada uno corriendo por su cuenta.

>[!NOTE]
> La imagen es solo lectura, cuando se crea un contenedor, Docker le agrega encima una capa de escritura (writable layer) propia, donde el contenedor guarda sus cambios sin modificar la imagen original 

### Ejercicio 3:​ ¿Qué es Union Filesystem? ¿Cómo lo utiliza Docker?

Es un mecanismo de montaje (no un filesystem nuevo en si) que permite que varios directorios se monten en el mismo punto de montaje y aparezcan como un único . Es decir, fusiona (de ahí union) varias capas de directorios en una sola vista unificada

- Las **capas inferiores** son de **solo lectura**
- La **capa superior** es de **escritura**

Docker construye las **imágenes como una pila de capas**, y usa Union Filesystem para presentarlas como un solo sistema de archivos al contenedor :
- Cada image está compuesta por **varias capas montadas una sobre otra**, donde **cada capa es un conjunto de diferencias respecto de la capa previa**.
- Todas las capas de la imagen son de **solo lectura**. **Solo la última capa**, la del contenedor, es de **lectura y escritura**
- Las capas de solo lectura **se pueden utilizar entre distintas imágenes** (ahorra espacio y acelera descargas)

El proceso:
1. Cada capa que se descarga se extrae en un directorio del filesystem del host.
2. Al ejecutar un contenedor desde una imagen, se genera un union-filesystem apilando esas capas una sobre otra.
3. Usando chroot, se establece ese union-filesystem como el directorio raíz del contenedor.
4. Se crea un directorio nuevo (capa escribible) para ese contenedor, donde guarda los cambios que haga en ejecución.

>[!NOTE]
> Por eso se puede correr muchos contenedores a partir de las mismas capas de solo lectura. Cada uno solo agrega su propia capa escribible encima, sin tocar ni duplicar las capas compartidas. Y por eso la imagen es inmutable, los cambios del contenedor viven en su capa R/W, no en la imagen.

### Ejercicio 4:​ ¿Qué rango de direcciones IP utilizan los contenedores cuando se crean? ¿De dónde la obtiene?

Por defecto, al crear un contenedor, Docker lo conecta a su **red bridge por defecto** (llamada bridge), que usa el rango `172.17.0.0/16`. Es decir, los contenedores reciben direcciones del estilo `172.17.0.2`, `172.17.0.3`, etc.

La dirección `172.17.0.1` es el gateway, que corresponde a la interfaz virtual docker0 que Docker crea en el host (el "puente" entre los contenedores y la red real).
Ese rango pertenece al bloque de IPs privadas (`172.16.0.0/12`), no son IPs públicas/ruteables en internet.

**De dónde la obtiene**:
La IP se la asigna el **propio Docker**, mediante su componente de gestión de direcciones llamado **IPAM** (IP Address Management). Cuando se crea el contenedor:
- Docker toma la **siguiente IP libre** dentro del rango de la red a la que se conecta (por defecto `172.17.0.0/16`).
- Se la asigna a la interfaz de red virtual del contenedor.

>[!NOTE]
> Los contenedores tienen networking habilitado por defecto, pueden conectarse a varias redes, y usan los mismos servidores DNS que el host (aunque se pueden modificar).

### Ejercicio 5:​ ¿De qué manera puede lograrse que las datos sean persistentes en Docker? ¿Qué dos maneras hay de hacerlo? ¿Cuáles son las diferencias entre ellas?

Los archivos que un contenedor crea se guardan en su capa escribible, que vive junto con el contenedor. Por esto, cuando el contenedor se destruye, esos datos se pierden. Para que los datos persistan más allá de la vida del contenedor, hay que almacenarlos en el host (fuera de la capa escribible) y montarlos en el contenedor.

**Dos maneras**:
1. **Volumnes (Volúmenes)**
   - Se almacenan en una parte del filesystem administrada por Docker (por defecto en `/var/lib/docker/volumes`)
   - Es la opción recomendada
   - Ofrecen mejor portabilidad entre sistemas
2. **Bind Mounts**
   - Pueden estar en cualquier parte del flesystem del host
   - Pueden ser modificados por procesos que no son Docker

La diferencias son, La portabilidad, mejor en Volumens ya que están desacoplados de la estructura del host a diferencia de Bind Mounts que estan atados a una ruta específica dle host. Y quien adiministra la ubicación, que en volumes estan pensados para ser manejados por Docker y los Bind Mounts, en cambio, pueden ser modificados por procesos ajenos a Docker 