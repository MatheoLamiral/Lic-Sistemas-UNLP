# Primera fecha 2025

## Ejercicio 1:​ Explique brevemente la arquitectura del kernel Linux, el tipo de kernel, modularidad y portabilidad.

El kernel linux es monolítico híbrido ejecuta todos los servicios del sistema operativo en un solo gran bloque de código en modo privilegiado. Sin embargo, se lo clasifica como híbrido porque admite módulos cargables en tiempo de ejecución. Una vez cargado, el código del módulo también se ejecuta en modo kernel (privilegiado), por lo que cualquier error en el mismo podría comprometer todo el sistema. El kernel es altamente portable, ya que una misma estructura de código fuente soporta muchas arquitecturas porque está escrito mayoritariamente en lenguaje C, dejando Assembler solo para  instrucciones específicas de bajo nivel de cada arquitectura

## Ejercicio 2:​

### a. ¿Qué es un módulo del kernel y para qué se utilizan los módulos?

Un módulo del kernel es una parte del kernel que puede cargarse y descargarse en tiempo de ejecución. Se usan para agregar funcionalidad al kernel (drivers, soporte de filesystems, etc.) cargándola solo cuando se necesita, sin recompilar ni reiniciar, y manteniendo el kernel base más liviano.

### b. ¿Qué sucede cuando se carga un módulo del kernel con insmod, y cómo interactúa con el resto del kernel? (marque la correcta)

- A. El módulo se carga en espacio de usuario y ejecuta su función principal como cualquier programa.
- B. El módulo se compila en tiempo real y reemplaza el kernel en ejecución.
- C. El módulo se carga en espacio de kernel, se inicializa mediante init_module, y puede registrar interfaces (como drivers) usando funciones como register_chrdev o platform_driver_register.
- D. El módulo se enlaza con system calls específicas para obtener privilegios temporales de ejecución.

La opción correcta es la C

## Ejercicio 3:​ ¿A qué hace referencia el archivo initramfs? ¿Cuál es su funcionalidad? ¿Bajo qué condiciones puede no ser necesario?

initramfs (initial RAM filesystem) es un sistema de archivos temporal que se monta en memoria principal (RAM) cuando se inicia el sistema, que contiene todos los elementos necesarios (módulos, drivers, etc.) para que el kernel pueda montar el filesystem real y arrancar. Puede no ser necesario cuando todos estos elementos ya se encuentren compilados built-in en el kernel, porque entonces puede montar el root directamente.

## Ejercicio 4:​

### a. ¿Qué es una system call y cuál es su propósito principal?

Una system call o llamada al sistema, es una API provista por el kerel para pasar de modo usuario a modo kernel mediante una de software. Su propósito principal es birndarle a los procesos que corren en modo usuario una forma para solicitar los servicios del kernel (realizar tareas que requieren modo supervisor) 

### b. ¿Cuál de las siguientes afirmaciones describe mejor el mecanismo mediante el cual una system call define un mecanismo en el kernel de Linux que se expone al espacio de usuario? (marque la correcta)

- A. Las system calls se implementan en archivos .S y se generan automáticamente a través de la libc.
- B. Cada system call debe implementarse en espacio de usuario y luego referenciarse desde el kernel con una tabla de punteros.
- C. La implementación de una system call implica su definición en el espacio kernel, su inclusión en la tabla de system calls (syscall_table), y su asociación con un número único.
- D. El kernel crea automáticamente interfaces de system call para cada función exportada con EXPORT_SYSCALL.

La opción correcta es la C

## Ejercicio 5:​ ¿Quién es responsable de la planificación de los ULT? ¿y los KLT? ¿Cómo afecta esto al rendimiento en sistemas con múltiples núcleos?

En el caso de los ULT los planifica la biblioteca de hilos en espacio de usuario y en el caso de los KLT los planifica el kernel. Los ULT son invisibles para el kernel, los ve como un solo proceso, por lo que no puede ejecutarlos en paralelo en varios núcleos (no hay paralelismo real). En cambio, en los KLT el kernel los planifica individualmente por lo que puede asignarlos a distintos núcleos simultáneamente (si hay paralelismo)

## Ejercicio 6:​ ¿Qué características tendrá el proceso creado si se ejecuta un fork() pero no se ejecuta exec()?

Al hacer fork(), el proceso creado (hijo) es una copia (clon) del proceso padre. Como no se ejecuta exec(), el hijo sigue ejecutando el mismo programa/código que el padre (no se reemplaza por otro). Sus características:
- Ejecuta el mismo programa que el padre
- Tiene su propio PID
- Su memoria es una copia de la del padre
- Hereda recursos
- El hijo devolverá 0 en el fork() y el padre el PID del hijo

## Ejercicio 7:​ Describa brevemente la diferencia entre Hypervisors de tipo 1 y tipo 2.

## Ejercicio 8:​ Describa brevemente las funcionalidades provistas por CGroups y por Namespaces. (No es necesario enumerar todos los CGroups ni todos los Namespaces).

## Ejercicio 9:​ ¿Cuál es la relación entre los union file system y las imágenes/contenedores?

## Ejercicio 10:​ ¿Qué es ASLR (Address Space Layout Randomization)? ¿Linux provee ASLR para los procesos de usuario? ¿Y para el kernel?
