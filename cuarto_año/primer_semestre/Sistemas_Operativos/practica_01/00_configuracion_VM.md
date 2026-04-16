# Configuración VM

### Concectar terminal local a la VM

Para poder copiar y pegar contenido o utilizar el mouse, es de utilidad conectar la terminal local a la VM. Para esto, se puede utilizar el comando `ssh` desde la terminal local

1. Primero obtenemos la dirección IP de la VM utilizando el comando `ip a` dentro de la VM y copiamos la IP de la tercera entrada
2. Luego, desde la terminal local, ejecutamos el comando `ssh so@<IP_VM>` y escribimos la contraseña `so` cuando se nos solicite

Una vez conectados, podemos ejecutar comandos dentro de la VM desde la terminal local, lo que nos permite copiar y pegar contenido o utilizar el mouse para seleccionar texto.