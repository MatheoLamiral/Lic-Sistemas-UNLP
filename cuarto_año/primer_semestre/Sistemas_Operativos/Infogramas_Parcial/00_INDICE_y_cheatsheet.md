# 🎯 Repaso Parcial SO — Índice + Cheatsheet Maestro

> **Alcance:** Prácticas 1–5 · Teorías 1–10. Estilo del parcial: preguntas conceptuales cortas, V/F con justificación y multiple-choice (a veces "A y C", "ninguna", "todas").

## 📂 Infogramas
1. [01 – Kernel y compilación](01_kernel_y_compilacion.md)
2. [02 – Módulos, drivers y syscalls](02_modulos_drivers_syscalls.md)
3. [03 – Threads (ULT/KLT)](03_threads.md)
4. [04 – Virtualización](04_virtualizacion.md)
5. [05 – cgroups y namespaces](05_cgroups_namespaces.md)
6. [06 – Docker](06_docker.md)
7. [07 – Seguridad y permisos](07_seguridad_y_permisos.md)
8. [08 – File Systems, RAID y LVM](08_filesystems_raid_lvm.md) ⭐ *muy preguntado*
9. [09 – Multiprocesadores](09_multiprocesadores.md)
10. [10 – Deadlocks](10_deadlocks.md)

---

## ⚡ Cheatsheet — respuestas de alto rendimiento (lo que más cae)

### Kernel
- **Funciones del kernel (5):** memoria principal · CPU · procesos · E/S · comunicación/concurrencia.
- **Monolítico-híbrido** = todo linkeado en una imagen **PERO** carga/descarga módulos en runtime.
- **Portable** porque su **código C se modifica fácil** para otras arquitecturas (NO porque el binario corra en cualquiera).
- **7 pasos compilación:** 1 obtener fuente → 2 preparar árbol → 3 configurar → 4 construir + instalar módulos → 5 reubicar kernel + crear initrd → 6 gestor de arranque (GRUB) → 7 reiniciar y probar.
- Reconfigurar GRUB = **actualizar el menú** con el nuevo kernel (no reinstala el binario del gestor).
- **initramfs:** FS temporal en RAM con módulos/drivers para montar el root real; **puede no ser necesario** si todo es built-in.

### Módulos / Drivers / Syscalls
- **Módulo:** cargable/descargable en runtime (insmod/rmmod/modprobe/modinfo), en **/lib/modules**, corre en **modo kernel/supervisor**. NO implementa syscalls dinámicas.
- **Driver = se implementa como un MÓDULO** (no servicio, no syscall, no kthread).
- `register_chrdev()` → registra char device, **solo en espacio kernel**, asocia **major + file_operations**.
- **Major** = identifica el **driver**; **Minor** = identifica el **dispositivo** concreto.
- **/dev:** char (`c`, byte a byte) vs block (`b`, bloques, acceso aleatorio).
- **/proc:** no ocupa disco, archivos tamaño 0, interfaz al kernel; **módulos cargables también** pueden crear entradas (no solo built-in).
- **Syscall:** se define **en el kernel** (no en libc, no en módulos), **identificada por un número**, adjuntada **estática en compilación**, agregada en la **tabla de syscalls + número único**. **libc = wrapper**. **strace** las monitorea.
- **3 file descriptors:** 0=stdin, 1=stdout, 2=stderr.

### Threads
- **ULT** → planifica la **biblioteca** (usuario); kernel ve 1 proceso; **sin paralelismo real**.
- **KLT** → planifica el **kernel**; **sí paralelismo real** (varios cores).
- **fork sin exec:** hijo = copia del padre, mismo programa, **PID distinto**, hereda descriptores.

### Virtualización
- **Hypervisor Tipo 1** = bare-metal (sobre HW). **Tipo 2** = sobre un SO anfitrión.
- **Paravirtualización** = **se modifica el kernel del guest** (mejor rendimiento) → no sirve para Windows cerrado.
- **Binary translation** = guest NO modificado.
- **LXC/containers** = **mismo kernel** que el host, sin hypervisor.

### cgroups / namespaces
- **cgroups** = **limitan Y priorizan** recursos, jerárquicos. (limitar CPU 80% → controlador cpu + cuota).
- Proceso por **fork** queda en el **mismo cgroup** del padre. No se modifica el proceso para meterlo en un cgroup.
- **v1:** múltiples jerarquías (1 por controlador), proceso en 1 cgroup por jerarquía. **v2:** jerarquía única, procesos solo en **hojas** (salvo root).
- **PID namespace** → mismo proceso tiene PID 1 dentro del container y PID real en el host.

### Docker
- **Imagen** = molde solo-lectura (no se ejecuta) → varios contenedores. **Contenedor** = instancia en ejecución.
- Docker usa del kernel: **chroot + namespaces + cgroups**. Sin hypervisor.
- **Union FS:** capas read-only (imagen) + 1 capa escribible (container); solo la última se modifica.
- **Dockerfile** construye **1 imagen**; **compose** orquesta **varios contenedores** (declarativo).
- **Persistencia:** **volumes** (gestionados por Docker, portables) vs **bind mounts** (ruta del host elegida por el usuario).

### Seguridad / permisos
- **ASLR** = aleatoriza el espacio de memoria. Linux lo da para **usuario Y kernel (KASLR)**.
- **UMASK** = permisos por defecto al crear. **setuid/setgid/sticky** = permisos especiales.
- **sticky bit** en dir → solo el dueño del archivo (o root) borra/renombra (ej /tmp).
- **/etc/shadow** = solo root.

### File Systems / RAID / LVM ⭐
- **Inodo** = metadatos (NO el **nombre**, que está en el directorio).
- **Hard link** comparte inodo (NO consume inodo nuevo); **symlink** consume inodo y se rompe si borrás el original.
- **XFS** = no se puede **achicar** (solo crecer); inodos dinámicos.
- **BTRFS** = Copy-on-Write, subvolúmenes (solo tipo BTRFS).
- **Journaling** = log para recuperación (NO "todas las operaciones sobre un archivo").
- **RAID 0** striping sin redundancia · **RAID 1** mirror (sin striping/paridad) · **RAID 5** striping + paridad distribuida, tolera **1 fallo**, útil **(N−1)** discos (5×1TB → **4TB**).
- **¿RAID sin striping?** → **RAID 1**.
- **LVM:** PV→VG→LV; extiende FS por varias particiones/discos; tamaño LV = múltiplo del extent; **achicar = primero FS, luego LV** (extender al revés); **snapshots = CoW**, crecen con las modificaciones del original.

### Deadlocks
- **4 condiciones (Coffman, las 4 a la vez):** exclusión mutua · retención y espera · no apropiación · espera circular.
- Manejo: prevención · evitación (**banquero**) · detección+recuperación · avestruz.

---
*Generado para repaso intensivo. Verificá siempre contra la teoría oficial ante cualquier duda.*
