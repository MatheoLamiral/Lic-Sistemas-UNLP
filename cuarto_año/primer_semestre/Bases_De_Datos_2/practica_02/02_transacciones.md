# Transacciones

## Aspectos avanzados de @Transactional

### Ejercicio 29: ​¿Cuál es el atributo readOnly = true en @Transactional? ¿Qué optimizaciones activa? ¿En qué métodos del servicio conviene aplicarlo?

`readOnly = true` es un **hint** sobre la transacción que le indica a Spring (y al proveedor JPA) que el método **no va a modificar datos**. No es una restricción dura sobre la base, sino una **señal de optimización**, JPA/Hibernate y el motor de la BD aprovechan esa información para hacer la transacción más liviana.

```java
@Transactional(readOnly = true)
public List<Route> findRoutesBelowPrice(float price) {
    return routeRepository.findRoutesBelowPrice(price);
}
```

**Qué optimizaciones activa:**

- **Desactiva el dirty checking de Hibernate.** En una transacción normal, al hacer flush o commit Hibernate compara cada entidad managed con su snapshot inicial para detectar cambios y generar los `UPDATE` correspondientes. En modo `readOnly`, Hibernate **no toma ese snapshot** y omite la comparación, ahorrando memoria y CPU.
- **No emite `UPDATE` al cerrar la sesión.** Aunque alguien por error modificara una entidad managed dentro del método, los cambios **no se persisten**, evitando efectos colaterales involuntarios.
- **Habilita el modo FlushMode = MANUAL/NEVER.** Hibernate no hace flush automáticamente antes de cada query, lo que reduce escrituras innecesarias.
- **Permite al driver/motor optimizar la conexión.** Algunos motores (PostgreSQL, MySQL con réplicas) pueden enrutar la conexión a una **réplica de solo lectura** cuando ven el flag `read-only`, descargando trabajo del master.

**En qué métodos conviene aplicarlo:**

En **todos los métodos del servicio que solo leen datos**, es decir, los típicos `getXxx`, `findXxx`, `searchXxx`, `existsXxx`, `countXxx`. Concretamente, en este TP corresponderían a:

- `getAllPurchasesOfUsername`, `getCountOfPurchasesBetweenDates`, `getUserSpendingMoreThan`, `getTopNSuppliersInPurchases`, `getRoutesWithStop`, `getMaxStopOfRoutes`, `getRoutesNotSell`, `getTop3RoutesWithMaxRating`, `getMostDemandedService`, `getTourGuidesWithRating1`, etc.

Una práctica común es marcar la **clase entera** del servicio con `@Transactional(readOnly = true)` y sobreescribir solo los métodos de escritura con `@Transactional` (sin `readOnly`), invirtiendo el default para minimizar el código:

```java
@Service
@Transactional(readOnly = true)            // por defecto, todo es solo lectura
public class ToursServiceImpl implements ToursService {

    @Transactional                          // sobreescribe: este método sí escribe
    public Purchase createPurchase(...) { ... }
}
```

>[!NOTE]
> `readOnly = true` **no impide** las escrituras a nivel de base de datos por sí solo, depende del proveedor JPA y del motor para que se respete realmente. Hibernate lo respeta a nivel de su propio ciclo de vida (no genera `UPDATE`), pero un `INSERT` ejecutado por una consulta nativa podría llegar a la BD igualmente. El valor principal es **declarativo y de optimización**, no de seguridad.

### Ejercicio 30: ​¿Cómo maneja Spring el rollback automático? ¿Sobre qué tipos de excepción hace rollback por defecto? ¿Cómo se configura para el rollback? Dar un ejemplo con el modelo.

Cuando un método anotado con `@Transactional` se ejecuta, el **proxy transaccional** de Spring envuelve la llamada en un `try/catch`. Si el método termina normalmente, se hace `commit`. Si lanza una excepción que cumple con los criterios de `rollback()`, el interceptor solicita automáticamente la operacion de `rollback()` la manejador de transacciones.

**Tipos de excepciones que hacer rollback por defecto:**

- **Excepciones no comprobadas**:
  - **Spring realiza el rollback automático por defecto solo cuando se lanzan subclases de `RuntimeException`** (como `NullPointerException` , `IllegalArgumentException` o las excepciones de persistencia de Spring) y errores de tipo Error.
- **Excepciones comprobadas**: Por defecto, **Spring no realiza rollback ante excepciones que heredan directamente de `Exception`** (pero no de RuntimeException ). Estas se consideran excepciones de "negocio" que el desarrollador debe manejar sin invalidar necesariamente la transacción

**Cómo se configura:**

La anotación `@Transactional` admite dos atributos para personalizar el rollback:

- **`rollbackFor = X.class`** (o una lista de clases): fuerza el rollback ante esas excepciones, incluso si son checked.
- **`noRollbackFor = X.class`**: lo inverso, evita el rollback ante esas excepciones aunque sean unchecked.

**Ejemplo aplicado al modelo:** `createPurchase` debe revertir la transacción ante cualquier `ToursException` (por ejemplo, si el cupo de la `Route` se agotó después de validaciones previas):

