# DTOs y proyecciones 

## Qué es un DTO y cuando usarlo 

### Ejercicio 32: ¿Que es un DTO (Data Transfer Object)? ¿Cuál es su propósito dentro de la arquitectura de una aplicación? ¿Por qué no siempre conviene devolver una entidad JPA directamente desde la capa de acceso a datos?

Un **DTO (Data Transfer Object)** es un objeto **plano**, sin lógica de negocio, cuya única finalidad es **transportar datos entre capas** (o entre sistemas) de una aplicación. Consiste en campos y, opcionalmente, getters/setters, sin métodos que modifiquen estado del dominio ni dependencias con el framework de persistencia.

**Propósito dentro de la arquitectura:**

- **Desacoplar capas.** El DTO permite que cada capa (acceso a datos, servicio, presentación, API REST) exponga solo los datos que necesita, sin filtrar detalles internos de las otras. Por ejemplo, la capa REST puede devolver un `RouteSummaryDTO` con `{name, totalPurchases, averagePrice}` sin exponer el resto de la entidad `Route` (chofers, guías, paradas, etc.).
- **Forma "a medida" del dato.** Un DTO se diseña según las necesidades del **consumidor** (una pantalla, un endpoint, un cliente externo), agrupando o transformando campos como convenga, mientras que una entidad refleja la estructura del **modelo de persistencia**, que rara vez coincide exactamente con lo que la UI o el cliente necesita.
- **Contratos estables.** Cuando se expone un DTO en un API público, su esquema queda fijo y se puede versionar independientemente. Si el modelo de dominio evoluciona, el DTO actúa como **traductor** y evita romper a los consumidores.

**Por qué no siempre conviene devolver una entidad JPA directamente:**

1. **Acoplamiento entre capas.** Si la capa de presentación recibe `Route`, queda atada al modelo de dominio y a las decisiones de mapeo JPA. Un rename de campo en la entidad, o un cambio en el `FetchType`, impacta directamente sobre el cliente. Con un DTO de por medio, el cambio queda contenido.

2. **Ciclos de serialización.** El modelo del TP tiene ciclos (`User ↔ Purchase ↔ Route ↔ User`). Al serializar una entidad managed con un serializador como Jackson, el ciclo provoca un **stack overflow** o se requieren anotaciones técnicas (`@JsonManagedReference`, `@JsonIgnore`) que ensucian el dominio. Un DTO con campos planos elimina el problema por construcción.

3. **Sobre-exposición de datos.** Las entidades suelen contener campos internos (passwords, flags de activación, claves de auditoría) que no deberían viajar al cliente. Devolver la entidad entera obliga a recordar anotaciones de filtrado en cada campo sensible, en vez de exponer solo lo necesario.

4. **Carga involuntaria por *lazy loading*.** Al serializar una entidad managed, los proxies de las relaciones se acceden e invocan consultas adicionales (problema **N+1**), que pueden disparar errores si la sesión ya está cerrada (`LazyInitializationException`) o degradar el rendimiento. El DTO se materializa una sola vez con los datos exactos requeridos.

5. **Rendimiento de las consultas.** Una proyección a DTO permite a JPA generar un `SELECT` con solo los campos necesarios (`SELECT new com.app.RouteSummaryDTO(r.name, COUNT(p), AVG(p.totalPrice)) FROM ...`), evitando traer columnas y relaciones que después se descartan.

>[!NOTE] En resumen ..
> La entidad JPA es la **representación del dominio dentro de la persistencia**, no un objeto pensado para viajar fuera de esa capa. El DTO es la herramienta para construir una vista a medida de los datos, desacoplada del modelo y segura para los consumidores externos.

### Ejercicio 33: Describir dos situaciones concretas del modelo donde devolver un DTO sería más adecuado que devolver la entidad completa. Para cada caso indicar qué campos contendría el DTO y por que.

**Situación 1: Listado público de rutas disponibles para comprar.**

Una pantalla típica de la app muestra al usuario las rutas que puede comprar, con la información mínima para decidir: nombre, precio, kilómetros y plazas disponibles. Devolver la entidad `Route` completa traería datos irrelevantes (choferes, guías, paradas, lista de compras asociadas) y forzaría a navegar relaciones que pueden disparar consultas adicionales o ciclos de serialización con `User` y `Purchase`.

