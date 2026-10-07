# Infograma: chroot, cgroups y Namespaces (base de contenedores)

> Los **3 mecanismos del kernel de Linux** que, combinados, hacen posible un contenedor:
> **chroot** aísla el *filesystem* · **namespaces** aíslan la *vista* de recursos · **cgroups** *limitan* el consumo.

---

## chroot (Service Isolation)

- **Cambia el directorio raíz (`/`) aparente** de un proceso (y de sus hijos). UNIX v7, 1979.
- Aislamiento **básico del filesystem**: el proceso no puede ver/acceder archivos ni comandos **fuera** de ese directorio. Al entorno se lo llama **jail chroot**.
- **Docker** lo usa para fijar el **union-fs** como raíz del contenedor.
- Por sí solo NO aísla procesos, red, etc. (para eso → namespaces).

```bash
chroot /new-root-dir comando
```

---

## CGROUPS (Control Groups)

> Característica del kernel que organiza procesos en **grupos jerárquicos** para **limitar, priorizar, contabilizar y controlar** el uso de recursos (CPU, memoria, E/S, red).

**4 funcionalidades** (NO solo limitación):
- **Limitación (Resource Limiting):** un grupo no puede exceder el uso de un recurso.
- **Priorización:** un grupo obtiene prioridad en el uso de recursos.
- **Accounting:** mide/monitorea el uso (estadísticas, billing).
- **Control:** freezar y reiniciar un grupo de procesos.

**Conceptos:**
- **Controlador / subsistema:** componente del kernel por recurso (`cpu`, `memory`, `blkio`/`io`, `cpuset`, `pids`...).
- **Jerarquía:** árbol de cgroups (cada cgroup = un directorio en el pseudo-filesystem cgroup).
- Un proceso **NO necesita ser modificado** para agregarse a un cgroup. Los procesos **desconocen** los límites.
- Un proceso creado por **`fork` pertenece al MISMO cgroup que el padre** (se hereda).
- Los **límites de un cgroup hijo NO pueden superar** los del padre.

**Receta: limitar la CPU de un proceso al 80%:**
1. Crear un cgroup en el controlador **`cpu`**.
2. Escribir la **cuota** (quota/period) correspondiente al 80%.
3. Agregar el **PID** del proceso al cgroup (`cgroup.procs`).

### Tabla: cgroups v1 vs v2

| Aspecto | **v1** | **v2** |
|---|---|---|
| Jerarquías | **Múltiples** (una por controlador) | **Única / unificada** |
| Montar controlador particular | **Sí** se puede | **No** (todos en la jerarquía única) |
| Pertenencia de un proceso | A **un** cgroup **por jerarquía** (varias jerarquías a la vez) | A **un solo** cgroup en toda la jerarquía |
| ¿Procesos en cgroups internos? | Permitidos | Solo en cgroups **sin hijos (hojas)**, salvo el **root** (*no internal process constraint*) |
| Desmontar un controlador | Solo si **no tiene cgroups hijos** | — |

> **Coexistencia:** ambas versiones **pueden estar montadas a la vez** en un sistema; lo que NO se puede es montar **el mismo controlador** en v1 y v2 simultáneamente.

---

## NAMESPACES

> Dan a un proceso una **vista aislada** de un recurso global del sistema: el proceso "cree" tener su propia instancia. Un proceso está en **un namespace de cada tipo** a la vez; un hijo **hereda** los del padre.

### Tabla: tipos de namespace

| Namespace | Flag | Qué aísla |
|---|---|---|
| **PID** | `CLONE_NEWPID` | Árbol de PIDs propio; el 1er proceso es **PID 1 (init)** del namespace |
| **NET** | `CLONE_NEWNET` | Interfaces de red, pilas, IPs, puertos |
| **MNT / Mount** | `CLONE_NEWNS` | Puntos de montaje (tabla de montajes propia) |
| **UTS** | `CLONE_NEWUTS` | Hostname y nombre de dominio |
| **IPC** | `CLONE_NEWIPC` | System V IPC, colas de mensajes POSIX |
| **USER** | `CLONE_NEWUSER` | Mapeo de UIDs/GIDs → **root dentro ≠ root host** |
| **Cgroup** | `CLONE_NEWCGROUP` | cgroup root directory |
| **Time** | `CLONE_NEWTIME` | Offset del clock por namespace |

**Syscalls:** `clone()` (crea proceso + namespace), `unshare()` (mueve el proceso actual a uno nuevo), `setns()` (lo une a uno existente).

> **PID namespace → doble PID:** un proceso `mi_proceso` tiene **PID 1** dentro del contenedor y un **PID alto** real en el host. Desde el host se ven TODOS los procesos de los contenedores; al revés NO.

---

## ⚠️ Trampas típicas de parcial

- **"¿Qué mecanismo del kernel limita el uso de CPU de un proceso al 80%?"** → **CGROUPS** (controlador `cpu`, cuota).
- "cgroups proveen limitación pero **NO priorización**" → **FALSO** (proveen **ambas**: priorización + limitación).
- "Una vez agregado a un cgroup, un proceso **no puede moverse** a otro" → **FALSO**.
- "Los procesos **deben ser modificados** para incorporarse a un cgroup" → **FALSO**.
- "Un proceso creado por `fork` **NO** pertenece al cgroup del padre" → **FALSO** (sí pertenece, lo hereda).
- **v1:** "están organizados jerárquicamente" → **V**. "Cada proceso pertenece a una sola jerarquía / un cgroup por jerarquía" → **V**. "Se puede montar un controlador en particular" → **V**. "Un controlador solo se desmonta si no tiene cgroups hijos" → **V**. "Una jerarquía/controlador no puede estar en v1 y v2 a la vez" → **V**.
- v1: "**solo existe una jerarquía** en todo el sistema" → **FALSO** (eso es **v2**).
- v1: "dentro de una jerarquía un proceso puede estar en **varios cgroups** a la vez" → **FALSO** (solo uno por jerarquía).
- **v2:** "los procesos deben agregarse a cgroups **sin hijos (hojas)**, salvo el root" → **V**.
- "**No es posible** tener las dos versiones de cgroups montadas simultáneamente" → **FALSO** (sí se puede; lo que no, es el mismo controlador en ambas).
- "Un proceso tiene **distinto PID** dentro del contenedor y en el host" → **V** (por el **PID namespace**).
