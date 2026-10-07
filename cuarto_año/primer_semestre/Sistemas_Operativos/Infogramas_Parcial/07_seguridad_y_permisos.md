# Infograma: Protección, Seguridad y Permisos en Linux

> Repaso denso para parcial de Sistemas Operativos (UNLP). **NO** cubre file systems, RAID ni LVM.

---

## 1. Protección vs Seguridad

| Concepto | Definición |
|---|---|
| **Protección** | **Mecanismos internos** del SO para controlar el acceso de **procesos/usuarios** a los recursos del sistema. Es el "cómo" técnico (los candados). |
| **Seguridad** | Concepto **más general**: defensa frente a **amenazas externas e internas**. Mide cuánto se puede confiar en que el sistema y sus datos mantienen su integridad. |

La **protección es una parte de la seguridad**.

### Políticas vs Mecanismos

- **Políticas (QUÉ):** definen qué se quiere hacer / qué está permitido. Decisión a alto nivel, **rara vez incluyen configuraciones**.
- **Mecanismos (CÓMO):** herramientas, configuraciones e implementaciones reales que hacen cumplir la política.
- Primero se define la **política**, después el mecanismo. Una misma política admite **varios mecanismos** → da **flexibilidad** (cambiar el mecanismo sin tocar la política).

### Qué garantiza la seguridad: la tríada **CIA**

- **Confidencialidad:** evitar la intercepción/lectura no autorizada de datos.
- **Integridad:** evitar la modificación no autorizada de datos.
- **Disponibilidad:** evitar la interrupción del servicio/recursos.

---

## 2. Permisos UNIX (rwx)

Cada archivo/directorio tiene **3 conjuntos** de permisos, uno por categoría:

| Categoría | Significado |
|---|---|
| **u** (user/owner) | El **dueño** del archivo |
| **g** (group) | El **grupo** del archivo |
| **o** (others) | Todos los **demás** |

Permisos: **r** (read=4), **w** (write=2), **x** (execute=1).

### Representación octal

Se suma por categoría. Ejemplo `rwxr-xr--`:
- owner `rwx` = 4+2+1 = **7**
- group `r-x` = 4+0+1 = **5**
- others `r--` = 4+0+0 = **4**
- → **754**

### Comandos

- **`chmod`** → cambia permisos (`chmod 754 f`, `chmod u+x f`).
- **`chown`** → cambia el **dueño** (`chown usuario f`).
- **`chgrp`** → cambia el **grupo** (`chgrp grupo f`).

> En UNIX el **dominio** de un proceso lo define el par **(UID, GID)**: determina a qué objetos accede y con qué derechos.

---

## 3. Permisos especiales (setuid, setgid, sticky)

Son un **4º dígito octal** que precede a los permisos normales (ej. `chmod 4755`).

| Permiso | Octal | Efecto sobre un **archivo (ejecutable)** | Efecto sobre un **directorio** |
|---|---|---|---|
| **setuid (SUID)** | **4** | El ejecutable corre con los privilegios del **DUEÑO del archivo**, no del usuario que lo lanza (ej. `passwd` corre como **root**). | (Generalmente sin efecto.) |
| **setgid (SGID)** | **2** | El ejecutable corre con los privilegios del **GRUPO** del archivo. | Los **archivos nuevos heredan el grupo del directorio** (no el del usuario que los crea). |
| **sticky bit** | **1** | (Sin efecto relevante hoy en ejecutables.) | Solo el **DUEÑO del archivo** (o el dueño del dir, o **root**) puede **renombrar/eliminar** sus archivos, aunque otros tengan permiso de escritura en el dir (ej. **`/tmp`**). |

> **setuid/setgid** implementan el **cambio de dominio dinámico** en UNIX: el proceso pasa al dominio del dueño/grupo justo cuando necesita más privilegio. En la salida de `ls -l` aparecen como **s** (en x) o **t** (sticky).

---

## 4. UMASK

- **Máscara** que define los permisos **por defecto** al crear archivos/directorios.
- Funciona por **resta**: se **quitan** sus bits de los permisos base.
  - Base archivos = **666**, base directorios = **777**.
  - Con `umask 022`: archivo → `666 - 022` = **644** ; directorio → `777 - 022` = **755**.
- Comando: **`umask`** (ver/establecer la máscara).

---

## 5. /etc/passwd vs /etc/shadow

| Archivo | Contiene | Permisos |
|---|---|---|
| **`/etc/passwd`** | Info de usuarios (login, UID, GID, home, shell). | **Legible por todos** (la contraseña NO está acá). |
| **`/etc/shadow`** | **Hashes de contraseñas** y políticas de expiración. | **Solo root** puede leerlo/modificarlo. |

---

## 6. ASLR (Address Space Layout Randomization)

- Mecanismo que **aleatoriza las direcciones** del espacio de memoria de un proceso (**stack, heap, librerías compartidas** y, si es PIE, el **código**) en cada ejecución.
- **Objetivo:** dificultar exploits de memoria (ej. buffer overflow / return-to-libc) que necesitan **direcciones fijas conocidas**. Si cambian, el atacante no puede predecirlas.
- **¿Linux lo provee para procesos de usuario?** → **SÍ**.
- **¿Y para el kernel?** → **SÍ**, mediante **KASLR** (Kernel ASLR), que aleatoriza la dirección base donde se carga el kernel al arrancar (mecanismo **separado**).
- Se controla con **`/proc/sys/kernel/randomize_va_space`**:
  - `0` = desactivado
  - `1` = parcial (stack, mmap/librerías, vdso)
  - `2` = completo (+ heap/brk) → **valor por defecto**

---

## 7. Explotación de errores (contexto)

- **Buffer overflow:** se escribe más allá del área de memoria reservada (C **no** chequea límites). Si se sobrescribe un valor sensible, puede encadenar código malicioso.
- **Shellcode:** código preparado para obtener los privilegios del programa atacado.
- ASLR y permisos especiales bien usados (POLA / mínimo privilegio) **mitigan** estos ataques.

---

## ⚠️ Trampas típicas de parcial

- **ASLR:** Linux lo provee para **procesos de usuario SÍ**, y para el **kernel también SÍ (KASLR)**. → **VERDADERO** para ambos.
- **"Mediante UMASK es posible indicar los permisos por default al crear un archivo/directorio"** → **VERDADERO**.
- **"El sticky-bit en un directorio indica que los archivos dentro solo pueden ser renombrados/eliminados por el dueño del archivo, el dueño del directorio o root"** → **VERDADERO**.
- **"En Linux, `/etc/shadow` solo puede ser modificado por root"** → **VERDADERO**.
- **"sticky-bit, setuid y setgid son permisos especiales"** → **VERDADERO**.
- Cuidado: **setuid** usa privilegios del **DUEÑO** del archivo (no del que lo ejecuta); **setgid en directorio** hereda **grupo** (no dueño).
- Cuidado: la contraseña **NO** está en `/etc/passwd` (legible por todos), sino en `/etc/shadow` (solo root).
