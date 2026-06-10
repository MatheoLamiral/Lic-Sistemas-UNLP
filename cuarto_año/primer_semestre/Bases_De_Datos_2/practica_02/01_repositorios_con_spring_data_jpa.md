# Repositorios con Spring Data JPA

## Migración de repositorios

### Ejercicio 12: Comparar el código de `PurchaseRepository` de la Práctica 1 (con `Session` de Hibernate) con el nuevo `PurchaseRepository` de Spring Data JPA. ¿Cuántas líneas de código se eliminaron? ¿Qué operaciones ya no es necesario implementar manualmente?

Comparando el código de `PurchaseRepository` del TP1 con el nuevo del TP2 implementado con Spring Data JPA, podemos observar que:
- Se redujeron **prácticamente a la mitad** las líneas de código (-27)
- Ya no es necesario implementar manualmente las funcionalidad de encontrar compras por código ya que es resuelta automáticamente por Spring Data a través de la **query derivation**
- El resto de funcionalidades, contar compras por ruta, obtener todas las compras de un usuario y obtener cantidad de compras entre fechas, se resuelven con consultas JPQL anotadas con `@Query` que son mucho más legibles y fáciles de escribir.

### Ejercicio 13: En la Práctica 1, los repositorios gestionaban internamente la Session. ¿Que recibe ahora un servicio que necesita usar un repositorio Spring Data? ¿Cómo se declara esa dependencia? ¿Dónde queda ahora la lógica de apertura y cierre de sesiones? 

**Qué recibe el servicio:** ya no recibe una clase concreta con la `Session` adentro, sino directamente la **interfaz del repositorio** (`PurchaseRepository`, `UserRepository`, etc.). Lo que Spring inyecta es el **proxy dinámico** que Spring Data generó en runtime y que implementa esa interfaz (ver [Ejercicio 10](00_introduccion_spring_data_jpa))

**Cómo se declara la dependencia:** mediante **inyección de dependencias por constructor** (recomendada) o por campo con `@Autowired`. Por ejemplo:

```java
@Service
public class ToursServiceImpl implements ToursService {

    private final PurchaseRepository purchaseRepository;
    private final UserRepository userRepository;

    @Autowired
    public ToursServiceImpl(PurchaseRepository purchaseRepository,
                            UserRepository userRepository) {
        this.purchaseRepository = purchaseRepository;
        this.userRepository = userRepository;
    }
    // ...
}
```

El servicio nunca toca la `Session`, ni la `SessionFactory`, ni el `EntityManager`, solo conoce la interfaz declarada.

**Dónde queda la lógica de apertura y cierre de sesiones:** la asume **Spring + Hibernate de forma transparente**, vinculada al ciclo de vida de la transacción. Cuando un método anotado con `@Transactional` (en la capa de servicio) empieza a ejecutarse, el `JpaTransactionManager` abre un `EntityManager` (que internamente envuelve una `Session` de Hibernate) y lo asocia al hilo actual. Todas las operaciones de repositorio que se invoquen dentro de ese método reutilizan ese mismo `EntityManager`. Al terminar el método, el transaction manager hace el commit (o rollback ante excepción) y cierra la sesión. El programador **ya no abre ni cierra nada**, solo decide los límites transaccionales con `@Transactional`.

## Query Methods

### Ejercicio 14: ¿Cómo funciona la generación de consultas por nombre de método en Spring Data JPA? Describir las palabras clave principales que puede interpretar (`findBy`, `existsBy`, `countBy`, `deleteBy`) y cómo se combinan con los atributos de la entidad.

Spring Data JPA implementa una técnica llamada **query derivation**: cuando arranca la aplicación, parsea el **nombre de cada método** declarado en la interfaz del repositorio, lo separa en un *prefijo de acción* y un *predicado*, y a partir de ahí construye automáticamente la consulta JPQL equivalente, sin que el programador escriba ni una línea de implementación.

**Estructura general:** `<prefijo>By<Atributo[Comparador]>[And|Or<Atributo[Comparador]>]*`. El prefijo define qué hacer con el resultado, el bloque después de `By` define el filtro `WHERE`.

**Prefijos principales:**

- **`findBy...`** (o sus sinónimos `getBy...`, `readBy...`, `queryBy...`): devuelve entidades que cumplen la condición. El tipo de retorno (`Optional<T>`, `T`, `List<T>`, `Page<T>`) decide la cardinalidad esperada. Ejemplo: `Optional<User> findByEmail(String email)`.
- **`existsBy...`**: devuelve `boolean`, indicando si existe al menos una entidad que cumpla la condición. Internamente se traduce a un `SELECT COUNT(*) > 0` o `SELECT 1 LIMIT 1`. Ejemplo: `boolean existsByRoute(Route route)`.
- **`countBy...`**: devuelve `long`, traducido a `SELECT COUNT(*)`. Ejemplo: `long countByRatingGreaterThanEqual(int rating)`.
- **`deleteBy...`** (o `removeBy...`): borra todas las entidades que cumplan la condición. Devuelve `void` o `long` (cantidad borrada). Requiere ejecutarse dentro de una transacción.

