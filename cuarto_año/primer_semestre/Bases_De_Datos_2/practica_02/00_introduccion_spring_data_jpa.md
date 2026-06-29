# Introducción a Spring Data JPA

## Spring Data JPA y su lugar en el ecosistema 

### Ejercicio 1: ¿Qué es Spring Data JPA? ¿Qué problema resuelve respecto de usar Hibernate directamente? Describir dos situaciones del proyecto donde Spring Data JPA simplifica código que en la Práctica 1 requería implementación manual.

**Spring Data JPA** es un módulo del ecosistema Spring que provee una **capa de abstracción declarativa sobre JPA**. No es un ORM en sí mismo, sino que delega el trabajo real de persistencia en un proveedor JPA (en nuestro caso, Hibernate), pero elimina prácticamente todo el código de infraestructura que rodea al acceso a datos. El desarrollador **declara una interfaz** que extiende `CrudRepository<T, ID>` y Spring Data genera su implementación en tiempo de ejecución mediante un proxy dinámico.

**Problema que resuelve respecto de usar Hibernate directamente:**

En la Práctica 1, usar Hibernate "a mano" implicaba:
- Inyectar la `SessionFactory` en cada repositorio y obtener la `Session` actual.
- Implementar manualmente las operaciones CRUD (`save`, `findById`, `findAll`, `delete`) en una clase abstracta genérica para no duplicarlas.
- Escribir cada consulta de dominio en HQL, abrir la `Query`, setear parámetros y ejecutar.

Con Spring Data JPA se obtienen las operaciones CRUD al extender `CrudRepository`, y muchas consultas se derivan del nombre del método (*query methods*) o se declaran con `@Query`.

**Dos situaciones concretas del proyecto donde simplifica el código de la Práctica 1:**

1. **Eliminación de `AbstractRepository<T>`.**   
   En la Práctica 1 tuvimos que crear una clase base genérica que inyectaba la `SessionFactory`, guardaba una referencia a `Class<T>` y reimplementaba `save`, `findById`, `findAll` y `delete` usando la `Session`. Cada repositorio concreto (`PurchaseRepository`, `RouteRepository`, etc.) extendía esa clase y pasaba su tipo por constructor. Con Spring Data JPA toda esa jerarquía desaparece, basta con declarar `public interface PurchaseRepository extends CrudRepository<Purchase, Long> {}` y las cuatro operaciones quedan disponibles sin escribir una sola línea de implementación.

2. **Consultas de dominio sin armar la `Query` a mano.**   
   En la Práctica 1, métodos como `getAllPurchasesOfUsername` requerían obtener la `Session`, invocar `createQuery("from Purchase p where p.user.username = :u", Purchase.class)`, hacer `setParameter("u", username)` y `getResultList()`. Con Spring Data JPA esa misma consulta puede expresarse declarando únicamente la firma `List<Purchase> findByUserUsername(String username)`. El método se deriva del nombre o, para consultas más complejas que no se pueden expresar por convención, usar `@Query("...")` sobre la firma sin escribir el código de ejecución.

### Ejercicio 2: Spring Data JPA no es un ORM sino una capa de abstracción sobre el ORM. Explicar la diferencia: ¿qué hace Spring Data JPA? ¿Qué sigue haciendo Hibernate internamente?

La diferencia se entiende mejor pensándolos como **dos capas distintas del stack de persistencia**:

- **Spring Data JPA** es una **capa declarativa sobre JPA**. No habla con la base de datos, su rol es generar en tiempo de ejecución la implementación de los repositorios a partir de las interfaces declaradas y traducir las intenciones del programador (firmas de métodos, `@Query`, `@Transactional`) en llamadas al `EntityManager`. En otras palabras, **ahorra el código de infraestructura** que antes había que escribir a mano.

- **Hibernate** sigue siendo el **ORM** debajo. Es quien interpreta las anotaciones de mapeo (`@Entity`, `@OneToMany`, herencia, cascadas, `FetchType`), administra el `PersistenceContext` (Caché L1, *dirty checking*, *flush*), traduce JPQL a SQL según el dialecto y ejecuta las consultas contra la base.

En resumen, **Spring Data JPA decide qué operaciones expone y cómo se invocan, mientras que Hibernate decide cómo esas operaciones se traducen a SQL y se aplican sobre las tablas.** Spring Data **no reemplaza al ORM, lo envuelve**.

