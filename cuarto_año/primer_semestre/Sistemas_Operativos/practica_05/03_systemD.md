# Ejercicio SystemD

## Ejercicio 1: Investigue los comandos:

### a. `systemctl enable`

Habilita un servicio para que arranque automáticamente al bootear el sistema. No lo inicia ahora, solo lo marca para el próximo arranque 

### b. `systemctl disable`

deshabilita el arranque automático. El servicio no se iniciará en el próximo boot, pero si está corriendo ahora, no lo detiene

### c. `systemctl daemon-reload`

Hace que **systemd relea los archivos de configuración de las units** (los `.service`). Es obligatorio ejecutarlo cada vez que creás o modificás un archivo `.service`, para que systemd tome los cambios. No reinicia los servicios, solo recarga la definición.

### d. `systemctl start`

Inicia el servicio ahora mismo (en esta sesión). No afecta si arranca o no en el próximo boot (eso es enable).

### e. `systemctl stop`

Detiene el servicio ahora mismo. No afecta el arranque automático (eso es disable).

### f. `systemctl status`

Muestra el estado del servicio: si está activo/inactivo (active (running), dead, failed), su PID, el uso de memoria, y las últimas líneas de log. Es el comando para **diagnosticar**.

### g. `systemd-cgls`

Muestra el árbol de cgroups de systemd: cómo están organizados los procesos jerárquicamente en grupos de control (por slice/service). Sirve para ver qué procesos pertenecen a cada servicio y cómo systemd los agrupa.

### h. `journalctl -u [unit]`

Muestra los logs de una unit específica desde el journal de systemd. `-u` filtra por unit. Útil: `-f` para seguir en vivo, `-e` para ir al final, `--since` para filtrar por fecha.

## Ejercicio 2: Investigue las siguientes opciones que se pueden configurar en una unit service de systemd:

### a. User y Group

Definen con qué usuario y grupo se ejecuta el servicio. Si no se especifican, corre como root (peligroso). Ponerle User=nobody y Group=nogroup hace que corra sin privilegios 

### b. ProtectHome

Controla el acceso del servicio a los directorios /home, /root y /run/user. 
- Valores:
  - true: esos directorios aparecen vacíos e inaccesibles para el servicio.
  - read-only: los ve pero no puede escribir.
  - Evita que un servicio comprometido lea/modifique archivos personales de los usuarios.

### c. PrivateTmp

Si es true, el servicio obtiene un /tmp (y /var/tmp) privado y aislado, propio de él, en vez del /tmp compartido del sistema. Cuando el servicio termina, ese tmp se borra. Evita ataques por archivos temporales compartidos.

### d. ProtectProc

Restringe qué información de otros procesos puede ver el servicio a través de /proc (similar a hidepid). Con ProtectProc=invisible, el servicio solo ve sus propios procesos en /proc, no los del resto del sistema. Limita la fuga de información.

### e. MemoryAccounting, MemoryHigh y MemoryMax

Son directivas de límites de memoria vía cgroups:

- `MemoryAccounting=true`: habilita el conteo/contabilidad del uso de memoria del servicio(necesario para que los límites funcionen). 
- `MemoryHigh=` es el límite "blando": si el servicio lo supera, el kernel lo presiona (throttling, recupera memoria agresivamente) pero no lo mata.
- `MemoryMax=` es el límite "duro": si el servicio intenta superarlo, se le niega la memoria y si insiste el kernel lo mata (OOM killer).

## Ejercicio 3: Tenga en cuenta para los siguientes puntos:

- a. La configuración del servicio se instala en: `/etc/systemd/system/insecure_service.service`
- b. Cada vez que modifique la configuración será necesario recargar el demonio de systemd y recargar el servicio:
    - i. `systemctl daemon-reload`
    - ii. `systemctl restart insecure_service.service`

## Ejercicio 4: En el directorio `insecure_service` del repositorio de la cátedra encontrará el binario `insecure_service`, el archivo de configuración `insecure_service.service` y el script `install.sh`.

### a. Instale el servicio usando el script install.sh.

`su -c "./install.sh"`

### b. Verifique que el servicio se está ejecutando con `systemctl status`.

```bash
so@so:~/codigo-para-practicas/practica5/insecure_service$ systemctl status insecure_service
● insecure_service.service - Insecure service
     Loaded: loaded (/etc/systemd/system/insecure_service.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-08-03 20:28:49 -03; 1min 23s ago
   Main PID: 1202 (insecure_servic)
      Tasks: 4 (limit: 2306)
     Memory: 2.4M
     CGroup: /system.slice/insecure_service.service
             └─1202 /opt/sistemasoperativos/insecure_service
```

### c. Verifique con qué UID se ejecuta el servicio usando `ps aux | grep insecure_service`.