**Cómo se combinan con los atributos de la entidad:** después de `By` se escribe el **nombre del atributo** de la entidad en PascalCase. Spring Data navega por las propiedades, incluso a través de relaciones, usando *dot notation* implícita.

- `findByUsername(String u)` → `WHERE u.username = ?1`.
- `findByUserUsername(String u)` → navega `Purchase → user → username`, equivalente a `WHERE p.user.username = ?1`.
- Se pueden encadenar condiciones con `And` / `Or`: `findByUserUsernameAndDateAfter(String u, Date d)`.
- Se aceptan **comparadores** como sufijo del atributo: `GreaterThan`, `LessThan`, `Between`, `Like`, `Containing`, `In`, `IsNull`, `IsNotNull`, `True`, `False`, etc.
- Se admiten **modificadores** sobre el resultado: `Top3`, `First10`, `Distinct`, `OrderByPriceAsc`. Ejemplo: `List<Route> findTop3ByOrderByPriceDesc()`.

>[!NOTE]
> Si el parser no logra emparejar el nombre del método con un atributo válido, Spring Data **falla al arrancar** la aplicación, no en runtime, lo que da seguridad temprana frente a errores de tipeo.

### Ejercicio 15: ​¿Cómo se pasan los parametros a un Query Method? ¿Cómo hace Spring Data JPA para asociar cada parámetro del método con la condición correspondiente en la consulta? ¿Qué ocurre si el orden de los parámetros no coincide con el orden de las condiciones en el nombre del método?

Los parámetros se pasan **como argumentos posicionales del método**, en el mismo orden en que aparecen las condiciones dentro del nombre. Spring Data no analiza el *nombre* de los parámetros: hace una asociación **estrictamente posicional** entre el i-ésimo argumento y la i-ésima condición declarada después de `By`.

Por ejemplo, dada la entidad `Purchase` con los atributos `user.username` y `date`:

```java
List<Purchase> findByUserUsernameAndDateAfter(String username, Date fromDate);
```

Spring Data construye internamente la JPQL:

```sql
SELECT p FROM Purchase p
WHERE p.user.username = ?1 AND p.date > ?2
```

El primer argumento (`username`) se asocia a la condición `UserUsername`, el segundo (`fromDate`) a `DateAfter`. Además, los **tipos** de los parámetros deben coincidir con los tipos del atributo correspondiente (incluido el envoltorio que exija el comparador, por ejemplo `Between` requiere **dos** argumentos para un mismo atributo).

**Qué pasa si el orden no coincide:** si los argumentos están **invertidos pero los tipos siguen siendo compatibles**, la app arranca sin error pero la consulta se ejecuta con los valores cruzados, produciendo un **bug silencioso** (devuelve resultados incorrectos). Si los tipos no son compatibles (por ejemplo, pasar un `Date` donde se esperaba un `String`), Spring Data **falla al arrancar** porque el parser detecta la incongruencia al asociar las condiciones del nombre con la firma del método. Por eso conviene escribir nombres claros y, cuando hay varios parámetros del mismo tipo, validar con tests que la consulta efectivamente discrimine cada caso.

### Ejercicio 16: ​Investigar y para cada uno de los siguientes requerimientos indicar si es posible resolverlo con un Query Method y escribir la firma del método correspondiente. Si no es posible, explicar por qué:

#### a)​ Buscar todas las Purchase de un usuario dado su username.

Es posible con un Query Method usanddo el prefijo `findBy` 

```java
    List<Purchase> findByUserUsername(String username);
```

#### b)​ Verificar si existe alguna Purchase para una Route dada.

Es posible con un Query Method usando el prefijo `existsBy`

```java
    boolean existsByRoute(Route route);
```

>[!NOTE]
> Si en el servicio solo tenemos el ID y no la entidad completa, podemos también declarar `existsByRouteId(Long routeId)` para evitar tener que cargar la Route antes.

#### c)​ Contar cuantas Review tienen un rating mayor o igual a un valor dado.

Es posible con un Query Method usando el prefijo `countBy` y el comparador `GreaterThanEqual`

```java
    long countByRatingGreaterThanEqual(int rating);
```

#### d)​ Obtener todas las Route cuyo precio sea menor a un valor dado, ordenadas por nombre.

Es posible con un Query Method usando el prefijo `findBy`, el comparador `LessThan` y el modificador `OrderBy`

```java
    List<Route> findByPriceLessThanOrderByNameAsc(double price);
```

>[!NOTE]
> `Asc` es el orden por defecto, por lo que también se podría omitir y escribir `findByPriceLessThanOrderByName(double price)`. Para orden descendente se usaría `Desc` en su lugar.

#### e)​ Buscar un User por su email.

Es posible con un Query Method usando el prefijo `findBy`

```java
    Optional<User> findByEmail(String email);
```