### Ejercicio 3:  La siguiente tabla lista tareas relacionadas con la persistencia. Marcar con una X la columna de la tecnología que resuelve ese problema en la nueva implementación con Spring Data JPA:

| Tarea                                                  | JDBC | Hibernate | Spring Data JPA |
| ------------------------------------------------------ | :--: | :-------: | :-------------: |
| Abrir y cerrar la conexión a la base de datos          |      |     X     |                 |
| Implementar `save()`, `findById()` y `deleteById()`    |      |           |        X        |
| Gestionar el ciclo de vida de las entidades (`@Entity`)|      |     X     |                 |
| Derivar una consulta a partir del nombre del método    |      |           |        X        |
| Manejar el pool de conexiones                          |      |     X     |                 |
| Propagar transacciones con `@Transactional`            |      |           |        X        |
| Generar la implementación del repositorio en runtime   |      |           |        X        |
| Mapear `ResultSet` a objetos Java                      |      |     X     |                 |
| Proveer soporte nativo de paginación (`Pageable`)      |      |           |        X        |

>[!NOTE]
> JDBC no aparece porque, una vez que se incorpora un ORM, todo lo que antes se hacía a mano con `Connection`, `PreparedStatement` y `ResultSet` queda absorbido por Hibernate.
> - **Hibernate** se queda con las tareas propias del ORM, como conexiones, pool, mapeo `ResultSet`→entidad y administración del `PersistenceContext` (ciclo de vida `transient`/`managed`/`detached`/`removed`).
> - **Spring Data JPA** se queda con todo lo que es infraestructura de repositorio, como CRUD listo, query methods derivados del nombre, generación del proxy en runtime, paginación con `Pageable` e integración del manejo transaccional declarativo de Spring vía `@Transactional`.

### Ejercicio 4:

#### 1. Dependencias

- **`pom.xml`** con las dependencias actualizadas
    ```xml
        <dependency>
		    <groupId>org.springframework.data</groupId>
			<artifactId>spring-data-jpa</artifactId>
        </dependency>
  ```

#### 2. `SpringDataConfiguration`

Eliminamos las clase `HibernateConfiguration` y utilizamos las configuraciones de la clase `SpringDataConfiguration` 

>[!NOTE]
> Esta clase se encuentra creada en la rama `tp2-springdata` del repositorio que provee la cátedra

Esta clase ya trae `@EnableJpaRepositories` apuntando al package `unlp.info.bd2.repositories`, así que Spring Data va a descubrir e instanciar los repositorios automáticamente cuando los creemos en el paso 4.

> [!NOTE] Por qué no `application.properties` 
> En la rama `tp2-springdata` se eliminó el `application.properties` y se utiliza `SpringDataConfiguration` para configurar la conexión a la base de datos, pero podría haberse dejado el `application.properties` y usarlo para configurar el datasource en lugar de `SpringDataConfiguration`.

#### 4. Repositorios (`repositories/`)

- **Eliminar** `AbstractRepository`

- **Crear una interfaz por entidad raíz** que extienda `CrudRepository<T, Long>` :

```java
public interface UserRepository     extends CrudRepository<User, Long>     { … }
public interface RouteRepository    extends CrudRepository<Route, Long>    { … }
public interface ServiceRepository  extends CrudRepository<Service, Long>  { … }
public interface SupplierRepository extends CrudRepository<Supplier, Long> { … }
public interface PurchaseRepository extends CrudRepository<Purchase, Long> { … }
public interface ReviewRepository   extends CrudRepository<Review, Long>   { … }
public interface StopRepository     extends CrudRepository<Stop, Long>     { … }
public interface ItemServiceRepository extends CrudRepository<ItemService, Long> { … }
```

>[!IMPORTANT]
> Por cada método declarado en las interfaces, reemplazarlo por la firma equivalente de Spring Data JPA. Por ejemplo, `findById(Long id)` se reemplaza por el método `findById` que ya provee `CrudRepository`, pero con la firma que devuelve `Optional<T>` en vez de `T` o `null`. Para los que no tengan equivalente directo, usar `@Query` para escribir la consulta JPQL manualmente sobre el método de la interfaz.


#### 5. Capa de servicio (`services/`)

