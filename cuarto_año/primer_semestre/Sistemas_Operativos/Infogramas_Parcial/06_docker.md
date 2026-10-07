# Infograma de Repaso: Docker y Contenedores

> Plataforma open-source para **empaquetar y ejecutar apps en contenedores livianos**. Trabaja a **nivel SO**, comparte el kernel del host y **NO usa hypervisor**.

---

## Imagen vs Contenedor

| | **Imagen** | **Contenedor** |
|---|---|---|
| **Qué es** | Template/molde de **solo lectura** | Instancia **en ejecución** de una imagen |
| **Contenido** | App + dependencias + librerías + instrucciones | Imagen + capa escribible propia |
| **Ejecución** | **NO se ejecuta** (es estática) | **SÍ se ejecuta** (proceso/s aislados) |
| **Relación** | De 1 imagen se crean **VARIOS** contenedores | Cada uno autónomo y aislado |
| **Analogía OOP** | Clase | Objeto/instancia |

- Una imagen puede **basarse en otras** (cadena de capas).
- Se puede generar una imagen **a partir de un contenedor** con `docker commit`.
- **Diferencia clave**: la imagen es solo lectura; el contenedor le agrega encima una **capa escribible**.

---

## Cómo lo provee el kernel (NO necesita hypervisor)

Docker corre en **espacio de usuario (Ring 3)** y **NO captura syscalls** (lo hace el kernel). SÍ requiere funcionalidades del kernel:

- **chroot**: cambia el **directorio raíz** del contenedor.
- **Namespaces**: vista **aislada** del sistema → `PID`, `Net`, `Mount(mnt)`, `UTS`, `IPC`, `User`.
- **Cgroups (Control Groups)**: **limitan/controlan recursos** (CPU, memoria, etc.).
- **Union Filesystem**: apila capas como un solo FS.

> El contenedor tiene sus propios filesystem, librerías, red, nombre... **excepto su propio kernel** (lo comparte con el host).

---

## Union Filesystem (overlay) y Capas

**Mecanismo de montaje** (no un FS nuevo): varios directorios montados en **un mismo punto** aparecen como **uno solo**.

- Capas **inferiores → solo lectura (read-only)**.
- Capa **superior → escritura (writable)**.
- Cada **imagen = varias capas apiladas**; cada capa guarda **solo las DIFERENCIAS** respecto de la anterior. **Todas las capas de la imagen son de solo lectura**.
- Las capas read-only se **reutilizan entre imágenes** (ahorra espacio/descargas).

**Al ejecutar un contenedor** (copy-on-write):
1. Docker **apila las capas read-only** de la imagen.
2. Con **chroot** establece ese union-FS como raíz del contenedor.
3. Agrega encima una **capa escribible propia** del contenedor.
4. Solo esa **última capa** puede modificarse → permite correr **muchos contenedores** sobre las **mismas capas compartidas**.

> Al borrar el contenedor se elimina su capa escribible; las inferiores quedan intactas.

---

## Containers vs VMs

| **Container** | **VM** |
|---|---|
| Comparte el **kernel del host** | SO **guest completo + kernel propio** |
| **Liviano y arranque rápido** | Pesada, arranque lento |
| Aislamiento a nivel de **proceso** | Aislamiento completo (HW virtual) |
| **NO necesita hypervisor** | **Requiere hypervisor** |

---

## Dockerfile vs docker-compose

| | **Dockerfile** | **docker-compose (compose.yaml)** |
|---|---|---|
| **Qué hace** | Instrucciones para **CONSTRUIR UNA imagen** (paso a paso) | Definición **DECLARATIVA** para levantar/**orquestar** una app de **VARIOS contenedores** |
| **Resultado** | Una **imagen** (1 pieza) | Conjunto de contenedores + redes + volúmenes |
| **Lenguaje** | Instrucciones (`FROM`, `RUN`, `COPY`, `CMD`...) | **YAML** (indentación, clave: valor) |
| **Comando** | `docker build` | `docker compose up` / `down` |

> **No son excluyentes**: compose puede usar `build:` apuntando a un Dockerfile. Cada instrucción del Dockerfile genera **una nueva capa**.

---

## Persistencia de datos (se guarda en el HOST)

Lo escrito en la capa del contenedor **se pierde** al destruirlo → para persistir hay que guardarlo en el host y montarlo.

| | **Volumes** (recomendado) | **Bind Mounts** |
|---|---|---|
| **Ubicación** | Gestionada por Docker en `/var/lib/docker/volumes` | **Cualquier ruta del host** elegida por el usuario |
| **Portabilidad** | Más portables, **desacoplados del host** | Atados a una ruta concreta |
| **Acceso externo** | Manejados por Docker | Pueden ser modificados por **procesos ajenos a Docker** |

---

## ⚠️ Trampas típicas de parcial

| Afirmación | Veredicto |
|---|---|
| "A partir de una imagen solo se puede generar un solo contenedor" | **FALSO** (varios) |
| "Docker necesita un hypervisor para ejecutarse" | **FALSO** (trabaja a nivel SO) |
| "Dockerfile es un archivo con instrucciones que permite crear un container" | **FALSO** (crea una **IMAGEN**, no un container) |
| "Cada imagen está compuesta por capas de las cuales solo la última puede ser modificada" | **VERDADERO** |
| "Docker usa namespaces, cgroups y union filesystems para proveer contenedores" | **VERDADERO** |
| "No es posible generar una imagen a partir de un container" | **FALSO** (sí, `docker commit`) |
| "Como trabaja en modo usuario no requiere ninguna funcionalidad del kernel" | **FALSO** (requiere chroot, namespaces, cgroups) |
| "Todo archivo que se agrega en un container automáticamente pasa a ser parte de la imagen" | **FALSO** (va a la **capa escribible** del container) |

> **Relación union-FS ↔ imágenes/contenedores**: capas **read-only** de la imagen + **capa escribible** del contenedor (copy-on-write).