#### f)​ Obtener los top 3 Route con mayor cantidad de Purchase.

No es posible con un Query Method
- El problema concreto es que requiere `GROUP BY` + `COUNT(p)` sobre la relación `Route` → `purchases` y ordenar por el resultado de esa agregación. Los Query Methods solo arman condiciones `WHERE` y `ORDER BY` sobre atributos directos, no sobre funciones de agregación.
- Para resolver este requerimiento sería necesario escribir una consulta JPQL personalizada con `@Query`

### Ejercicio 17: ​Investigar cuales son las palabras clave (keywords) disponibles en Spring Data JPA para construir Query Methods. ¿Qué tipos de condiciones, comparaciones y operadores lógicos soporta?

Las palabras clave de Spring Data JPA se agrupan en **cuatro categorías**: 
- Prefijos de acción
- Operadores lógicos
- Comparadores
- Modificadores del resultado.

**Prefijos de acción** (qué hacer con la consulta): `findBy`, `getBy`, `readBy`, `queryBy`, `searchBy` (devuelven entidades), `existsBy` (devuelve `boolean`), `countBy` (devuelve `long`) y `deleteBy` / `removeBy` (borran y devuelven `void` o `long`).

**Operadores lógicos** para encadenar condiciones: `And` y `Or`. Por ejemplo, `findByPriceLessThanAndNameContaining(...)` o `findByEmailOrUsername(...)`. No existen paréntesis ni operadores de precedencia, las combinaciones complejas requieren `@Query`.

**Comparadores** (sufijo del atributo). Los más usados son:

- **Comparación numérica/temporal:** `GreaterThan`, `GreaterThanEqual`, `LessThan`, `LessThanEqual`, `Between`, `Before`, `After`.
- **Igualdad:** `Is`, `Equals` (implícitos si no hay sufijo) y `Not`.
- **Strings:** `Like`, `NotLike`, `Containing`, `StartingWith`, `EndingWith`, `IgnoreCase` (combinable, ej.: `findByEmailIgnoreCase`).
- **Nulos y booleanos:** `IsNull`, `IsNotNull`, `True`, `False`.
- **Colecciones:** `In`, `NotIn` (espera un `Collection<T>` o array), y comparadores sobre relaciones como `Empty` / `NotEmpty` para colecciones de la entidad.

**Modificadores del resultado:**

- **Limitación:** `First`, `Top` con un número opcional (`findFirstByOrderByDateDesc`, `findTop3ByOrderByPriceAsc`).
- **Deduplicación:** `Distinct` (`findDistinctByCategory`).
- **Ordenamiento estático:** `OrderBy<Atributo>[Asc|Desc]`, encadenable (`OrderByPriceDescNameAsc`). Para ordenamiento dinámico se usa el parámetro `Sort` o `Pageable`.

>[!NOTE]
> Los operadores lógicos soportados son solamente `And` y `Or`, lineales y sin precedencia explícita. Para `NOT` lógico se usa el comparador `Not` aplicado al atributo (`findByStatusNot(...)`). Combinaciones más sofisticadas (paréntesis, agregaciones, joins con condiciones, subconsultas) **escapan al lenguaje de Query Methods** y deben resolverse con `@Query`.

### Ejercicio 18: ​¿Qué limitaciones tienen los Query Methods? Describir al menos tres casos del modelo donde esta técnica resulta insuficiente y es necesario otro enfoque. Describa los otros enfoques posibles para implementar dichas consultas.

Los Query Methods son ideales para consultas **simples** (filtros sobre uno o dos atributos, igualdad, comparaciones básicas, navegación por relaciones), pero su DSL(Domain Specific Language) es deliberadamente limitado. Sus principales limitaciones son:

- **No soportan funciones de agregación** (`COUNT`, `SUM`, `AVG`, `MAX`, `MIN`) ni `GROUP BY`.
- **No soportan subconsultas** ni `NOT EXISTS` / `EXISTS` con condiciones.
- **No permiten proyecciones arbitrarias** (`SELECT new DTO(...)`, selección de columnas específicas).
- **No tienen precedencia ni paréntesis** en operadores lógicos, todo se evalúa de izquierda a derecha.
- **No expresan joins explícitos con condiciones** sobre la entidad relacionada más allá de la navegación simple.

**Tres casos concretos del modelo donde Query Methods resulta insuficiente:**

1. **`getMostDemandedService()` — agregación + GROUP BY + ordenar por agregado.** Requiere contar la `quantity` total de cada `Service` a través de los `ItemService` y devolver el de mayor demanda. Necesita `SUM(item.quantity)` agrupando por `Service` y ordenando por la suma, todo fuera del alcance de los Query Methods.

2. **`getRoutesNotSell()` — subconsulta o left join filtrando por ausencia.** Pide todas las `Route` que no tienen ninguna `Purchase` asociada. Se resuelve naturalmente con `WHERE r NOT IN (SELECT p.route FROM Purchase p)` o con `LEFT JOIN` + `WHERE p IS NULL`. Los Query Methods no expresan ninguna de las dos formas.