- Al cambiar los repos a interfaces de Spring Data, varias firmas cambian y el servicio rompe en varios puntos. Hay que adaptarlo.
  - Inyectar los repositorios vía `@Autowired` (ya estaba hecho con inyección por constructor en el TP1, no requiere cambios).
  - Adaptar las llamadas a `findById`: en Spring Data devuelve `Optional<T>` en vez de la entidad o `null`. Hay que reemplazar comparaciones contra `null` por `.isEmpty()` y desempaquetar con `.orElseThrow(...)` cuando se quiera fallar si no existe:
    - Antes
        ```java
        User user = userRepository.findById(userId);
        if (user == null) { throw new NotFoundException("El usuario no existe"); }
        ```
    - Ahora
        ```java
        User user = userRepository.findById(userId)
                                  .orElseThrow(() -> new NotFoundException("El usuario no existe"));
        ```
  - Reemplazar `merge()` por  `save()`: `CrudRepository` no expone `merge`. El `save()` de Spring Data **decide internamente entre `persist` (si la entidad es nueva) y `merge` (si ya tiene ID)**, así que es el reemplazo semánticamente equivalente para actualizar entidades detached.
- Las anotaciones `@Transactional` ya existentes **se conservan tal cual**. La única mejora opcional es marcar como `@Transactional(readOnly = true)` los métodos que solo leen.

#### 6. Entidades (`model/`)

Solo hay que **revisar imports**: si alguna entidad usa `org.hibernate.annotations.*` con semántica propietaria (no sus equivalentes JPA estándar), reemplazar por `jakarta.persistence.*`. 

#### 7. Tests

`ToursApplicationTests` y `ToursQuerysTests` utilizan `HibernateConfiguration` para arrancar el contexto de Spring. Hay que modificar su anotación `@ContextConfiguration` para que apunte a `SpringDataConfiguration` y así cargar la nueva configuración correcta.

### Ejercicio 5:  En la Práctica 1 se configuraba Hibernate mediante una clase de configuración Java para obtener la `SessionFactory`. ¿Cómo se reemplaza esta configuración usando `application.properties` en Spring Boot?

En la Práctica 1, la `HibernateConfiguration` era un `@Configuration` Java que declaraba **explícitamente** tres beans, el `DataSource` (con un `BasicDataSource` y la URL/credenciales hardcodeadas), el `LocalSessionFactoryBean` (con `packagesToScan` apuntando a `unlp.info.bd2.model` y las propiedades de Hibernate cargadas a mano en un `Properties`) y el `HibernateTransactionManager` colgado de esa `SessionFactory`.

Con Spring Boot esa clase deja de ser necesaria. Toda esa información se traslada a un archivo **declarativo** (`application.properties` o `application.yml`) que Spring Boot lee al arrancar:

- Al detectar la dependencia `spring-boot-starter-data-jpa` en el `pom.xml`, dispara una **auto-configuración** (`DataSourceAutoConfiguration`, `HibernateJpaAutoConfiguration`, `JpaRepositoriesAutoConfiguration`) que crea automáticamente los beans equivalentes al `DataSource`, al `EntityManagerFactory` (reemplaza a la `SessionFactory`) y al `JpaTransactionManager`.
- Esos beans se **parametrizan leyendo las propiedades** del archivo, ya no hay que instanciarlos a mano.
- Las entidades se detectan solas, no hace falta declarar `packagesToScan` mientras la clase `@SpringBootApplication` esté en un paquete padre de `unlp.info.bd2.model`.          |

El `application.properties` final queda así:

```properties
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.datasource.url=jdbc:mysql://localhost:3306/bd2_tours_0?createDatabaseIfNotExist=true&useSSL=false&useTimezone=true&serverTimezone=UTC&allowPublicKeyRetrieval=true
spring.datasource.username=root
spring.datasource.password=root

spring.jpa.hibernate.ddl-auto=create
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQLDialect
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.properties.hibernate.use_sql_comments=false
```

> [!NOTE]
> En este proyecto la cátedra optó por mantener una clase Java de configuración (`SpringDataConfiguration`) en lugar de usar `application.properties`. Ambos enfoques son válidos y producen el mismo resultado, lo que cambia es si la configuración se expresa como **código Java** (anotaciones `@Configuration` + beans) o como **propiedades declarativas** leídas por la auto-configuración de Spring Boot.

### Ejercicio 6:  Describir las propiedades más relevantes de Spring Data JPA que deben configurarse en `application.properties` para este proyecto. Incluir al menos: datasource (url, username, password, driver), dialecto de Hibernate, y la propiedad que controla si Hibernate debe crear, actualizar o validar el esquema. ¿Cuál de estos valores conviene usar durante el desarrollo?

