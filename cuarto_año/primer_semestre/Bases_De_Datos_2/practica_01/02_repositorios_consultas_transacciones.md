# Repositorios, consultas y transacciones

## Patrón de acceso a datos: DAO y Repository

### Ejercicio 39: ​Definir el patrón DAO (Data Access Object) y el patrón Repository. ¿Cuál es la diferencia conceptual más importante entre ambos? ¿En qué se diferencia su rol dentro de la arquitectura de la aplicación?

- **Patrón DAO (Data Access Object)**:
  - Es un patrón de la familia *Core J2EE Patterns* cuyo objetivo es **encapsular y abstraer el acceso a una fuente de datos** (típicamente una base relacional, pero podría ser un archivo, un servicio remoto, etc.).
  - Un DAO expone operaciones CRUD orientadas a la **fuente de datos**: `insert`, `update`, `delete`, `find`, `findAll`. Su firma habla en términos del recurso que persiste (tabla, registro, fila, conexión) más que del modelo de dominio.
  - Su responsabilidad principal es traducir entre el modelo de objetos de la aplicación y la representación que entiende la fuente — manejando conexiones, statements, mapeos columna→atributo, manejo de errores SQL, etc.
  - Es un patrón **técnico**: nace de la necesidad de no acoplar la lógica de negocio con la API del mecanismo de persistencia (JDBC, JPA, JNDI, sockets…).
- **Patrón Repository** (Domain-Driven Design, Eric Evans):
  - Es un patrón de **diseño de dominio** que modela una colección de objetos persistentes como si fueran una **colección en memoria**: el código cliente trabaja con la abstracción "agregue este objeto", "buscame los que cumplan este criterio", "quitelo de la colección" sin pensar en persistencia.
  - Las operaciones de un repositorio están expresadas en el lenguaje del dominio (`getAllPurchasesOfUsername`, `getRoutesNotSell`, `getMostDemandedService`) y devuelven entidades del modelo, no DTOs ni filas crudas.
  - Su responsabilidad es **mantener la ilusión de la colección**: que el usuario del repositorio nunca tenga que pensar en transacciones, sesiones, fetch types, mapeos o queries — sólo en agregados de dominio.

- **Diferencia conceptual más importante**:
  - **Nivel de abstracción**: el DAO es un *patrón de infraestructura* (mira hacia la fuente de datos); el Repository es un *patrón de dominio* (mira hacia el modelo de negocio). Un DAO es exitoso si oculta JDBC; un Repository es exitoso si oculta **cualquier** mecanismo de persistencia y le habla al cliente como si fuera una colección Java de toda la vida.
  - Otra forma de verlo: un DAO típicamente tiene **una clase por tabla/fuente** y replica la estructura de la base; un Repository tiene **una clase por agregado del dominio** (no por tabla — un agregado puede involucrar varias tablas) y refleja la estructura del modelo de objetos.

- **Diferencia en su rol dentro de la arquitectura**:
  - El **DAO** es la interfaz que separa la *capa de acceso a datos* del resto de la aplicación. La capa de servicios (o incluso la capa de presentación, en arquitecturas más simples) lo usa directamente y razona en términos de "guardar este registro" o "leer este `ResultSet`".
  - El **Repository** vive en la *capa de dominio* (o como un puente entre dominio y persistencia, según la lectura DDD que se haga) y suele ser usado **únicamente desde la capa de servicio**, que coordina la transacción y la lógica de negocio. La presentación nunca toca un repositorio directamente: trabaja con servicios que devuelven entidades o DTOs ya consistentes.
  - En frameworks modernos (Spring Data, Hibernate JPA), el repositorio suele *implementarse* internamente con técnicas DAO (la `Session` de Hibernate es, en esencia, un DAO genérico). La diferencia, entonces, no es sólo conceptual: es **dónde y cómo se exponen las operaciones al resto del sistema**. Un repositorio bien diseñado expone operaciones del dominio aunque internamente delegue en mecanismos DAO; un DAO mal usado se filtra hacia capas de negocio y obliga a hablar de tablas y conexiones donde debería hablarse de agregados.

### Ejercicio 40: ​El patrón Repository puede pensarse como una colección de objetos en memoria que además persiste su estado. Describir cómo se implementa este concepto usando Hibernate: ¿qué responsabilidades concentra un repositorio? ¿Con qué objeto de Hibernate interactúa internamente?

- **El concepto de "colección que persiste su estado"**:
  - La metáfora central del patrón Repository es que el cliente debería poder tratar al repositorio como si fuera una colección Java (una `List`, un `Set`, un `Map`) que vive en memoria, con la diferencia de que sus modificaciones quedan automáticamente reflejadas en una base de datos. El cliente hace `repository.add(purchase)` y olvida; al volver a consultar, el objeto sigue ahí, aunque la JVM se haya reiniciado.
  - Hibernate ofrece exactamente esta abstracción a través del **`PersistenceContext`** (representado por la `Session`): mientras la sesión está abierta, las entidades managed se comportan como objetos en memoria normales, y los cambios se sincronizan con la base en el flush. El repositorio aprovecha ese mecanismo para exponer una API de "colección viva" hacia el resto del sistema.

- **¿Qué responsabilidades concentra un repositorio?**:
  - **Operaciones CRUD básicas** sobre el agregado: `save(entity)`, `findById(id)`, `findAll()`, `delete(entity)`. Son las "operaciones de colección" que cualquier `List` provee, traducidas a la jerga del dominio.
  - **Consultas de dominio expresivas**: cada repositorio publica métodos en el lenguaje del negocio (`getAllPurchasesOfUsername`, `getRoutesNotSell`, `getMostDemandedService`). Es la responsabilidad que distingue a un repositorio bien diseñado de un DAO: las queries no se filtran al cliente como SQL/HQL crudo — se ofrecen ya envueltas en métodos con nombre.
  - **Encapsular el mecanismo de persistencia**: el repositorio es la única clase que importa `org.hibernate.Session`, conoce el HQL del modelo o sabe que existe un esquema relacional debajo. Cualquier cambio futuro en el ORM (migrar a JPA puro, a Spring Data, a un *event store*) debería poder hacerse modificando sólo los repositorios.
  - **Exponer entidades del dominio**, no proyecciones técnicas. Un repositorio devuelve `Purchase`, `Route`, `User` — no `ResultSet`s, ni mapas de columnas, ni DTOs específicos de la presentación.
  - **No gestionar transacciones**: la apertura/commit de transacciones es responsabilidad de la **capa de servicio**, no del repositorio (ver ejercicio 43). El repositorio asume que está corriendo dentro de una transacción ya abierta y se limita a usar la `Session` actual.