3. **`getTop3RoutesWithMaxRating()` — agregación sobre relación indirecta.** Implica unir `Route` con sus `Purchase`, luego con sus `Review`, calcular `AVG(rating)` por ruta y traer las tres con mayor promedio. Combina join multi-nivel, agregación, `GROUP BY` y ordenamiento por el agregado, todo fuera de lo que el parser puede derivar.

**Enfoques posibles para resolverlos:**

- **`@Query` con JPQL**: la opción más común. Permite escribir la consulta en términos del modelo de objetos (`SELECT r FROM Route r LEFT JOIN r.purchases p WHERE p IS NULL`). Sigue siendo portable entre motores porque Hibernate la traduce al dialecto correspondiente.
- **`@Query(nativeQuery = true)`**: cuando se necesitan funciones específicas del motor (window functions, hints, sintaxis particular de MySQL/PostgreSQL). Pierde portabilidad y devuelve resultados sin mapeo automático a entidad si la proyección no coincide.
- **Spring Data JPA Specifications** (`JpaSpecificationExecutor`): construcción **programática** y composable de filtros usando la Criteria API de JPA. Útil para consultas dinámicas armadas en runtime (filtros que se aplican condicionalmente según parámetros del usuario).
- **Criteria API de JPA** directamente: equivalente a Specifications pero sin la integración de Spring Data. Verbosa pero type-safe.
- **Custom repository implementation**: crear una interfaz `XxxRepositoryCustom` con métodos arbitrarios y una clase `XxxRepositoryImpl` que use el `EntityManager` directamente. Spring Data la compone automáticamente con la interfaz principal del repositorio. Es la salida cuando ninguna de las anteriores alcanza (por ejemplo, llamadas a stored procedures, uso de la API nativa de Hibernate, queries que generan resultados muy custom).

## Consultas con @Query

### Ejercicio 19: En la Práctica 1 se utilizaron consultas HQL (Hibernate Query Language). ¿Que diferencia hay entre HQL y JPQL (Java Persistence Query Language)? ¿Son intercambiables? ¿Cual de los dos acepta `@Query` por defecto?

Ambos son **lenguajes de consulta orientados a objetos**: en lugar de escribir SQL sobre tablas y columnas, se consulta sobre **entidades y sus atributos**, y el ORM traduce esa consulta al SQL del motor.

**Diferencia entre HQL y JPQL:**

- **JPQL** es el lenguaje de consulta definido por la **especificación JPA**. Es un estándar, por lo que funciona igual con cualquier proveedor JPA (Hibernate, EclipseLink, etc.).
- **HQL** es el lenguaje **propietario de Hibernate**, anterior a JPA. JPQL nació tomando a HQL como base, por lo que HQL es esencialmente un **superconjunto de JPQL**, soporta todo lo que JPQL soporta y además agrega características propias de Hibernate (por ejemplo, ciertos operadores, funciones extra, `UPDATE`/`DELETE` con sintaxis ampliada, fetch joins más flexibles, etc.).

**¿Son intercambiables?** Parcialmente. Como JPQL es un subconjunto de HQL, **toda consulta JPQL es válida como HQL**, pero **no al revés**. Una consulta que use características exclusivas de HQL no será portable a otro proveedor JPA. En la práctica, las consultas del TP1 escritas en "HQL" eran en su mayoría JPQL estándar (selects, joins, where con parámetros), por lo que funcionan sin cambios.

**¿Cuál acepta `@Query` por defecto?** La anotación `@Query` de Spring Data JPA interpreta **JPQL por defecto**. Para escribir SQL nativo del motor hay que indicarlo explícitamente con `@Query(value = "...", nativeQuery = true)`. Como Spring Data corre sobre un proveedor JPA (Hibernate, en este proyecto), una consulta `@Query` con sintaxis HQL no estándar igual podría llegar a ejecutarse, pero **no es recomendable**, lo correcto y portable es atenerse a JPQL.

### Ejercicio 20: ¿Que diferencia hay entre una consulta `@Query` con JPQL y una con `nativeQuery = true`? ¿Cuándo conviene cada una? Dar un ejemplo concreto del modelo para cada caso.

La diferencia está en **el lenguaje en el que se escribe la consulta** y, en consecuencia, en su nivel de abstracción:

- **`@Query` con JPQL** (comportamiento por defecto): se consulta sobre **entidades y atributos** del modelo de objetos. Hibernate traduce esa JPQL al SQL del dialecto configurado, por lo que la consulta es **portable** entre motores. El resultado se mapea automáticamente a entidades.
- **`@Query(nativeQuery = true)`**: la consulta se escribe en **SQL nativo**, sobre las tablas y columnas reales de la base. No pasa por la traducción de Hibernate, se ejecuta tal cual contra el motor. Es **no portable** (atada a la sintaxis de MySQL/PostgreSQL/etc.) y el mapeo del resultado solo es automático si las columnas devueltas coinciden con la entidad.

