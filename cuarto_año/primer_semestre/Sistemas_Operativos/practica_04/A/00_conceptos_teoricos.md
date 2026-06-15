# Conceptos teóricos

## Ejercicio 1:​ Defina virtualización. Investigue cuál fue la primera implementación que se realizó.

La virtualización es una técnica que permite **realizar una abstracción de los recursos de una computadora**. Es una capa que **desacopla el hardware físico del software**, ocultando detalles técnicos mediante encapsulación, y permite que una sola máquina física haga el trabajo de varias compartiendo sus recursos

- El primer sistema fue **CP-40**, desarrollado por el **IBM Cambridge Scientific Center**, que corría sobre un mainframe IBM System/360 Model 67. **Introdujo el concepto de máquina virtual**, mediante un programa de control (Control Program, el precursor del hypervisor) creaba varias copias virtuales del hardware, de modo que cada usuario tenía la ilusión de disponer de su propia máquina completa

## Ejercicio 2:​ ¿Qué diferencia existe entre virtualización y emulación?

La diferencia central está en cómo se ejecutan las instrucciones y en si el hardware "imitado" es de la misma arquitectura que el físico o de otra distinta.

- Virtualización
  - SO guest corre sobre la **misma arquitectura** que el host, por eso la mayoría de las instrucciones se ejecutan **directamente sobre la CPU física**, sin intermediaros
  - Muy **poco overheadt**, performance **casi nativa**
  - **No se puede** correr una **arquitectura distinta a la del host**
- Emulación
  - Un programa (emulador) **simula por software la totalidad del hardware**, **traduciendo/interpretando cada instrucción** del gest. Por eso **puede ejecutar una arquitectura diferente** a la del host
  - Mucho **más lento**, porque **cada instrucción pasa por software** en vez de correr directo en la CPU

>[!NOTE]
> Virtualizar es repartir el hardware real para correr SO de la misma arquitectura ejecutando casi todo directo en la CPU (rápido). Emular es simular por software un hardware completo, pudiendo ser de otra arquitectura, traduciendo cada instrucción (lento pero flexible).

## Ejercicio 3:​ Investigue el concepto de hypervisor y responda:

### a. ¿Qué es un hypervisor?

Un hypervisor (también llamado VMM, Virtual Machine Monitor) es el programa que corre sobre el hardware para implementar las máquinas virtuales. Es la **capa que está entre el hardware físico y las VMs**, y se encarga de:

- **Crear las máquinas virtuales** (el hardware virtual de cada guest).
- Controlar los **recursos físicos** y **planificar** (schedulear) la **ejecución** de los guests, repartiendo CPU, RAM, etc.
- **Aislar** cada guest de los demás.

Cómo funciona internamente:

- El **VMM se ejecuta en modo supervisor** (privilegiado), mientras que el **software guest corre en modo usuario**.
- Cuando un guest intenta ejecutar una instrucción privilegiada, se genera un **trap al VMM**, que la **interpreta/emula y devuelve el control al guest**. Así el VMM **mantiene siempre el control del hardware**. 

### b. ¿Qué beneficios traen los hypervisors? ¿Cómo se clasifican?

Beneficios:
- Mejor aprovechamiento del hardware
- Correr varios SO simultáneamente
- Aislamiento/seguridad
- Aplicaciones heredadas (legacy)
- Facilidad de migración, backup y clonado
- Ahorro de energía

- Se clasifican en 2 tipos:
  - Tipo 1/Bare-metal
    - Corre directo sobre el hardware
    - Más rápido
    - Se usa tipicamente para servidores, data centers, etc.
  - Tipo 2/Hosted
    - Corre sobre un SO host ya instalado, como una aplicación más
    - Es más lento, ya que pasa por el SO host
    - Es más cómodo para uso personal/escritorio 

## Ejercicio 4:​ ¿Qué es la full virtualization? ¿Y la virtualización asistida por hardware?

**Full virtualization**:

Es el modo en el que se **virtualiza el hardware por completo**, de forma que el **SO guest corre sin ninguna modificación** (cree que está sobre hardware real).

- La ventaja es la **compatibilidad total**, corre cualquier SO sin tocarlo. 
- La desventaja es el **overhead de emular/interceptar**.

**Virtualización asistida por hardware**:

Es una mejora en la que el propio procesador trae **soporte para virtualización**, de modo que el hypervisor no tiene que emular ni traducir las instrucciones por software. El hardware se encarga de manejar las instrucciones privilegiadas del guest de forma eficiente. Se introduce un **nivel de privilegio extra para el hypervisor** (un "modo raíz" por debajo del SO guest), así el guest puede correr sin modificar y casi a velocidad nativa, sin necesidad de binary translation.

- La ventaja es la **mejora en la performance** sobre la full virtulaización (menos traps emulados, menos traducción), **manteniendo compatibilidad** (el guest no se modifica).

>[!NOTE]
> La full virtualization es el objetivo (correr un SO sin modificar). Lo que cambia es cómo se logra:
> - Por software: binary translation + emulación de instrucciones sensibles (más lento).
> - Asistida por hardware (VT-x/AMD-V): el procesador lo resuelve por hardware (más rápido).

## Ejercicio 5:​ ¿Qué implica la técnica binary translation? ¿Y trap-and-emulate?

**Trao-and-emulate**:

- Es el mecanismo clásico de virtualización
- El **SO guest corre en modo usuario**, mientras el **VMM/hypervisor corre en modo supervisor**.
- Mientras el guest ejecuta **instrucciones normales, corren directo en la CPU**.
- Cuando el guest intenta ejecutar una **instrucción privilegiada**, como esta en modo usuario, la CPU **genera una trap que transfiere el control al VMM**.
- El **VMM emula** esa instrucción (la ejecuta de forma controlada, como si el guest tuviera el hardware) y **devuelve** el control al guest