```bash
so@so:~/codigo-para-practicas/practica5/insecure_service$ ps aux | grep insecure_service
root        1202  0.0  0.4 1232060 8164 ?        Ssl  20:28   0:00 /opt/sistemasoperativos/insecure_service
so          1274  0.0  0.1   6484  2136 pts/0    S+   20:33   0:00 grep insecure_service
```

Se ejecuta como root

### d. Abra localhost:8080 en el navegador y explore los links provistos por este servicio.

Se accedió al servicio con `wget -qO- http://localhost:8080` (no hay entorno gráfico en la VM). El menú tiene tres secciones: Home (`/`), Recursos (`/resources/`) y Memoria (`/mem/`).
- En la sección Recursos se observa que, al correr como root, el servicio tiene acceso total al sistema y expone información sensible:
  - Directorio `/`: lista todo el filesystem de la máquina, incluyendo `/home`, `/root`, `/etc`, etc., y permite navegarlo.
  - Processes: lista todos los procesos del sistema (PID, usuario y nombre), no solo los suyos.
  - Network Interfaces: muestra todas las interfaces de red y sus IPs.
  - Environment Variables: expone las variables de entorno del proceso.
  - Connectivity: hace ping/curl a hosts externos.

> [!NOTE]
> Esto evidencia el problema de seguridad, un servicio "inseguro" corriendo como root, si fuera comprometido, le daría al atacante acceso a todo el sistema (archivos personales en `/home`, información de todos los procesos, etc.)

## Ejercicio 5: Configure el servicio para que se ejecute con usuario y grupo no privilegiados (en Debian y derivados se llaman nobody y nogroup). Verifique con qué UID se ejecuta el servicio usando `ps aux | grep insecure_service`.

1. `su -c "nano /etc/systemd/system/insecure_service.service"`
2. agregar `User=nobody` y `Group=nogroup` en el apartado `[Service]`
3. `su -c "systemctl daemon-reload && systemctl restart insecure_service"`
4. `ps aux | grep insecure_service`
   ```bash
    so@so:~/codigo-para-practicas/practica5/insecure_service$ ps aux | grep insecure_service
    nobody      1338  0.0  0.2 1231804 4880 ?        Ssl  20:44   0:00 /opt/sistemasoperativos/insecure_service
    so          1343  0.0  0.1   6484  2136 pts/0    S+   20:46   0:00 grep insecure_service
   ```

## Ejercicio 6: Explore el directorio /home y el directorio /tmp usando el servicio y luego:

### a. Reconfigúrelo para que no pueda visualizar el contenido de /home y tenga su propio /tmp privado.

1. `su -c "nano /etc/systemd/system/insecure_service.service"`
2. En `[Service]`, `ProtectHome=true` y `PrivateTmp=true`

### b. Recargue el servicio y verifique que estas restricciones surtieron efecto.

3. `su -c "systemctl daemon-reload && systemctl restart insecure_service"`

Ahora `/home` no muestra nada y `/tmp` solo muestra el link "Up" (es un `/tmp` privado y nuevo, ya no ve ni los temporales de otros servicios ni nada del `/tmp` real)

## Ejercicio 7: Limite el acceso a información de otros procesos por parte del servicio.

1. `su -c "nano /etc/systemd/system/insecure_service.service"`
2. En `[Service]`, `ProtectProc=invisible`
3. `su -c "systemctl daemon-reload && systemctl restart insecure_service"`

>[!NOTE]
> Con `invisible`, el servicio solo verá sus propios procesos en `/proc`, no los del resto del sistema.

## Ejercicio 8: Establezca un límite de 16M al uso de memoria del servicio e intente alocar más de esa memoria en la sección "Memoria" usando el link "Aumentar Reserva de Memoria".

1. `su -c "nano /etc/systemd/system/insecure_service.service"`
2. En `[Service]`, `MemoryAccounting=true` y `MemoryMax=16M`
3. `su -c "systemctl daemon-reload && systemctl restart insecure_service"`

```bash
so@so:~$ systemctl status insecure_service | grep -i memory
Memory: 2.4M (max: 16.0M available: 13.5M)
```

Tras varias llamadas a `/mem/alloc`, el servicio intenta reservar más de 16M y el kernel lo **mata por OOM**. Se confirma con el log (como root):

```bash
so@so:~$ su -c "journalctl -u insecure_service -n 20 --no-pager"
...
insecure_service.service: Main process exited, code=killed, status=9/KILL
insecure_service.service: Failed with result 'signal'.
```

El `status=9/KILL` es la señal **SIGKILL** que envía el kernel al superar `MemoryMax`. Es un límite **duro**: a diferencia de `MemoryHigh` (que solo ralentiza), `MemoryMax` no deja pasar el límite y termina el proceso.

>[!NOTE]
> Con `MemoryAccounting=true` se habilita la contabilidad de memoria vía cgroups (necesaria para aplicar el límite), y `MemoryMax=16M` fija el tope duro.

