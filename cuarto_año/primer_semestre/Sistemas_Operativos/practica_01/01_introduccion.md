# Introducción

### Ejercicio 1: ¿Qué es GCC?

**GCC** es un compilador de C. En el contexto de la administración y configuración de sistemas operativos, es una de las herramientas de software fundamentales que se necesitan para compilar o recompilar el kernel de Linux a partir de su código fuente, trabajando en conjunto con otros componentes como make, binutils y las bibliotecas de desarrollo (libc6)

### Ejercicio 2: ¿Qué es make y para que se usa?

**make** es una herramienta de software que se utiliza para ejecutar las directivas definidas en los archivos conocidos como **Makefiles**. Es una herramienta fundamental que se necesita para compilar o recompilar el kernel de Linux a partir de su código fuente, trabajando en conjuto con el compilador de C (GCC), binutils y las bibliotecas de desarrollo (libc6)

### Ejercicio 3:  La carpeta /home/so/practica1/ejemplos/01-make de la VM contiene ejemplos de uso de make. Analice los ejemplos, en cada caso ejecute `make` y luego `make run` (es opcional ejecutar el ejemplo 4, el mismo requiere otras dependencias que no vienen preinstaladas en la VM):

- `01-helloworld`
  ```zsh
    so@so:~/practica1/ejemplos/01-make/01-helloworld$ make
    gcc -Wall --std=c99 -o helloworld helloworld.c
    so@so:~/practica1/ejemplos/01-make/01-helloworld$ make run
    ./helloworld
    Hello world!
  ```
- `02-multiplefiles`
  ```zsh
    so@so:~/practica1/ejemplos/01-make/02-multiplefiles$ make
    cc -Wall --std=c11   -c -o dlinkedlist.o dlinkedlist.c
    gcc -Wall --std=c11 dlinkedlist.o revert.c -o revert
    so@so:~/practica1/ejemplos/01-make/02-multiplefiles$ make run 
    ./revert
    Value 9
    Value 8
    Value 7
    Value 6
    Value 5
    Value 4
    Value 3
    Value 2
    Value 1
    Value 0
  ```
- `03-htmltotxt`
  ```zsh
    so@so:~/practica1/ejemplos/01-make/03-htmltotxt$ make
    sed 's/<.*>//' src/pg345-images.html > pg345-images.txt
    sed 's/<.*>//' src/pg84-images.html > pg84-images.txt
    so@so:~/practica1/ejemplos/01-make/03-htmltotxt$ make run
    make: *** No hay ninguna regla para construir el objetivo 'run'.  Alto.
  ```

#### a) Vuelva a ejecutar el comando `make`. ¿Se volvieron a compilar los programas?¿Por qué?

No se volvieron a compilar los programas porque `make` **compara la fecha de modificación de cada target con la de sus dependencias**. Como los targets ya existían y eran más nuevos que sus archivos fuente, `make` determinó que no había nada que actualizar y no hizo nada.

#### b) Cambie la fecha de modificación de un archivo con el comando `touch` o editando el archivo y ejecute `make`. ¿Se volvieron a compilar los programas? ¿Por qué?

si por ejemplo ejecutamos lo siguiente:
  ```zsh
    so@so:~/practica1/ejemplos/01-make/02-multiplefiles$ ls
    dlinkedlist.c  dlinkedlist.h  dlinkedlist.o  Makefile  revert  revert.c
    so@so:~/practica1/ejemplos/01-make/02-multiplefiles$ touch dlinkedlist.c
    so@so:~/practica1/ejemplos/01-make/02-multiplefiles$ make
    cc -Wall --std=c11   -c -o dlinkedlist.o dlinkedlist.c
    gcc -Wall --std=c11 dlinkedlist.o revert.c -o revert
  ```

Vemos que sí se volvieron a compilar los programas porque al cambiar la fecha de modificación del archivo `dlinkedlist.c`, este archivo se volvió más nuevo que el target `dlinkedlist.o` que depende de él. Por lo tanto, `make` detectó que el target estaba desactualizado y ejecutó las reglas necesarias para recompilarlo. Luego, como `revert` depende de `dlinkedlist.o`, también se volvió a compilar para reflejar los cambios.

#### c) ¿Por qué “run” es un target “phony”?