Las propiedades se dividen en dos grupos
- las del **`DataSource`** (cómo se conecta a la base)
- las del **proveedor JPA/Hibernate** (cómo se mapean las entidades y se gestiona el esquema).

**DataSource:** 
- `spring.datasource.url` define el JDBC URL (motor, host, puerto, base y parámetros)
- `spring.datasource.username` las credenciales 
- `spring.datasource.password` las credenciales
- `spring.datasource.driver-class-name` la clase del driver (en MySQL, `com.mysql.cj.jdbc.Driver`)

**Hibernate:** 
- `spring.jpa.properties.hibernate.dialect` indica el dialecto SQL a usar (`org.hibernate.dialect.MySQLDialect` en este caso)
- `spring.jpa.hibernate.ddl-auto` controla qué hace Hibernate con el esquema al arrancar. Sus opciones:
  - `none` (no toca nada)
  - `validate` (verifica que el esquema coincida con las entidades)
  - `update` (aplica cambios incrementales sin borrar datos)
  - `create` (borra y recrea el esquema en cada arranque)
  - `create-drop` (igual que `create`, pero además borra al apagar). Como propiedades opcionales útiles en desarrollo
- `spring.jpa.show-sql=true` imprime y formatea el SQL generado
- `spring.jpa.properties.hibernate.format_sql=true` imprime y formatea el SQL generado

**Qué valor conviene usar en desarrollo:** 

Durante la etapa de desarrollo, lo más conveniente suele ser utilizar el valor `update`. Esto permite que el **esquema de la base de datos evolucione a la par de los cambios en el modelo de objetos** (como agregar nuevos atributos a
`User`) sin perder los datos de prueba ya cargados. Adicionalmente, se recomienda activar la propiedad `spring.jpa.show-sql=true `durante esta etapa para poder **visualizar en la consola las sentencias SQL que Hibernate genera** automáticamente y así facilitar el proceso de depuración.

## La interfaz `CrudRepository` y la jerarquía de repositorios

### Ejercicio 7:​ ¿Qué es `CrudRepository`? ¿De qué interfaz hereda y qué operaciones provee automáticamente?

`CrudRepository<T, ID>` es la interfaz base de Spring Data que expone las operaciones **CRUD genéricas** sobre una entidad `T` cuya clave primaria es de tipo `ID`. Hereda directamente de **`Repository<T, ID>`**, una interfaz marcadora (sin métodos) que Spring usa para descubrir los repositorios en el classpath y generar su implementación.

Las operaciones que provee automáticamente al extenderla son:

- **Escritura:** `save(entity)`, `saveAll(iterable)`, `delete(entity)`, `deleteById(id)`, `deleteAll()`, `deleteAll(iterable)`.
- **Lectura:** `findById(id)` (devuelve `Optional<T>`), `findAll()`, `findAllById(ids)`, `existsById(id)`, `count()`.

>[!IMPORTANT]
> Con solo declarar `interface UserRepository extends CrudRepository<User, Long> {}` ya quedan disponibles las once operaciones, sin escribir implementación.

### Ejercicio 8:​ ¿Que agrega cada nivel de la jerarquía respecto del anterior? Describir brevemente las diferencias entre `CrudRepository`, `PagingAndSortingRepository` y `JpaRepository`, indicando que operaciones o capacidades incorpora cada uno

La jerarquía es **acumulativa**, donde cada nivel hereda del anterior y agrega capacidades.

- **`CrudRepository<T, ID>`**: **CRUD básico** y funciona sobre cualquier store de Spring Data (JPA, MongoDB, Redis, etc.).

- **`PagingAndSortingRepository<T, ID>`** (extiende `CrudRepository`): agrega `findAll(Sort sort)` para **devolver los resultados ordenados** según un criterio y `findAll(Pageable pageable)` para **paginar** (devuelve `Page<T>` con metadatos: cantidad total, página actual, etc.). Útil cuando una colección puede crecer mucho y no se quiere traerla entera a memoria.

- **`JpaRepository<T, ID>`** (extiende `PagingAndSortingRepository`): incorpora operaciones **específicas de JPA** que no tienen sentido en otros stores, principalmente: `flush()` (forzar el flush del `EntityManager`), `saveAndFlush(entity)`, `deleteInBatch(iterable)` y `deleteAllInBatch()` (borrado en una sola sentencia JPQL, sin cargar entidades), y **devuelve `List<T>` en lugar de `Iterable<T>` en los `findAll`, lo cual es más práctico**.