- **¿Con qué objeto de Hibernate interactúa internamente?**:
  - El objeto central es la **`Session`** (`org.hibernate.Session`), obtenida típicamente vía `sessionFactory.getCurrentSession()`. La `Session` es el `PersistenceContext` de Hibernate y ofrece los métodos sobre los que se construyen todas las operaciones del repositorio:
    - `session.persist(entity)` / `session.save(entity)` — para `save`.
    - `session.get(Class, id)` / `session.find(Class, id)` — para `findById`.
    - `session.createQuery("from Entity", Entity.class).getResultList()` — para `findAll` y consultas custom.
    - `session.remove(entity)` / `session.delete(entity)` — para `delete`.
    - `session.merge(entity)` — para reconciliar entidades detached.
  - La `Session` se obtiene a través de la **`SessionFactory`**, que se inyecta en el repositorio (en el TP, vía Spring `@Autowired`). La `SessionFactory` es la que mantiene el pool de conexiones, el mapping y la configuración global; cada operación del repositorio le pide la `Session` "actual" — la asociada al hilo/transacción en curso.
  - Un esqueleto típico:

    ```java
    @Repository
    public class PurchaseRepository {

        @Autowired
        private SessionFactory sessionFactory;

        private Session session() {
            return sessionFactory.getCurrentSession();
        }

        public Purchase save(Purchase purchase) {
            session().persist(purchase);
            return purchase;
        }

        public Purchase findById(Long id) {
            return session().get(Purchase.class, id);
        }

        public List<Purchase> findAll() {
            return session().createQuery("from Purchase", Purchase.class).getResultList();
        }

        public void delete(Purchase purchase) {
            session().remove(purchase);
        }
    }
    ```

> [!NOTE]
> La diferencia entre `openSession()` y `getCurrentSession()` (discutida en el ejercicio 7 del archivo `00_introduccion_ORM.md`) es relevante acá: `getCurrentSession()` devuelve la `Session` ligada a la transacción en curso, evitando que cada repositorio abra y cierre su propia sesión. Esto es lo que permite que múltiples llamadas a distintos repositorios dentro de un mismo método de servicio compartan el mismo `PersistenceContext` y, por lo tanto, se vean los cambios entre sí sin tener que hacer flush manual.

### Ejercicio 41: ​Implementar un repositorio por cada entidad del modelo (PurchaseRepository, RouteRepository, UserRepository, ServiceRepository, SupplierRepository, ReviewRepository). Cada repositorio debe incluir al menos las operaciones básicas: guardar, buscar por ID, listar todos y eliminar. Utilizar la Session de Hibernate en cada implementación, tal como se ha explicado previamente utilizando el método getCurrentSession() sobre la SessionFactory (genere una inyección de este objeto tal como se muestra en el código de ejemplo proporcionado)

Como las seis entidades comparten exactamente las mismas operaciones básicas (`save`, `findById`, `findAll`, `delete`), conviene factorizar la lógica común en una **clase base genérica** y dejar a cada repositorio concreto sólo la declaración de su tipo. Esto evita duplicar el `SessionFactory` y la lógica de las operaciones CRUD en seis lugares distintos, y mantiene a cada repositorio listo para crecer con consultas específicas del dominio (ejercicio 46).

#### Clase base genérica

```java
package com.tp.bbdd2.tours.repositories;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;

public abstract class AbstractRepository<T> {

    @Autowired
    private SessionFactory sessionFactory;

    private final Class<T> entityClass;

    protected AbstractRepository(Class<T> entityClass) {
        this.entityClass = entityClass;
    }

    protected Session session() {
        return sessionFactory.getCurrentSession();
    }

    public T save(T entity) {
        session().persist(entity);
        return entity;
    }

    public T findById(Long id) {
        return session().get(entityClass, id);
    }

    public List<T> findAll() {
        return session()
            .createQuery("from " + entityClass.getSimpleName(), entityClass)
            .getResultList();
    }

    public void delete(T entity) {
        session().remove(entity);
    }
}
```

Notar que:

- La `SessionFactory` se inyecta una sola vez en la clase base, vía `@Autowired`.
- `session()` siempre devuelve la `Session` ligada a la transacción en curso (`getCurrentSession()`), nunca abre una nueva — la apertura de transacciones es responsabilidad de la capa de servicio (ejercicio 43).
- `findAll()` arma el HQL dinámicamente a partir del `Class<T>` para no tener que repetirlo en cada subclase.
- No hay `@Transactional` en este nivel: los repositorios no manejan transacciones.

#### Repositorios concretos

Cada repositorio extiende la clase base y queda mínimo. Sólo se diferencian en el tipo y, eventualmente, en las consultas custom que se agreguen.

```java
@Repository
public class PurchaseRepository extends AbstractRepository<Purchase> {
    public PurchaseRepository() { super(Purchase.class); }

    // Consultas específicas del ejercicio 46 se agregan acá:
    // List<Purchase> getAllPurchasesOfUsername(String username) { ... }
    // int getCountOfPurchasesBetweenDates(Date start, Date end) { ... }
}

@Repository
public class RouteRepository extends AbstractRepository<Route> {
    public RouteRepository() { super(Route.class); }

    // List<Route> getRoutesWithStop(Stop stop) { ... }
    // int getMaxStopOfRoutes() { ... }
    // List<Route> getRoutesNotSell() { ... }
    // List<Route> getTop3RoutesWithMaxRating() { ... }
}

@Repository
public class UserRepository extends AbstractRepository<User> {
    public UserRepository() { super(User.class); }

    // List<User> getUserSpendingMoreThan(float mount) { ... }
    // List<User> getUsersWithMoreThanNPurchases(int n) { ... }
    // List<TourGuideUser> getTourGuidesWithRating1() { ... }
}

@Repository
public class ServiceRepository extends AbstractRepository<Service> {
    public ServiceRepository() { super(Service.class); }

    // Service getMostDemandedService() { ... }
}

@Repository
public class SupplierRepository extends AbstractRepository<Supplier> {
    public SupplierRepository() { super(Supplier.class); }

    // List<Supplier> getTopNSuppliersInPurchases(int n) { ... }
}

@Repository
public class ReviewRepository extends AbstractRepository<Review> {
    public ReviewRepository() { super(Review.class); }
}

@Repository
public class StopRepository extends AbstractRepository<Stop> {
    public StopRepository() { super(Stop.class); }
}

@Repository
public class ItemServiceRepository extends AbstractRepository<ItemService> {
    public ItemServiceRepository() { super(ItemService.class); }
}
```

Con esto, cada repositorio del modelo expone las cuatro operaciones básicas pedidas por el enunciado (`save`, `findById`, `findAll`, `delete`) usando la `Session` actual de Hibernate vía `getCurrentSession()`. Aunque el enunciado original lista seis repositorios, la implementación final incluye también `StopRepository` e `ItemServiceRepository` porque varios casos de uso (creación de rutas, finders por nombre de parada, persistencia explícita del ítem desde el servicio) los requieren.

> [!NOTE]
> Además de los CRUD básicos, `AbstractRepository` expone también `merge(T entity)` (delegando en `session.merge`). Lo usa `ToursServiceImpl.updateUser` para reasociar entidades detached que llegan desde los tests, y se discute con más detalle en el ejercicio 44.

> [!NOTE]
> Detalles de diseño relevantes:
> - **`@Repository`** (no `@Component`) marca la clase como bean de Spring y además habilita la traducción automática de excepciones nativas de persistencia (`HibernateException`, `SQLException`) a `DataAccessException` de Spring. Es lo que se espera para una capa de acceso a datos en una arquitectura Spring estándar.
> - **`persist` vs `save`**: se usa `persist` (estándar JPA) y no `save` (API nativa de Hibernate, deprecada en versiones recientes). Funcionalmente similar para inserciones unitarias, pero `persist` es portable.
> - **`remove` vs `delete`**: misma lógica — `remove` es el método estándar JPA; `delete` es el legado de Hibernate.
> - El repositorio asume que la entidad pasada a `delete` está **managed** (es decir, que viene de una `findById` previa o de una creación dentro de la misma transacción). Para borrar por ID directamente sin cargar la entidad, hay que hacer `findById` + `remove`, lo cual es lo correcto en la mayoría de los casos: garantiza que las cascadas y los listeners JPA corran como corresponde.

