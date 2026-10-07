# Deadlocks (Interbloqueos)

> Infograma de repaso - Sistemas Operativos (UNLP)

## Definicion

Un conjunto de procesos esta en **deadlock** cuando cada proceso del conjunto esta **bloqueado**, reteniendo recursos y **esperando** un recurso que esta retenido por otro proceso del mismo conjunto. Ninguno avanza ni libera lo suyo (*abrazo mortal*: A tiene lo que B pide y B tiene lo que A pide).

## Recursos

- **Fisicos** (CPU, memoria, dispositivos) / **Logicos** (archivos, registros, semaforos).
- **Apropiables / preemptibles**: se pueden quitar sin dano (memoria, CPU).
- **No apropiables**: si se quitan, el proceso falla (escritura a CD/impresora a medias).
- Un recurso `Rj` puede tener varias **instancias** identicas (clase de recurso).

**Secuencia de uso**: 1) **Solicitar** (si no se concede, esperar) → 2) **Usar** → 3) **Liberar**.

## ⭐ Las 4 condiciones de Coffman (1971)

> **Deben darse las CUATRO simultaneamente.** Si falta una sola, NO hay deadlock (base de la prevencion).

1. **Exclusion mutua**: el recurso no es compartible; solo un proceso lo usa a la vez.
2. **Retencion y espera** (*hold and wait*): el proceso mantiene recursos asignados mientras espera otros.
3. **No apropiacion** (*no preemption*): no se pueden quitar los recursos a quien los posee.
4. **Espera circular** (*circular wait*): lista circular de procesos donde cada uno espera un recurso del siguiente.

## ⭐ Grafo de asignacion de recursos

- **Nodos**: procesos `Pi` y recursos `Rj` (un recurso con varias instancias = varios "puntos" dentro del nodo).
- **Aristas dirigidas**:
  - `Pi → Rj`: el proceso **solicita** una instancia.
  - `Rj → Pi`: el recurso esta **asignado** al proceso.

| Estado del grafo | Resultado |
|---|---|
| **Sin ciclos** | NO hay deadlock (seguro) |
| **Con ciclo + 1 instancia/recurso** | SI hay deadlock (ciclo = necesario y **suficiente**) |
| **Con ciclo + varias instancias** | **Posibilidad** de deadlock (necesario, NO suficiente) |

## Estrategias de manejo

| Estrategia | Idea | Como |
|---|---|---|
| **Prevencion** (prevention) | Que **nunca** se cumpla una de las 4 condiciones | Restringe la forma de solicitar recursos (orden de recursos, reservar todo al inicio, spooling/virtualizar) |
| **Evitacion** (avoidance) | Asignar con cuidado segun el estado | **Algoritmo del Banquero**; conoce la demanda maxima por adelantado; nunca entra a estado inseguro |
| **Deteccion y recuperacion** | Permitir el deadlock y luego romperlo | Grafo *wait-for* (1 inst.) o banquero (varias); abortar procesos / expropiar (seleccion de victima) |
| **Avestruz** (ostrich) | **Ignorar** el problema | Asumir que casi nunca ocurre (lo usa UNIX/Windows) |

### Prevencion: como atacar cada condicion
- **Exclusion mutua** → recursos compartibles / spooling (no siempre posible).
- **Retencion y espera** → reservar TODO al inicio, o pedir solo si no tiene nada (riesgo: starvation, baja utilizacion).
- **No apropiacion** → virtualizar el recurso via un demonio que encola (spooler).
- **Espera circular** → ordenar recursos con `F: R→N`; solo pedir `Rj` si `F(Ri) < F(Rj)`.

### ⭐ Avoidance: estado seguro vs inseguro
- **Estado seguro**: existe una **cadena segura** `<P0,...,Pn>` con TODOS los procesos que pueden terminar con los recursos disponibles → **garantiza que NO hay deadlock**.
- **Estado inseguro**: no se puede construir esa cadena → **posibilidad** de deadlock (no implica deadlock seguro).
- Si hay deadlock ⇒ estoy en estado inseguro. (La reciproca NO vale.)

### ⭐ Algoritmo del Banquero (multiples instancias)
Cada proceso declara su **maximo**. El SO solo asigna si el estado resultante sigue siendo **seguro**.
- `disponible` (vector `m`): instancias libres por recurso.
- `asignacion` (matriz `n×m`): lo que cada `Pi` ya tiene.
- `max` (matriz `n×m`): maximo que `Pi` necesitara.
- `need = max − asignacion`: lo que le falta.

Busca una **secuencia segura**; si existe, el estado es seguro. Para **1 instancia** no hace falta: basta el grafo (buscar que no haya ciclos).

## Deadlock vs Starvation (inanicion)

| Deadlock | Starvation |
|---|---|
| Conjunto de procesos **bloqueados mutuamente**, ninguno progresa | Un proceso **nunca obtiene** el recurso (siempre posterga) |
| Espera **circular** entre ellos | NO requiere ciclo; suele ser por planificacion/prioridades |
| Se rompe matando/expropiando | Se evita con politicas justas (aging, FIFO) |

---

## ⚠️ Conceptos clave / posibles preguntas

- **Las 4 condiciones de Coffman** (nombrarlas y saber que las 4 deben darse a la vez). MUY preguntado.
- **Grafo de asignacion**: interpretar aristas y la regla ciclo ⇒ deadlock SOLO con 1 instancia; con varias es condicion necesaria pero NO suficiente.
- **Algoritmo del Banquero**: estructuras (`disponible`, `asignacion`, `max`, `need`), encontrar/justificar una **secuencia segura**.
- Diferencia **estado seguro vs inseguro** (inseguro ≠ deadlock; deadlock ⇒ inseguro).
- Diferencia entre las 4 **estrategias**, y como prevencion ataca cada condicion.
- **Deadlock ≠ Starvation**: deadlock = bloqueo circular mutuo; starvation = postergacion infinita sin ciclo.
- Seleccion de **victima** en recuperacion (evitar elegir siempre al mismo → starvation).