**Cuándo conviene cada una:**

- **JPQL** es la opción por defecto y debe preferirse siempre que sea posible. Es portable, más legible, valida los nombres contra el modelo y devuelve entidades directamente.
- **SQL nativo** se reserva para lo que JPQL no puede expresar, como funciones específicas del motor (*window functions*, expresiones particulares), optimizaciones puntuales con *hints*, o consultas sobre tablas que no están mapeadas como entidades.

**Ejemplo con JPQL** — obtener todas las `Route` que no tienen ninguna `Purchase` (`getRoutesNotSell`):

```java
@Query("SELECT r FROM Route r WHERE r NOT IN (SELECT p.route FROM Purchase p)")
List<Route> getRoutesNotSell();
```

**Ejemplo con SQL nativo** — usar una *window function* de MySQL para rankear las rutas por cantidad de compras, algo que JPQL estándar no soporta:

```java
@Query(value = """
    SELECT r.* FROM route r
    JOIN (
        SELECT route_id, RANK() OVER (ORDER BY COUNT(*) DESC) AS rnk
        FROM purchase GROUP BY route_id
    ) ranked ON r.id = ranked.route_id
    WHERE ranked.rnk <= 3
    """, nativeQuery = true)
List<Route> getTop3RoutesByPurchases();
```

### Ejercicio 21: ¿Cómo se pasan parámetros a una consulta @Query? Describir y comparar las dos formas: parámetros posicionales `(?1, ?2)` y parámetros nombrados `(@Param)`. ¿Cuál es la forma recomendada y por qué?

Los parámetros a una consulta `@Query` pueden pasarse de dos formas, por **posición** o por **nombre**.

**1. Parámetros posicionales (`?1`, `?2`, …):** dentro de la JPQL se referencia cada parámetro con `?n`, donde `n` es la posición (1-indexada) del argumento en la firma del método.

```java
@Query("SELECT p FROM Purchase p WHERE p.user.username = ?1 AND p.date > ?2")
List<Purchase> getPurchasesAfter(String username, Date fromDate);
```

Acá `?1` se sustituye por `username` y `?2` por `fromDate`. No requieren anotación adicional, pero el binding es **estrictamente por orden**.

**2. Parámetros nombrados (`@Param`):** dentro de la JPQL se referencia cada parámetro con `:nombre`, y en la firma del método se anota cada argumento con `@Param("nombre")`.

```java
@Query("SELECT p FROM Purchase p WHERE p.user.username = :username AND p.date > :fromDate")
List<Purchase> getPurchasesAfter(@Param("username") String username,
                                 @Param("fromDate") Date fromDate);
```

El binding se hace por el **nombre** del parámetro, no por su posición.

**Comparación:**

- **Legibilidad:** la versión con `@Param` deja claro qué representa cada placeholder en la consulta. Con `?1`/`?2` hay que ir y volver entre el SQL y la firma del método para entender qué es cada uno.
- **Mantenibilidad:** si se cambia el orden de los parámetros de la firma, la versión posicional se rompe silenciosamente (si los tipos siguen siendo compatibles); la versión nombrada sigue funcionando correctamente porque el binding va por nombre.
- **Reutilización del parámetro:** con nombres, se puede usar el mismo parámetro varias veces en la consulta (`:date` aparece en dos condiciones) sin pasarlo dos veces. Con posicionales también se puede repetir `?1`, pero la lectura es más confusa.

>[!NOTE]Forma recomendada
> La forma recomendada son los parámetros nombrados con `@Param`**. Es la práctica estándar en Spring Data JPA por su mejor legibilidad y porque desacopla el orden de los argumentos del orden en que aparecen en la consulta, evitando bugs silenciosos al refactorizar.

## Paginación y ordenamiento

### Ejercicio 22: ​¿Qué es la interfaz Pageable? ¿Cómo se construye una instancia de Pageable? ¿Qué información encapsula (número de página, tamaño, ordenamiento)?

`Pageable` es una **interfaz de Spring Data** que encapsula los parámetros necesarios para solicitar una página específica de resultados, sin tener que modificar la consulta JPQL ni armar manualmente `LIMIT` y `OFFSET`. Cuando se pasa como parámetro a un método de repositorio, Spring Data le agrega automáticamente a la consulta el `LIMIT`, el `OFFSET` y el `ORDER BY` correspondientes.

**Qué información encapsula:**

- **Número de página** (0-indexado): qué página se quiere.
- **Tamaño de página**: cuántos elementos trae cada página.
- **Ordenamiento** (`Sort`): por qué atributo/s y en qué dirección se ordenan los resultados. Es opcional, si no se especifica los resultados vienen sin orden definido.

**Cómo se construye una instancia:** la implementación más común es `PageRequest`, que provee varios métodos de factoría:

```java
// Página 0 (la primera), tamaño 10, sin ordenamiento
Pageable p1 = PageRequest.of(0, 10);

// Página 1 (la segunda), tamaño 20, ordenado por precio ascendente
Pageable p2 = PageRequest.of(1, 20, Sort.by("price").ascending());

// Ordenamiento compuesto: precio descendente y luego nombre ascendente
Pageable p3 = PageRequest.of(0, 5,
    Sort.by(Sort.Order.desc("price"), Sort.Order.asc("name")));
```

### Ejercicio 23: ​¿Que diferencia hay entre los tipos de retorno `Page<T>` y `Slice<T>`? ¿Cuándo conviene cada uno? ¿Qué consulta adicional ejecuta `Page<T>` que `Slice<T>` no ejecuta?

Ambos representan un **subconjunto** de resultados devueltos por una consulta paginada, pero difieren en la cantidad de información que traen.

- **`Slice<T>`**: trae los elementos de la página actual y un *flag* que indica si **existe una página siguiente** (`hasNext()`). Para saber eso, Spring Data pide al motor `pageSize + 1` filas, no necesita una consulta extra.
- **`Page<T>`** (extiende `Slice<T>`): además de lo anterior, conoce la **cantidad total de elementos** (`getTotalElements()`) y la **cantidad total de páginas** (`getTotalPages()`). Para calcular eso ejecuta una **segunda consulta `SELECT COUNT(*)`** sobre la misma condición.

**Cuándo conviene cada uno:**

- **`Page<T>`**: cuando la UI necesita mostrar el total de páginas o de resultados (típica paginación con "Página 3 de 47"). Tiene el costo extra del `COUNT`.
- **`Slice<T>`**: cuando solo importa saber si hay más resultados ("Cargar más", scroll infinito). Es más eficiente porque ahorra el `COUNT`, sobre todo en tablas grandes donde el conteo es costoso.

**Consulta adicional:** la única diferencia real en términos de queries es ese `SELECT COUNT(*)` extra que `Page<T>` dispara y `Slice<T>` no.

### Ejercicio 24: ​Mostrar como se invocará desde la capa de servicio un método paginado para obtener la segunda página de compras de un usuario, con 10 resultados ordenados por fecha descendente.

Suponiendo que `PurchaseRepository` declara un método paginado que recibe el `username` y un `Pageable`:

```java
@Query("SELECT p FROM Purchase p WHERE p.user.username = :username")
Page<Purchase> findPurchasesOfUser(@Param("username") String username, Pageable pageable);
```

La invocación desde el servicio sería:

```java
public Page<Purchase> getSecondPagePurchasesOf(String username) {
    Pageable pageable = PageRequest.of(
        1,                                  // página 1 = la segunda (0-indexado)
        10,                                 // 10 resultados por página
        Sort.by("date").descending()        // ordenadas por fecha desc
    );
    return purchaseRepository.findPurchasesOfUser(username, pageable);
}
```

Spring Data agrega automáticamente a la consulta el `ORDER BY p.date DESC LIMIT 10 OFFSET 10` (la segunda página de 10 elementos arranca en el índice 10).

### Ejercicio 25: ​¿Cómo se agrega ordenamiento a un Query Method sin usar Pageable? ¿Qué palabra clave se usa en el nombre del método? Mostrar un ejemplo concreto con el modelo.

La palabra clave es **`OrderBy`**, que se incluye en el nombre del método seguida del atributo y la dirección (`Asc` o `Desc`). Es un ordenamiento **estático**, queda fijo en la firma del método, a diferencia de `Sort`/`Pageable` que permiten variar el orden en runtime.

La sintaxis general es `...OrderBy<Atributo>[Asc|Desc]`, y se pueden encadenar varios atributos, `OrderByPriceDescNameAsc` ordena primero por precio descendente y luego por nombre ascendente.

**Ejemplo con el modelo**: obtener todas las `Route` cuyo precio es menor a un valor dado, ordenadas por nombre ascendente:

```java
List<Route> findByPriceLessThanOrderByNameAsc(float price);
```

Spring Data lo traduce internamente a:

```sql
SELECT r FROM Route r WHERE r.price < ?1 ORDER BY r.name ASC
```

Como `Asc` es el orden por defecto, también podría escribirse `findByPriceLessThanOrderByName(float price)` y funciona igual.

## Implementación de consultas del modelo

### Ejercicio 26: ​Para cada consulta, indicar la estrategia elegida (Query Method o @Query) e implementarla en el repositorio correspondiente:

| Consulta                                            | Repositorio          | Estrategia elegida    |
| --------------------------------------------------- | -------------------- | --------------------- |
| `getAllPurchasesOfUsername(String username)`        | `PurchaseRepository` | Query Method          |
| `getUserSpendingMoreThan(float amount)`             | `UserRepository`     | `@Query`              |
| `getTopNSuppliersInPurchases(int n)`                | `SupplierRepository` | `@Query` + `Pageable` |
| `getCountOfPurchasesBetweenDates(Date from, Date to)` | `PurchaseRepository` | Query Method        |
| `getRoutesWithStop(Stop stop)`                      | `RouteRepository`    | Query Method          |
| `getMaxStopOfRoutes()`                              | `RouteRepository`    | `@Query`              |
| `getRoutesNotSell()`                                | `RouteRepository`    | `@Query`              |
| `getTop3RoutesWithMaxRating()`                      | `RouteRepository`    | `@Query` + `Pageable` |
| `getMostDemandedService()`                          | `ServiceRepository`  | `@Query` + `Pageable` |
| `getTourGuidesWithRating1()`                        | `UserRepository`     | `@Query`              |