## Transacciones

### Ejercicio 42: ​¿Que es una transacción en el contexto de Hibernate? ¿Por qué es necesaria? ¿Qué ocurre si se realizan operaciones de escritura sin una transacción activa?

- **¿Qué es una transacción en el contexto de Hibernate?**:
  - Una transacción es la **unidad atómica de trabajo** sobre la base de datos: un conjunto de operaciones que se ejecutan como un todo y deben cumplir las propiedades ACID (atomicidad, consistencia, aislamiento, durabilidad). O se aplican todas con éxito (`commit`), o no se aplica ninguna (`rollback`).
  - Hibernate la representa con la interfaz **`org.hibernate.Transaction`**, obtenida desde la `Session` (`session.beginTransaction()`). Por debajo, esa transacción se delega al motor de la base (vía JDBC), donde se traduce a `START TRANSACTION`/`COMMIT`/`ROLLBACK`. La transacción de Hibernate es entonces una fachada sobre la transacción nativa del motor — no es una segunda transacción "lógica" superpuesta.
  - En aplicaciones Spring (como el TP), la transacción se gestiona declarativamente con `@Transactional` en la capa de servicio. Spring se encarga de abrirla, hacer `commit` al final del método si todo salió bien, y `rollback` si la ejecución arroja una excepción no chequeada (`RuntimeException`). Internamente sigue siendo la misma `Transaction` JDBC, sólo coordinada por Spring en lugar de por código manual.
  - Adicionalmente, la transacción de Hibernate marca el **alcance del `PersistenceContext`** (la `Session`): el `getCurrentSession()` devuelve siempre la misma `Session` mientras dure la transacción, y al hacer commit Hibernate **flushea** los cambios pendientes (los `INSERT`/`UPDATE`/`DELETE` acumulados en memoria) sincronizándolos con la base.

- **¿Por qué es necesaria?**:
  - **Atomicidad ante operaciones múltiples**: una sola operación de negocio puede involucrar varias filas o varias tablas (por ejemplo, registrar una `Purchase` implica insertar la fila de la compra, insertar sus `ItemService`, posiblemente actualizar el saldo del usuario, etc.). Sin una transacción que las englobe, una falla a mitad de camino dejaría la base en un estado inconsistente — la mitad de las inserciones aplicadas, la otra mitad no.
  - **Consistencia ante errores**: si algo falla (excepción de la aplicación, violación de FK, caída de conexión), el motor revierte automáticamente todo lo hecho dentro de la transacción al hacer `rollback`. El estado previo se preserva.
  - **Aislamiento entre usuarios concurrentes**: la transacción define qué cambios ve cada cliente concurrente. Sin ella, un usuario podría leer datos parcialmente escritos por otro (lecturas sucias, fantasmas, etc.). El nivel de aislamiento (READ COMMITTED, REPEATABLE READ, etc.) se configura precisamente sobre la transacción.
  - **Coordinación con el `PersistenceContext` de Hibernate**: el `flush` automático que Hibernate hace al hacer commit es lo que sincroniza los cambios en memoria con la base. Sin transacción no hay momento bien definido para hacer ese flush, y los cambios pueden quedar en limbo o aplicarse de manera impredecible.
  - **Durabilidad**: una vez confirmada (`commit`), la base garantiza que los cambios sobreviven a fallos del sistema. Sin transacción explícita, esa garantía no está bien definida desde el punto de vista de la aplicación.

- **¿Qué ocurre si se realizan operaciones de escritura sin una transacción activa?**:
  - El comportamiento depende de la versión de Hibernate y de la configuración, pero las posibilidades concretas son:
    - **Excepción al intentar el flush**: en Hibernate 5+ con la configuración por defecto, llamar a `session.persist(...)`, `session.merge(...)` o `session.remove(...)` fuera de una transacción **lanza una excepción** (`TransactionRequiredException` o similar) cuando llega el momento de sincronizar con la base. La operación nunca se aplica.
    - **Modo "auto-commit" implícito**: en configuraciones más laxas, JDBC puede operar en modo *auto-commit*, donde cada sentencia se confirma de inmediato como una transacción de un solo paso. Esto **rompe la atomicidad**: si una operación de negocio implica varios `INSERT`s y falla a mitad de camino, los primeros quedan persistidos sin manera de revertirlos. Es un escenario peligroso y desaconsejado.
    - **Cambios "fantasma" en memoria**: si la operación no llega a flushearse (porque nunca se cierra la sesión correctamente), los cambios quedan sólo en el `PersistenceContext` y se descartan al cerrar la `Session` sin commit. La base no recibe nada, pero el código vio el objeto "managed" como si se hubiera guardado — bug silencioso difícil de diagnosticar.
  - En el contexto del TP (Spring + Hibernate con `getCurrentSession()`), la condición habitual es que `getCurrentSession()` requiere una transacción activa para funcionar. Si se invoca desde código que no está bajo `@Transactional`, lanza `HibernateException: No Session found for current thread`. Es Spring negándose a entregar una `Session` que no estaría asociada a una unidad de trabajo bien definida.

> [!NOTE]
> El `flush` automático no implica `commit`: Hibernate puede flushear varias veces dentro de una misma transacción (por ejemplo, antes de una query, para asegurar que los cambios pendientes se apliquen y la query los vea). El commit ocurre una sola vez al final, cuando se cierra la unidad de trabajo. Confundir flush con commit lleva a creer que los cambios son persistentes cuando en realidad todavía pueden revertirse con un rollback.

### Ejercicio 43: ​¿En qué capa de la aplicación debería gestionarse la transacción: en el repositorio o en la capa de servicio? Justificar la elección. ¿Qué ocurre si una misma operación necesita de varios accesos a la base de datos?

La transacción debe gestionarse en la **capa de servicio**, nunca en el repositorio. La justificación se apoya en varios argumentos concretos:

- **La transacción es una decisión de negocio, no de acceso a datos**:
  - Una operación de negocio define qué cambios deben aplicarse "todos o ninguno". Por ejemplo, registrar una `Purchase` con sus `ItemService` es una sola unidad lógica: si falla la inserción de un ítem, la compra entera debe deshacerse. Esa frontera la conoce la capa de servicio (sabe cuál es el caso de uso completo); el repositorio no — sólo conoce la operación atómica que se le pide.
  - Si el repositorio gestionara su propia transacción, cada llamada (`save`, `delete`, etc.) abriría y cerraría una transacción independiente. La atomicidad del caso de uso se rompería: un fallo a mitad de camino dejaría parte de los cambios persistidos y parte no.