Un target "phony" es uno que no representa un archivo real que make deba generar.
run es phony porque su único propósito es ejecutar el programa, no crear ningún archivo llamado run. Si no se declarara como .PHONY y existiera un archivo llamado run en el directorio, make creería que el target ya está construido y no haría nada al ejecutar make run.

#### d) En el ejemplo 2 la regla para el target `dlinkedlist.o` no define cómo generar el target, sin embargo el programa se compila correctamente. ¿Por qué es esto?

Porque `make` tiene reglas implícitas predefinidas que sabe aplicar automáticamente. Una de ellas establece que para generar un archivo `.o` a partir de un `.c` del mismo nombre, debe compilarlo con `cc -c`. Al no encontrar una regla explícita para `dlinkedlist.o` en el `Makefile`, `make` busca entre sus reglas implícitas, encuentra que existe un `dlinkedlist.c` y aplica la regla automáticamente para generar el `.o` correspondiente.

### Ejercicio 4: ¿Qué es el kernel de GNU/Linux? ¿Cuáles son sus funciones principales dentro del Sistema Operativo?

Es el núcleo del sistema operativo, un programa fundamental que se encarga de ejecutar otros programas y gestionar los dispositivos de hardware, logrando que el software y el hardware puedan trabajar juntos de manera coordinada. De hecho, en un sentido estricto, el kernel es el Sistema Operativo en sí mismo

El kernel implementa los servicios más críticos y esenciales. Sus funciones principales son:
- **Administración de la memoria principal**: asigna, gestiona y protege el espacio de memoria que necesita cada programa para funcionar correctamente.
- **Manejo del uso de la CPU**: planifica y decide qué procesos o hilos de ejecución utilizan el procesador, garantizando un reparto equitativo del tiempo de cálculo.
- **Administración de procesos**: Se encarga de todo el ciclo de vida de los procesos que corren en el sistema, desde su creación hasta su terminación.
- **Gestión de la Entrada/Salida (E/S)**: Controla y coordina el acceso a todos los dispositivos de hardware y periféricos.
- **Comunicación y Concurrencia**: Provee los mecanismos necesarios para que los múltiples procesos que coexisten en el sistema puedan comunicarse de forma segura y sincronizar sus tareas.

### Ejercicio 5: Explique brevemente la arquitectura del kernel Linux teniendo en cuenta: tipo de kernel, módulos, portabilidad, etc.

- **Tipo de kernel**
  - Se define funcionalmente como un núcleo **monolítico híbrido**. Su naturaleza es monolítica porque incluye todos los servicios del sistema operativo (gestión de procesos, memoria, archivos, controladores, etc.) en un solo gran bloque de código que se ejecuta en modo supervisor o privilegiado, lo que le otorga un acceso completo y directo a los recursos de hardware para una máxima eficiencia. Sin embargo, se lo clasifica como híbrido debido a que incorpora la capacidad de comportarse de manera modular.
- **Módulos**
  - Para flexibilizar su estructura monolítica, Linux utiliza módulos. Un módulo es un fragmento de código que puede cargarse o descargarse en el mapa de memoria del kernel bajo demanda. Esto permite extender la funcionalidad del sistema operativo "en caliente" (sin necesidad de reiniciar el equipo), facilitando un desarrollo más modular. Cabe destacar que, una vez cargado, el código del módulo también se ejecuta en modo kernel (privilegiado), por lo que cualquier error en el mismo podría comprometer todo el sistema.
- **Portabilidad**
  - El kernel es altamente portable, ya que en una misma estructura de código fuente se brinda soporte a todas las arquitecturas de hardware compatibles. Esto se logra porque está escrito mayoritariamente en lenguaje C, limitando el uso del lenguaje Assembler exclusivamente a las instrucciones especiales y de muy bajo nivel de cada arquitectura. Adicionalmente, de forma reciente se ha integrado soporte para el lenguaje Rust, orientado principalmente a la implementación segura de módulos.
- **Interfaz de acceso (System Calls)**
  - A nivel arquitectónico, existe una separación estricta entre el "espacio de kernel" (donde residen los drivers y funciones del núcleo) y el "espacio de usuario" (donde corren las aplicaciones comunes). Para que los programas puedan interactuar con el hardware de manera segura, la arquitectura provee una interfaz estandarizada llamada llamadas al sistema (system calls). El programa emite una interrupción por software (trap) que cambia el procesador a modo kernel, permitiendo que el núcleo atienda la solicitud y gestione los recursos con equidad.
