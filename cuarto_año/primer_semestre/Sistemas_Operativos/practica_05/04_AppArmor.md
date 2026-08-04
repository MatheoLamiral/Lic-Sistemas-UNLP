# AppArmor

## Ejercicio 9: Instale las herramientas de espacio de usuario, perfiles por defecto de app-armor y auditd (necesario para generar perfiles de forma interactiva).

```bash
 su -c "apt install -y apparmor apparmor-profiles apparmor-utils auditd" 
```

## Ejercicio 10: Verifique si apparmor se encuentra habilitado con el comando `aa-enabled`. Si no se encuentra habilitado verifique el kernel que está ejecutando (el kernel de Debian de la VM lo trae habilitado por defecto).

```bash
so@so:~$ aa-enabled
S?
```

## Ejercicio 11: Utilice la herramienta `aa-status` para determinar:

```bash
so@so:~$ su -c "/usr/sbin/aa-status"
Contraseña: 
apparmor module is loaded.
31 profiles are loaded.
10 profiles are in enforce mode.
   /usr/bin/man
   /usr/lib/NetworkManager/nm-dhcp-client.action
   /usr/lib/NetworkManager/nm-dhcp-helper
   /usr/lib/connman/scripts/dhclient-script
   /{,usr/}sbin/dhclient
   lsb_release
   man_filter
   man_groff
   nvidia_modprobe
   nvidia_modprobe//kmod
21 profiles are in complain mode.
   avahi-daemon
   dnsmasq
   dnsmasq//libvirt_leaseshelper
   identd
   klogd
   mdnsd
   nmbd
   nscd
   php-fpm
   ping
   samba-bgqd
   samba-dcerpcd
   samba-rpcd
   samba-rpcd-classic
   samba-rpcd-spoolss
   smbd
   smbldap-useradd
   smbldap-useradd///etc/init.d/nscd
   syslog-ng
   syslogd
   traceroute
0 profiles are in kill mode.
0 profiles are in unconfined mode.
2 processes have profiles defined.
2 processes are in enforce mode.
   /usr/sbin/dhclient (363) /{,usr/}sbin/dhclient
   /usr/sbin/dhclient (364) /{,usr/}sbin/dhclient
0 processes are in complain mode.
0 processes are unconfined but have a profile defined.
0 processes are in mixed mode.
0 processes are in kill mode.
```

### a. ¿Cuántos perfiles se encuentran cargados?

- Se encuentran cargados 31 perfiles
  - 10 en modo enforce (bloquean lo non permitido)
  - 21 en modo complain (solo registran/avisan, non bloquean)

### b. ¿Cuántos procesos y cuáles procesos de tu sistema tienen perfiles definidos?

- 2 procesos tienen perfiles definidos y ambos en modo enforce:
  -  `/usr/sbin/dhclient` (PID 363)
  -  `/usr/sbin/dhclient` (PID 364)

## Ejercicio 12: Detenga y deshabilite el servicio insecure_service creado en la parte 1 de la práctica de forma que no vuelva a iniciarse automáticamente.

```bash
su - -c "systemctl stop insecure_service.service && systemctl disable insecure_service.service"
```

## Ejercicio 13: Ejecute `insecure_service` manualmente usando el usuario root y verifique que puede acceder libremente al filesystem en http://localhost:8080 (o la IP correspondiente donde se ejecuta el servicio).

```bash
so@so:~$ su - -c "/opt/sistemasoperativos/insecure_service"
Contraseña: 
2026/08/04 09:42:23 Servidor iniciado en http://0.0.0.0:8080
```

Chequeamos con `wget -qO- "http://localhost:8080/resources///home"` y `wget -qO- "http://localhost:8080/resources///root"`
 

## Ejercicio 14: Generación de un nuevo profile:

### a. Ejecutar aa-genprof /…