>[!NOTE]
> - se usa **Query Method** cuando la consulta se resuelve con un filtro simple sobre atributos o navegación directa por relaciones
> - se usa **`@Query`** cuando se necesitan agregaciones (`SUM`, `COUNT`, `AVG`, `MAX`), subconsultas (`NOT IN`, `NOT EXISTS`) o joins con `GROUP BY`. Las consultas que requieren limitar el resultado a los *N* primeros según un agregado (`getTopN...`, `getTop3...`, `getMostDemanded...`) combinan `@Query` con `Pageable` para aplicar el `LIMIT` de forma portable.

### Ejercicio 27: ​Implementar cada una de las consultas de la tabla anterior en el repositorio correspondiente, utilizando la estrategia indicada. Para las consultas que requieran paginación, utilizar Pageable como parámetro adicional.

**`PurchaseRepository`**

```java
@Query("select p from Purchase p where p.user.username = :username")
public List<Purchase> getAllPurchasesOfUsername(String username);

@Query("select count(p) from Purchase p where p.date between :start and :end")
public long getCountOfPurchasesBetweenDates(Date start, Date end);
```

`getAllPurchasesOfUsername` podría resolverse también como Query Method (`findByUserUsername`), pero se mantuvo como `@Query` por consistencia con el TP1 y para que la JPQL quede explícita. `getCountOfPurchasesBetweenDates` usa `count(p)` con el comparador `BETWEEN` sobre la fecha.

**`UserRepository`**

```java
@Query("select distinct p.user from Purchase p where p.totalPrice >= :mount")
public List<User> getUserSpendingMoreThan(float mount);

@Query("select distinct g " +
        "from TourGuideUser g " +
        "join g.routes r " +
        "where exists (" +
        "    select 1 from Purchase p " +
        "    where p.route = r and p.review.rating = 1" +
        ")")
public List<TourGuideUser> getTourGuidesWithRating1();
```

`getUserSpendingMoreThan` filtra `Purchase` por `totalPrice` y proyecta `distinct p.user` para no repetir usuarios. `getTourGuidesWithRating1` hace `JOIN` con las rutas del guía y usa `EXISTS` para chequear que alguna compra de esa ruta tenga `rating = 1`, con `distinct` para evitar duplicados cuando un mismo guía cumple por varias rutas.

**`SupplierRepository`** (con `Pageable`)

```java
@Query("select i.service.supplier " +
        "from ItemService i " +
        "group by i.service.supplier " +
        "order by count(i) desc")
public List<Supplier> getTopNSuppliersInPurchases(Pageable pageable);
```

Agrupa los `ItemService` por el `Supplier` de su servicio y ordena por el conteo descendente. El `Pageable` aplica el `LIMIT N` desde el servicio (ej. `PageRequest.of(0, n)`), evitando hardcodear el límite en la JPQL.

**`RouteRepository`**

```java
@Query("select r from Route r where :stop member of r.stops")
public List<Route> getRoutesWithStop(Stop stop);

@Query("select max(size(r.stops)) from Route r")
public Long getMaxStopOfRoutes();

@Query("select r from Route r " +
        "where not exists (select 1 from Purchase p where p.route = r)")
public List<Route> getRoutesNotSell();

@Query("select p.route " +
        "from Purchase p " +
        "where p.review is not null " +
        "group by p.route " +
        "order by avg(p.review.rating) desc")
public List<Route> getTop3RoutesWithMaxRating(Pageable pageable);
```

- `getRoutesWithStop` usa el operador JPQL `MEMBER OF` para verificar pertenencia a la colección `stops` de la ruta.
- `getMaxStopOfRoutes` aplica la función `size(...)` de JPQL sobre la colección y obtiene el `MAX`.
- `getRoutesNotSell` usa `NOT EXISTS` con una subconsulta correlacionada sobre `Purchase`, equivalente al `LEFT JOIN ... WHERE p IS NULL`.
- `getTop3RoutesWithMaxRating` agrupa las compras por ruta y ordena por el promedio de rating descendente. El filtro `p.review is not null` evita incluir compras sin reseña (`Review` es opcional en el modelo). El `Pageable` aplica el `LIMIT 3` desde el servicio.

**`ServiceRepository`** (con `Pageable`)

```java
@Query("select i.service " +
        "from ItemService i " +
        "group by i.service " +
        "order by sum(i.quantity) desc")
public List<Service> getMostDemandedService(Pageable pageable);
```