**Binary translation**:

Surge porque en la arquitectura **x86 clásica el trap-and-emulate puro no alcanzaba**. Había instrucciones **"sensibles" que NO eran privilegiadas**, es decir, que afectaban el estado del sistema pero **no generaban trap** al ejecutarse en modo usuario. Sin trap, el VMM no se enteraba, por lo que la virtualización fallaba. La solución de binary translation:
- El hypervisor **escanea el código del guest antes/durante la ejecución**, buscando esas instrucciones sensibles problemáticas.
- Las **reescribe/sustituye en tiempo de ejecución por llamadas seguras al VMM** (o por secuencias equivalentes que sí puede controlar).
- El resto del código se ejecuta sin tocar.

>[!NOTE]
> En resumen Trap-and-emulate espera que las instrucciones sensibles generen un trap y ahí las emula. Funciona si toda instrucción sensible es privilegiada (genera trap). El costo es bajo, solo las privilegiadas pasan por el VMM. Por otro lado, Binary translation, detecta y reescribe las instrucciones sensibles antes de que se ejecuten. Cubre las instrucciones sensibles de x86 que no generaban trap. El costo es mayor, ya que requiere analizar/reescribir código en runtime

## Ejercicio 6:​ Investigue el concepto de paravirtualización y responda:

### a. ¿Qué es la paravirtualización?

Es un modo de virtualización en el que el **SO guest está modificado** para "saber que está virtualizado" y **colaborar con el hypervisor**, en vez de creer que corre sobre hardware real

- SO guest modificado **ejecuta sobre un microkernel/hypervisor**.
- En lugar de ejecutar instrucciones privilegadas que haya que atrapar y emular, el guest **accede directamente a la API del hypervisor**(llamadas conocidas como hypercalls) para todas o ciertas instrucciones.
- Se **desacopla** la función del hypervisor y del VMM

### b. Mencione algún sistema que implemente paravirtualización.

- **Xen** (Universidad de Cambridge): es el ejemplo clásico, un hypervisor tipo 1/nativo que **soporta paravirtualización**.
- **KVM** también **soporta paravirtualización de algunos dispositivos mediante API** (paravirtualización parcial, p. ej. drivers virtio).

### c. ¿Qué beneficios trae con respecto al resto de los modos de virtualización?

- **Mejor performance**, al usar la API del hypervisor directamente, evita el overhead de atrapar y emular instrucciones (trap-and-emulate) o reescribir código (binary translation)
- Es un esquema **más eficiente** que la full virtualización por software, porque elimina gran parte de la intervención del VMM

>[!NOTE]
> A cambio de esto, soporta pocos SO, requiriendo modificar el SO guest, y no todos los SO permiten/tienen esas modificiaciones (por eso no se puede paravirtualizar cualquier sistema, a diferencia de la full virtualización)

## Ejercicio 7:​ Investigue sobre containers y responda:

### a. ¿Qué son?

Los contenedores son una **tecnología de virtualización liviana a nivel sistema operativo**, que permite ejecutar **múltiples sistemas aislados** (conjuntos de procesos) sobre un único host

- Las instancias corren en **espacio de usuario** y **comparten el mismo kernel** (el del SO base/host)
- **Desde adentro** parecen **máquinas virtuales** (cada uno con sus binarios, librerías, etc.), **desde afuera** son simplemente **procesos** normales del SO host
- **No necesitan un hypervisor** ni un SO guest completo
- Son **autocontenidos** (traen todo lo que necesitan), **aislados**, **independientes** y **portables**

### b. ¿Dependen del hardware subyacente?

**No dependen del hardware** en el sentido en que sí lo hacen las VMs, **no requieren extensiones de virtualización** (VT-x/AMD-V) ni emulan/virtualizan hardware. **Corren como procesos** comunes sobre el host. Pero **sí dependen del kernel del host** (que es lo que comparten).

No es posible ejecutar una instancia con un kernel distinto al del SO base (por ejemplo, no se puede correr un contenedor de Windows sobre un host Linux).

La dependencia no es del hardware, sino del kernel del host. Por eso son tan livianos (no recrean hardware), pero por eso mismo están atados al SO base.

### c. ¿Qué lo diferencia por sobre el resto de las tecnologías estudiadas?

La diferencia principal es que **comparten el kernel del host** en vez de virtualizar/emular hardware y correr un SO guest completo

### d. Investigue qué funcionalidades son necesarias para poder implementar containers.

Los contenedores se contruyen combinando tres funcionalidades del kernel de Linux:

1. **chroot** (asilamiento del sistema de archivos): cambia el directorio raíz que ve un proceso y sus hijos, limitando qué parte del filesystem pueden ver. Es la base histórica del aislamiento
2. **Namespaces** (aislamiento de recursos): le dan a cada contenedor su propia "vista" aislada de distintos recursos del sistema (PID, red, montajes, hostname, IPC, usuarios). Es lo que hace que in proceso dentro del contenedor crea que está solo en el sistema 
3. **Cgroups** (Control Groups, control de recursos): limitan y monitorean cuánto CPU, memoria, I/O, etc. puede usar cada grupo de procesos, evitando que un contenedor consuma todos los recursos del host 

>[!NOTE]
> En resumen, **chroot aísla el filesystem**, los **namespaces aíslan la "vista"** de los recursos, y los **cgroups limitan el consumo**. Esos tres mecanismos del kernel, combinados, son lo que hace posible un contenedor.