- **Un caso de uso típicamente involucra varios repositorios**:
  - Por ejemplo, "agregar un ítem a una compra" toca `PurchaseRepository` (recuperar la compra), `ServiceRepository` (recuperar el servicio) y eventualmente vuelve a `PurchaseRepository` (persistir el ítem por cascada). Si cada repositorio abriera su propia transacción, no habría una sola unidad de trabajo que englobe el caso de uso completo, y el aislamiento entre operaciones se perdería.
  - Con la transacción en el servicio, los tres repositorios reciben la **misma `Session`** vía `getCurrentSession()`, comparten el mismo `PersistenceContext` y al hacer commit (al final del método de servicio) los cambios se aplican atómicamente.
- **Coherencia con el patrón Repository**:
  - Como se discutió en el ejercicio 40, una de las responsabilidades **explícitamente excluidas** del repositorio es la gestión transaccional. El repositorio asume que está corriendo dentro de una transacción ya abierta. Esta división es lo que permite que un mismo repositorio pueda usarse en distintos casos de uso (cada uno con su propia transacción) sin acoplarse a la duración de ninguno.
- **Cómo se implementa concretamente**:
  - En Spring + Hibernate, basta con anotar los métodos del servicio con `@Transactional`. Spring abre la transacción al entrar al método, hace `commit` al salir si todo fue bien, y `rollback` si se lanza una `RuntimeException`. Los repositorios invocados por dentro reusan automáticamente esa transacción vía `getCurrentSession()`.

  ```java
  @Service
  public class PurchaseService {
      @Autowired private PurchaseRepository purchaseRepo;
      @Autowired private ServiceRepository serviceRepo;

      @Transactional
      public ItemService addItemToPurchase(Long purchaseId, Long serviceId, int quantity, float price) {
          Purchase purchase = purchaseRepo.findById(purchaseId);
          Service service = serviceRepo.findById(serviceId);
          ItemService item = new ItemService(service, quantity, price);
          purchase.addItem(item, price);
          // No hace falta llamar a save: cascade PERSIST + persistencia por alcance hacen el resto.
          return item;
      }
  }
  ```

- **¿Qué ocurre si una misma operación necesita varios accesos a la base de datos?**:
  - Si la transacción está en la **capa de servicio** (lo correcto), todas las llamadas a la base hechas dentro del método transaccional viajan en la misma transacción. Sea cual sea la cantidad de queries, todas se confirman o se descartan juntas. Además, comparten el `PersistenceContext`: una entidad cargada por el primer repositorio queda managed para el siguiente, evitando consultas redundantes.
  - Si la transacción estuviera en el **repositorio**, cada llamada abriría su propia transacción independiente. Esto rompe la atomicidad (los primeros cambios pueden quedar persistidos aunque el último falle), rompe el aislamiento (otro hilo podría leer estados intermedios entre operaciones del mismo caso de uso) y multiplica los costos (cada commit JDBC tiene overhead — abrir/cerrar transacciones para cada `save` saturaría la base bajo carga).
  - Adicionalmente, **fuera de transacción no hay `PersistenceContext` compartido**: cada `findById` cargaría la entidad, la marcaría como detached al cerrarse la transacción, y la siguiente operación recibiría una entidad "vieja" sin posibilidad de aprovechar los cambios en memoria. La metáfora del repositorio como "colección que persiste su estado" deja de funcionar.

> [!NOTE]
> El alcance de `@Transactional` se hereda por defecto de los métodos del servicio anotados, no de los repositorios. Si se quiere ser explícito, se puede usar `@Transactional(readOnly = true)` en consultas y `@Transactional` (escritura) en operaciones de modificación: Spring usa esa pista para optimizar el flush y para que el motor pueda elegir un nivel de aislamiento más liviano en lecturas.

> [!NOTE]
> Si un método de servicio llama a otro método de servicio, ambos comparten la transacción por defecto (propagación `REQUIRED`). Si por alguna razón se necesita aislamiento entre los dos (por ejemplo, que el segundo se commitee aunque el primero haga rollback), se configura con `@Transactional(propagation = REQUIRES_NEW)`. Esos casos son raros — la regla general es **una transacción por caso de uso**.

### Ejercicio 44: ​Implementar una capa de servicio que coordine las operaciones del modelo usando transacciones correctamente. Como mínimo implementar:​

Siguiendo el criterio del ejercicio 43 (transacción en la capa de servicio, no en el repositorio), la capa de servicio se materializa en una única clase `ToursServiceImpl` (anotada con `@Service`) que implementa la interfaz `ToursService`. Esta clase inyecta por constructor los ocho repositorios granulares del ejercicio 41 y anota cada método público con `@Transactional`. Los snippets que aparecen abajo (un "servicio por agregado") son una **vista didáctica**: el código real consolida todo en `ToursServiceImpl` para satisfacer el contrato `ToursService` que consumen los tests provistos (`ToursApplicationTests`, `ToursQuerysTests`).

> [!NOTE]
> **Traducción de excepciones**. `ToursServiceImpl` envuelve cada `create*`/`update*`/`delete*` en `try { ... } catch (RuntimeException e) { throw new ToursException("Constraint Violation"); }`. Esto traduce las violaciones de constraint de Hibernate (username/email/code duplicados, etc.) al tipo de excepción que los tests esperan capturar (los `assertThrows(ToursException.class, ...)` de `ToursApplicationTests`). En una arquitectura Spring "ortodoxa" lo idiomático sería propagar la `RuntimeException` original (`PersistenceException`, `DataIntegrityViolationException`, etc.) y dejar que el caller decida; aquí se hace la traducción en el servicio para no tocar la firma esperada por los tests.

> [!NOTE]
> **`updateUser` y `merge`**. El método `updateUser` recibe una entidad que puede llegar **detached** desde el test (modificada fuera de la transacción donde se cargó). Por eso el código primero verifica que el `id` existe (`userRepository.findById(...)`) y luego llama a `userRepository.merge(user)` — ese `merge` se delega en `session.merge` de Hibernate, que reasocia los cambios al `PersistenceContext` activo y devuelve la copia managed. Es uno de los casos de uso "canónicos" de `merge` (ver ejercicio 11).
>
> **`User.username` con `updatable = false`**. La columna `username` en el mapeo de `User` está declarada como `@Column(nullable = false, unique = true, updatable = false)`. Esto la convierte en un campo *inmutable* a nivel JPA: aunque el código de aplicación llame a `setUsername("nuevo")` y luego `updateUser(...)`, Hibernate ignorará ese cambio en el `UPDATE` generado y la fila en la base preservará el valor original. El test `updateUserTest` valida exactamente este comportamiento: setea un nuevo username, hace `updateUser`, busca por el nuevo username y verifica que **no** existe (porque el cambio se descartó). Es una decisión de modelado: el `username` actúa como identificador de negocio estable a lo largo del ciclo de vida de la cuenta.

#### a) Creación de todas las entidades persistentes.

