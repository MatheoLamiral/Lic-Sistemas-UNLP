# Introducción

## Ejercicio 1:​ Defina política y mecanismo.

**Política** (el qué): define **qué se quiere hacer** en base a los objetivos de seguridad,qué está permitido y qué no, quién puede acceder a qué. Es la **decisión** o el **objetivo**, a alto nivel. Rara vez incluye configuraciones concretas 

**Mecanismo** (el cómo): define cómo se logra esa política, son las herramientas, configuraciones e implementaciones reales que la hacen cumplir. Acá aparecen los detalles técnicos concretos

>[!NOTE]
> Es importante definir las políticas antes que los mecanísmos (primero se decide qué se quiere lograr, después cómo)

>[!NOTE]
> Una misma política puede implementarsecon distintos mecanismos. Esa separación es lo que le da flexibilidad al sistema, se puede cambiar el mecanismo sin cambiar la política

## Ejercicio 2:​ Defina objeto, dominio y right.

**Objeto**: es un **recurso del sistema** sobre el que se puede operar. Puede ser de **hardware** o de **software**. Cada objeto tiene un **identificador único** que permite referenciarlo. Los procesos pueden realizar un conjunto finito de operaciones sobre los objetos
**Right**(derecho): es la **autorización para efectuar una operación** sobre un objeto (p. ej. permiso de leer o escribir un archivo)
**Dominio**: es un **conjunto de pares** `(objeto, derecho)`. Cada par especifica un objeto y el **subconjutno de operaciones (derechos)** que se puede realizar sobre él. Define, entonces, **qué puede hacer** un proceso que se ejecuta dentro de ese dominio

>[!NOTE]
> Por ejemplo, el dominio D contiene el par `(archivo A, {read, write})`. Un proceso que corre dentro del dominio D puede leer y escribir el archivo A, pero no realizar otras operaciones que no estén en su conjunto de derechos.

## Ejercicio 3:​ Defina POLA (Principle of least authority).

**POLA (Principle of least authority)**, también conocido como **principio de mínimo privilegio** o **need-to-know**, establece que los **procesos (o usuarios) deben acceder únicamente a los objetos que necesitan, con los derechos que necesitan, para completar su tarea**. Ni más objetos, ni más permisos de los estrictamente necesarios.

La idea es **minimizar la "autoridad"** que tiene cada entidad. Si un proceso solo necesita leer un archivo, debería tener solo el derecho de lectura sobre ese archivo, y nada más

>[!NOTE]
> Aplicar POLA significa que el dominio de cada proceso debe ser lo más acotado posible (solo los pares `(objeto, derecho)` imprescindibles)

## Ejercicio 4:​ ¿Qué valores definen el dominio en UNIX?

En UNIX, el dominio de un proceso está definido por dos valores, el **UID (User ID)** y **el GID (Group ID)**. Es decir, el par `(UID, GID)` determina a qué objetos puede acceder un proceso y con qué derechos. El conjunto de objetos accesibles depende de la **identidad** (usuario y grupo) con la que corre el proceso.

**UID (User ID)**: identifica al **usuario** dueño del proceso.
**GID (Group ID)**: identifica al **grupo** al que pertenece.

**Cambio de dominio (relación dinámica)**

Como la relación proceso-dominio en UNIX es **dinámica**, un proceso puede **cambiar de dominio** cambiando su UID/GID efectivo. Esto se logra con los bits **SETUID** y **SETGID** sobre los archivos ejecutables:

- `setuid`/`setgid` hacen que un programa se ejecute con los permisos del dueño del archivo, no del usuario que lo lanza

>[!NOTE]
> Por ejemplo, `passwd` es propiedad de root y tiene el bit `setuid`, por eso un usuario común puede ejecutarlo y, durante esa ejecución, el proceso pasa al dominio de root para poder modificar el archivo de contraseñas

>[!NOTE]
> En términos del modelo de dominios, el `(UID, GID)` define qué pares `(objeto, derecho)` tiene el proceso. `setuid`/`setgid` permiten ese cambio dinámico de dominio justo cuando se necesita un privilegio mayor, en línea con POLA 

## Ejercicio 5:​ ¿Qué es ASLR (Address Space Layout Randomization)? ¿Linux provee ASLR para los procesos de usuario? ¿Y para el kernel?

**ASLR** (Address Space Layout Randomization, "aleatorización del diseño del espacio de direcciones") es un **mecanismo de seguridad** que **coloca en posiciones de memoria aleatorias** las distintas regiones de un programa cada vez que se ejecuta: el **stack**, el **heap**, las **librerías compartidas** y, según el caso, el **código** (ejecutable).

Su objetivo es **dificultar los ataques de explotación de memoria**. Muchos exploits necesitan **saber de antemano la dirección exacta** de una función o de un buffer para redirigir la ejecución hacia ahí (p. ej. saltar a `privileged_fn()` o a un shellcode). Si esas direcciones **cambian aleatoriamente en cada ejecución**, el atacante **no puede predecirlas**, y el exploit que dependía de una dirección fija deja de funcionar.

**Linux provee ASLR para los procesos de usuario?**

Sí, Linux implementa ASLR para los procesos de usuario (aleatoriza stack, heap, librerías y, si el binario se compila como PIE (Position Independent Executable), también el código). Se controla con el archivo `/proc/sys/kernel/randomize_va_space`.

**Y para el kernel?**

Sí, mediante **KASLR (Kernel ASLR)**, que aleatoriza la **dirección base donde se carga el propio kernel** en memoria al arrancar, para dificultar exploits contra el kernel. Es una funcionalidad **separada** de la ASLR de procesos de usuario (se controla aparte, p. ej. con el parámetro de arranque `kaslr`/`nokaslr`).

## Ejercicio 6:​ ¿Cómo se activa/desactiva ASLR para todos los procesos de usuario en Linux?

Se controla mediante el archivo virtual /proc/sys/kernel/randomize_va_space, que acepta tres valores:

- `0`, ASRL **desactivado** (direcciones fijas en cada ejecución)
- `1`, ASRL **parcial** (aleatoriza stack, librerías/mmap y vdso)
- `2`, ASRL **completo** (lo anterior + el heap/brk), es el **valor por defecto de Linux**

Para cambiarlo (como root): 

```bash
    # Ver el estado actual
    cat /proc/sys/kernel/randomize_va_space

    # Desactivar ASLR
    echo 0 > /proc/sys/kernel/randomize_va_space

    # Activarlo (completo)
    echo 2 > /proc/sys/kernel/randomize_va_space
```

Alternativa con `sysctl`:

```bash
    sysctl -w kernel.randomize_va_space=0      # desactivar (temporal)
```
- Para que sea persistente entre reinicios, se agrega a `/etc/sysctl.conf` o un archivo en `/etc/sysctl.d/`:
    ```bash
        kernel.randomize_va_space = 0
    ```