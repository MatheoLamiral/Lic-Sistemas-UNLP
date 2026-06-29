# Repositorios, consultas y transacciones

## Patrón de acceso a datos: DAO y Repository

### Ejercicio 39: ​Definir el patrón DAO (Data Access Object) y el patrón Repository. ¿Cuál es la diferencia conceptual más importante entre ambos? ¿En qué se diferencia su rol dentro de la arquitectura de la aplicación?

- **Patrón DAO (Data Access Object)**:
  - Es un patrón cuyo objetivo es **encapsular y abstraer el acceso a una fuente de datos**, exponiendo operaciones CRUD orientadas a la **fuente de datos** (`insert`, `update`, `delete`, `find`, `findAll`). y su responsabilidad principal es traducir entre el modelo de objetos de la aplicación y la representación que entiende la fuente, manejando conexiones, statements, mapeos columna → atributo, manejo de errores SQL, etc.
- **Patrón Repository**:
  - Es un patrón de **diseño de dominio** que **modela una colección de objetos persistentes como si fueran una colección en memoria**, el código cliente trabaja con abstracción, sin pensar en persistencia (transacciones, mapeos, queries, etc.), sólo en agregados de dominio (grupo de entidades que deben cambiar y mantenerse consistentes como una sola unidad). Las operaciones de un repositorio están expresadas en el lenguaje del dominio (p.ej. `getAllPurchasesOfUsername`, `getRoutesNotSell`, `getMostDemandedService`) y devuelven entidades del modelo, no DTOs ni filas crudas.

- **Diferencia conceptual más importante (Nivel de abstracción)**:
  - El **DAO es un patrón de infraestructura** (mira hacia la fuente de datos), el **Repository es un patrón de dominio** (mira hacia el modelo de negocio). Un **DAO es exitoso si oculta JDBC**, y un **Repository es exitoso si oculta cualquier mecanismo de persistencia y le habla al cliente como si fuera una colección** Java de toda la vida.
  >[!NOTE]
  > Un DAO típicamente tiene **una clase por tabla/fuente** y replica la estructura de la base. Un Repository tiene **una clase por agregado del dominio** (no por tabla, un agregado puede involucrar varias tablas) y refleja la estructura del modelo de objetos.

- **Diferencia en su rol dentro de la arquitectura**:
  - El **DAO** es la **interfaz que separa la capa de acceso a datos del resto de la aplicación**. La capa de servicios (o incluso la capa de presentación, en arquitecturas más simples) lo usa directamente y razona en términos de "guardar este registro" o "leer este `ResultSet`".
  - El **Repository vive en la capa de dominio y suele ser usado únicamente desde la capa de servicio**, que coordina la transacción y la lógica de negocio. La **presentación nunca toca un repositorio directamente**, trabaja con **servicios que devuelven entidades o DTOs** ya consistentes.

>[!NOTE] En frameworks modernos (Spring Data, Hibernate JPA), el repositorio suele implementarse internamente con técnicas DAO (la `Session` de Hibernate es, en esencia, un DAO genérico). La diferencia, entonces, no es sólo conceptual, es **dónde y cómo se exponen las operaciones al resto del sistema**. Un repositorio bien diseñado expone operaciones del dominio aunque internamente delegue en mecanismos DAO. Un DAO mal usado se filtra hacia capas de negocio y obliga a hablar de tablas y conexiones donde debería hablarse de agregados.

### Ejercicio 40: ​El patrón Repository puede pensarse como una colección de objetos en memoria que además persiste su estado. Describir cómo se implementa este concepto usando Hibernate: ¿qué responsabilidades concentra un repositorio? ¿Con qué objeto de Hibernate interactúa internamente?

- **El concepto de "colección que persiste su estado"**:
  - Hibernate ofrece exactamente esta abstracción a través del **`PersistenceContext`** (representado por la `Session`). Mientras la sesión está abierta, las entidades managed se comportan como objetos en memoria normales, y los cambios se sincronizan con la base en el flush. El repositorio aprovecha ese mecanismo para exponer una API de "colección viva" hacia el resto del sistema.

