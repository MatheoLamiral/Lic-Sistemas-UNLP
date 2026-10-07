# CopyFail

## Ejercicio 1: Investigue la vulnerabilidad CopyFail (ver links en practica5/copy_fail/README.md)

El kernel de Linux trae dentro un subsistema cripto, una colección de implementaciones de operaciones criptográficas (cifrar, descifrar, calcular hashes o firmas) con algoritmos como AES, SHA, etc. A ese conjunto de código se lo llama el **crypto subsystem** o **Kernel Crypto API**.
- **`AF_ALG` (Address Family Algorithm)**: es la **interfaz tipo socket** que Linux ofrece para que un **programa de usuario común**, **sin privilegios**, le pida al **subsistema cripto del kernel** que cifre, descifre o hashee datos. Se abre un socket, se lo ata (bind) a un algoritmo, se mandan datos y devuelve el resultado cifrado/descifrado.
- **AEAD (el tipo de algoritmo)**: es una familia de algoritmos de cifrado (Authenticated Encryption with Associated Data). Es un **algoritmo que transforma un buffer de datos, toma una entrada y produce una salida**. En CopyFail el algoritmo concreto es `authencesn`.
- **La optimización "in-place" de 2017 (el origen del bug)**: Normalmente, cuando el kernel descifra, usa dos buffers separados, uno de origen (los datos de entrada) y uno de destino (donde escribe el resultado). Para ahorrar memoria y ser más rápido, en 2017 metieron una **optimización, hacer la operación "in-place" (en el lugar), o sea usar el mismo buffer como origen Y como destino**. El **resultado se escribe encima de la entrada**. Hasta acá no hay problema si el buffer de entrada fuera escribible.
- **`splice()` (lo que introduce las páginas peligrosas)**: es una syscall que mueve datos entre descriptores sin copiarlos. Por ejemplo, mandar el contenido de un archivo hacia el **socket `AF_ALG`**. La clave es que, **para evitar copiar, el kernel no duplica los datos del archivo, sino que le pasa al socket referencias directas a las páginas del archivo que ya están en la page cache** (la copia en RAM que el kernel mantiene de los archivos abiertos). Y esas páginas de un archivo abierto para lectura son, por diseño, de **solo lectura**.
- **La vulnerabilidad**: al hacer `splice()` de un archivo hacia el socket `AF_ALG` y pedir un descifrado `AEAD`, las **páginas de solo lectura de la page cache entran como buffer de entrada, pero la optimización in-place las usa también como destino y escribe encima**. El **kernel termina escribiendo sobre páginas que deberían ser de solo lectura**, porque **"cree" que escribe en un buffer legítimo** y nunca chequea permisos.

### a. ¿Es una vulnerabilidad en espacio de usuario o del kernel?

Es una vulnerabilidad en espacio del Kernel, particularmete del subsistema cripto.

### b. ¿Por qué el exploit abre un archivo con suid?
### c. ¿La página modificada se almacena luego en disco?

## Ejercicio 2: Ejecute en exploit copy_fail_exp.py en la máquina virtual de la cátedra y pruebe lo siguiente:

### a. Verifique que obtuvo root
### b. Abra otra terminal con el usuario "so" y ejecute el comando "su" ¿Qué sucedió? ¿Por qué?
### c. Reinicie la máquina virtual, abra una terminal con el usuario "so" y ejecute el comando "su" ¿Qué sucedió? ¿Por qué?

## Ejercicio 3: ¿Por qué se dice que puede permitir saltar el aislamiento de containers?

## Ejercicio 4: ¿Qué condiciones deben darse para que CopyFail permita afectar el sistema host si se ataca un container?

## Ejercicio 5: Laboratorio con docker compose (en la VM de la cátedra):

### a. Compile `superuser.c` con el comando `make`. Asegúrese que el binario generado tenga propietario root y suid. El contenido del programa no es importante, No necesariamente tiene que tener alguna vulnerabilidad, podría ser cualquier binario con SUID + propietario root.
### b. Ejecute lo servicios con `docker-compose up --build -d`
### c. Abra un shell en el container "attacker": `docker exec -it attacker /bin/bash`

#### i. Verifique que el comando "superuser" pide una contraseña y si la contraseña no es ingresada correctamente no da permisos de root.
#### ii. Ejecute el exploit "copy_fail_exp_for_docker.py"
#### iii. Verifique si obtuvo root
### d. Abra un shell en victim "docker exec -it victim /bin/bash"
#### i. Ejecute "superuser"
#### ii. ¿Qué sucedió? ¿Por qué no pide password?
#### iii. Ejecute el siguiente oneliner:
```bash
mount /dev/sda1 /mnt/ && touch /mnt/home/so/me_escape_del_container
```
### e. Desde el usuario "so" de la VM ejecute "ls $HOME" ¿Qué sucedió?

## Ejercicio 6: ¿Qué nos permite que el container "victim" se ejecute con --privileged?

## Ejercicio 7: ¿Por qué si el exploit se ejecutó en un container también afecta al otro container?