- **Desarrollo y licenciamiento**
  - Todo el kernel es un proyecto de software libre liberado bajo la licencia GPLv2. Su desarrollo no está centralizado en una sola entidad, sino que es colaborativo, organizado en distintos subsistemas (como red, gestión de memoria, archivos) que son mantenidos por diferentes responsables, quienes finalmente elevan los cambios a Linus Torvalds.

### Ejercicio 6: ¿Cómo se define el versionado de los kernels Linux en la actualidad?

En la actualidad, y a partir del lanzamiento de la versión 3.0 en 2011, el versionado del kernel de Linux se define mediante un **esquema de tres números**, opcionalmente acompañado de un **sufijo**, con el formato **A.B.C[-rcX]**
- **A (Revisión mayor)**
  - Denota la versión principal del kernel y cambia con menor frecuencia (generalmente cada varios años). En la práctica, el cambio de este número no suele deberse a modificaciones arquitectónicas drásticas, sino a la decisión de Linus Torvalds de evitar que el segundo número crezca demasiado y se vuelva incómodo de manejar
- **B (Revisión menor)**
  - Representa las actualizaciones importantes y solo cambia cuando se introducen nuevos drivers o características
- **C (Número de revisión)**
  - Indica revisiones menores que suelen estar destinadas a corregir errores (bugfixes) y aplicar parches de seguridad
- **-rcX (Release Candidate o Versiones de prueba)**
  - Se utiliza para identificar versiones que aún están en desarrollo y pruebas. Durante el ciclo de desarrollo, van apareciendo distintas candidatas (como rc1, rc2, etc.) en la ventana de integración de código (merge window) hasta que se consideran lo suficientemente estables para una versión de producción.

### Ejercicio 7: ¿Cuáles son los motivos por los que un usuario/a GNU/Linux puede querer re-compilar el kernel?

Un usuario de GNU/Linux puede tener diversas razones para querer recompilar su kernel, aprovechando que al ser software libre permite compilar versiones totalmente personalizadas. Los motivos principales incluyen:
- **Soportar nuevos dispositivos**
  - La recompilación permite añadir compatibilidad con hardware reciente o específico que no esté soportado en el kernel actual, como por ejemplo los controladores de una placa de video.
- **Agregar mayor funcionalidad**
  - Permite incluir características adicionales o módulos que no vienen activados por defecto, como el soporte para nuevos sistemas de archivos.
- **Optimizar el funcionamiento**
  - Se puede ajustar y afinar el núcleo para que ofrezca su máximo rendimiento de acuerdo a la arquitectura y características exactas del sistema en el que corre.
- **Adaptar y "limpiar" el sistema**
  - Al configurarlo manualmente, el usuario puede decidir quitar el soporte para todo aquel hardware que no posee o no utiliza, logrando un kernel más pequeño, eficiente y a medida.
- **Corrección de bugs**
  - Permite aplicar parches y actualizaciones de manera rápida para solucionar problemas críticos de seguridad o errores de programación.

### Ejercicio 8: ¿Cuáles son las distintas opciones y menús para realizar la configuración de opciones de compilación de un kernel? Cite diferencias, necesidades (paquetes adicionales de software que se pueden requerir), pro y contras de cada una de ellas.

La configuración del kernel de Linux se realiza a través de la generación de un archivo llamado `.config`, el cual reside en el directorio del código fuente y contiene las instrucciones de qué es lo que el kernel debe compilar. Dado que configurar un kernel desde cero manualmente es una tarea muy tediosa y propensa a errores (pudiendo generar kernels que no arranquen), se proveen diferentes herramientas que automatizan el proceso.
Las tres opciones principales para configurar las opciones de compilación son:
- `make config`
  - Es una interfaz en modo texto que opera de forma completamente secuencial. Al ser interactiva pero secuencial, obliga al usuario a responder afirmativa o negativamente a cada una de las opciones del kernel una por una, lo que la convierte en una opción muy tediosa. No requiere paquetes adicionales más allá de las herramientas base de compilación.
- `make menuconfig`
  - Es el modo generalmente más utilizado. Proporciona una interfaz con paneles interactivos y menús navegables (usando flechas del teclado) pero funcionando íntegramente dentro de la terminal de comandos. Combina la facilidad de uso de los menús visuales sin el gran consumo de recursos que exige un entorno gráfico completo, haciéndola ideal para servidores y conexiones remotas. Para dibujar esta interfaz en la terminal, este método requiere la instalación de la librería ncurses