```java
public record RouteListingDTO(
    Long id,
    String name,
    float price,
    float totalKm,
    int availableSlots          // maxNumberUsers - cantidad de compras existentes
) {}
```

>[!NOTE] Por qué estos campos 
> Representan lo único que el cliente necesita ver al elegir. `availableSlots` se calcula como `maxNumberUsers - COUNT(purchases)` en la propia consulta JPQL (`SELECT new ...RouteListingDTO(r.id, r.name, r.price, r.totalKm, r.maxNumberUsers - COUNT(p)) FROM Route r LEFT JOIN r.purchases p GROUP BY r`), evitando que el cliente reciba el dato bruto y tenga que recomputarlo.

**Situación 2: Perfil del usuario autenticado.**

Cuando un usuario consulta su propio perfil, devolver la entidad `User` completa expondría su `password` y arrastraría la `purchaseList` entera (que puede ser muy grande). Además, en el modelo `User` tiene subclases (`DriverUser`, `TourGuideUser`), y la presentación no necesariamente quiere conocer esa jerarquía.

```java
public record UserProfileDTO(
    Long id,
    String username,
    String fullName,
    String email,
    String phoneNumber,
    Date birthdate,
    int totalPurchases          // tamaño de la lista, sin traer la lista
) {}
```

>[!NOTE] Por qué estos campos
> Son la información de contacto y resumen que la UI muestra en "mi cuenta". Se excluye explícitamente `password` (sensible) y se reemplaza la `purchaseList` completa por un contador (`COUNT(p)`), lo que evita cargar todas las compras a memoria. Si el cliente luego quiere el detalle, hay un endpoint paginado separado.

### Ejercicio 34: ¿Qué riesgos concretos tiene exponer entidades JPA directamente como respuesta de un servicio o endpoint? Mencionar al menos: ciclos de serialización y acoplamiento entre capas.

Exponer entidades JPA hacia afuera de la capa de persistencia trae varios riesgos concretos:

**1. Ciclos de serialización.**

El modelo del TP tiene relaciones bidireccionales que forman ciclos: `User → purchases → Purchase → user → ...`, `Route → drivers → DriverUser → routes → ...`. Cuando un serializador como Jackson recorre el grafo para producir JSON, recursivamente vuelve sobre los mismos objetos y termina lanzando `StackOverflowError` (o un `JsonMappingException: Infinite recursion`). Las "soluciones" típicas son anotaciones técnicas sobre las entidades del dominio (`@JsonManagedReference`/`@JsonBackReference`, `@JsonIgnore`, `@JsonIdentityInfo`), que **mezclan responsabilidades**, la entidad de dominio termina describiendo cómo se serializa para el API, contaminando el modelo con detalles de presentación.

**2. Acoplamiento entre capas.**

Si la capa de presentación (controller, vista, cliente externo) recibe la entidad, queda atada a su forma exacta. Cualquier cambio en el modelo de dominio se propaga, renombrar `fullName` a `name` rompe el contrato del API, agregar un `FetchType.EAGER` cambia el payload sin que nadie lo note, mover un campo a una superclase modifica la jerarquía visible. El DTO actúa de **traductor estable**: el dominio puede evolucionar sin romper a los consumidores.

**3. Sobre-exposición de datos sensibles.**

`User.password`, `Supplier.authorizationNumber`, flags de auditoría, soft-delete (`deletedAt`), información interna... todo viaja al cliente por defecto. Hay que recordar anotar campo por campo con `@JsonIgnore` y aceptar que un olvido futuro filtre datos. Con un DTO, **solo viaja lo que está declarado en el DTO**, y los campos sensibles ni siquiera entran al universo posible.

**4. Carga involuntaria por *lazy loading* y N+1.**

Las entidades suelen tener relaciones marcadas como `LAZY` (`Purchase → items`, `User → purchaseList`). Cuando el serializador accede a una colección lazy, se dispara una consulta adicional **por cada elemento** padre que se está serializando, generando el clásico problema **N+1** o un `LazyInitializationException` si la sesión ya fue cerrada (típico al serializar fuera de la transacción). El DTO se materializa de una sola consulta con los datos exactos.