```bash
so@so:~$ su - -c "aa-genprof /opt/sistemasoperativos/insecure_service"
Contraseña: 
Updating AppArmor profiles in /etc/apparmor.d.
        no es un ejecutable dinámico
Writing updated profile for /opt/sistemasoperativos/insecure_service.
Estableciendo /opt/sistemasoperativos/insecure_service al modo reclamar.

Before you begin, you may wish to check if a
profile already exists for the application you
wish to confine. See the following wiki page for
more information:
https://gitlab.com/apparmor/apparmor/wikis/Profiles

Profiling: /opt/sistemasoperativos/insecure_service

Please start the application to be profiled in
another window and exercise its functionality now.

Once completed, select the "Scan" option below in 
order to scan the system logs for AppArmor events. 

For each AppArmor event, you will be given the 
opportunity to choose whether the access should be 
allowed or denied.

[(S)can system log for AppArmor events] / (F)inalizar
```

### b. Abrir otra terminal, ejecutar insecure_service y navegue el sistema de archivos usando la interfaz web provista por el servicio.

```bash
so@so:~$ su - -c "/opt/sistemasoperativos/insecure_service"
Contraseña: 
2026/08/04 09:48:02 Servidor iniciado en http://0.0.0.0:8080
```

Despues:
- `wget -qO- "http://localhost:8080/"`
- `wget -qO- "http://localhost:8080/resources/"          # lista / y hace conexiones`
- `wget -qO- "http://localhost:8080/resources///proc"     # lista /proc`


### c. Genere un perfil que permita:

Con el servicio ya activo (punto b), en la terminal de `aa-genprof` activamos el Scan y se responde cada evento detectado. A las lecturas internas (libs, `/etc/ld.so.cache`, `/sys/...`, `/proc/sys/...`) se les responde **`I`** (Ignore) porque las cubre `abstractions/base`, y a las capabilities (`net_admin`) **`D`** (Deny) por ser privilegios peligrosos no requeridos. El resto se resuelve según cada inciso:

#### i. Abrir conexiones tcp ipv4

Cuando aparece el evento `Network Family: inet / Socket Type: stream`, se selecciona la opción **`network inet stream,`** (no los includes ofrecidos) y se responde **`A`** (Allow). Genera la regla:

```
network inet stream,
```

#### ii. Abrir conexiones tcp ipv6

Igual que el anterior pero para `Network Family: inet6`. Se selecciona **`network inet6 stream,`** y **`A`** (Allow):

```
network inet6 stream,
```

#### iii. El perfil debe incluir los siguientes perfiles (y ningún otro):
  1. include <abstractions/base>
  2. include <abstractions/nameservice>

`aa-genprof` ofrece varios includes (`opencl-pocl`, `apache2-common`, etc.) que **NO** se seleccionan, porque el perfil solo debe incluir `base` y `nameservice`. El `base` ya lo agrega `aa-genprof` por defecto, el `nameservice` se agrega **a mano**:

```
include <abstractions/base>
include <abstractions/nameservice>
```

#### iv. Listar el contenido de / y /proc pero no de otros subdirectorios de /

Cuando aparecen los eventos de lectura del directorio `/` y `/proc/` (vienen como `owner / r` y `owner /proc/ r`), se selecciona la regla específica (no el include), **`O`** para quitar el `owner` y luego **`A`** (Allow). Quedan las reglas:

```
/ r,
/proc/ r,
```

Estas permiten **listar** el contenido de `/` y `/proc`, pero NO acceder a sus subdirectorios (para eso haría falta `/*` o `/**`).

#### v. Ejecutar con los permisos del perfil actual (mrix) los siguientes comandos:
  1. /usr/bin/dash
  2. /usr/bin/ip
  3. /usr/bin/mawk
  4. /usr/bin/ps

Cuando aparece un evento `Ejecutar: /usr/bin/dash` (etc.), se responde **`I`** (Inherit) para que el comando se ejecute heredando el perfil actual, esto genera el modo **`mrix`**. A los ejecutables NO listados (`ping`, `curl`) se les responde **`D`** (Deny). Como `aa-genprof` solo capturó `dash`, los otros tres (`ip`, `mawk`, `ps`) se agregan **a mano**:

```
/usr/bin/dash mrix,
/usr/bin/ip mrix,
/usr/bin/mawk mrix,
/usr/bin/ps mrix,
```

---

### Perfil final

Como `aa-genprof` no captura todos los eventos, se completa el perfil **a mano** (`nano`) y se recarga con `apparmor_parser -r`. Perfil final en `/etc/apparmor.d/opt.sistemasoperativos.insecure_service`:

```
abi <abi/3.0>,

include <tunables/global>

/opt/sistemasoperativos/insecure_service {
  include <abstractions/base>
  include <abstractions/nameservice>

  deny capability net_admin,

  network inet stream,
  network inet6 stream,

  deny /usr/bin/ping x,

  / r,
  /proc/ r,

  /opt/sistemasoperativos/insecure_service mr,

  /usr/bin/dash mrix,
  /usr/bin/ip mrix,
  /usr/bin/mawk mrix,
  /usr/bin/ps mrix,
}
```

Después recargamos el perfil editado con:

```bash
su - -c "apparmor_parser -r /etc/apparmor.d/opt.sistemasoperativos.insecure_service"
```

## Ejercicio 15: Habilite el modo enforcing y verifique si funciona (aa-enforcing).

Se pone el perfil en enforce con `aa-enforce /opt/sistemasoperativos/insecure_service` y se
verifica con `aa-status`s.

Al ejecutar el servicio confinado y navegarlo, AppArmor bloquea todo lo que el perfil no
permite. En `/var/log/audit/audit.log` aparecen las denegaciones:

```
...
name="/home/" ... comm="insecure_servic"  → DENIED (el servicio no puede leer /home)
name="/etc/"  ... comm="insecure_servic"  → DENIED (ni /etc)
name="/proc/PID/stat" ... comm="ps"        → DENIED (ps, heredando el perfil, no puede leer el interior de /proc)
...
```

Solo funciona listar `/` y `/proc` (las reglas `/ r,` y `/proc/ r,`). El confinamiento está
activo, el servicio pasó de tener acceso total a estar encajonado por el perfil.


## Ejercicio 16: Si necesita volver a generar un perfil puede usar aa-complain + aa-logprof o editar el profile a mano y aplicar con apparmor_parser -r

Hay dos formas de volver a generar o ajustar un perfil ya existente:

### Método 1: `aa-complain` + `aa-logprof` (interactivo)

Útil cuando **no se sabe** qué accesos le faltan al perfil:

```bash
aa-complain /opt/sistemasoperativos/insecure_service   # 1. pasar a modo complain (no bloquea, solo registra)
# 2. ejecutar y usar el programa para generar los eventos
aa-logprof                                              # 3. lee el log y agrega reglas interactivamente
aa-enforce /opt/sistemasoperativos/insecure_service    # 4. volver a enforce
```

- `aa-complain` deja el perfil en modo **complain**: los accesos no se bloquean, solo se registran en el log.
- `aa-logprof` lee esos eventos y pregunta Allow/Deny (como `aa-genprof`), agregando las reglas nuevas al perfil.

### Método 2: Editar a mano + `apparmor_parser -r`

Útil cuando **ya se sabe** qué regla agregar/cambiar:

```bash
nano /etc/apparmor.d/opt.sistemasoperativos.insecure_service                  # editar
apparmor_parser -r /etc/apparmor.d/opt.sistemasoperativos.insecure_service    # recargar (-r = replace)
```

Es el método que se usó en el ejercicio 14 para agregar el include `nameservice` y los execs `ip`, `mawk`, `ps` que `aa-genprof` no capturó.

>[!NOTE]
> Siempre volver a **enforce** antes de dar por probado el perfil: en complain el programa accede a todo y no se estaría probando el confinamiento real.