- **¿Qué responsabilidades concentra un repositorio?**:
  - **Interfaz de colección**: expone métodos que se asemejan a una colección clásica en lugar de operaciones técnicas de bases de datos.
  - **Encapsular el mecanismo de persistencia**: actúa como máscara para ocultar la complejidad del SQL o HQL. Concentra la responsabilidad de las consultas complejas para que no "ensucien" el código del dominio.
  - **Exponer entidades del dominio**, no proyecciones técnicas. Un repositorio devuelve `Purchase`, `Route`, `User`, no `ResultSet`s, ni mapas de columnas, ni DTOs específicos de la presentación.
  - **Mediador de capas**: es un puente entre la capa de servicio y la persistencia.

- **¿Con qué objeto de Hibernate interactúa internamente?**:
  - El objeto central es la **`Session`**, que es el `PersistenceContext` de Hibernate y ofrece los métodos sobre los que se construyen todas las operaciones del repositorio (`session.persist(entity)`, `session.find(Class, id)`, etc.).
  - **Obtención de la sesión**: Para realizar su trabajo, el repositorio utiliza el método `getCurrentSession()` sobre la `SessionFactory`.
  - **Uso de HQL/JPQL**: Dentro de sus métodos, el repositorio utiliza la sesión para ejecutar consultas en HQL (Hibernate Query Language), las cuales son luego traducidas a SQL por el ORM.
  
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
> La diferencia entre `openSession()` y `getCurrentSession()` es relevante acá: `getCurrentSession()` devuelve la `Session` ligada a la transacción en curso, evitando que cada repositorio abra y cierre su propia sesión. Esto es lo que permite que múltiples llamadas a distintos repositorios dentro de un mismo método de servicio compartan el mismo `PersistenceContext` y, por lo tanto, se vean los cambios entre sí sin tener que hacer flush manual.

### Ejercicio 41: ​Implementar un repositorio por cada entidad del modelo (PurchaseRepository, RouteRepository, UserRepository, ServiceRepository, SupplierRepository, ReviewRepository). Cada repositorio debe incluir al menos las operaciones básicas: guardar, buscar por ID, listar todos y eliminar. Utilizar la Session de Hibernate en cada implementación, tal como se ha explicado previamente utilizando el método getCurrentSession() sobre la SessionFactory (genere una inyección de este objeto tal como se muestra en el código de ejemplo proporcionado)

Como las seis entidades comparten exactamente las mismas operaciones básicas (`save`, `findById`, `findAll`, `delete`), conviene factorizar la lógica común en una **clase base genérica** y dejar a cada repositorio concreto sólo la declaración de su tipo. Esto evita duplicar el `SessionFactory` y la lógica de las operaciones CRUD en seis lugares distintos.

#### Clase base genérica

```java
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


>[!NOTE]
> - La `SessionFactory` se inyecta una sola vez en la clase base, vía `@Autowired`.
> - `session()` siempre devuelve la `Session` ligada a la transacción en curso (`getCurrentSession()`).
> - `findAll()` arma el HQL dinámicamente a partir del `Class<T>` para no tener que repetirlo en cada subclase.
> - No hay `@Transactional` en este nivel: los repositorios no manejan transacciones.

#### Repositorios concretos

Cada repositorio extiende la clase base y queda mínimo. Sólo se diferencian en el tipo y, eventualmente, en las consultas custom que se agreguen.

```java
@Repository
public class PurchaseRepository extends AbstractRepository<Purchase> {
    public PurchaseRepository() { super(Purchase.class); }

}

@Repository
public class RouteRepository extends AbstractRepository<Route> {
    public RouteRepository() { super(Route.class); }

}

@Repository
public class UserRepository extends AbstractRepository<User> {
    public UserRepository() { super(User.class); }

}

@Repository
public class ServiceRepository extends AbstractRepository<Service> {
    public ServiceRepository() { super(Service.class); }

}