- `make xconfig`
  -  Es una interfaz puramente gráfica que hace uso de un sistema de ventanas para mostrar las opciones del kernel de forma similar a una aplicación de escritorio tradicional. Es extremadamente amigable y visual para interactuar con el mouse, permitiendo expandir o colapsar árboles de configuración fácilmente. Su gran contra es que depende de un entorno gráfico, por lo que no se puede utilizar en sistemas o servidores que solo operen en modo texto puro. Requiere tener instalado y corriendo un sistema de ventanas X (servidor gráfico) en el equipo.

### Ejercicio 9: Indique qué tarea realiza cada uno de los siguientes comandos durante la tarea de configuración/compilación del kernel:

#### a) `make menuconfig`

Ejecuta una **herramienta interactiva en modo texto** (valiéndose de la librería ncurses) que genera una i**nterfaz con paneles navegables** en la terminal. Su objetivo es permitir la configuración de las opciones del kernel de manera amigable para crear el archivo `.config` con las directivas de compilación

#### b) `make clean`

Se encarga de borrar todos los archivos binarios e intermedios que fueron generados durante un proceso de compilación previo

#### c) `make` (investigue la funcionalidad del parámetro `-j`)

Es el comando principal que busca el archivo `Makefile`, interpreta sus reglas y directivas, y realiza la compilación del kernel.
- Parámetro `-j`
  - Sirve para indicarle al compilador el **número de trabajos (hilos) concurrentes** que debe ejecutar en paralelo. Por ejemplo, `make -j 8` ejecutará 8 trabajos a la vez, lo que permite aprovechar los procesadores multinúcleo y acelerar considerablemente el tiempo total de compilación.

#### d) `make modules` (utilizado en antiguos kernels, actualmente no es necesario)

Compila todos los módulos necesarios correspondientes a aquellas funcionalidades de hardware o software que el usuario seleccionó como "módulo" en lugar de "built-in". Hoy en día, esta tarea ya se encuentra incluida automáticamente durante la compilación general iniciada con el comando `make`

#### e) `make modules_install`

Ejecuta una regla del `Makefile` que se encarga de ubicar o instalar los módulos que se acaban de compilar en el directorio correspondiente del sistema, el cual por convención es `/lib/modules/version-del-kernel`

#### f) `make install`

Realiza el proceso de instalación automática de la imagen del kernel. Ubica la imagen recién compilada (frecuentemente llamada `bzImage`), junto con el mapa de símbolos (`System.map`) y el archivo de configuración (`.config`), dentro del directorio de arranque `/boot`.

### Ejercicio 10: Una vez que el kernel fue compilado, ¿dónde queda ubicada su imagen? ¿dónde debería ser reubicada? ¿Existe algún comando que realice esta copia en forma automática?

Una vez finalizado el proceso de compilación, la imagen del kernel queda ubicada dentro del árbol del código fuente, específicamente en la ruta `directorio-del-código/arch/arquitectura/boot/` (por ejemplo, el archivo suele llamarse `bzImage` bajo una ruta como `arch/i386/boot/bzImage` dependiendo de la arquitectura).
Esta imagen, junto con otros archivos importantes como el mapa de símbolos (`System.map`) y el archivo de configuración (`.config`), debería ser reubicada en el directorio `/boot` del sistema para que el gestor de arranque pueda encontrarlo.
Para realizar esta tarea de copia e instalación en su destino definitivo de forma automática, existe el comando `make install` (que debe ejecutarse con privilegios de superusuario). Este comando ejecuta una regla del archivo `Makefile` que se encarga de ubicar la imagen y los archivos correspondientes en el directorio `/boot` sin necesidad de copiarlos manualmente.

### Ejercicio 11: ¿A qué hace referencia el archivo initramfs? ¿Cuál es su funcionalidad? ¿Bajo qué condiciones puede no ser necesario?

`initramfs` hace referencia a un **sistema de archivos temporal** que se monta durante el arranque del sistema. Su funcionalidad principal es proporcionar un entorno mínimo inicial que contiene los ejecutables, drivers y módulos necesarios para lograr iniciar el sistema correctamente. Una vez que el proceso de arranque avanza y se logra montar el sistema de archivos definitivo, este disco temporal se desmonta.
- Un `initramfs` puede omitirse si todos los controladores (drivers) y sistemas de archivos críticos para montar el disco raíz se compilan de manera integrada (built-in) directamente dentro del kernel, en lugar de hacerlo como módulos separados.