### Ejercicio 9:​ Crear las interfaces de repositorio para las entidades del modelo extendiendo `CrudRepository`. Indicar los parámetros de tipo correctos (entidad e ID) para cada una: `PurchaseRepository`, `RouteRepository`, `UserRepository`, `ServiceRepository`, `SupplierRepository` y `ReviewRepository`.

Todas las entidades raíz del modelo usan `Long` como tipo de clave primaria (campo `id: Long` en el diagrama de clases), por lo que las seis interfaces comparten la forma `CrudRepository<Entidad, Long>`:

```java
public interface PurchaseRepository extends CrudRepository<Purchase, Long> {}
public interface RouteRepository    extends CrudRepository<Route, Long>    {}
public interface UserRepository     extends CrudRepository<User, Long>     {}
public interface ServiceRepository  extends CrudRepository<Service, Long>  {}
public interface SupplierRepository extends CrudRepository<Supplier, Long> {}
public interface ReviewRepository   extends CrudRepository<Review, Long>   {}
```

>[!NOTE]
> Para `UserRepository` no se declaran tres repositorios distintos (uno por `User`, `DriverUser` y `TourGuideUser`): al usar herencia JPA, el repositorio de la superclase `User` ya puede recuperar y persistir las subclases gracias al polimorfismo del ORM.

### Ejercicio 10:​ ¿Cómo genera Spring Data JPA la implementación concreta de los repositorios en tiempo de ejecución? ¿Qué rol juega el proxy dinámico de Java en este mecanismo?

Al arrancar la aplicación, **`@EnableJpaRepositories`** (o la auto-configuración de Spring Boot) dispara un escaneo del classpath que detecta todas las interfaces que extienden `Repository`. Para cada una, Spring Data:

1. Crea un **proxy dinámico de Java** (`java.lang.reflect.Proxy`) que implementa la interfaz declarada.
2. Conecta cada llamada del proxy a un **`InvocationHandler`** interno (`SimpleJpaRepository` para los métodos heredados de `CrudRepository`, o `RepositoryFactorySupport` que enruta a la implementación correspondiente).
3. Para los métodos declarados por el usuario, el handler decide en runtime cómo resolverlos: 
   - si llevan `@Query` ejecuta esa JPQL
   - si no, parsea el nombre del método y construye la consulta automáticamente (query derivation).

El **proxy dinámico** es la pieza clave porque **permite tener una implementación concreta de una interfaz sin escribir la clase**. Java genera en memoria un objeto que respeta el contrato de la interfaz, y todas las invocaciones se redirigen al `InvocationHandler` que sabe qué hacer con cada método. Ese objeto proxy es el que Spring inyecta en los servicios cuando estos declaran `@Autowired UserRepository userRepository`.

### Ejercicio 11:​ ¿Que diferencia hay entre `save()` en Spring Data JPA y `session.save()` / `session.merge()` en Hibernate directo? ¿Cómo decide Spring Data JPA si debe hacer un `INSERT` o un `UPDATE`?

En **Hibernate directo** existen dos operaciones distintas con semántica distinta:

- `session.save(entity)` / `session.persist(entity)`: asume que la entidad es **nueva** y genera un `INSERT`. Falla si ya tiene un ID asignado o si ya existe en la BD.
- `session.merge(entity)`: asume que la entidad está **detached** (existía en la BD pero no está managed) y genera un `UPDATE`, reincorporándola al `PersistenceContext`.

En **Spring Data JPA** existe **un único método** `save(entity)` que **decide automáticamente** entre uno y otro. La decisión se toma consultando si la entidad es nueva mediante el `EntityInformation` asociado al repositorio, que aplica el siguiente criterio:

1. Si la entidad implementa `Persistable<ID>`, se llama a `isNew()` y se respeta lo que esa lógica devuelva.
2. Si no, se mira el campo anotado con `@Id`: si su valor es `null` (o `0` para tipos primitivos), la entidad se considera **nueva** y se llama internamente a `entityManager.persist(entity)` → **INSERT**.
3. Si el `@Id` ya tiene valor, se considera **existente** y se llama a `entityManager.merge(entity)` → **UPDATE**.

Por eso `save()` reemplaza limpiamente a las llamadas a `merge()` del TP1: la elección entre `INSERT` y `UPDATE` deja de ser responsabilidad del programador y la asume Spring Data en función del estado del ID.