```java
@Service
public class SupplierService {
    @Autowired private SupplierRepository supplierRepo;

    @Transactional
    public Supplier createSupplier(String businessName, String authorizationNumber) {
        Supplier supplier = new Supplier(businessName, authorizationNumber);
        return supplierRepo.save(supplier);
    }
}

@Service
public class ServiceService {
    @Autowired private ServiceRepository serviceRepo;
    @Autowired private SupplierRepository supplierRepo;

    @Transactional
    public Service createService(String name, float price, String description, Long supplierId) {
        Supplier supplier = supplierRepo.findById(supplierId);
        Service service = new Service(name, price, description, supplier);
        supplier.addService(service);     // mantiene ambos lados de la relación bidireccional
        return serviceRepo.save(service);
    }
}

@Service
public class UserService {
    @Autowired private UserRepository userRepo;

    @Transactional
    public User createUser(String username, String password, String fullName, String email,
                           Date birthdate, String phoneNumber) {
        User user = new User(username, password, fullName, email, birthdate, phoneNumber);
        return userRepo.save(user);
    }

    @Transactional
    public DriverUser createDriver(String username, String password, String fullName, String email,
                                   Date birthdate, String phoneNumber, String expedient) {
        DriverUser driver = new DriverUser(username, password, fullName, email, birthdate, phoneNumber, expedient);
        return (DriverUser) userRepo.save(driver);
    }

    @Transactional
    public TourGuideUser createTourGuide(String username, String password, String fullName, String email,
                                         Date birthdate, String phoneNumber, String education) {
        TourGuideUser guide = new TourGuideUser(username, password, fullName, email, birthdate, phoneNumber, education);
        return (TourGuideUser) userRepo.save(guide);
    }
}

@Service
public class StopService {
    @Autowired private StopRepository stopRepo;

    @Transactional
    public Stop createStop(String name, String description) {
        return stopRepo.save(new Stop(name, description));
    }
}

@Service
public class RouteService {
    @Autowired private RouteRepository routeRepo;

    @Transactional
    public Route createRoute(String name, float price, float totalKm, int maxNumberUsers,
                             List<Stop> stops, List<DriverUser> drivers, List<TourGuideUser> tourGuides) {
        Route route = new Route(name, price, totalKm, maxNumberUsers);
        stops.forEach(route::addStop);
        drivers.forEach(route::addDriver);
        tourGuides.forEach(route::addTourGuide);
        return routeRepo.save(route);
    }
}

@Service
public class PurchaseService {
    @Autowired private PurchaseRepository purchaseRepo;
    @Autowired private UserRepository userRepo;
    @Autowired private RouteRepository routeRepo;

    @Transactional
    public Purchase createPurchase(String code, Long userId, Long routeId) {
        User user = userRepo.findById(userId);
        Route route = routeRepo.findById(routeId);

        // Validación 1: código único de compra
        if (purchaseRepo.findByCode(code).isPresent()) {
            throw new ToursException("Constraint Violation");
        }
        // Validación 2: cupo de la ruta no superado
        if (purchaseRepo.countByRoute(route) >= route.getMaxNumberUsers()) {
            throw new ToursException("No puede realizarse la compra");
        }

        Purchase purchase = new Purchase(code, new Date(), user, route);
        purchase.setTotalPrice(route.getPrice());   // base = precio de la ruta; los items lo incrementan
        user.getPurchaseList().add(purchase);       // sincroniza el lado inverso in-memory
        // No se persisten los itemServiceList acá: se agregan luego con addItemToPurchase().
        return purchaseRepo.save(purchase);
    }
}
```

> [!NOTE]
> Cada método `@Transactional` abre una transacción al entrar y la cierra al salir. Si el constructor o el `save` lanza una excepción, Spring hace rollback y nada queda persistido. Las relaciones bidireccionales (como `Supplier ↔ Service`, o `User ↔ Purchase`) deben sincronizarse manualmente — por eso `supplier.addService(service)` y `user.getPurchaseList().add(purchase)` además del `save` del lado dueño (Hibernate no lo hace solo, ver nota del PDF al final de la sección 2.2).

#### b) Actualización del precio de un servicio existente.

```java
@Service
public class ServiceService {
    @Autowired private ServiceRepository serviceRepo;

    @Transactional
    public Service updatePrice(Long serviceId, float newPrice) {
        Service service = serviceRepo.findById(serviceId);
        service.setPrice(newPrice);
        // No hace falta llamar a save: la entidad está managed dentro de la transacción
        // y el dirty checking de Hibernate detecta el cambio y hace UPDATE en el flush.
        return service;
    }
}
```

> [!NOTE]
> Este es uno de los casos en los que la "metáfora de la colección que persiste" del ejercicio 40 se vuelve más clara: modificar un atributo de una entidad managed dentro de una transacción es **suficiente** para que el cambio se persista. No hay que llamar a `update()` ni a `save()` — Hibernate compara el estado actual contra el snapshot que tomó al cargar la entidad y emite el `UPDATE` correspondiente al hacer flush.

#### c) Agregar un nuevo ítem a una compra existente.

```java
@Service
public class PurchaseService {
    @Autowired private PurchaseRepository purchaseRepo;
    @Autowired private ServiceRepository serviceRepo;

    @Transactional
    public ItemService addItemToPurchase(Long purchaseId, Long serviceId, int quantity) {
        Purchase purchase = purchaseRepo.findById(purchaseId);
        Service service = serviceRepo.findById(serviceId);

        // El precio del ítem es un *snapshot* del Service.price actual:
        // si Service.price cambia luego, este ítem preserva el valor cobrado.
        float snapshotPrice = service.getPrice();

        ItemService item = new ItemService(service, quantity, snapshotPrice);
        purchase.addItem(item, snapshotPrice);          // setea item.purchase, agrega a la lista, suma price * quantity al totalPrice
        service.getItemServiceList().add(item);         // sincroniza el lado inverso de la relación Service ↔ ItemService

        // No hay que llamar a itemRepo.save(item):
        // cascade = PERSIST en Purchase.itemServiceList (ej. 28) lo persiste por alcance.

        return item;
    }
}
```

> [!NOTE]
> Dos puntos importantes que conectan con ejercicios previos:
> - **Cascada `PERSIST` en `Purchase.itemServiceList`** (ejercicio 28): basta con agregar el `ItemService` a la lista para que se persista en el flush.
> - **`ItemService.price` como snapshot** (ejercicio 20): el `price` del ítem se setea a partir de `service.getPrice()` *al momento de la compra* y queda persistido como información histórica. Si el `Service.price` cambia después, los `ItemService` ya guardados preservan el valor que efectivamente se cobró. Esto es crítico para la coherencia contable de las compras pasadas.

#### d) Eliminar una ruta existente siempre que no tenga compras asociadas.

La verificación se resuelve con una consulta HQL específica `countPurchasesByRoute(routeId)` que cuenta sin cargar entidades — más eficiente que recorrer en memoria con `findAll().stream()`. Esta consulta vive en `PurchaseRepository` y la consume directamente `ToursServiceImpl.deleteRoute`.

```java
@Service
public class RouteService {
    @Autowired private RouteRepository routeRepo;
    @Autowired private PurchaseRepository purchaseRepo;

    @Transactional
    public void deleteRoute(Long routeId) {
        Route route = routeRepo.findById(routeId);
        if (route == null) {
            throw new EntityNotFoundException("Route " + routeId + " no encontrada");
        }

        if (purchaseRepo.countByRoute(route) > 0) {
            throw new ToursException(
                "No puede eliminarse una ruta con compras asociadas"
            );
        }

        routeRepo.delete(route);
        // Las filas de las tablas join (route_stop, route_driver, route_tour_guide)
        // se borran automáticamente al eliminar la entidad dueña — no hace falta cascade
        // sobre las @ManyToMany (ver ejercicios 31 y 32).
    }
}
```