>[!NOTE]
> Cuando una característica se compila como built-in, su ejecución es más eficiente porque el kernel tiene acceso directo y no hay necesidad de cargar un adicional en memoria. Por lo tanto, si el kernel ya posee todo lo necesario en su propio núcleo para reconocer el disco duro y el sistema de archivos al arrancar, el uso del `initramfs` (cuyo propósito es cargar módulos de arranque bajo demanda) deja de ser un requisito estricto.

### Ejercicio 12: ¿Cuál es la razón por la que una vez compilado el nuevo kernel, es necesario reconfigurar el gestor de arranque que tengamos instalado?

Es necesario reconfigurar el gestor de arranque (como GRUB) para que este **pueda reconocer e indexar** el nuevo kernel que se acaba de compilar e instalar en el sistema. Aunque la imagen del nuevo kernel y sus archivos asociados se hayan reubicado correctamente en el directorio `/boot` (paso previo en el proceso de instalación), el gestor de arranque no detecta estos cambios de forma automática. Al reconfigurarlo, el sistema actualiza los archivos de configuración del gestor (por ejemplo, `grub.cfg`) incorporando las rutas de la nueva imagen y del initramfs, permitiendo así que el nuevo kernel aparezca como una opción válida para arrancar cuando se enciende el equipo.

En el caso específico de utilizar la versión 2 de GRUB, esta reconfiguración se logra simplemente ejecutando el comando `update-grub2` con privilegios de superusuario. Luego de esto, se puede comprobar que la reconfiguración fue exitosa verificando si la versión del nuevo kernel fue efectivamente indexada dentro del archivo `/boot/grub/grub.cfg`

### Ejercicio 13: ¿Qué es un módulo del kernel? ¿Cuáles son los comandos principales para el manejo de módulos del kernel?

Un módulo del kernel es un fragmento de código que puede cargarse o descargarse en el mapa de memoria del Sistema Operativo (Kernel) bajo demanda. 
- Sus características principales son:
  - **Extensión en "caliente"**: Permiten añadir nuevas funcionalidades al kernel sin necesidad de reiniciar el sistema.
  - **Ejecución privilegiada**: Todo el código del módulo se ejecuta en modo Kernel (modo privilegiado), lo que significa que cualquier error de programación en el módulo puede llegar a colgar todo el sistema operativo.
  - **Diseño modular**: Permiten que el kernel mantenga un desarrollo basado en un diseño mucho más modular.
  - **Ubicación**: Los módulos que se encuentran disponibles en el sistema se ubican dentro del directorio `/lib/modules/version-del-kernel`
- En cuanto a los comandos principales para su manejo y gestión:
  - `lsmod`: Es el comando utilizado para poder visualizar qué módulos se encuentran cargados actualmente en el sistema.
  - `make modules`: Se utiliza durante el proceso de compilación del kernel para compilar específicamente todos los módulos necesarios.
  - `make modules_install`: Es una regla del archivo `Makefile` que se ejecuta (frecuentemente con privilegios de administrador) para instalar y ubicar los módulos recién compilados en su directorio correspondiente del sistema.

### Ejercicio 14: ¿Qué es un parche del kernel? ¿Cuáles son las razones principales por las cuáles se deberían aplicar parches en el kernel? ¿A través de qué comando se realiza la aplicación de parches en el kernel?

Un **parche del kernel** es un mecanismo de actualización que permite modificar el código fuente de una versión base del núcleo. Su funcionamiento se apoya en **archivos de diferencia (archivos diff)**, los cuales contienen las instrucciones precisas que indican qué porciones de código específico se deben agregar y qué porciones se deben quitar. Dentro de los repositorios oficiales (como `kernel.org`), estos parches se pueden encontrar en formatos incrementales (se aplican sobre la versión inmediatamente anterior) o no incrementales (se aplican sobre la versión principal o mainline anterior)