@Repository
public class SupplierRepository extends AbstractRepository<Supplier> {
    public SupplierRepository() { super(Supplier.class); }

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
> Además de los CRUD básicos, `AbstractRepository` expone también `merge(T entity)` (delegando en `session.merge`).

> [!NOTE]
> Detalles de diseño relevantes:
> - **`@Repository`** (no `@Component`) marca la clase como bean de Spring y además habilita la traducción automática de excepciones nativas de persistencia (`HibernateException`, `SQLException`) a `DataAccessException` de Spring.

## Transacciones

### Ejercicio 42: ​¿Que es una transacción en el contexto de Hibernate? ¿Por qué es necesaria? ¿Qué ocurre si se realizan operaciones de escritura sin una transacción activa?

- **¿Qué es una transacción en el contexto de Hibernate?**:
  - Una transacción es la **unidad atómica de trabajo** sobre la base de datos, un conjunto de operaciones que se ejecutan como un todo y deben cumplir las propiedades ACID (atomicidad, consistencia, aislamiento, durabilidad). O se aplican todas con éxito (`commit`), o no se aplica ninguna (`rollback`).
  - Hibernate la representa con la interfaz `Transaction`, obtenida desde la `Session` (`session.beginTransaction()`). Por debajo, **esa transacción se delega al motor de la base** (vía JDBC), donde se traduce a `START TRANSACTION`/`COMMIT`/`ROLLBACK`. La **transacción de Hibernate es entonces una fachada sobre la transacción nativa del motor**, no es una segunda transacción "lógica" superpuesta.

- **¿Por qué es necesaria?**:
  - **Atomicidad ante operaciones múltiples**: una sola operación de negocio puede involucrar varias filas o varias tablas. Sin una transacción que las englobe, una falla a mitad de camino dejaría la base en un estado inconsistente, la mitad de las inserciones aplicadas, la otra mitad no.
  - **Consistencia ante errores**: si algo falla (excepción de la aplicación, violación de FK, caída de conexión), el motor revierte automáticamente todo lo hecho dentro de la transacción al hacer `rollback`. El estado previo se preserva.
  - **Aislamiento entre usuarios concurrentes**: la transacción define qué cambios ve cada cliente concurrente. Sin ella, un usuario podría leer datos parcialmente escritos por otro.

- **¿Qué ocurre si se realizan operaciones de escritura sin una transacción activa?**:
  - En el contexto del TP (Spring + Hibernate con `getCurrentSession()`), la condición habitual es que `getCurrentSession()` requiere una transacción activa para funcionar. Si se invoca desde código que no está bajo `@Transactional`, lanza `HibernateException: No Session found for current thread`. Es Spring negándose a entregar una `Session` que no estaría asociada a una unidad de trabajo bien definida.
  - **Cambios "fantasma" en memoria**: si la operación no llega a flushearse (porque nunca se cierra la sesión correctamente), los cambios quedan sólo en el `PersistenceContext` y se descartan al cerrar la `Session` sin commit. La base no recibe nada, pero el código vio el objeto "managed" como si se hubiera guardado.

> [!NOTE]
> El `flush` automático no implica `commit`: Hibernate puede flushear varias veces dentro de una misma transacción (por ejemplo, antes de una query, para asegurar que los cambios pendientes se apliquen y la query los vea). El commit ocurre una sola vez al final, cuando se cierra la unidad de trabajo. Confundir flush con commit lleva a creer que los cambios son persistentes cuando en realidad todavía pueden revertirse con un rollback.

### Ejercicio 43: ​¿En qué capa de la aplicación debería gestionarse la transacción: en el repositorio o en la capa de servicio? Justificar la elección. ¿Qué ocurre si una misma operación necesita de varios accesos a la base de datos?

La transacción debe gestionarse en la **capa de servicio**, nunca en el repositorio:
- **La transacción es una decisión de negocio, no de acceso a datos**:
  - Una operación de negocio define qué cambios deben aplicarse "todos o ninguno". Esa frontera la conoce la **capa de servicio que sabe cuál es el caso de uso completo**, el repositorio no, **sólo conoce la operación atómica que se le pide**.
  - Si el repositorio gestionara su propia transacción, **cada llamada abriría y cerraría una transacción independiente, rompiendo la atomicidad del caso de uso**.
  - Con la transacción en el servicio, los repositorios que se llamen dentro de una transacción, reciben la **misma `Session`** vía `getCurrentSession()`, comparten el mismo `PersistenceContext` y al hacer commit (al final del método de servicio) los **cambios se aplican atómicamente**.
- **Transparencia y desacoplamiento**:
  - Al delegar la demarcación transaccional a la capa de servicio, los repositorios se mantienen enfocados únicamente en la ejecución de consultas y el acceso a datos, sin "ensuciarse" con la lógica de control transaccional.

- **¿Qué ocurre si una misma operación necesita varios accesos a la base de datos?**:
  - Si la transacción está en la **capa de servicio**, todas las llamadas a la base hechas **dentro del método transaccional viajan en la misma transacción**.
  - Si la transacción estuviera en el **repositorio**, **cada llamada abriría su propia transacción independiente**, **rompiendo la atomicidad** (los primeros cambios pueden quedar persistidos aunque el último falle), el **aislamiento** (otro hilo podría leer estados intermedios entre operaciones del mismo caso de uso) y **multiplicando los costos** (cada commit JDBC tiene overhead, abrir/cerrar transacciones para cada `save` saturaría la base).
  - **fuera de transacción no hay `PersistenceContext` compartido**, cada `findById` cargaría la entidad, la **marcaría como detached al cerrarse** la transacción, y la **siguiente operación recibiría una entidad "vieja" sin posibilidad de aprovechar los cambios en memoria**.

> [!NOTE]
> Si un método de servicio llama a otro método de servicio, ambos comparten la transacción por defecto (propagación `REQUIRED`). Si por alguna razón se necesita aislamiento entre los dos (por ejemplo, que el segundo se commitee aunque el primero haga rollback), se configura con `@Transactional(propagation = REQUIRES_NEW)`. Esos casos son raros, la regla general es **una transacción por caso de uso**.

### Ejercicio 44: ​Implementar una capa de servicio que coordine las operaciones del modelo usando transacciones correctamente. Como mínimo implementar:​

#### a) Creación de todas las entidades persistentes.

La capa de servicio se implementa como un **único `ToursServiceImpl`** que implementa la interfaz `ToursService` provista por la cátedra. Cada operación de creación va anotada con `@Transactional` y delega la persistencia en los repositorios. Se respetan las firmas reales de la interfaz (objetos de dominio como parámetros, no ids; `createDriverUser`/`createTourGuideUser`; `addServiceToSupplier`; `createRoute` solo con stops, etc.).

```java
@Service
public class ToursServiceImpl implements ToursService {

    @Autowired private UserRepository userRepository;
    @Autowired private StopRepository stopRepository;
    @Autowired private RouteRepository routeRepository;
    @Autowired private SupplierRepository supplierRepository;
    @Autowired private ServiceRepository serviceRepository;
    @Autowired private PurchaseRepository purchaseRepository;

    // --- Usuarios (la jerarquía comparte la misma estrategia de mapeo) ---
    @Override
    @Transactional
    public User createUser(String username, String password, String fullName, String email,
                           Date birthdate, String phoneNumber) throws ToursException {
        try {
            return userRepository.save(new User(username, password, fullName, email, birthdate, phoneNumber));
        } catch (RuntimeException e) {
            throw new ToursException("Constraint Violation");
        }
    }

    @Override
    @Transactional
    public DriverUser createDriverUser(String username, String password, String fullName, String email,
                                       Date birthdate, String phoneNumber, String expedient) throws ToursException {
        try {
            return (DriverUser) userRepository.save(
                new DriverUser(username, password, fullName, email, birthdate, phoneNumber, expedient));
        } catch (RuntimeException e) {
            throw new ToursException("Constraint Violation");
        }
    }

    @Override
    @Transactional
    public TourGuideUser createTourGuideUser(String username, String password, String fullName, String email,
                                             Date birthdate, String phoneNumber, String education) throws ToursException {
        try {
            return (TourGuideUser) userRepository.save(
                new TourGuideUser(username, password, fullName, email, birthdate, phoneNumber, education));
        } catch (RuntimeException e) {
            throw new ToursException("Constraint Violation");
        }
    }

    // --- Stops y Rutas ---
    @Override
    @Transactional
    public Stop createStop(String name, String description) throws ToursException {
        try {
            return stopRepository.save(new Stop(name, description));
        } catch (RuntimeException e) {
            throw new ToursException("Constraint Violation");
        }
    }

    @Override
    @Transactional
    public Route createRoute(String name, float price, float totalKm, int maxNumberOfUsers,
                             List<Stop> stops) throws ToursException {
        Route route = new Route(name, price, totalKm, maxNumberOfUsers);
        stops.forEach(route::addStop);   // los choferes/guías se asignan después (assignDriver/TourGuideByUsername)
        return routeRepository.save(route);
    }

    // --- Proveedores y Servicios ---
    @Override
    @Transactional
    public Supplier createSupplier(String businessName, String authorizationNumber) throws ToursException {
        try {
            return supplierRepository.save(new Supplier(businessName, authorizationNumber));
        } catch (RuntimeException e) {
            throw new ToursException("Constraint Violation");
        }
    }

    @Override
    @Transactional
    public Service addServiceToSupplier(String name, float price, String description, Supplier supplier)
            throws ToursException {
        Supplier persisted = supplierRepository.findById(supplier.getId())
                .orElseThrow(() -> new ToursException("El proveedor no existe"));
        Service service = new Service(name, price, description, persisted);
        persisted.addService(service);   // sincroniza el lado inverso de la relación bidireccional
        return serviceRepository.save(service);
    }

    // --- Compras (dos sobrecargas: fecha actual o fecha dada) ---
    @Override
    @Transactional
    public Purchase createPurchase(String code, Route route, User user) throws ToursException {
        return createPurchase(code, new Date(), route, user);
    }

    @Override
    @Transactional
    public Purchase createPurchase(String code, Date date, Route route, User user) throws ToursException {
        if (purchaseRepository.findByCode(code).isPresent()) {            // código único de compra
            throw new ToursException("Constraint Violation");
        }
        Route persistedRoute = routeRepository.findById(route.getId())
                .orElseThrow(() -> new ToursException("La ruta no existe"));
        User persistedUser = userRepository.findById(user.getId())
                .orElseThrow(() -> new ToursException("El usuario no existe"));
        if (purchaseRepository.countPurchasesByRoute(persistedRoute.getId()) >= persistedRoute.getMaxNumberUsers()) {
            throw new ToursException("No puede realizarse la compra");    // cupo de la ruta no superado
        }
        Purchase purchase = new Purchase(code, date, persistedUser, persistedRoute);
        purchase.setTotalPrice(persistedRoute.getPrice());               // base = precio de la ruta
        persistedUser.getPurchaseList().add(purchase);                   // sincroniza el lado inverso in-memory
        return purchaseRepository.save(purchase);
        // los ItemService se agregan luego con addItemToPurchase()
    }
}
```

> [!NOTE]
> Cada método `@Transactional` abre una transacción al entrar y la cierra al salir. Si el constructor o el `save` lanza una excepción, Spring hace rollback y nada queda persistido. Las relaciones bidireccionales (como `Supplier ↔ Service`, o `User ↔ Purchase`) deben sincronizarse manualmente, por eso `supplier.addService(service)` y `user.getPurchaseList().add(purchase)` además del `save` del lado dueño.

#### b) Actualización del precio de un servicio existente.

```java
// (método de ToursServiceImpl — usa el ServiceRepository ya inyectado)
@Override
@Transactional
public Service updateServicePriceById(Long id, float newPrice) throws ToursException {
    Service service = serviceRepository.findById(id);
    if (service == null) {
        throw new ToursException("No existe el producto");
    }
    service.setPrice(newPrice);
    // No hace falta llamar a save: la entidad está managed dentro de la transacción
    // y el dirty checking de Hibernate detecta el cambio y hace UPDATE en el flush.
    return service;
}
```

> [!NOTE]
> Modificar un atributo de una entidad managed dentro de una transacción es **suficiente** para que el cambio se persista. No hay que llamar a `update()` ni a `save()`. Hibernate compara el estado actual contra el snapshot que tomó al cargar la entidad y emite el `UPDATE` correspondiente al hacer flush.

#### c) Agregar un nuevo ítem a una compra existente.

```java
// (método de ToursServiceImpl, usa PurchaseRepository, ServiceRepository
//  e ItemServiceRepository ya inyectados). Recibe los OBJETOS, no ids.
@Override
@Transactional
public ItemService addItemToPurchase(Service service, int quantity, Purchase purchase) throws ToursException {
    Service persistedService = serviceRepository.findById(service.getId());
    Purchase persistedPurchase = purchaseRepository.findById(purchase.getId());
    if (persistedService == null || persistedPurchase == null) {
        throw new ToursException("Servicio o compra no existen");
    }

    // El precio del ítem es un *snapshot* del Service.price actual:
    // si Service.price cambia luego, este ítem preserva el valor cobrado.
    ItemService item = new ItemService(persistedService, quantity, persistedService.getPrice());
    persistedPurchase.addItem(item, persistedService.getPrice());   // setea item.purchase, agrega a la lista, suma price * quantity al totalPrice
    persistedService.getItemServiceList().add(item);                // sincroniza el lado inverso Service ↔ ItemService

    return itemServiceRepository.save(item);                        // se persiste el ítem explícitamente
}
```

#### d) Eliminar una ruta existente siempre que no tenga compras asociadas.

```java
// (método de ToursServiceImpl — usa RouteRepository y PurchaseRepository
//  ya inyectados). Recibe el OBJETO Route, no un id.
@Override
@Transactional
public void deleteRoute(Route route) throws ToursException {
    Route persisted = routeRepository.findById(route.getId());
    if (persisted == null) {
        throw new ToursException("La ruta no existe");
    }
    if (purchaseRepository.countPurchasesByRoute(persisted.getId()) > 0) {
        throw new ToursException("No puede eliminarse una ruta con compras asociadas");
    }
    routeRepository.delete(persisted);
    // Las filas de las tablas join (route_stop, route_driver, route_tour_guide)
    // se borran automáticamente al eliminar la entidad dueña — no hace falta cascade
    // sobre las @ManyToMany (ver ejercicios 31 y 32).
}
```

> [!NOTE]
> La validación se hace en el servicio, no a nivel BD ni en el repositorio. Es una regla de **dominio** ("no se puede eliminar una ruta vendida") y por lo tanto debe expresarse donde vive la lógica de negocio. Si el chequeo se hace dentro de la transacción (como en este caso), la verificación y el delete viajan juntos, ningún proceso concurrente puede insertar una `Purchase` entre el chequeo y el `delete`, porque la transacción aísla la operación.

#### Resumen del patrón

- Cada método público del servicio es **un caso de uso** y lleva `@Transactional`.
- Las validaciones de negocio (precondiciones, reglas como "no eliminar si tiene compras") se ejecutan dentro de la transacción, antes de cualquier cambio.
- Los repositorios sólo proveen las operaciones CRUD y las consultas de dominio; no abren transacciones ni hacen `try/catch`.
- Las modificaciones aprovechan el dirty checking del `PersistenceContext`, no hace falta `save` para un `setX()` sobre una entidad managed (como en `updateServicePriceById`). Para las altas de entidades nuevas, la implementación las persiste **explícitamente** con `save` (p. ej. `addItemToPurchase`), aunque la cascada `PERSIST` del mapeo también las arrastraría por alcance.
- Las excepciones de negocio se modelan con `ToursException`, que es **checked** (`extends Exception`). Spring, por defecto, **solo hace rollback ante `RuntimeException`/`Error`**, **no** ante excepciones checked. En estos métodos las validaciones se ejecutan **antes** de cualquier modificación, así que al lanzar `ToursException` no hay estado parcial que revertir. Si una operación pudiera fallar **después** de haber modificado datos, habría que forzar el rollback con `@Transactional(rollbackFor = ToursException.class)`.

## Consultas con HQL y JPQL

### Ejercicio 45: ​¿Que diferencia hay entre HQL/JPQL y SQL nativo? ¿Qué entidades, atributos y relaciones entienden HQL/JPQL que SQL no conoce directamente?

La diferencia entre **HQL/JPQL** y **SQL** nativo, es que los primeros son lenguajes de consulta **orientados a objetos** delegando al ORM la traducción al SQL concreto que entiende el motor, mientras que el último es un **lenguaje relacional** basado en tablas y columnas. Mientras **SQL** **devuelve filas y columnas**, **HQL/JPQL** puede devolver **objetos "enteros" o grafos de objetos**, manteniendo el encapsulamiento del modelo.

>[!NOTE]
> **JPQL** es la **especificación estándar definida por JPA**, funciona con cualquier proveedor (Hibernate, EclipseLink, etc.). **HQL** es la **implementación específica de Hibernate**, que es un superset de JPQL con extensiones propias.

>[!NOTE]
> **Portabilidad**: HQL/JPQL es independiente del motor, mientras que el SQL generado se adapta al dialecto configurado (MySQL, PostgreSQL, Oracle, etc.). Una query SQL nativa que use funciones específicas de un motor (`NOW()`, `LIMIT`, ventanas) deja al proyecto atado a ese motor.

- **Qué entiende HQL/JPQL que SQL no conoce directamente**:
  - **Entidades en lugar de tablas**: `from Purchase p` se refiere a la clase `Purchase`, no a la tabla `purchase`. Si en el futuro la tabla se renombra (`@Table(name = "purchases")`), el HQL no cambia.
  - **Atributos en lugar de columnas**: `p.totalPrice` se refiere al atributo Java, no a la columna `total_price`. La traducción al nombre real de columna la hace el ORM consultando los `@Column`.
  - **Navegación de relaciones por dot-notation**: `p.user.username` recorre la relación `Purchase → User → username` directamente. Mucho más legible y directo que los `JOIN`s
  - **Polimorfismo y herencia**: `from User` devuelve usuarios de **todas** las subclases (`User`, `DriverUser`, `TourGuideUser`) si la jerarquía está configurada con `@Inheritance`. SQL nativo desconoce la jerarquía y obliga a escribir manualmente la lógica (`UNION` para `TABLE_PER_CLASS`, joins para `JOINED`, filtros por discriminador para `SINGLE_TABLE`).
  - **Tipos Java en los parámetros y resultados**: el `setParameter("date", new Date())` recibe un `java.util.Date`; el resultado de `getResultList()` devuelve `List<Purchase>` con entidades managed listas para usar. SQL devuelve filas crudas que requieren un mapeo manual.
  - **`fetch join` para resolver relaciones LAZY**: HQL ofrece `LEFT JOIN FETCH p.itemServiceList` para cargar la colección en la misma query y evitar `LazyInitializationException` (ver ejercicio 24). Es una construcción específica del ORM, sin equivalente directo en SQL.
  - **Operadores de colecciones**: `WHERE :stop MEMBER OF route.stops` o `WHERE route.stops IS EMPTY` operan sobre colecciones del modelo. En SQL hay que armar manualmente `EXISTS` o `LEFT JOIN` para representar esos predicados.

### Ejercicio 46: ​Implementar las siguientes consultas en los repositorios correspondientes:​

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

> [!NOTE]
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

> [!NOTE]
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

> [!NOTE]
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

> [!NOTE]
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

> [!NOTE]
> `member of` es uno de los operadores de colección que ofrece HQL y se traduce a un `EXISTS` sobre la tabla join `route_stop`.

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

> [!NOTE]
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

> [!NOTE]
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

> [!NOTE]
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

> [!NOTE]
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

> [!NOTE]
> Para que esto compile, `TourGuideUser` debe declarar `routes` como lado inverso de la `@ManyToMany` con `Route`. El `exists` filtra rutas que tengan al menos una compra con review de 1 estrella, y se proyecta el guía con `distinct` para no repetirlo si participa en varias rutas mal calificadas.

> [!NOTE]
> Patrones que se repiten en este ejercicio:
> - **Dot-notation** para evitar joins explícitos (`p.user.username`, `p.review.rating`, `i.service.supplier`).
> - **`group by` + `order by` + `setMaxResults`** para los "top N" (c, h, i).
> - **`distinct`** cuando la proyección puede repetirse por joins implícitos (b, j).
> - **Operadores de colección** (`member of`, `size(...)`) para predicados sobre relaciones (e, f).
> - **Subqueries con `not exists`** para "ausencia de" (g), porque no hay relación inversa modelada.

### Ejercicio 47: ​¿En qué casos conviene usar una consulta SQL nativa en lugar de HQL/JPQL? Describir al menos un caso concreto del modelo donde esto sería necesario.

La regla por defecto es usar HQL/JPQL, pero hay escenarios concretos en los que el SQL nativo es la mejor o la única opción. Hibernate los soporta vía `session.createNativeQuery(...)` o `entityManager.createNativeQuery(...)`.

- **Funciones específicas del motor que JPQL no estandariza**:
  - **Window functions** (`ROW_NUMBER`, `RANK`, `LAG`, `LEAD`, `OVER (PARTITION BY ...)`): muy útiles para ranking, comparativas con valores anteriores, running totals, etc. JPQL no las soporta.
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
> El SQL nativo pierde portabilidad entre motores, no se valida en compilación contra el modelo de objetos, y rompe la abstracción del ORM. Por eso conviene reservarlo para casos puntuales donde el beneficio es claro, funciones que JPQL no soporta, performance crítica, o operaciones bulk que el ORM hace torpemente, y mantener el resto del proyecto en HQL/JPQL.