```java
@Transactional(rollbackFor = ToursException.class)
public Purchase createPurchase(String routeCode, String username) throws ToursException {
    User user = userRepository.findByUsername(username)
        .orElseThrow(() -> new ToursException("Usuario inexistente"));

    Route route = routeRepository.findByCode(routeCode)
        .orElseThrow(() -> new ToursException("Ruta inexistente"));

    if (route.getMaxNumberUsers() <= route.getCurrentSold()) {
        throw new ToursException("Cupo agotado");        // dispara rollback gracias a rollbackFor
    }

    Purchase p = new Purchase(user, route, ...);
    purchaseRepository.save(p);
    return p;
}
```

Sin `rollbackFor = ToursException.class`, el `throw new ToursException("Cupo agotado")` propagaría la excepción al servicio que llamó, **pero cualquier escritura previa de esta transacción se commitearía igual** (porque la excepción es checked). Agregando el atributo, el proxy reconoce a `ToursException` como motivo válido de rollback y revierte todo lo escrito en esa transacción.

>[!NOTE]
> Una práctica común para evitar olvidos es marcar **la clase del servicio** con `@Transactional(rollbackFor = Exception.class)`, asegurando rollback ante cualquier excepción (checked o unchecked) en todos los métodos. Es lo más seguro cuando el código usa excepciones de dominio como `ToursException`.

## Adaptación de la capa de servicio 

### Ejercicio 31: ​Revisar y actualizar la capa de servicio de la Práctica 1 para que utilice los repositorios Spring Data JPA. Reemplazar todas las llamadas directas a la Session (`session.save`, `session.get`, `session.createQuery`, etc.) por las operaciones equivalentes de los repositorios. La lógica de negocio y las anotaciones `@Transactional` ya existentes no deben modificarse salvo que sea necesario por los cambios anteriores.

**Reemplazos realizados respecto del TP1:**

- **Eliminación de la dependencia con Hibernate directo.** En el TP1, el servicio inyectaba `SessionFactory` y operaba con `session.save(...)`, `session.get(Entity.class, id)`, `session.createQuery(...)`, etc. En el TP2 esas referencias **desaparecen por completo**, el servicio solo importa los repositorios (`UserRepository`, `RouteRepository`, `PurchaseRepository`, etc.).
- **Inyección por constructor de los ocho repositorios** (`UserRepository`, `RouteRepository`, `StopRepository`, `ServiceRepository`, `SupplierRepository`, `PurchaseRepository`, `ReviewRepository`, `ItemServiceRepository`), siguiendo la práctica recomendada (ver Ejercicio 13).
- **`session.save(x)` → `xxxRepository.save(x)`**, por ejemplo en `createUser`, `createStop`, `createRoute`, `createSupplier`, `createPurchase`, etc.
- **`session.get(X.class, id)` → `xxxRepository.findById(id)`**, que ahora devuelve `Optional<T>` y se desempaqueta con `.orElseThrow(() -> new ToursException(...))`. Por ejemplo en `getUserById`, `assignDriverByUsername`, `updateUser`, `deletePurchase`.
- **`session.createQuery(...)` → método del repositorio con `@Query` o Query Method**, por ejemplo `userRepository.findByUsername(username)`, `purchaseRepository.findByCode(code)`, `routeRepository.findRoutesBelowPrice(price)`.
- **`session.delete(x)` → `xxxRepository.delete(x)`**, por ejemplo en `deleteUser`, `deletePurchase`, `deleteRoute`.
- **Las consultas complejas del TP1** (`getAllPurchasesOfUsername`, `getUserSpendingMoreThan`, `getTopNSuppliersInPurchases`, `getCountOfPurchasesBetweenDates`, `getRoutesWithStop`, `getMaxStopOfRoutes`, `getRoutesNotSell`, `getTop3RoutesWithMaxRating`, `getMostDemandedService`, `getTourGuidesWithRating1`) **delegan ahora en los repositorios Spring Data**, y para las paginadas se construye un `PageRequest.of(0, n)` desde el servicio.

**Cambios menores forzados por la nueva firma de los repositorios:**

- En `updateUser` y `deleteUser` se reemplaza la comparación `== null` por `.isEmpty()` / `.orElseThrow(...)` sobre el `Optional` devuelto por `findById`.
- En `getMostDemandedService` se delega en una consulta paginada que devuelve `List<Service>`, y el servicio toma el primer elemento (`res.get(0)`) si la lista no está vacía.
- `merge()` del TP1 desaparece porque `CrudRepository.save()` ya decide internamente entre `persist` y `merge` según el estado del ID (ver ejercicio 11).

**Anotaciones `@Transactional`:**

- Los métodos de **escritura** (`createXxx`, `updateXxx`, `deleteXxx`, `assignXxx`, `addXxx`) mantienen `@Transactional` sin parámetros.
- Los métodos de **lectura** (`getXxx`, `findXxx`) se anotan con `@Transactional(readOnly = true)` aprovechando las optimizaciones descritas en el Ejercicio 29.
- La lógica de negocio (validaciones de cupo, chequeos de existencia, propagación de `ToursException`) **se conservó intacta**.