Las razones principales por las cuales es recomendable o necesario aplicar parches en el kernel son:
- **Agregar nueva funcionalidad**: Permiten incorporar soporte para hardware reciente instalando nuevos drivers o habilitar características adicionales en el sistema.
- **Aplicar correcciones (bugfixes)**: Son fundamentales para aplicar soluciones rápidas a errores de programación o vulnerabilidades de seguridad críticas sin alterar todo el sistema.
- **Optimizar el proceso de actualización**: A menudo resulta mucho más rápido y sencillo descargar únicamente el archivo con las diferencias (el parche) y aplicarlo al código que ya se posee, en lugar de tener que descargar el árbol completo del código fuente de la nueva versión.
- **Actualizar en caliente**: A partir del lanzamiento de la versión 4.0 de Linux, se introdujo la posibilidad de aplicar ciertos parches y actualizaciones menores (particularmente en módulos) sin la necesidad de reiniciar el sistema operativo.

La tarea de aplicar un parche en el código fuente se realiza a través del comando `patch`. En la práctica, este comando suele combinarse mediante tuberías (pipes) con herramientas de descompresión para leer el parche directamente. Un ejemplo típico de ejecución en la terminal es: `xzcat ../patch-6.13.7.xz | patch -p1`. Adicionalmente, el comando `patch` cuenta con parámetros muy útiles como `--dry-run`, que le permite al administrador simular la aplicación del parche para comprobar que no existan conflictos o errores antes de modificar los archivos de código reales.

### Ejercicio 15: ​Investigue la característica Energy-aware Scheduling incorporada en el kernel 5.0 y explique brevemente con sus palabras:

#### a) ¿Qué característica principal tiene un procesador ARM big.LITTLE?

La característica principal de una arquitectura big.LITTLE es que **combina dos tipos diferentes de núcleos (cores) en un mismo procesador (un diseño asimétrico)**. Por un lado, tiene núcleos **"LITTLE"** (pequeños), que están diseñados para consumir muy poca energía y manejar tareas ligeras o de fondo. Por otro lado, incluye núcleos **"big"** (grandes), que están diseñados para ofrecer el máximo rendimiento y potencia de cómputo para tareas pesadas, aunque consumen mucha más energía.

#### b) En un procesador ARM big.LITTLE y con esta característica habilitada. Cuando se despierta un proceso ¿a qué procesador lo asigna el scheduler?

Con el Energy-aware Scheduling habilitado, el planificador ya no solo mira el rendimiento, sino que evalúa el costo energético. Cuando un proceso se despierta, el planificador **intentará asignarlo por defecto al núcleo más eficiente energéticamente (el núcleo "LITTLE") que tenga la capacidad ociosa suficiente** para ejecutar la tarea sin afectar drásticamente el rendimiento. Si la tarea es demasiado demandante y el núcleo pequeño no da abasto, el planificador calculará si vale la pena el costo energético extra y lo asignará a un núcleo "big".

#### c) ¿A qué tipo de dispositivos opinás que beneficia más esta característica?

Esta característica fue **pensada idealmente para minimizar el consumo energético en smartphones**. En términos generales, beneficia de manera directa a **cualquier dispositivo móvil o integrado que dependa de una batería** (como teléfonos, tablets, relojes inteligentes y laptops), ya que la administración inteligente de la energía permite prolongar significativamente la autonomía del dispositivo sin sacrificar la respuesta del sistema cuando el usuario realmente requiere potencia.

### Ejercicio 16: Investigue la system call memfd_secret() incorporada en el kernel 5.14 y explique brevemente con sus palabras

#### a)​ ¿Cuál es su propósito?

El propósito principal de esta llamada al sistema introducida en el kernel 5.14 es permitir la creación de **áreas de memoria secretas que no pueden ser accedidas ni siquiera por el usuario administrador del sistema** (el usuario root)

#### b) ¿Para qué puede ser utilizada?

Su caso de uso fundamental es **guardar de manera segura información sumamente sensible**, como por ejemplo el almacenamiento de claves o contraseñas en memoria, protegiéndolas del resto del sistema

#### c) ¿El kernel puede acceder al contenido de regiones de memoria creadas con esta system call?

La característica más importante de `memfd_secret()` es que **remueve las páginas de memoria del mapa de acceso directo del propio kernel**. Esto significa que el **kernel mismo pierde el acceso a estas regiones de memoria**, lo cual es vital para garantizar que la información secreta no pueda ser leída accidentalmente por volcados de memoria (dumps), funciones de depuración del núcleo o mediante la explotación de vulnerabilidades.