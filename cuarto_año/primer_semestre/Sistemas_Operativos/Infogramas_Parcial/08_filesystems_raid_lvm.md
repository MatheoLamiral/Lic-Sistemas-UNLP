# Infograma de Repaso: File Systems, RAID y LVM

> **Tema clave del parcial (UNLP - Sistemas Operativos).** Denso pero conciso.
> *Nota: el PDF de cátedra `07_Seguridad_Transparencia_1.pdf` cubre solo Protección y Seguridad (dominios, matriz de acceso, ACL, capacidades, buffer overflow). El contenido de File Systems / RAID / LVM no está en esa teoría, por lo que este infograma se arma con el material estándar de la materia.*

---

## 1. File Systems: conceptos base

Un **file system (FS)** organiza cómo se almacenan, nombran y recuperan los datos en un dispositivo.

- **Una partición debe tener un FS definido para poder ser accedida.** Sin FS no se puede montar ni leer/escribir.
- El FS administra el espacio mediante **bloques** y describe cada archivo con un **inodo**.
- El **nombre** del archivo NO vive en el inodo: vive en la **entrada de directorio** (que asocia nombre -> número de inodo).

### INODO (i-nodo)
Estructura que guarda los **METADATOS** de un archivo:

- Permisos (rwx), **dueño** (UID) y grupo (GID)
- **Tamaño** del archivo
- **Fechas**: acceso (atime), modificación (mtime), cambio de metadatos (ctime); en Ext4 también **creación** (crtime)
- **Punteros a los bloques de datos** (directos, indirectos, doble/triple indirecto)
- **Contador de hard links** (link count)

> **NO contiene el NOMBRE del archivo.** El nombre está en el directorio.
> Se puede montar con **`noatime`** para no actualizar la fecha de acceso en cada lectura (mejora rendimiento).

### BLOQUE
- Unidad **mínima de almacenamiento** de datos del FS.
- Su **tamaño se elige al crear el FS** (ej. 1K, 2K, 4K) y **NO se puede cambiar dinámicamente** después.

### EXTENT
- Conjunto de **bloques contiguos** descritos como un **rango** (`inicio + longitud`) en vez de bloque por bloque.
- Ventaja: **menos metadatos** y mejor rendimiento para **archivos grandes**.
- Usado por Ext4, XFS, BTRFS.

---

## 2. Tipos de File System

### EXT2 / EXT3 / EXT4
- Dividen el FS en **GRUPOS DE BLOQUES** (block groups).
- El **SUPERBLOQUE** (info global del FS) está **REPLICADO** en varios grupos de bloques (redundancia ante corrupción).
- **Ext2**: SIN journaling.
- **Ext3**: agrega **journaling**.
- **Ext4**: usa **extents**, journaling, y **SÍ guarda fecha de creación**; soporta volúmenes y archivos más grandes.

### JOURNALING
- Es un **log/registro** donde se anotan las operaciones **ANTES** de aplicarlas al FS.
- Permite **recuperar el FS** a un estado consistente tras un corte de energía o caída.
- **TRAMPA:** NO almacena "todas las operaciones que se realizan sobre un archivo"; registra las operaciones de metadatos/transacciones pendientes para recuperación.

### XFS
- Los **inodos se asignan DINÁMICAMENTE** (no hay tabla fija reservada al crear el FS).
- Alto rendimiento, usa extents, journaling.
- **NO se puede REDUCIR / achicar un FS XFS**: solo se puede **CRECER** (extender).

### BTRFS
- Usa **COPY-ON-WRITE (CoW)**: al modificar un dato **NO sobrescribe** el bloque original; escribe en un **bloque nuevo** y actualiza los punteros -> **snapshots eficientes** y baratos.
- Soporta **SUBVOLÚMENES** (raíces de árbol de archivos independientes dentro del mismo FS).
- En un subvolumen **NO se puede definir un tipo de FS distinto a BTRFS**.
- Para **montar un subvolumen que ocupa más de una partición** basta indicar **UNA sola** de esas particiones.
- Soporta RAID interno, checksums, compresión.

---

## 3. Links (enlaces)

| Característica | HARD LINK (enlace duro) | LINK SIMBÓLICO (soft / symlink) |
|---|---|---|
| Apunta a... | el **mismo INODO** que el original | una **RUTA / nombre** del archivo |
| ¿Consume inodo nuevo? | **NO** (comparte el inodo) | **SÍ** (tiene su propio inodo) |
| Si se borra el original | **SIGUE funcionando** (los datos viven hasta que link count = 0) | **Queda roto**: NO puede acceder a los datos |
| ¿Cruza particiones? | **NO** | **SÍ** |
| ¿Cruza FS distintos? | NO | SÍ |

**Clave del inodo:** el inodo (y sus datos) se elimina recién cuando su **contador de links llega a 0**. Por eso un hard link mantiene vivos los datos aunque borres el nombre original.

---

## 4. RAID (Redundant Array of Independent Disks)

Combina varios discos físicos en una unidad lógica para mejorar **velocidad**, **capacidad** y/o **redundancia**.

- **Striping**: reparte los datos en varios discos (paralelismo -> velocidad).
- **Mirroring**: copia idéntica de los datos en otro disco (redundancia).
- **Paridad**: información calculada que permite **reconstruir** datos ante un fallo.

### Tabla de niveles RAID

| Nivel | Striping | Paridad | Redundancia | Capacidad útil | Tolera fallo de |
|---|---|---|---|---|---|
| **RAID 0** | SÍ | NO | **NO** | Suma de todos (100%) | **0 discos** (si falla 1, se pierde todo) |
| **RAID 1** | **NO** | **NO** | SÍ (espejo) | La de **1 disco** (50% con 2) | 1 disco |
| **RAID 4** | SÍ | **Dedicada** (1 disco) | SÍ | N-1 discos | 1 disco |
| **RAID 5** | SÍ | **Distribuida** entre todos | SÍ | **N-1 discos** | **1 disco** |
| **RAID 6** | SÍ | **Doble** distribuida | SÍ | N-2 discos | **2 discos** |