> [!NOTE]
> La validación se hace en el servicio, no a nivel BD ni en el repositorio. Es una regla de **dominio** ("no se puede eliminar una ruta vendida") y por lo tanto debe expresarse donde vive la lógica de negocio. Si el chequeo se hace dentro de la transacción (como en este caso), la verificación y el delete viajan juntos: ningún proceso concurrente puede insertar una `Purchase` entre el chequeo y el `delete`, porque la transacción aísla la operación.
>
> Esta es además la razón por la que en el ejercicio 32 se decidió **no** declarar `cascade = REMOVE` en `Purchase` → `Route` (que tampoco tendría sentido, porque la `Route` no es una composición de `Purchase`). Eliminar una ruta es una operación de gestión administrativa y la integridad la garantiza la lógica de servicio, no una cascada implícita.

#### Resumen del patrón

- Cada método público del servicio es **un caso de uso** y lleva `@Transactional`.
- Las validaciones de negocio (precondiciones, reglas como "no eliminar si tiene compras") se ejecutan dentro de la transacción, antes de cualquier cambio.
- Los repositorios sólo proveen las operaciones CRUD y las consultas de dominio; no abren transacciones ni hacen `try/catch`.
- Las modificaciones aprovechan el dirty checking del `PersistenceContext` (no hace falta `save` para un `setX()` sobre entidad managed) y la cascada configurada en el mapeo (no hace falta persistir ítems manualmente cuando `cascade = PERSIST` está activo).
- Las excepciones lanzadas dentro del servicio (`IllegalStateException`, `EntityNotFoundException`, etc.) disparan automáticamente el rollback al ser `RuntimeException`.

## Consultas con HQL y JPQL

### Ejercicio 45: ​¿Que diferencia hay entre HQL/JPQL y SQL nativo? ¿Qué entidades, atributos y relaciones entienden HQL/JPQL que SQL no conoce directamente?

- **Diferencia fundamental**:
  - **SQL nativo** opera sobre el **modelo relacional**: tablas, columnas, filas, joins, claves foráneas. Habla en el idioma de la base de datos y depende de su esquema físico (los nombres de tablas, columnas, dialectos específicos del motor, etc.).
  - **HQL/JPQL** opera sobre el **modelo de objetos**: entidades, atributos, relaciones, jerarquías de herencia. Habla en el idioma del dominio Java y delega al ORM la traducción al SQL concreto que entiende el motor.
  - Aunque la sintaxis sea muy parecida (`SELECT … FROM … WHERE …`), lo que aparece después del `FROM` cambia de naturaleza: en SQL es una tabla; en HQL/JPQL es **una clase Java**. Toda la expresión se escribe en términos del modelo de objetos y Hibernate genera el SQL apropiado en tiempo de ejecución.
  - **JPQL** es la especificación estándar definida por JPA — funciona con cualquier proveedor (Hibernate, EclipseLink, etc.). **HQL** es la implementación específica de Hibernate, que es un superset de JPQL con extensiones propias (por ejemplo, joins implícitos por dot-notation, funciones específicas, etc.). En la práctica del TP, ambos se escriben prácticamente igual.

- **Comparación lado a lado**:

  Una consulta como "todas las compras del usuario `juanperez`" se ve así en ambos lenguajes:

  ```sql
  -- SQL nativo
  SELECT p.*
    FROM purchase p
    JOIN user u ON u.id = p.user_id
   WHERE u.username = 'juanperez';
  ```

  ```java
  // HQL/JPQL
  SELECT p FROM Purchase p WHERE p.user.username = 'juanperez'
  ```

  En el HQL no aparece la tabla `user`, ni la columna `user_id`, ni el `JOIN` explícito: Hibernate los infiere a partir del mapeo de la relación `Purchase.user` (un `@ManyToOne`). El resultado es código que sigue el modelo de dominio en lugar del esquema físico.

- **Qué entiende HQL/JPQL que SQL no conoce directamente**:
  - **Entidades en lugar de tablas**: `from Purchase p` se refiere a la clase `Purchase`, no a la tabla `purchase`. Si en el futuro la tabla se renombra (`@Table(name = "purchases")`), el HQL no cambia.
  - **Atributos en lugar de columnas**: `p.totalPrice` se refiere al atributo Java, no a la columna `total_price`. La traducción al nombre real de columna la hace el ORM consultando los `@Column`.
  - **Navegación de relaciones por dot-notation**: `p.user.username` recorre la relación `Purchase → User → username` directamente. SQL exige escribir el `JOIN` explícito; HQL lo infiere a partir del mapeo `@ManyToOne`/`@OneToMany`/etc. Esto se generaliza a cualquier nivel: `purchase.route.stops` o `itemService.service.supplier.businessName` son válidos sin escribir joins.
  - **Polimorfismo y herencia**: `from User` devuelve usuarios de **todas** las subclases (`User`, `DriverUser`, `TourGuideUser`) si la jerarquía está configurada con `@Inheritance`. SQL nativo desconoce la jerarquía y obliga a escribir manualmente la lógica (`UNION` para `TABLE_PER_CLASS`, joins para `JOINED`, filtros por discriminador para `SINGLE_TABLE` — ver ejercicio 33).
  - **Tipos Java en los parámetros y resultados**: el `setParameter("date", new Date())` recibe un `java.util.Date`; el resultado de `getResultList()` devuelve `List<Purchase>` con entidades managed listas para usar. SQL devuelve filas crudas que requieren un mapeo manual.
  - **`fetch join` para resolver relaciones LAZY**: HQL ofrece `LEFT JOIN FETCH p.itemServiceList` para cargar la colección en la misma query y evitar `LazyInitializationException` (ver ejercicio 24). Es una construcción específica del ORM, sin equivalente directo en SQL.
  - **Operadores de colecciones**: `WHERE :stop MEMBER OF route.stops` o `WHERE route.stops IS EMPTY` operan sobre colecciones del modelo. En SQL hay que armar manualmente `EXISTS` o `LEFT JOIN` para representar esos predicados.
  - **Constructor expressions / proyección a DTOs**: `SELECT new com.app.PurchaseDTO(p.id, p.totalPrice) FROM Purchase p` instancia DTOs directamente en la query, evitando el paso intermedio por la entidad. Es código de aplicación dentro del HQL.

- **Otras diferencias prácticas**:
  - **Portabilidad**: HQL/JPQL es independiente del motor; el SQL generado se adapta al dialecto configurado (MySQL, PostgreSQL, Oracle, etc.). Una query SQL nativa que use funciones específicas de un motor (`NOW()`, `LIMIT`, ventanas) deja al proyecto atado a ese motor.
  - **Verificación temprana**: como HQL referencia clases y atributos, herramientas estáticas (IDE, compilador, validadores) pueden detectar errores de tipeo o renombres. SQL nativo es opaco al compilador — un cambio en el esquema rompe queries que sólo se descubren en tiempo de ejecución.
  - **Integración con el `PersistenceContext`**: las entidades devueltas por HQL son **managed**: cualquier modificación dentro de la transacción se persiste por dirty checking. SQL nativo devuelve filas crudas o entidades detached según la configuración, perdiendo esa propiedad.

### Ejercicio 46: ​Implementar las siguientes consultas en los repositorios correspondientes:​