Agrupa los `ItemService` por `Service` y ordena por la suma de `quantity` descendente. Al usar `Pageable` con tamaño 1 se obtiene el servicio más demandado, manteniendo flexibilidad para pedir el top *N* si fuera necesario.

>[!NOTE]
> Las consultas paginadas (`getTopNSuppliersInPurchases`, `getTop3RoutesWithMaxRating`, `getMostDemandedService`) reciben `Pageable` y devuelven `List<T>` en lugar de `Page<T>` porque no se necesita el conteo total ni `hasNext()`. Esto evita la consulta adicional `SELECT COUNT(*)` que `Page<T>` dispararía (ver [Ejercicio 23](#ejercicio-23-que-diferencia-hay-entre-los-tipos-de-retorno-paget-y-slicet-cuándo-conviene-cada-uno-qué-consulta-adicional-ejecuta-paget-que-slicet-no-ejecuta)).


### Ejercicio 28: ​Comparar la implementación de al menos dos consultas complejas (por ejemplo `getTopNSuppliersInPurchases` y `getTop3RoutesWithMaxRating`) entre la Práctica 1 y esta práctica. ¿Qué diferencias hay en términos de cantidad de código, legibilidad y acoplamiento a la infraestructura de persistencia? A partir de esta comparación, ¿que es el código boilerplate y que ventaja concreta representa su reducción para el mantenimiento de un proyecto real?

**1. `getTopNSuppliersInPurchases`**

TP1 (Hibernate directo, sobre `AbstractRepository<Supplier>`):

```java
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

TP2 (Spring Data JPA, interfaz `SupplierRepository`):

```java
@Query("select i.service.supplier " +
        "from ItemService i " +
        "group by i.service.supplier " +
        "order by count(i) desc")
public List<Supplier> getTopNSuppliersInPurchases(Pageable pageable);
```

**2. `getTop3RoutesWithMaxRating`**

TP1:

```java
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

TP2:

```java
@Query("select p.route " +
        "from Purchase p " +
        "where p.review is not null " +
        "group by p.route " +
        "order by avg(p.review.rating) desc")
public List<Route> getTop3RoutesWithMaxRating(Pageable pageable);
```

**Diferencias concretas:**

- **Cantidad de código:** la JPQL es prácticamente la misma en ambos casos, pero alrededor se eliminan 5–7 líneas por consulta: ya no hay `session().createQuery(...)`, ni el segundo argumento con el `Class<T>` esperado, ni `setMaxResults(n)`, ni `getResultList()`. El TP1 además dependía de `AbstractRepository<T>` que en el TP2 desaparece por completo.
- **Legibilidad:** en el TP2 la consulta queda **declarada al lado del método**, en una sola anotación. El lector ve la firma (qué entra, qué sale) y la JPQL (qué hace), sin ruido de envoltorios de Hibernate. En el TP1 hay que leer "ignorando" llamadas técnicas (`session()`, `createQuery`, `getResultList`) para llegar al `select`.
- **Acoplamiento a la infraestructura de persistencia:** el TP1 importa `org.hibernate.Session` y `org.hibernate.SessionFactory` directamente, atando los repositorios a Hibernate como producto específico. El TP2 solo importa anotaciones de Spring Data y JPA, una migración a otro proveedor JPA (EclipseLink, etc.) sería transparente. Además, en el TP2 el límite del resultado (`setMaxResults`) deja de estar hardcodeado dentro de la consulta y se decide desde el servicio vía `Pageable`, lo que la hace más reutilizable.


>[!NOTE] ¿Qué es el código boilerplate?**
> Se llama **código boilerplate** a todo aquel código repetitivo, estructural, que hay que escribir una y otra vez para que la lógica de negocio pueda existir, pero que **no aporta valor al problema que se está resolviendo**. Es código de "andamiaje" que no describe *qué* hace la aplicación, sino *cómo* hablar con el framework, la API o el lenguaje.


**Ventaja concreta de reducirlo en un proyecto real:**

- **Menos código para leer y mantener:** el ojo va directo a la lógica relevante (la JPQL, la regla del negocio) sin atravesar capas técnicas.
- **Menos superficie para bugs:** cada línea repetitiva es una oportunidad de cometer un error sutil (un `setParameter` olvidado, un tipo equivocado en `createQuery`). Si esa línea no existe, ese error no es posible.
- **Cambios globales más simples:** si mañana se cambia el mecanismo de persistencia (de Hibernate a EclipseLink, o se agrega caché, o se cambia el manejo transaccional), el código de negocio no se ve afectado, solo cambia la configuración del framework.
- **Onboarding más rápido:** alguien que entra al proyecto entiende qué hace cada repositorio leyendo solamente las firmas y las anotaciones. No necesita saber primero cómo se obtiene una `Session` o por qué hay una `AbstractRepository`.

En resumen, eliminar boilerplate **no es una cuestión estética**, sino de mantenibilidad, ya que reduce el costo de leer, modificar y verificar el código a lo largo del ciclo de vida del proyecto.