### Cálculos típicos de parcial
- **RAID 5 con 5 discos de 1 TB** -> capacidad útil = **(N-1) = 4 TB**. Tolera el fallo de **1** disco.
- **Discos de distinto tamaño:** el RAID se **limita al disco más chico**. Ej.: discos de 1, 2 y 3 GB -> el array usa 3 x 1 GB efectivos; en RAID 5 la capacidad útil sería **2 GB** (uno se va en paridad).

### Otros conceptos
- **Chunk size**: tamaño del bloque de striping (cuánto se escribe en un disco antes de pasar al siguiente). **NO depende de la cantidad de discos.**
- **DDP (Dynamic Disk Pool)**: distribuye datos, paridad y repuesto (*spare*) sobre **todos** los discos de un *pool*; reconstrucción más rápida. **NO** funciona como "11 discos fijos reservando 2".

---

## 5. LVM (Logical Volume Manager)

Capa de abstracción sobre los discos físicos que da **flexibilidad** frente al particionado clásico: permite **extender un FS a través de DIFERENTES particiones e incluso discos rígidos distintos**.

### Jerarquía LVM

```
   Discos / Particiones físicas
            |
            v
   PV  (Physical Volume)      <- partición o disco inicializado para LVM
            |
            v
   VG  (Volume Group)         <- pool que agrupa uno o varios PV; define el tamaño del EXTENT
            |
            v
   LV  (Logical Volume)       <- volumen lógico sobre el que se crea el FS y se monta
```

`PV` -> `VG` -> `LV`

### Reglas clave
- El **tamaño de un LV** es **siempre MÚLTIPLO del tamaño del EXTENT** definido en el Volume Group.
- Un LV puede **abarcar varios discos**: no está limitado al espacio de un único disco físico.

### Orden de operaciones (¡el orden importa!)
- **EXTENDER (agrandar):** primero el **LV** y luego el **File System**.
- **ACHICAR (reducir):** primero el **File System** y luego el **LV**.
  - (Mnemotecnia: para crecer, primero el contenedor; para achicar, primero el contenido, así no se pierden datos.)

### Snapshots LVM
- Usan **COPY-ON-WRITE (CoW)**.
- **Al crear el snapshot NO se copian los datos** ni metadatos del LV original: se copian **a medida que el LV original se modifica** (solo los bloques que cambian).
- El **espacio del snapshot CRECE** a medida que hay modificaciones en el LV original.
- **NO se eliminan solos**: hay que borrarlos manualmente (si se llena, se invalidan).

---

## ⚠️ Trampas típicas de parcial

| Afirmación | V/F | Por qué |
|---|---|---|
| "RAID 1 provee striping y paridad distribuida" | **F** | RAID 1 es **mirroring**, sin striping ni paridad |
| "¿En qué nivel de RAID NO existe striping?" | **RAID 1** | Es espejado puro |
| "RAID 5 con 5 discos de 1 TB -> capacidad útil" | **4 TB** | Regla (N-1) |
| "¿Cuántos discos pueden fallar en RAID 5 sin pérdida?" | **1** | RAID 6 tolera 2 |
| "El chunk size depende de la cantidad de discos" | **F** | Es independiente de la cantidad de discos |
| "DDP usa mínimo 11 discos de los cuales 2 se reservan" | **F** | Distribuye datos/paridad/spare en un pool dinámico |
| "El nombre del archivo está en el inodo" | **F** | El nombre está en el **directorio**; el inodo guarda metadatos |
| "Cada vez que se crea un hard-link se usa un nuevo inodo" | **F** | El hard link **comparte** el inodo |
| "Si se elimina un symlink, también se elimina el archivo apuntado" | **F** | Borrar el symlink no afecta al original |
| "Si se elimina el archivo original, el symlink no puede acceder a los datos" | **V** | El symlink apunta a una ruta -> queda roto |
| "En XFS los inodos se asignan dinámicamente pero NO se puede reducir el FS" | **V** | XFS solo crece |
| "¿En qué FS no se puede disminuir el tamaño?" | **XFS** | Solo extensión |
| "El journaling es un log que almacena TODAS las operaciones sobre un archivo" | **F** | Registra operaciones **antes** de aplicarlas, para recuperación |
| "En BTRFS no se puede definir en un subvolumen un FS distinto a BTRFS" | **V** | El subvolumen es siempre BTRFS |
| "Para montar un subvolumen que ocupa más de una partición basta indicar una sola partición" | **V** | LVM/BTRFS resuelven el resto |
| "El tamaño de un LV siempre es múltiplo del extent del VG" | **V** | Por definición de LVM |
| "Un LV solo se puede extender si hay espacio en el disco físico donde está definido" | **F** | LVM puede abarcar varios discos/particiones |
| "Con LVM se puede extender un FS a través de diferentes particiones e incluso discos" | **V** | Es su principal ventaja |
| "Para achicar un LV: primero el FS y luego el LV" | **V** | Para extender, al revés |
| "Los snapshots LVM usan CoW" | **V** | Copy-on-write |
| "El espacio del snapshot se incrementa al modificar datos del LV original" | **V** | Solo se copian los bloques que cambian |
| "Al crear el snapshot se copian metadatos y datos del LV original" | **F** | No se copia nada al crearlo |
| "Una partición debe tener un FS definido para poder ser accedida" | **V** | Sin FS no se monta |