Cada consulta se agrega al repositorio que devuelve su tipo principal (la entidad listada). Se asume el helper `session()` definido en el `AbstractRepository` del ejercicio 41 (`return sessionFactory.getCurrentSession();`). En la implementación final cada consulta vive **una sola vez** en el repositorio granular correspondiente y la expone `ToursServiceImpl` con un método `@Transactional` que delega directamente.

#### a) List<Purchase> getAllPurchasesOfUsername(String username) — Obtiene y retorna el listado de compras realizadas por el usuario con el nombre de usuario especificado por parámetro.

```java
// PurchaseRepository
public List<Purchase> getAllPurchasesOfUsername(String username) {
    return session()
        .createQuery(
            "select p from Purchase p where p.user.username = :username",
            Purchase.class)
        .setParameter("username", username)
        .getResultList();
}
```

> Se aprovecha la dot-notation `p.user.username` (ejercicio 45): Hibernate genera el `JOIN` con `User` automáticamente.

#### b) List<User> getUserSpendingMoreThan(float mount) — Listado de usuarios que hayan efectuado alguna compra por un valor mayor o igual al pasado por parámetro.

```java
// UserRepository
public List<User> getUserSpendingMoreThan(float mount) {
    return session()
        .createQuery(
            "select distinct p.user from Purchase p where p.totalPrice >= :mount",
            User.class)
        .setParameter("mount", mount)
        .getResultList();
}
```

> El `distinct` evita repetir el usuario si tiene varias compras que superan el monto. Se busca "alguna compra" (existe al menos una), por eso el filtro va en `p.totalPrice` y se proyecta el `user`.

#### c) List<Supplier> getTopNSuppliersInPurchases(int n) — Los n proveedores con mayor cantidad de apariciones en compras.

```java
// SupplierRepository
public List<Supplier> getTopNSuppliersInPurchases(int n) {
    return session()
        .createQuery(
            "select i.service.supplier " +
            "from ItemService i " +
            "group by i.service.supplier " +
            "order by count(i) desc",
            Supplier.class)
        .setMaxResults(n)
        .getResultList();
}
```

> Cada `ItemService` representa una "aparición" del servicio (y, transitivamente, de su proveedor) en una compra. `setMaxResults(n)` recorta al top N. Si se quisiera contar apariciones únicas por compra (no por ítem), habría que agrupar adicionalmente por `i.purchase` o usar `count(distinct i.purchase)`.

#### d) int getCountOfPurchasesBetweenDates(Date start, Date end) — Cantidad de compras registradas entre dos fechas.

```java
// PurchaseRepository
public long getCountOfPurchasesBetweenDates(Date start, Date end) {
    Long count = session()
        .createQuery(
            "select count(p) from Purchase p where p.date between :start and :end",
            Long.class)
        .setParameter("start", start)
        .setParameter("end", end)
        .uniqueResult();
    return count == null ? 0L : count;
}
```

> `count(...)` en HQL devuelve `Long`. **Desviación respecto al enunciado**: la práctica pide `int`, pero el contrato `ToursService` y los tests provistos (`getCountOfPurchasesBetweenDatesTest`) usan `long` como tipo de retorno (`long countOfPurchasesBetweenDates1 = this.service.getCountOfPurchasesBetweenDates(...)`). Para no romper los tests se mantiene `long` en toda la cadena (repositorio → servicio → interfaz). `between` incluye los extremos.

#### e) List<Route> getRoutesWithStop(Stop stop) — Listado de rutas que incluyen una parada especificada.

```java
// RouteRepository
public List<Route> getRoutesWithStop(Stop stop) {
    return session()
        .createQuery(
            "select r from Route r where :stop member of r.stops",
            Route.class)
        .setParameter("stop", stop)
        .getResultList();
}
```

> `member of` es uno de los operadores de colección que ofrece HQL (ejercicio 45) y se traduce a un `EXISTS` sobre la tabla join `route_stop`.

#### f) int getMaxStopOfRoutes() — Cantidad de paradas que posee el recorrido con mayor cantidad de stops.

```java
// RouteRepository
public Long getMaxStopOfRoutes() {
    Integer max = session()
        .createQuery(
            "select max(size(r.stops)) from Route r",
            Integer.class)
        .uniqueResult();
    return max == null ? null : max.longValue();
}
```

> `size(r.stops)` es la función HQL que devuelve la cardinalidad de la colección. El `max(...)` global ya devuelve un único número, sin necesidad de `group by`. **Desviación respecto al enunciado**: la práctica pide `int`, pero el contrato `ToursService` y el test provisto (`getMaxStopOfRoutesTest`) usan `Long`. Se mantiene `Long` en toda la cadena para no romper los tests; el `null` se preserva para el caso "no hay rutas" (el test asume que sí hay).

#### g) List<Route> getRoutesNotSell() — Listado de recorridos que no fueron vendidos.

```java
// RouteRepository
public List<Route> getRoutesNotSell() {
    return session()
        .createQuery(
            "select r from Route r " +
            "where not exists (select 1 from Purchase p where p.route = r)",
            Route.class)
        .getResultList();
}
```

> Se usa `NOT EXISTS` porque en el modelo no hay relación inversa `Route.purchases` (ejercicio 32), así que la pregunta se responde desde el lado de `Purchase`. Una alternativa equivalente es `where r not in (select p.route from Purchase p)`.

#### h) List<Route> getTop3RoutesWithMaxRating() — Los tres recorridos con mayor promedio de rating en las reviews de compras asociadas a dicha ruta.

```java
// RouteRepository
public List<Route> getTop3RoutesWithMaxRating() {
    return session()
        .createQuery(
            "select p.route " +
            "from Purchase p " +
            "where p.review is not null " +
            "group by p.route " +
            "order by avg(p.review.rating) desc",
            Route.class)
        .setMaxResults(3)
        .getResultList();
}
```

> Se navega `p.review.rating`. El filtro `p.review is not null` excluye compras sin review (la relación es opcional, ver ejercicio 18). El promedio se calcula por `Route` y se ordena descendente.

#### i) Service getMostDemandedService() — Servicio que más veces fue incluido en compras, teniendo en cuenta la cantidad.

```java
// ServiceRepository
public Service getMostDemandedService() {
    List<Service> result = session()
        .createQuery(
            "select i.service " +
            "from ItemService i " +
            "group by i.service " +
            "order by sum(i.quantity) desc",
            Service.class)
        .setMaxResults(1)
        .getResultList();
    return result.isEmpty() ? null : result.get(0);
}
```

> "Teniendo en cuenta la cantidad" se interpreta como `sum(i.quantity)` y no como `count(i)`: importa cuántas unidades del servicio se vendieron en total, no cuántas veces apareció. Se usa `setMaxResults(1)` y se devuelve el primer (y único) elemento.

#### j) List<TourGuideUser> getTourGuidesWithRating1() — Listado de guías asignados a algún tour con un rating de una estrella.

```java
// UserRepository
public List<TourGuideUser> getTourGuidesWithRating1() {
    return session()
        .createQuery(
            "select distinct g " +
            "from TourGuideUser g " +
            "join g.routes r " +
            "where exists (" +
            "    select 1 from Purchase p " +
            "    where p.route = r and p.review.rating = 1" +
            ")",
            TourGuideUser.class)
        .getResultList();
}
```