**5. Riesgo de modificación accidental al recibir entidades como input.**

El espejo del problema anterior: si el endpoint **recibe** una entidad JPA en lugar de un DTO, un cliente malicioso podría enviar campos que no debería poder modificar (`id`, `password`, flags de admin, totales calculados). Esto se conoce como **mass assignment vulnerability**. Con un DTO de entrada, solo los campos declarados son aceptados.

**6. Dependencia del mecanismo de persistencia en el contrato externo.**

Los proxies de Hibernate, los enums mapeados con `@Enumerated`, el comportamiento de `equals`/`hashCode` basado en `id`, etc., se cuelan en la serialización y producen JSON con campos extra (`hibernateLazyInitializer`, `handler`) que **revelan detalles internos** del ORM al cliente. Esto ata el contrato al producto de persistencia elegido.

>[!NOTE] En resumen
> Los riesgos no son solo de "limpieza", sino que abarcan **errores en runtime** (ciclos, N+1, *lazy exceptions*), **seguridad** (sobre-exposición, *mass assignment*) y **mantenibilidad** (acoplamiento al modelo). El DTO los elimina por construcción, definiendo explícitamente qué entra y qué sale de cada capa.

## Implementación

### Ejercicio 35: Definir e implementar un DTO que resuma información de las rutas del modelo: nombre de la ruta, cantidad de compras realizadas y el precio promedio de esas compras. Implementar la consulta correspondiente en RouteRepository.

**1. Definición del DTO.**

Se crea un nuevo paquete `unlp.info.bd2.dto`. El DTO se modela como un **record** de Java, es inmutable, no tiene anotaciones JPA y solo expone los tres campos requeridos.

```java
package unlp.info.bd2.dto;

public record RouteSummaryDTO(
    String name,
    long totalPurchases,
    double averagePrice
) {}
```

**2. Consulta en `RouteRepository`.**

Se implementa con `@Query` usando **constructor projection** de JPQL (`SELECT new ...`), que invoca directamente al constructor del DTO con los valores agregados. Se usa `LEFT JOIN` para incluir también las rutas sin compras (en cuyo caso `totalPurchases = 0` y `averagePrice` queda en `null`/`0`).

```java
@Query("SELECT new unlp.info.bd2.dto.RouteSummaryDTO(" +
        "    r.name, " +
        "    COUNT(p), " +
        "    COALESCE(AVG(p.totalPrice), 0.0)) " +
        "FROM Route r LEFT JOIN Purchase p ON p.route = r " +
        "GROUP BY r.id, r.name")
List<RouteSummaryDTO> getRoutesSummary();
```

Notas sobre la consulta:

- **`SELECT new <FQN>(...)`** requiere el **nombre totalmente cualificado** del DTO (`unlp.info.bd2.dto.RouteSummaryDTO`) y que exista un constructor que acepte exactamente esos tipos.
- **`COUNT(p)`** cuenta compras por ruta. Como el `LEFT JOIN` puede dejar `p` en `null` para rutas sin compras, `COUNT(p)` devuelve `0` correctamente (ignora los nulos).
- **`COALESCE(AVG(p.totalPrice), 0.0)`** evita que el promedio sea `null` para rutas sin compras, devolviendo `0.0` en ese caso.
- **`GROUP BY r.id, r.name`** agrupa por ruta. Incluir el `id` además del `name` evita ambigüedad si dos rutas distintas comparten nombre.
- Se proyecta directamente al DTO desde la base de datos: JPA genera **un solo `SELECT`** con las columnas necesarias, sin traer las entidades completas (no hay N+1 ni lazy loading).

**3. Uso desde el servicio.**

```java
@Override
@Transactional(readOnly = true)
public List<RouteSummaryDTO> getRoutesSummary() {
    return routeRepository.getRoutesSummary();
}
```

El método se anota con `@Transactional(readOnly = true)` porque solo lee y aprovecha las optimizaciones descritas en el Ejercicio 29. El DTO viaja del repositorio al servicio (y, eventualmente, al controller) sin necesidad de mapeo manual.

