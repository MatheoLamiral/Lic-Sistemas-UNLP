# Virtualización — Infograma de Repaso (SO · UNLP)

## ¿Qué es virtualizar?

Técnica de **abstracción** de recursos: una capa que **desacopla el hardware físico** del software, oculta detalles por **encapsulación** y permite que **una máquina haga el trabajo de varias** compartiendo un mismo hardware.

- **Sin virtualizar:** un único SO controla todo el HW.
- **Virtualizado:** múltiples entornos/VMs aislados sobre el mismo HW.
- **Host:** SO anfitrión + capa de virtualización. **Guest:** lo que se simula (SO completo).

## ¿Por qué virtualizar?

- **Consolidación:** servidores subutilizados (HW ~10-18% → ~70% de uso).
- **Aislamiento:** entornos separados, probar apps inseguras, correr legacy.
- **Aprovechamiento del HW:** varios SO distintos en simultáneo, ahorro de energía (green IT).
- **Flexibilidad:** VMs encapsuladas en archivos → fácil backup, copia y **migración** entre servidores.

## Hypervisor / VMM

Programa que corre sobre el HW, implementa las VMs y controla recursos y planificación de los guests.

- VMM en **modo supervisor**; guest en **modo usuario**.
- Las **instrucciones privilegiadas** del guest generan **traps al VMM**, que las interpreta/emula.

### Tipo 1 vs Tipo 2

| | **Tipo 1 (bare-metal)** | **Tipo 2 (hosted)** |
|---|---|---|
| Dónde corre | **Directo sobre el hardware** | Como **aplicación sobre un SO anfitrión** |
| ¿SO anfitrión? | **No** (es el "SO base") | **Sí** |
| Rendimiento | Mayor | Menor (capa extra del host) |
| Uso típico | Servidores / data center | Escritorio / pruebas |
| Ejemplos | **ESXi, Xen, Hyper-V, KVM** | **VirtualBox, VMware Workstation** |

**Diferencia clave:** el tipo 1 NO necesita SO anfitrión (corre sobre el bare-metal); el tipo 2 sí.

## Técnicas de virtualización

### Full virtualization con Binary Translation
- El hypervisor **traduce/intercepta en tiempo de ejecución** las instrucciones privilegiadas del guest (busca bloques básicos y sustituye instrucciones sensibles por llamadas al VMM).
- El **SO guest NO se modifica** → no sabe que está virtualizado.
- Debe emular todo el HW → costo de performance.

### Paravirtualización
- El **kernel del SO guest SE MODIFICA**: reemplaza instrucciones privilegiadas por **hypercalls** (llamadas a la API del hypervisor) → **mejor rendimiento**.
- **Limitación:** no sirve para SO que **no se pueden modificar** (ej. Windows de código cerrado).

### Virtualización asistida por hardware
- Extensiones de CPU **Intel VT-x / AMD-V** que dan soporte directo a la virtualización (requiere flag habilitado en BIOS para VMs).

### Emulación
- Simula por software un **hardware/arquitectura completo**; puede correr **otra arquitectura** distinta a la real. Es la más **lenta** (ej. QEMU).

### Comparativa

| Técnica | ¿Modifica el guest? | Rendimiento | Nota |
|---|---|---|---|
| **Binary translation (full virt.)** | **No** | Medio | Traduce/intercepta instr. privilegiadas en runtime |
| **Paravirtualización** | **Sí (kernel modificado)** | Alto | Usa hypercalls; no sirve para SO cerrados |
| **Emulación** | No | **Bajo (lento)** | Puede simular otra arquitectura |

## Contenedores (LXC / Docker) — Virtualización a nivel SO

- **NO usan hypervisor**.
- **Usan el MISMO kernel que el SO base** (no instalan su propio kernel) → más livianos.
- Aíslan espacio de usuario mediante **namespaces** y **cgroups**.
- **No** pueden ejecutar un SO con kernel distinto al del host (no virtualizan Windows sobre Linux).
- A diferencia de las VMs: los **procesos del container SÍ aparecen como procesos en el host**.

---

## ⚠️ Trampas típicas de parcial

- "¿En cuál técnica se debe **modificar el kernel del guest** para mejorar rendimiento?" → **PARAVIRTUALIZACIÓN**.
- "En paravirtualización el SO guest NO se debe modificar" → **FALSO** (sí se modifica).
- "La paravirtualización permite virtualizar Windows sobre Linux" → **FALSO** (Windows no se puede modificar).
- LXC: "los containers usan el mismo kernel que el SO base" → **VERDADERO**. "usan su propio kernel" → **FALSO**.
- "Containers necesitan habilitar flag de virtualización en BIOS" → **FALSO**.
- "Los containers permiten virtualizar Windows" → **FALSO**.
- "Docker/containers necesitan un hypervisor tipo 2" → **FALSO**.
- "Cada container instala/ejecuta su propio kernel" → **FALSO**.
- "No es posible ejecutar un SO con kernel diferente al del SO base (containers)" → **VERDADERO**.
- En hypervisor tipo 1 / VMs, los **PIDs del guest NO aparecen como procesos en el anfitrión** (a diferencia de los containers).