> Para que esto compile, `TourGuideUser` debe declarar `routes` como lado inverso de la `@ManyToMany` con `Route` (consistente con el ejercicio 17). El `exists` filtra rutas que tengan al menos una compra con review de 1 estrella, y se proyecta el guía con `distinct` para no repetirlo si participa en varias rutas mal calificadas.

<!-- Nota: el ítem k) `getUsersWithMoreThanNPurchases` no aparece en la lista a)–j) del enunciado. Quedó como consulta extra en el `UserRepository` durante el desarrollo y se documenta a continuación por completitud, aunque no es parte de lo pedido por la cátedra. -->

#### Extra (no pedido por el enunciado): List<User> getUsersWithMoreThanNPurchases(int n)

```java
// UserRepository
public List<User> getUsersWithMoreThanNPurchases(int n) {
    return session()
        .createQuery(
            "select p.user " +
            "from Purchase p " +
            "group by p.user " +
            "having count(p) > :n",
            User.class)
        .setParameter("n", (long) n)
        .getResultList();
}
```

> Esta consulta **no aparece en la lista a)–j) del ejercicio 46**, pero quedó implementada en el repositorio durante el desarrollo. `having` permite filtrar después del `group by` con la función agregada `count(p)`. El parámetro se castea a `long` para alinearse con el tipo que retorna `count` en HQL.

> [!NOTE]
> Patrones que se repiten en este ejercicio:
> - **Dot-notation** para evitar joins explícitos (`p.user.username`, `p.review.rating`, `i.service.supplier`).
> - **`group by` + `order by` + `setMaxResults`** para los "top N" (c, h, i).
> - **`distinct`** cuando la proyección puede repetirse por joins implícitos (b, j).
> - **Operadores de colección** (`member of`, `size(...)`) para predicados sobre relaciones (e, f).
> - **Subqueries con `not exists`** para "ausencia de" (g), porque no hay relación inversa modelada.

### Ejercicio 47: ​¿En qué casos conviene usar una consulta SQL nativa en lugar de HQL/JPQL? Describir al menos un caso concreto del modelo donde esto sería necesario.

La regla por defecto es usar HQL/JPQL (ver ejercicio 45), pero hay escenarios concretos en los que el SQL nativo es la mejor o la única opción. Hibernate los soporta vía `session.createNativeQuery(...)` o `entityManager.createNativeQuery(...)`.

- **Funciones específicas del motor que JPQL no estandariza**:
  - **Window functions** (`ROW_NUMBER`, `RANK`, `LAG`, `LEAD`, `OVER (PARTITION BY ...)`): muy útiles para ranking, comparativas con valores anteriores, *running totals*, etc. JPQL no las soporta.
  - **CTEs y queries recursivas** (`WITH ...`, `WITH RECURSIVE ...`): para recorridos jerárquicos, expansiones combinatorias, queries que se vuelven inmanejables sin recursión.
  - **Tipos de datos y operadores no estándar**: `JSON`/`JSONB` (PostgreSQL), `ARRAY`, full-text search (`MATCH AGAINST` en MySQL, `tsvector` en PostgreSQL), funciones geoespaciales (`ST_Distance`, `ST_Within`).
  - **Hints específicos del motor**: forzar el uso de un índice, paralelismo, particiones.
- **Operaciones bulk de mantenimiento**:
  - `INSERT ... SELECT`, `UPDATE ... FROM`, `DELETE ... USING`, `MERGE`/`UPSERT`. JPQL soporta `update`/`delete` pero limitado: no permite joins explícitos en el `UPDATE`/`DELETE` ni operaciones que modifican tablas join directamente.
  - Migraciones masivas, depuración de datos huérfanos, reorganización del esquema.
- **Performance**:
  - Reportes pesados sobre tablas grandes donde la query generada por Hibernate (joins implícitos, fetch eager, mapeo de proyecciones) introduce overhead innecesario. SQL nativo permite afinar exactamente el plan de ejecución.
  - Cuando la query devuelve sólo unas pocas columnas crudas (no entidades) y no hace falta el `PersistenceContext`. Se evita el costo de mapear filas a entidades managed.
- **Casos en los que el ORM "pelea" contra la query**:
  - Joins muy complejos con varias tablas donde la traducción del HQL produce SQL subóptimo o ambiguo.
  - Queries que mezclan tablas no mapeadas como entidades (tablas de auditoría, logs, datos importados).

#### Caso concreto del modelo: ranking de servicios por proveedor con `ROW_NUMBER`

Supongamos que el negocio quiere un reporte que muestre, **por cada `Supplier`**, cuál es su servicio más vendido (en cantidad). En HQL es difícil expresarlo en una sola consulta: `getMostDemandedService` devuelve el más demandado *globalmente*, no el más demandado *por cada proveedor*. Para resolverlo en HQL habría que hacer una query por proveedor (problema de N+1 invertido) o postprocesar en aplicación.

Con SQL nativo y window functions queda en una sola query eficiente:

```java
// SupplierRepository (versión con SQL nativo)
public List<Object[]> getTopServicePerSupplier() {
    return session().createNativeQuery(
        "SELECT supplier_id, service_id, total_quantity " +
        "  FROM ( " +
        "    SELECT s.supplier_id, " +
        "           s.id AS service_id, " +
        "           SUM(i.quantity) AS total_quantity, " +
        "           ROW_NUMBER() OVER ( " +
        "             PARTITION BY s.supplier_id " +
        "             ORDER BY SUM(i.quantity) DESC " +
        "           ) AS rn " +
        "      FROM item_service i " +
        "      JOIN service s ON s.id = i.service_id " +
        "  GROUP BY s.supplier_id, s.id " +
        "  ) ranked " +
        " WHERE ranked.rn = 1"
    ).getResultList();
}
```

- `PARTITION BY s.supplier_id` reinicia la numeración por proveedor.
- `ORDER BY SUM(i.quantity) DESC` ranquea por la cantidad total vendida.
- `WHERE ranked.rn = 1` deja sólo el primero de cada partición — el servicio top de cada proveedor.

JPQL no soporta `ROW_NUMBER OVER (...)` ni el patrón de subquery con ranking, por lo que la única manera limpia de resolverlo en una sola query es usar SQL nativo.

> [!NOTE]
> Otros casos del modelo donde SQL nativo encaja: una **purga histórica** (`DELETE FROM purchase WHERE date < ?`) sobre millones de filas con índices específicos, o un **reporte con paginación tipo "siguiente/anterior"** usando `LAG`/`LEAD` para mostrar la compra inmediatamente anterior y posterior de un usuario. En todos los casos, la decisión de bajar a SQL nativo debe quedar **localizada en el repositorio** correspondiente, sin filtrarse a la capa de servicio: el resto del sistema sigue viendo la API del Repository en términos de dominio.

> [!NOTE]
> El SQL nativo paga el precio que advierte el ejercicio 45: pierde portabilidad entre motores, no se valida en compilación contra el modelo de objetos, y rompe la abstracción del ORM. Por eso conviene reservarlo para casos puntuales donde el beneficio es claro — funciones que JPQL no soporta, performance crítica, o operaciones bulk que el ORM hace torpemente — y mantener el resto del proyecto en HQL/JPQL.