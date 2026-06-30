# Mapeo de entidades

## Mapeo de una entidad simple: Service

### Ejercicio 12: ​¿Cuál es el conjunto mínimo de anotaciones que debe tener una clase para ser persistente con JPA?

El conjunto mínimo de anotaciones que debe tener una clase para ser persistente con JPA es:
- `@Entity`: Se coloca a nivel de la declaración de la clase para indicarle al framework que dicha clase es una entidad (POJO persistente) y que debe ser mapeada a la base de datos
- `@Id`: Se coloca sobre el atributo que servirá como identificador único o clave primaria, cumpliendo con la regla obligatoria de los POJOs persistentes de proveer un identificador

>[!NOTE]
> No es obligatorio agregar anotaciones adicionales para los demás atributos de la clase. Gracias al principio de "Convención sobre Configuración", JPA asume por defecto que todos los atributos declarados en la clase deben persistirse en la base de datos, a menos que se indique explícitamente lo contrario (por ejemplo, utilizando la anotación `@Transient` para que un campo sea ignorado)

### Ejercicio 13: ¿Qué significa que JPA use persistencia por alcance (persistence by reachability)? ¿Qué consecuencia tiene si un objeto referenciado no está todavía persistido?

La persistencia por alcance (o persistencia transitiva) significa que **todo objeto al cual se pueda llegar** navegando **a partir de un objeto que ya es persistente**, **debe ser necesariamente persistente a su vez**. Esto permite que, para almacenar un objeto en la base de datos, el desarrollador solamente necesite vincularlo orgánicamente (por ejemplo, agregándolo a una colección o asignándolo a un atributo) con algún otro objeto que ya exista en el repositorio, reduciendo de esta forma las operaciones explícitas de guardado y respetando el principio de independencia
- La consecuencia de que un objeto referenciado no esté todavía persistido depende de la configuración de cascada:
  - **Si la persistencia por alcance está activa** (por ejemplo, configurada con `CascadeType.PERSIST` o `ALL`): **Al momento de realizar el commit** de la transacción, el **framework recorrerá el grafo** de objetos modificados y, **al encontrar este nuevo objeto volátil referenciado, lo insertará y persistirá automáticamente en la base de datos** sin requerir ninguna acción adicional por parte del desarrollador
  - **Si la persistencia por alcance NO está activa** (el comportamiento por defecto de JPA): **La operación de guardado no se propagará** hacia la entidad asociada. Como consecuencia, el **ORM intentará guardar en la base de datos una relación hacia un registro que físicamente aún no existe, lo cual desencadenará una excepción**, típicamente `org.hibernate.TransientObjectException` o `TransientPropertyValueException`, o, si se llega al flush, una falla de integridad referencial a nivel de base de datos.

### Ejercicio 14: ¿Qué diferencia hay entre las estrategias IDENTITY, SEQUENCE y TABLE para la generación de IDs? ¿Cuál tiene mejor rendimiento en inserciones masivas y por qué?

En JPA la anotación `@GeneratedValue` permite definir **cómo se crearán las claves primarias automáticamente**, utilizando tres estrategias principales:

- `IDENTITY`:
  - **Delega la generación del identificador enteramente a la base de datos** utilizando columnas de tipo **"autoincremental"** (como `AUTO_INCREMENT` en MySQL).
  >[!IMPORTANT]
  > En Hibernate no se conoce el ID del objeto hasta que la sentencia `INSERT` se ejecuta realmente en la base de datos.
- `SEQUENCE`:
  - Utiliza un **objeto nativo de la base de datos llamado "Secuencia"** (muy común en Oracle o PostgreSQL).
  >[!IMPORTANT] 
  > En Hibernate se realiza una consulta a la base de datos para pedirle el próximo valor de la secuencia antes de ejecutar el `INSERT`. Esto le permite a Hibernate conocer el ID del objeto y asignárselo en memoria antes de guardar el registro.
- `TABLE`:
  - Es la estrategia más genérica. En lugar de usar características nativas del motor (como columnas autoincrementales o secuencias), **crea una tabla auxiliar en la base de datos dedicada exclusivamente a llevar la cuenta de los identificadores**.
  >[!IMPORTANT]
  > En Hibernate para generar un nuevo ID, Hibernate debe hacer un `SELECT` en esta tabla auxiliar, bloquear la fila (lock), hacer un `UPDATE` para incrementar el valor, y liberar la fila.

>[!NOTE]
> También existe otro tipo que se llama `AUTO`, que consiste en que el proveedor elige la estrategia según el dialecto de la base (suele resolver a `SEQUENCE` o a una tabla). Es el valor por defecto.

En cuanto al **rendimiento en inserciones masivas**, la estrategia más eficiente es `SEQUENCE`. La razón es que **Hibernate necesita conocer el ID de la entidad antes de insertarla para poder asignárselo en memoria**. Con `SEQUENCE`, Hibernate **puede pedir varios IDs de antemano** (con `allocationSize` obtiene bloques completos en una sola consulta), lo que le permite agrupar múltiples `INSERT` en un **batch JDBC** y reducir los round-trips a la base (1 para "reservar" los N IDs y uno para ejecutar el bloque de N INSERTs). En cambio, con `IDENTITY` el **ID sólo se conoce después de ejecutar el** `INSERT`, por lo que **Hibernate se ve obligado a ejecutar cada sentencia individualmente** (N viajes a la base). La estrategia `TABLE` es la peor de las tres, porque cada generación implica un `SELECT ... FOR UPDATE` + `UPDATE` con bloqueo de fila sobre la tabla auxiliar, lo que agrega contención y sobrecarga.

### Ejercicio 15: Implementar el mapeo completo de la entidad Service según el diagrama. La implementación debe incluir:

#### a) Clave primaria con estrategia de generación automática. Elegir entre IDENTITY, SEQUENCE o TABLE y justificar la elección.

- Agregamos la anotación `@Entity` a la clase para marcarla como una entidad persistente
- Luego, definimos el atributo `id` como clave primaria utilizando la anotación `@Id`
- Configuramos la estrategia de generación automática con `IDENTITY`, `@GeneratedValue(strategy = GenerationType.IDENTITY)`
  - La elección de `IDENTITY` se justifica porque estamos usando MySQL, motor que soporta nativamente columnas autoincrementales (`AUTO_INCREMENT`). Esto evita tener que crear y mantener objetos adicionales en el esquema (un objeto secuencia en el caso de `SEQUENCE`, que además MySQL no soporta de forma nativa, o una tabla auxiliar en el caso de `TABLE`) y mantiene la generación de IDs simple y transparente para el motor. Si bien para inserciones masivas `SEQUENCE` suele rendir mejor, el TP no contempla un escenario de carga masiva y las operaciones típicas son inserciones unitarias, donde el costo de `IDENTITY` es despreciable.

#### b) Atributos: name (no nulo, max. 100 caracteres), description (opcional), price (no nulo).

- Sobre el atributo `name` agregamos las anotaciones `@Column(nullable = false, length = 100)`
- Sobre el atributo `description` agregamos la anotación `@Column(nullable = true)` (por defecto los campos son nulleables, pero queda mejor expresado si se escribe)
- Sobre el atributo `price` agregamos la anotación `@Column(nullable = false)`

#### c) Al menos una restricción de unicidad a nivel de columna.

La opción natural sería agregar `@Column(unique = true)` sobre el atributo `name`, garantizando que no existan dos servicios con el mismo nombre.

> [!IMPORTANT]
> No se puede aplicar esta restricción en el trabajo, ya que los datos provistos por `DBInitializer.prepareDB()` (viene en el repo de cátedra) crean dos servicios llamados `"souvenir t-shirt"`, lo cual viola la restricción. Por ese motivo, en `Service` queda únicamente `nullable = false` sobre `name` y `price`, sin restricciones de unicidad a nivel de columna.

## Relaciones entre entidades

### Ejercicio 16: Para la relación Purchase -> ItemService (composición uno-a-muchos):

#### a)​ ¿Qué anotaciones se necesitan en cada lado?

- En el lado de `Purchase` (lado "uno"):  
  - `@OneToMany` sobre el atributo que representa la colección de `ItemService`.
  - `mappedBy` para indicar que esta es la parte inversa de la relación y que el propietario es `ItemService`. 
  ```java
    @OneToMany(mappedBy = "purchase")
    private List<ItemService> itemServiceList = new ArrayList<>();
  ```
- En el lado de `ItemService` (lado "muchos"):
  - `@ManyToOne` sobre el atributo que representa la referencia a `Purchase`. 
  - Este lado es el propietario de la relación, por lo que **no se utiliza** `mappedBy`.
  - `@JoinColumn` para especificar el nombre de la columna que actuará como clave foránea en la base de datos. En este caso, utilizaremos `@JoinColumn(name = "purchase_id")` para indicar que la columna `purchase_id` en la tabla de `ItemService` será la clave foránea que referencia a `Purchase`.
  ```java
    @ManyToOne()
    @JoinColumn(name = "purchase_id", nullable = false)
    private Purchase purchase;
  ```

#### b)​ ¿Qué columna o tabla aparece en la base de datos para representar esta relación?

- Aparece una columna llamada `purchase_id` en la tabla correspondiente a `ItemService`, que actúa como clave foránea y referencia a la tabla de `Purchase`. Esta columna se utiliza para establecer la relación entre cada registro de `ItemService` y su correspondiente registro de `Purchase`.

>[!NOTE]
> Esta columna se genera automáticamente por JPA debido a la anotación `@JoinColumn` en el lado de `ItemService`

#### c)​ ¿Qué es mappedBy y en qué lado de la relación va? ¿Qué ocurre si se omite en ambos lados?

- `mappedBy` es un atributo de la anotación `@OneToMany` que se utiliza para **indicar que esta parte de la relación es la inversa y que el propietario de la relación es el otro lado** (en este caso, `ItemService`). Especifica el **nombre del atributo en la clase del lado "muchos" que mantiene la referencia a la clase del lado "uno"**. En este caso, `mappedBy = "purchase"` indica que el atributo `purchase` en `ItemService` es el propietario de la relación.
- **Si se omite** `mappedBy` **en ambos lados**, **JPA no podrá determinar cuál es el propietario de la relación**, lo que **resultará en la creación de una tabla intermedia adicional para gestionar la relación** entre `Purchase` e `ItemService`, **en lugar de utilizar una clave foránea directa** en la tabla de `ItemService`. Esto puede llevar a una **estructura de base de datos más compleja e ineficiente**, ya que se requerirán operaciones adicionales para gestionar la relación entre las entidades.

#### d)​ ¿Es esta relación bidireccional o unidireccional según el diagrama? ¿Cómo se refleja en el código Java?

- Según el diagrama, esta relación es **bidireccional**, ya que tanto `Purchase` como `ItemService` **mantienen referencias mutuas entre sí**. En el código Java, esto se refleja mediante la **presencia de un atributo en** `Purchase` **que es una colección de** `ItemService` y un **atributo en** `ItemService` **que es una referencia a** `Purchase`. Esta configuración permite navegar desde una instancia de `Purchase` hacia sus `ItemService` asociados, así como desde una instancia de `ItemService` hacia su correspondiente `Purchase`.

### Ejercicio 17: ​Para las relaciones Route <-> DriverUser y Route <-> TourGuideUser (muchos-a-muchos):

#### a)​ ¿Qué anotaciones se usan?

- Las anotaciones que se utilizan son:
  - Del lado de `Route`:
    - `@ManyToMany` sobre los atributos que representan las colecciones de `DriverUser` y `TourGuideUser`.
    - `@JoinTable` para definir explícitamente la tabla intermedia que gestionará la relación muchos-a-muchos, especificando los nombres de las columnas de clave foránea y declarando que no pueden ser nulos ya que se especifica que la relación es obligatoria. 
    ```java
      @ManyToMany()
      @JoinTable(
              name = "route_driver",
              joinColumns = @JoinColumn(name = "route_id", nullable = false),
              inverseJoinColumns = @JoinColumn(name = "driver_id", nullable = false)
      )
      private List<DriverUser> driverList = new ArrayList<>();

      @ManyToMany()
      @JoinTable(
              name = "route_tour_guide",
              joinColumns = @JoinColumn(name = "route_id", nullable = false),
              inverseJoinColumns = @JoinColumn(name = "tour_guide_id", nullable = false)
      )
      private List<TourGuideUser> tourGuideList = new ArrayList<>();
    ```
  - Del lado de `DriverUser` y `TourGuideUser`:
    - `@ManyToMany` sobre los atributos que representan las colecciones de `Route`. 
    - `mappedBy` para indicar que esta es la parte inversa de la relación y que el propietario es `Route`. 
    - En este lado, no utilizamos `@JoinTable` porque la tabla intermedia ya está definida en el lado de `Route`.
    ```java
      // DriverUser
      @ManyToMany(mappedBy = "driverList")
      private List<Route> routes = new ArrayList<>();

      //TourGuideUser
      @ManyToMany(mappedBy = "tourGuideList")
      private List<Route> routes = new ArrayList<>();
    ```

#### b)​ ¿Qué tabla adicional genera JPA? ¿Qué columnas tiene? Definirla explícitamente usando @JoinTable.

- **JPA genera una tabla adicional para cada relación muchos-a-muchos**. Por convención **por defecto**, JPA las nombraría **combinando los nombres de las entidades** (`route_driver_user` / `route_tour_guide_user`), pero **en el proyecto se personalizan explícitamente mediante** `name` dentro de `@JoinTable`:
  - Para la relación entre `Route` y `DriverUser`, se genera la tabla `route_driver` con las siguientes columnas:
    - `route_id`: Clave foránea que referencia a la tabla de `Route`, con `nullable = false`.
    - `driver_id`: Clave foránea que referencia a la tabla de `DriverUser`, con `nullable = false`.
  - Para la relación entre `Route` y `TourGuideUser`, se genera la tabla `route_tour_guide` con las siguientes columnas:
    - `route_id`: Clave foránea que referencia a la tabla de `Route`, con `nullable = false`.
    - `tour_guide_id`: Clave foránea que referencia a la tabla de `TourGuideUser`, con `nullable = false`.

#### c)​ ¿Pueden ambas relaciones compartir la misma tabla join? ¿Por qué?

- No, ambas relaciones **no pueden compartir la misma tabla join porque cada relación muchos-a-muchos representa una asociación distinta entre diferentes entidades**. Cada tabla join debe ser específica para la relación que está gestionando, ya que **contiene claves foráneas que hacen referencia a las entidades involucradas en esa relación particular**. Compartir la misma tabla join para ambas relaciones podría generar confusión y problemas de integridad referencial, ya que no habría una forma clara de distinguir entre los registros que corresponden a la relación `Route`-`DriverUser` y los que corresponden a la relación `Route`-`TourGuideUser`. Por lo tanto, **es necesario tener tablas join separadas para cada relación muchos-a-muchos**.

### Ejercicio 18: ​La relación Purchase -> Review es opcional (0..1). Implementar el mapeo de ambos lados. ¿Cómo se representa la opcionalidad en JPA?

- En el lado de `Purchase`
  - `@OneToOne` sobre el atributo que representa la review
  - `mappedBy = "purchase"` para indicar que esta es la parte inversa de la relación y el propietario es `Review` ya que una `Purchase` no necesariamente tiene una `Review`, pero si existe una `Review`, si o si, está relacionada con una `Purchase`
  >[!NOTE]
  > En el caso de 1:1, el mappedBy puede ir de cualquiera de los dos lados, en este caso lo ponemos del lado de `Purchase` porque es 1:0
  - `optional = true` para representar el `0..1`
  
  >[!NOTE]
  > La opcionalidad en JPA se representa utilizando el atributo `optional = true` en la anotación de relación (`@OneToOne`, `@ManyToOne`, etc.) en el lado que es opcional.
  ```java
    @OneToOne(mappedBy = "purchase", optional = true)
    private Review review;
  ```
- En el lado de `Review`
  - `@OneToOne` sobre el atributo que representa la review
  - `@JoinColumn(name = "purchase_id", nullable = false, unique = true)` para establecer la clave foránea que referencia a `Purchase`.
  >[!NOTE]
  > Para que la relación sea realmente 1–1 (y no 1–*) a nivel de base de datos, la columna `purchase_id` en `Review` debe tener una restricción `UNIQUE`. JPA la agrega de forma **implícita** cuando se combina `@OneToOne` + `@JoinColumn`, por lo que no es obligatorio declararla de forma explícita. Si se quiere dejarla visible en el código, puede escribirse `@JoinColumn(name = "purchase_id", nullable = false, unique = true)`.
  ```java
    @OneToOne()
    @JoinColumn(name = "purchase_id", nullable = false, unique = true)
    private Purchase purchase;
  ```


### Ejercicio 19: ItemService referencia a Service (muchos-a-uno). Analizar el diagrama: ¿es navegable esta relación desde Service hacia ItemService? Justificar si conviene hacerla bidireccional o no.

- Es navegable, ya que `Service` tiene una colección de `ItemService`, por lo cual, se puede navegar desde una instancia de `Service` hacia sus `ItemService` asociados.
- Es conveniente hacerla bidireccional ya que nos permitirá consultar desde un servicio sus ítems, lo cual es útil para reportes, métricas, auditoría, etc. 
- Se debe tener en cuenta que al ser bidireccional, se debe **gestionar adecuadamente la sincronización de ambas partes de la relación para evitar inconsistencias** en el modelo de datos, lo cual agrega cierta complejidad al código.

>[!NOTE]
> Los tests provistos con el proyecto base asumen esta bidireccionalidad. Por ejemplo, en `ToursApplicationTests.removePurchaseAndItems` se valida `assertEquals(1, service1.getItemServiceList().size())`, es decir, se accede explícitamente a los `ItemService` desde el `Service`. Esto convierte la decisión en un requerimiento concreto del dominio dentro del TP.

### Ejercicio 20.​Implementar el mapeo completo de las siguientes entidades con todas sus relaciones, siguiendo las anotaciones y decisiones discutidas: Supplier, Purchase, ItemService, Route, Stop y Review. Para cada relación bidireccional, incluir las anotaciones en ambos lados.

#### Supplier

```java
  @OneToMany(mappedBy = "supplier")
  private List<Service> services = new java.util.ArrayList<>();
```

#### Service

- Relación con `Supplier`
  ```java
    @ManyToOne()
    @JoinColumn(name = "supplier_id", nullable = false)
    private Supplier supplier;
  ```
- Relación con `ItemService`
  ```java
    @OneToMany(mappedBy = "service")
    private List<ItemService> itemServiceList = new java.util.ArrayList<>();
  ```

#### Purchase

- Relación con `Usuario`
  ```java
    @ManyToOne()
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
  ```
- Relación con `Route`
  ```java
    @ManyToOne()
    @JoinColumn(name = "route_id", nullable = false)
    private Route route;
  ```
- Relación con `Review`
  ```java
    @OneToOne(mappedBy = "purchase", optional = true)
    private Review review;
  ```
- Relación con `ItemService`
  ```java
    @OneToMany(mappedBy = "purchase")
    private List<ItemService> itemServiceList = new ArrayList<>();
  ```

>[!NOTE]
> `@Temporal(TemporalType.DATE)` sobre el atributo `date` para persistir sólo la fecha (sin hora).

#### ItemService

- Relación con `Purchase`: 
  ```java
    @ManyToOne()
    @JoinColumn(name = "purchase_id", nullable = false)
    private Purchase purchase;
  ```
- Relación con `Service`: 
  ```java
    @ManyToOne()
    @JoinColumn(name = "service_id", nullable = false)
    private Service service;
  ```

>[!NOTE]
> `price: float` con `@Column(nullable = false)` **agregado en la implementación**. Si el `Service.price` cambia después, los `ItemService` históricos preservan el precio que efectivamente se cobró. Es información económica/contable que no puede recalcularse desde el catálogo actual.

#### Route

- Relación con `Stop`
  ```java
    @ManyToMany()
    @JoinTable(
            name = "route_stop",
            joinColumns = @JoinColumn(name = "route_id", nullable = false),
            inverseJoinColumns = @JoinColumn(name = "stop_id", nullable = false)
    )
    private List<Stop> stops = new ArrayList<>();
  ```
- Relación con `DriverUser`
  ```java    
    @ManyToMany()
    @JoinTable(
            name = "route_driver",
            joinColumns = @JoinColumn(name = "route_id", nullable = false),
            inverseJoinColumns = @JoinColumn(name = "driver_id", nullable = false)
    )
    private List<DriverUser> driverList = new ArrayList<>();
  ```
- Relación con `TourGuideUser`
  ```java
    @ManyToMany()
    @JoinTable(
            name = "route_tour_guide",
            joinColumns = @JoinColumn(name = "route_id", nullable = false),
            inverseJoinColumns = @JoinColumn(name = "tour_guide_id", nullable = false)
    )
    private List<TourGuideUser> tourGuideList = new ArrayList<>();
  ```

#### Stop

- Entidad simple, sin referencias salientes. El lado dueño de la relación con `Route` es `Route` (a través del `@JoinTable` `route_stop`), por lo que `Stop` no necesita anotaciones de relación.

#### Review

- Relación con `Purchase`
  ```java
    @OneToOne()
    @JoinColumn(name = "purchase_id", nullable = false, unique = true)
    private Purchase purchase;
  ```

## Fetch Type: LAZY vs. EAGER

### Ejercicio 21: ¿Para qué sirve la propiedad `fetch` en las anotaciones de relación? ¿Cuáles son los valores posibles? ¿Cuál es el valor por defecto para `@OneToMany`, para `@ManyToOne` y para `@ManyToMany`?

- La propiedad `fetch` define la **estrategia de carga de los objetos asociados en una relación**. Su configuración impacta directamente en la performance (cantidad de queries y volumen de datos transferidos) y en el consumo de memoria.
  
- Los valores posibles son dos, definidos por el enum `FetchType`:
  - `FetchType.EAGER`: La entidad asociada se carga **inmediatamente** junto con la entidad principal, típicamente mediante un `JOIN` o una consulta adicional automática.
  - `FetchType.LAZY`: La entidad asociada **no** se carga al traer la entidad principal. En su lugar, Hibernate coloca un proxy (o una colección "wrappeada") y sólo ejecuta la consulta cuando el código accede al atributo por primera vez.

- Los valores por defecto dependen del tipo de relación y están pensados según la cardinalidad del "otro lado":
  - `@OneToMany`: `LAZY` (la colección puede tener muchos elementos → traerlos siempre es costoso).
  - `@ManyToMany`: `LAZY` (mismo razonamiento).
  - `@ManyToOne`: `EAGER` (se asume que cargar un único objeto asociado es barato).
  - `@OneToOne`: `EAGER` (mismo razonamiento que `@ManyToOne`).

> [!NOTE]
> La regla general es: **las relaciones "a-muchos" son LAZY por defecto, las "a-uno" son EAGER por defecto**..

### Ejercicio 22: Describir ventajas y desventajas concretas de EAGER y LAZY, en términos de performance de acceso como de espacio en memoria. ¿Por qué configurar EAGER en todas las relaciones suele ser una mala idea en aplicaciones reales?

- **EAGER**:
  - **Ventajas**:
    - Al cargarse la entidad principal junto con las entidades relacionadas, ya las tenemos disponibles en memoria, evitando consultas para recuperarlas después.
    - Como todos se cargan en memoria, al cerrar un contexto de persistencia, se siguen podiendo leer.
  - **Desventajas**:
    - **Sobrecarga de memoria**: se cargan datos que quizá nunca se usen. Si una `Purchase` trae siempre su `User`, `Route`, `itemServiceList`, y cada ítem su `Service`, y cada `Service` su `Supplier`, una sola query termina arrastrando un grafo enorme.
    - **Consultas pesadas**: Hibernate debe realizar `JOIN`s adicionales o ejecutar queries extra (problema de *N+1 queries* si la relación EAGER es una colección y no se optimiza con fetch join).

- **LAZY**:
  - **Ventajas**:
    - **Menor consumo de memoria inicial**: sólo se carga lo que se pide.
    - **Mejor performance en consultas básicas**: la query de la entidad principal es más chica y más rápida.
    - **Flexibilidad**: cada caso de uso puede decidir qué traer explícitamente.
  - **Desventajas**:
    - Cada acceso a una asociación no cargada genera una **consulta adicional**, lo que puede derivar en el problema de **N+1 queries** si no se planifica bien.
    - Si se accede a la relación **fuera del contexto de persistencia** (con la `Session` cerrada), se produce `LazyInitializationException`.
  
- **¿Por qué configurar EAGER en todas las relaciones es mala idea?**
  - En un modelo con relaciones transitivas como el de tours (`Purchase` → `User`, `Route`, `itemServiceList` → `Service` → `Supplier`, etc.), marcar todo como `EAGER` provoca que **cada consulta a una entidad termine arrastrando gran parte del grafo de dominio**, incluso cuando el caso de uso sólo necesita un par de campos.
  - Esto degrada gravemente la performance (queries largas con múltiples `JOIN`s o cascadas de **N+1**), agota la memoria de la JVM en listados grandes y hace imposible optimizar caso por caso.

### Ejercicio 23: Para cada relación del modelo, elegir el FetchType más adecuado y justificar. Luego implementar su decisión en el proyecto tours.

| Relación | Tipo de anotación | FetchType elegido | Justificación |
| --- | --- | --- | --- |
| `Purchase` → `User` | `@ManyToOne` | `LAZY` | No todos los casos de uso sobre `Purchase` necesitan el `User` (listar compras por fecha, calcular totales, etc.)|
| `Purchase` → `Route` | `@ManyToOne` | `LAZY` | Mismo criterio, hay consultas sobre `Purchase` que no requieren la `Route` completa (con sus stops, drivers y tour guides).|
| `Purchase` → `itemServiceList` | `@OneToMany` | `LAZY` | Una compra puede tener múltiples ítems, no tiene sentido cargar todos los items de una compra si por jemplo, solo queremos consultar  datos relacionados a la `Purchase`|
| `Purchase` → `Review` | `@OneToOne` | `LAZY` | La review es opcional y no siempre se consulta junto con la `Purchase`.|
| `ItemService` → `Service` | `@ManyToOne` | `EAGER` | Para procesar un item de servicio es necesario conocer qué servicio es (nombre, precio), de esta forma se facilita el acceso directo a esos datos|
| `Route` → `stops` | `@OneToMany` | `LAZY` | Las paradas pueden ser muchas. En la mayoría de los listados de rutas basta con nombre, precio y km totales. |
| `Route` → `drivers` (`DriverUser`) | `@ManyToMany` | `LAZY` | Lista potencialmente larga y ademas al ser muchos a muchos implica una tabla intermedia, por lo que el costo de procesamiento es alto. Solo cargaremos los `drivers` si se quiere administrar el personal |
| `Route` → `tourGuides` (`TourGuideUser`) | `@ManyToMany` | `LAZY` | Mismo criterio que con `drivers`. |
| `User` → `purchases` | `@OneToMany` | `LAZY` | Un usuario puede tener muchísimas compras, y las traeríamos a todas en cada carga de un `User` cuando hay varios casos en los que queremos realizar consultas sobre el usuario en particular y no en relación a sus compras. |
| `Service` → `supplier` | `@ManyToOne` | `LAZY` | No todos los casos de uso sobre `Service` (listar servicios, buscar por nombre, actualizar precio) necesitan conocer el `Supplier`. |

### Ejercicio 24: ¿Cómo podría producirse una `LazyInitializationException` en el modelo? Investigue de qué representa esta excepción y escribir un escenario concreto explicando al menos formas de resolverlo sin cambiar el FetchType a EAGER.

- La `org.hibernate.LazyInitializationException` es la excepción que se lanza cuando se intenta **acceder a una asociación marcada como `LAZY` una vez que el contexto de persistencia (la `Session`) que cargó la entidad ya está cerrado o desvinculado**. Como la colección o el proxy está "vacío" y necesita una `Session` abierta para ir a buscar los datos a la base, Hibernate no puede cumplir el acceso y falla con esta excepción.

- **Escenario concreto en el modelo tours**:
  - En la capa de servicio se abre una transacción, se llama al `PurchaseRepository` y se obtiene una `Purchase` por ID. La transacción finaliza y con ella se cierra la `Session`.
  - Posteriormente, en la capa de presentación, se ejecuta `purchase.getItemServiceList().size()` o `purchase.getRoute().getName()`.
  - Como `itemServiceList` y `route` están marcadas como `LAZY` y la `Session` que cargó la `Purchase` ya está cerrada, Hibernate lanza `LazyInitializationException` al intentar resolver el proxy.

- **Formas de resolverlo sin cambiar el FetchType a `EAGER`**:
  1. **`JOIN FETCH` en la consulta HQL/JPQL**: en lugar de hacer un `findAll()` genérico, creamos una consulta JPQL que fuerce la carga de la entidad asociada en la misma consulta. Por ejemplo:
     ```java
      // Tree la Purchase con si lista de items
      public Purchase getPurchaseWithItems(Long id) {
          Session session = sessionFactory.getCurrentSession();
          return session.createQuery(
                  "SELECT p FROM Purchase p " +
                  "JOIN FETCH p.itemServiceList " +
                  "WHERE p.id = :id", Purchase.class)
              .setParameter("id", id)
              .uniqueResult();
      }
     ```
  2. **Inicializar explícitamente con `Hibernate.initialize(...)`**: dentro de la transacción, forzar la carga de la colección o del proxy antes de devolverlo (`Hibernate.initialize(purchase.getItemServiceList())`).
  3. **Mapear un DTO en la consulta**: en lugar de devolver la entidad al resto de la aplicación, proyectar directamente a un objeto plano (`new PurchaseDTO(p.id, p.code, ...)`) que contenga sólo los campos que se van a usar. Así nunca se accede a relaciones LAZY fuera del contexto de persistencia.

> [!NOTE]
> Cambiar el `FetchType` a `EAGER` "resuelve" el síntoma pero introduce problemas de sobrecarga de memoria, queries innecesarias, acoplamiento del mapeo a un caso de uso.

## Operaciones en cascada

### Ejercicio 25: ​Enumerar todos los valores de CascadeType y explicar qué operación propaga cada uno sobre las entidades relacionadas.

- `CascadeType.PERSIST`:
  - Propaga la operación `EntityManager.persist()` o `Session.persist()`.
  - Al **persistir la entidad principal**, **todas las entidades asociadas** que estén en **estado transitorio** se **insertan automáticamente en la base de datos**.
- `CascadeType.MERGE`:
  - Propaga la operación `EntityManager.merge()` o `Session.update()`.
  - Al hacer **merge de una entidad detached** (devolviéndola al contexto de persistencia), también **se mergean las entidades asociadas**.
- `CascadeType.REMOVE`:
  - Propaga la operación `EntityManager.remove()` o `Session.delete()`.
  - Al **eliminar la entidad principal**, las **entidades asociadas se eliminan también**. Fundamental para mantener la **integridad referencial**.
  >[!NOTE]
  > tiene sentido en relaciones de **composición** (relación de "parte-todo", como `Purchase` → `ItemService`), donde la existencia de la parte depende del todo.
- `CascadeType.REFRESH`:
  - Propaga la operación `EntityManager.refresh()`.
  - Al **refrescar la entidad principal** (en memoria) con su estado actual de la base, las **entidades asociadas también** se vuelven a leer y se descartan los cambios pendientes en memoria sobre ellas.
- `CascadeType.DETACH`:
  - Propaga la operación `EntityManager.detach()`.
  - Al **desvincular la entidad principal del contexto de persistencia** (pasándola a estado *detached*), las **entidades asociadas también se desvinculan**.
- `CascadeType.ALL`:
  - Equivale a declarar todas las anteriores simultáneamente.
  >[!NOTE]
  > Es el más común en relaciones de composición fuerte, donde el ciclo de vida del hijo está totalmente atado al del padre

> [!NOTE]
> Hibernate define adicionalmente sus propios valores en `org.hibernate.annotations.CascadeType` para cubrir operaciones que no son parte del estándar JPA: `SAVE_UPDATE` (propaga `Session.saveOrUpdate()`), `LOCK` (propaga `Session.lock()`) y `REPLICATE` (propaga `Session.replicate()`). Sólo se utilizan cuando se trabaja con la API nativa de Hibernate vía `@Cascade(...)`. Con anotaciones JPA puras no aparecen.

### Ejercicio 26:  ​¿Cuál es el comportamiento por defecto cuando no se define cascade? ¿Cuál es la finalidad general de CASCADE? Proponga un caso del modelo donde definir un CASCADE inadecuado podría traer problemas a la consistencia de la base de datos.

- **Comportamiento por defecto**:
  - Cuando no se define el atributo `cascade` en una anotación de relación, JPA asume `cascade = {}`,**ninguna operación se propaga** desde la entidad principal hacia las asociadas.

- **Finalidad general de CASCADE**:
  - La finalidad es la **automatización del ciclo de vida del grafo de objetos**, permitiendo que las operaciones de persistencia se propaguen de forma transitiva a través de las asociaciones. Esto garantiza **integridad referencial** sin que el programador tenga que realizar las operaciones manualmente.
  - Es la **herramienta concreta con la que se implementa la persistencia por alcance** y se **modelan relaciones de composición** (donde el ciclo de vida de la parte está atado al del todo).

- **Caso de CASCADE inadecuado en el modelo tours**:
  - **Escenario**: declarar `cascade = CascadeType.ALL` o `cascade = CascadeType.REMOVE` en la relación `Route` → `drivers` (`@ManyToMany`).
  - **Problema**: los `DriverUser` son entidades **independientes** del ciclo de vida de una `Route`, ya que un mismo chofer puede participar en muchas rutas distintas. Si se elimina una `Route` con `CascadeType.REMOVE` activo sobre `drivers`, JPA intentará eliminar también a los choferes asociados.
  - **Consecuencia para la consistencia**:
    - Se borran usuarios `DriverUser` que **siguen siendo válidos en otras rutas**, dejando el sistema con choferes "fantasma" referenciados desde la tabla join `route_driver` de esas otras rutas → falla de integridad referencial o, si las FKs están con `ON DELETE CASCADE`, una **baja en cascada masiva e involuntaria** que limpia las asociaciones de rutas que no tenían nada que ver con la operación original.

### Ejercicio 27: ​¿Cuál es la diferencia entre cascade = REMOVE y orphanRemoval = true? ¿Pueden usarse conjuntamente? Ejemplificar con el par Purchase -> ItemService.

- **Diferencia conceptual**:
  - `cascade = CascadeType.REMOVE` propaga la operación `remove()` desde la **entidad principal hacia las asociadas**. En cambio, `orphanRemoval = true` (propiedad disponible en `@OneToMany` y `@OneToOne`) actúa **a nivel de la colección/asociación**, no de la entidad padre. Cuando un hijo es **desvinculado**, Hibernate detecta que ese hijo se "quedó sin padre" y emite un `DELETE` sobre él en el siguiente flush. También se dispara, transitivamente, cuando se elimina el padre, si los hijos pierden su referencia, igual se borran.
  
  >[!NOTE]
  > `REMOVE` reacciona a "padre eliminado", `orphanRemoval` reacciona a "hijo desvinculado" (incluido el caso particular en que la desvinculación viene del padre eliminado).

- **¿Pueden usarse conjuntamente?**
  - Sí, son **complementarios**, no redundantes:
  - `CascadeType.REMOVE` cubre el caso "se elimina el padre" → propaga el `DELETE` a los hijos.
  - `orphanRemoval = true` cubre el caso "el padre sigue vivo pero un hijo se sacó de la colección" → elimina ese hijo huérfano.
  - En una composición, usarlos juntos es la única forma de asegurar que un `ItemService` nunca exista sin su `Purchase`  

- **Ejemplo con `Purchase` → `ItemService`**:

  ```java
  @OneToMany(
      mappedBy = "purchase",
      fetch = FetchType.LAZY,
      cascade = {CascadeType.REMOVE, CascadeType.PERSIST},
      orphanRemoval = true
  )
  private List<ItemService> itemServiceList = new ArrayList<>();
  ```

  - **Caso 1 — eliminar la compra entera**: al eliminar una `Purchase`, `CascadeType.REMOVE` propaga la baja y los `ItemService` asociados se eliminan automáticamente. Sin esta cascada, la operación fallaría porque la FK `purchase_id` en `item_service` quedaría apuntando a una `Purchase` inexistente.
  - **Caso 2 — quitar un ítem de la compra**: al eliminar un item de la compra (`purchase.getItemServiceList().remove(item)`), `CascadeType.REMOVE` **no se dispara**, es `orphanRemoval = true` el que detecta que `item` quedó sin padre lógico y emite el `DELETE`. Sin esta opción, el ítem seguiría existiendo en la base como registro huérfano.

> [!NOTE]
> La diferencia más sutil entre ambos: `CascadeType.REMOVE` se dispara una sola vez por borrado del padre. `orphanRemoval` está activo en cada flush de la transacción y observa los cambios sobre la colección de manera continua. 

### Ejercicio 28: ​Para la relación Purchase -> ItemService (composición):

#### a)​ ¿Qué tipos de cascade configurarías? Justificar cada uno.

Para esta relación, configuraría `cascade = {CascadeType.PERSIST, CascadeType.MERGE, CascadeType.REMOVE}`:

- `CascadeType.PERSIST`: la composición implica que un `ItemService` no tiene sentido fuera de la `Purchase` que lo contiene. `PERSIST` permite que al guardar una nueva `Purchase`, todos sus `ItemService` se guarden automáticamente.
- `CascadeType.REMOVE`: como los ítems no tienen sentido sin la compra, eliminar la `Purchase` debe arrastrar la baja de todos sus `ItemService`. Sin esta cascada, el `DELETE` sobre `purchase` fallaría por integridad referencial (la FK `purchase_id` en `item_service` apuntaría a un padre inexistente) o, peor, dejaría registros huérfanos si la FK lo permitiera.
- `CascadeType.MERGE`: es esencial para actualizaciones. Si se edita una compra (cambiar la cantidad de un item, agregar o eliminar uno, etc.) y se llama a `update`, los cambios se propagan a los hijos.
- **¿Por qué no `DETACH` o `REFRESH`?**:
  - `DETACH`/`REFRESH` no aportan valor concreto en este modelo, el TP no transfiere grafos detached de un lado a otro de la red, ni necesita refrescar/desvincular agregados completos como unidad.

#### b)​ ¿Usarías orphanRemoval? ¿Por qué?

Sí, configuraría `orphanRemoval = true`.

- Un `ItemService` por si solo no tiene sentido dentro del dominio. No es un objeto que viva por su cuenta y pueda reasignarse a otra compra. Por ende, si un `ItemService` se desvincula de su compra, debe ser eliminado.

#### c)​ Describir qué ocurre a nivel de base de datos cuando se elimina un ItemService de la lista de una Purchase y Hibernate realiza el flush.

1. **Detección de la modificación en el `PersistenceContext`**: Hibernate, al hacer flush, compara el estado actual de la entidad gestionada `Purchase` contra el snapshot que tenía cargado. Detecta que la colección `itemServiceList` perdió una referencia a un hijo.
2. **Identificación del huérfano por `orphanRemoval`**: como la relación tiene `orphanRemoval = true`, ese `ItemService` desvinculado se marca para eliminación.
3. **Emisión del SQL `DELETE`**: Hibernate ejecuta una sentencia `DELETE FROM item_service WHERE id = ?` sobre la fila correspondiente al ítem eliminado.
4. **Commit**: al cerrar la transacción, los cambios se hacen permanentes. 
  >[!NOTE]
  > Si por algún motivo el `DELETE` falla (por ejemplo, una restricción adicional o un trigger), Hibernate hace rollback de toda la unidad de trabajo y la lista vuelve a su estado original en memoria al recargar.

### Ejercicio 29: ​Para la relación Purchase -> Review:

#### a)​ ¿Qué cascades configurarías?

- `CascadeType.REMOVE`: la `Review` no es una entidad independiente en el dominio, sólo existe en función de una `Purchase`. Eliminar la compra debe arrastrar la baja del review asociado.
- `CascadeType.MERGE`:  Si el usuario edita algún dato de la compra (como el estado) y al mismo tiempo la reseña ya existe, queremos que cualquier cambio en el grafo de objetos se sincronice.

#### b)​ Si se elimina una Purchase, ¿debería eliminarse también su Review? Justificar desde el modelo de negocio.

- Si, ya que el `Review` **no tiene existencia propia fuera de la compra que lo originó**. Representa la opinión del usuario sobre **esa** experiencia concreta. Si la compra desaparece, no queda nada a lo que la opinión refiera.
- Desde la perspectiva del negocio descripto, los reviews se utilizan para promociones del emprendimiento y para captar más público. Mantener reviews huérfanos (sin compra trazable) los vuelve inutilizables para esos fines, ya que no se puede vincular la opinión al recorrido, al usuario ni a la fecha de la experiencia.

### Ejercicio 30: ​Para la relación Supplier -> Service:

#### a)​ ¿Qué cascades tienen sentido?

- Justificaciones:
  - `CascadeType.PERSIST`: Dar de alta un `Supplier` con su catálogo inicial de `Service` en una sola operación. Si el flujo de la aplicación crea ambos en el mismo momento, agregarlo evita persistir cada `Service` manualmente.
  - `CascadeTyzpe.MERGE`: Si el proveedor actualiza sus servicios, el cambio se propaga correctamente a cada `Supplier`

#### b)​ Si se elimina un Supplier, ¿qué debería ocurrir con sus Service? ¿Y con las Purchase que los contienen a través de ItemService?

- **Qué debería ocurrir con sus `Service`**:
  - **No deberían eliminarse en cascada**. Un `Service` ya vendido (es decir, referenciado por algún `ItemService`) representa una transacción histórica que la aplicación necesita preservar para trazabilidad, contabilidad y soporte al cliente.
- **Qué debería ocurrir con las `Purchase` que los contienen a través de `ItemService`**:
  - **Nada**, que el proveedor del servicio adquirido se haya eliminado **no afecta la validez de la compra**.

### Ejercicio 31: ​¿Por que CascadeType.REMOVE en una relación @ManyToMany (por ejemplo Route <-> DriverUser) suele ser peligroso? Describir un escenario donde su uso cause pérdida no deseada de datos.

Una relación `@ManyToMany` modela una **asociación entre entidades**, no una composición. **Cada extremo existe independientemente del otro**, una `Route` puede operar con distintos choferes a lo largo del tiempo, y un `DriverUser` puede participar en varias rutas distintas. `CascadeType.REMOVE` propaga el `DELETE` **asumiendo que el objeto hijo es propiedad exclusiva del padre**, su uso provoca la eliminación en cascada de entidades compartidas, rompiendo la integridad de otras relaciones del sistema. Incluso, sii la cascada se declara **en ambos lados** (`Route` con `cascade = REMOVE` sobre `drivers` y `DriverUser` con `cascade = REMOVE` sobre `routes`), una sola baja puede dispararse recursivamente y arrastrar prácticamente toda la red de rutas y choferes conectados transitivamente.

- **Escenario concreto en el modelo tours**:
  - Supongamos que se configura `cascade = CascadeType.REMOVE` en `Route.drivers` (`@ManyToMany` con `DriverUser`).
  - El sistema tiene tres rutas activas:
    - `Route A` ("Tour tradicional de Bs. As.") con choferes `D1`, `D2`, `D3`.
    - `Route B` ("Tour del Delta") con choferes `D2`, `D4`.
    - `Route C` ("Recorrido nocturno") con choferes `D1`, `D5`.
  - Se decide retirar la `Route A` del catálogo y se ejecuta `routeRepository.delete(routeA)`.
  - **Lo que ocurre con `CascadeType.REMOVE` activo**: se propaga el `DELETE` a `D1`, `D2` y `D3`.
    - `D1` desaparece de la tabla `user`/`driver_user`, pero `Route C` sigue teniendo en su tabla join `route_driver` una fila `(C, D1)`. Eso o **rompe la integridad referencial** (si la FK no permite huérfanos) y la transacción aborta dejando estado inconsistente, o **se borra también la fila de `route_driver` de `Route C`** si la FK está con `ON DELETE CASCADE`, despoblando silenciosamente la asignación de choferes de `Route C`.
    - Lo mismo para `D2`.
    - Se pierden, además, los **antecedentes laborales** (`expedient`) de los tres choferes, datos que la descripción del dominio del TP pide explícitamente conservar.
  - El mismo razonamiento se replica simétricamente, si se diera de baja un chofer con `cascade = REMOVE` activo, se borrarían las rutas en las que participa (junto con sus stops, sus tour guides asociados, sus compras y reviews vía `Purchase`), arrastrando un grafo masivo y completamente involuntario.

### Ejercicio 32: ​Implemente las operaciones en cascada adecuada para todas las relaciones del modelo tours

Consolidando las decisiones tomadas en los ejercicios 28–31, la configuración de cascadas para todas las relaciones queda como sigue. La regla general es la enunciada en el ejercicio 26: **CASCADE donde haya composición; cascade vacío donde haya asociación**.

- `Purchase` → `itemServiceList` 

  |`CascadeType` | Justificación |
  | --- | --- |
  | `PERSIST` | permite construir la compra como agregado |
  |`REMOVE` | arrastra los ítems al borrar la compra|
  |`MERGE`| Si el objeto llega en estado detached (ej.desde el frontend), sincroniza los cambios tanto en los datos de la compra, como en su lista de items de forma consistente |

- `Purchase` → `Review` (`@OneToOne`, inverso · composición · `orphanRemoval = true`)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `REMOVE` | una `Review` no tiene sentido sin la compra, al borrarla, debe eliminarse el review |
  | `MERGE`| sincroniza los cambios tanto en los datos de la compra, como en su reseña |

- `ItemService` → `Purchase` (`@ManyToOne`, lado dueño)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}` | la propagación se maneja **desde** `Purchase` (padre), nunca desde el ítem (hijo)  |

- `ItemService` → `Service` (`@ManyToOne`)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}` | el `Service` es independiente y compartido con otros ítems históricos |

- `Service` → `Supplier` (`@ManyToOne`)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}` | el `Supplier` existe independientemente del servicio |

- `Supplier` → `services` (`@OneToMany`, inverso)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}` | los `Service` no son parte del agregado `Supplier` |

- `Service` → `itemServiceList` (`@OneToMany`, inverso)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}` | los `ItemService` pertenecen al agregado `Purchase`, no a `Service` |

- `Purchase` → `User` (`@ManyToOne`)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}` | el `User` es independiente y vive más allá de cualquier compra particular |

- `Purchase` → `Route` (`@ManyToOne`)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}` | la `Route` existe antes y después de cualquier compra |

- `User` → `purchases` (`@OneToMany`, inverso)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}` | las `Purchase` son hechos económicos que sobreviven a la baja del usuario |

- `Route` ↔ `DriverUser` (`@ManyToMany`)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}`| `REMOVE` causaría pérdida masiva de datos compartidos con otras rutas (ejercicio 31). |

- `Route` ↔ `TourGuideUser` (`@ManyToMany`)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}` |mismo razonamiento que `Route` ↔ `DriverUser` |

- `Route` ↔ `Stop` (`@ManyToMany`)

  |`CascadeType` | Justificación |
  | --- | --- |
  | `{}`|las paradas existen de forma independiente y pueden ser reutilizadas por otras rutas |

## Jerarquía de herencia: User, DriverUser y TourGuideUser

### Ejercicio 33: ​Describir las tres estrategias de mapeo de herencia. Para cada una indicar qué tablas se crean, si aparece columna discriminadora y cómo resuelve Hibernate una consulta polimórfica. Completar la tabla:

| Aspecto | `SINGLE_TABLE` | `JOINED` | `TABLE_PER_CLASS` |
| --- | --- | --- | --- |
| Tablas creadas en la BD | Una sola para toda la jerarquía | Una por cada clase (tanto la superclases como cada subclase)| Una tabla por cada clase concreta (los atributos de la superclase se repiten en cada una) |
| Columna discriminadora | Sí, obligatoria. Se configura con `@DiscriminatorColumn` y cada subclase con `@DiscriminatorValue` | Opcional. Hibernate puede deducir el tipo por las filas en las tablas hijas, pero conviene declararla | No aplica. La identidad de la subclase está implícita en la tabla en la que vive la fila. |
| NULLs en columnas de subclases | **Sí, inevitablemente**. Los atributos específicos deben permitir nulos | **No**, cada tabla solo contiene columnas para sus propios atributos  | **No**, cada tabla tiene todas las columnas completas |
| Consulta polimórfica `from User` | Muy eficiente, un solo select sobre la única tabla| Costosa, requiere `OUTER JOIN` entre la tabla base y las de las subclases | Costosa. Requiere un `UNION` de todas las tablas de clases concretas. |
| Cargar un `DriverUser` por ID | Eficiente, un solo `SELECT` por ID sobre la tabla única| Media, requiere `JOIN` entre la tabla superclase y las subclases | Eficiente, un solo `SELECT` sobre la tabla específica |
| Integridad referencial (FK posibles) | Limitada, ya que como toda fila vive en `user`, una FK de otra tabla apuntando específicamente a "un `DriverUser`" no puede expresarse a nivel relacional. Se necesita una restricción CHECK que combine `dtype` con la FK, o validación por aplicación | **Buena**, ya que cada subclase tiene su propia tabla. Otras tablas pueden definir FK hacia `driver_user` o `tour_guide_user` directamente | Difícil, ya que como solo hay tablas de las clases concretas, no existe una tabla única a la que la FK pueda apuntar, y el motor no puede validar la referencia |
| Performance en lecturas simples (de una entidad) | Muy alta, un `SELECT` simple por ID sin `JOIN`s | Baja/Media, cada carga de subclase requiere `JOIN` con la tabla base | Alta para subclases concretas (`SELECT` simple en una sola tabla), pero costosa para consultas polimórficas (`UNION ALL`). |
| Qué implica agregar una nueva subclase | Agregar **columnas nuevas** a la tabla `user` (todas `nullable = true`) y un nuevo `@DiscriminatorValue` | Agregar **una nueva tabla** para la subclase con FK a `user` y columnas propias. La tabla base no se toca | Agregar una **nueva tabla independiente** con todas las columnas (incluidos los atributos de la clase base, duplicados). Las consultas polimórficas existentes deben actualizarse para incluir el nuevo `UNION`. |

> [!NOTE]
> Resumen de trade-offs:
> - `SINGLE_TABLE` favorece **performance** y simplicidad pero **sacrifica integridad** (NULLs forzados, FKs por subclase imposibles a nivel BD).
> - `JOINED` es la más **normalizada e íntegra**, paga el costo de los `JOIN`s y es la más amigable a evoluciones del modelo.
> - `TABLE_PER_CLASS` rinde bien para consultas no polimórficas pero degrada las polimórficas y rompe la unicidad del ID a nivel global.

### Ejercicio 34: ​Implementar el mapeo de la jerarquía User/DriverUser/TourGuideUser usando la estrategia SINGLE_TABLE. Especificar @Inheritance, @DiscriminatorColumn y @DiscriminatorValue para cada clase. Incluir todos los atributos.

```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "user_type", discriminatorType = DiscriminatorType.STRING)
@DiscriminatorValue("USER")
public class User {
    // atributos comunes: id, username, password, name, email, birthdate, phoneNumber, active
    // resto del código 
}

@Entity
@DiscriminatorValue("DRIVER")
public class DriverUser extends User {
    private String expedient;
    // resto del código 
}

@Entity
@DiscriminatorValue("TOUR_GUIDE")
public class TourGuideUser extends User {
    private String education;
    // resto del código 
}
```

#### a)​ Ejecutar los tests provistos y analizar el DDL generado: ¿cuántas tablas aparecen? ¿Qué columnas tiene la tabla? ¿Dónde están los atributos expedient y education?

Con `@Inheritance(strategy = InheritanceType.SINGLE_TABLE)`, Hibernate genera una sola tabla `User` que aloja a las tres entidades. Tiene las columnas de `User`, la columna discriminadora y las columnas de las subclases `expedient` y `education` (ambas opcionales). El DDL:

```sql
CREATE TABLE User (
    id          BIGINT       NOT NULL AUTO_INCREMENT,
    user_type   VARCHAR(31)  NOT NULL,            -- columna discriminadora
    username    VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    birthdate   DATETIME(6)  NOT NULL,
    phoneNumber VARCHAR(255) NOT NULL UNIQUE,
    active      BIT          NOT NULL,
    expedient   VARCHAR(255),                     -- de DriverUser
    education   VARCHAR(255),                     -- de TourGuideUser
    PRIMARY KEY (id)
);
```

#### b)​ ¿Qué ocurre con las columnas de subclase cuando se inserta un TourGuideUser? ¿Y cuando se inserta un DriverUser?

- Al insertar un `TourGuideUser`:
  - `user_type = 'TOUR_GUIDE'`.
  - `education` recibe el valor cargado.
  - `expedient` queda en `NULL` (la columna existe en la tabla pero el `TourGuideUser` no tiene ese atributo).
- Al insertar un `DriverUser`:
  - `user_type = 'DRIVER'`.
  - `expedient` recibe el valor cargado.
  - `education` queda en `NULL`.

> [!NOTE]
> Por esta razón, JPA/Hibernate no permite declarar `nullable = false` (`NOT NULL`) sobre las columnas exclusivas de subclase. El DDL fallaría o las inserciones de la otra subclase violarían la restricción. La validación de obligatoriedad debe hacerse a nivel **aplicación** (por ejemplo, exigiendo el atributo en el constructor de `DriverUser`/`TourGuideUser`).

#### c)​ ¿Cuáles son las ventajas y desventajas de esta estrategia para este modelo concreto?

- **Ventajas**:
  - Consultas polimórficas más simples sobre toda la jerarquía.
  - Menor necesidad de `JOIN` entre tablas de herencia.
  - Buen rendimiento en lecturas generales de usuario.
  - Implementación inicial más directa y fácil de mantener.
  - Inserciones simples, un único `INSERT` por usuario, sin coordinación entre tablas.
- **Desventajas**:
  - Menor normalización del esquema.
  - Si crecen las subclases, la tabla se vuelve más ancha, menos clara y con muchos nulos.
  - Reglas de integridad por subtipo más difíciles de imponer solo con constraints SQL (por ejemplo, exigir expedient cuando `user_type` es `DRIVER`).
  - No se pueden usar restricciones `NOT NULL` sobre `expedient` ni `education` aunque conceptualmente sean obligatorios para sus subclases perdiendo integridad declarativa en la BD.

### Ejercicio 35: ​Reimplementar el mapeo de la misma jerarquía usando la estrategia JOINED.

```java
@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public class User {
    // atributos comunes: id, username, password, name, email, birthdate, phoneNumber, active
}

@Entity
public class DriverUser extends User {
    @Column(nullable = false)
    private String expedient;
}

@Entity
public class TourGuideUser extends User {
    @Column(nullable = false)
    private String education;
}
```

>[!NOTE]
> Ahora sí podemos declarar `nullable = false` sobre `expedient` y `education`, porque cada uno vive en su propia tabla.

#### a)​ Ejecutar los tests y analizar el DDL: ¿cuantas tablas aparecen? ¿Qué FK existe entre ellas?

Con `@Inheritance(strategy = InheritanceType.JOINED)`, Hibernate genera **tres tablas**,s una para la clase base con los atributos comunes, y una por cada subclase con sólo sus atributos propios. Cada tabla de subclase tiene una **FK desde su PK hacia `User(id)`**, es decir, la clave primaria de `DriverUser` y `TourGuideUser` no es autoincremental propia, reusa el `id` asignado en `User` y lo "extiende" con los atributos específicos de la subclase.

```sql
CREATE TABLE User (
    id          BIGINT       NOT NULL AUTO_INCREMENT,
    username    VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    birthdate   DATETIME(6)  NOT NULL,
    phoneNumber VARCHAR(255) NOT NULL UNIQUE,
    active      BIT          NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE DriverUser (
    id        BIGINT       NOT NULL,
    expedient VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT FK_driver_user FOREIGN KEY (id) REFERENCES User(id)
);

CREATE TABLE TourGuideUser (
    id        BIGINT       NOT NULL,
    education VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT FK_tour_guide_user FOREIGN KEY (id) REFERENCES User(id)
);
```

>[!NOTE]
> No hay columna discriminadora explícita, la pertenencia a una subclase queda determinada por la presencia de la fila en `DriverUser` o `TourGuideUser`.

#### b)​ Comparar el SQL generado por Hibernate al cargar un DriverUser en JOINED vs. en SINGLE_TABLE. ¿Cómo difiere?

- En **`SINGLE_TABLE`**:
  ```sql
  SELECT id, username, password, name, email, birthdate, phoneNumber, active, expedient
    FROM User
   WHERE id = ?
     AND user_type = 'DRIVER';
  ```
  Una sola query a una sola tabla, filtrando por la columna discriminadora.
- En **`JOINED`**:
  ```sql
  SELECT u.id, u.username, u.password, u.name, u.email, u.birthdate, u.phoneNumber, u.active, d.expedient
    FROM User u
   INNER JOIN DriverUser d ON d.id = u.id
   WHERE u.id = ?;
  ```
  Hibernate hace un `INNER JOIN` entre la tabla base y la de la subclase para reconstruir la entidad. Si no se conoce el tipo concreto de antemano (consulta polimórfica `from User`), suma `LEFT OUTER JOIN` también con `TourGuideUser` y deduce el tipo a partir de cuál de los dos joins encontró fila.

**Diferencia concreta**: `JOINED` paga un `JOIN` extra en cada lectura de subclase, priorizando la normalización de las tablas, mientras que `SINGLE_TABLE` lee siempre de una sola tabla, priorizando el rendimiento de lectura. Para cargas frecuentes y polimorfismo intensivo, `SINGLE_TABLE` es más rápida. `JOINED` es más cara en lectura pero más limpia en almacenamiento e integridad.

#### c)​ ¿Cuáles son las ventajas y desventajas de JOINED para este modelo?

- **Ventajas**:
  - Esquema normalizado, cada tabla guarda sólo lo que le corresponde (sin nulos).
  - Pueden declararse `nullable = false` a nivel BD, alineando la integridad declarativa con la regla de negocio.
  - Si en el futuro otra entidad necesitara apuntar específicamente a un `DriverUser` por ejemplo, puede declararse una FK contra `DriverUser(id)` con garantía de tipo a nivel BD.
  - Agregar una nueva subclase implica crear una nueva tabla, **no se modifica `User`** ni las tablas existentes.
- **Desventajas**:
  - Cada lectura de subclase requiere `JOIN` con la tabla base, las consultas polimórficas requieren `LEFT JOIN` con todas las subclases.
  - Dar de alta un `DriverUser` implica **dos `INSERT`** (uno en `User` y otro en `DriverUser`), coordinados por Hibernate dentro de la misma transacción.
  - Eliminar un `DriverUser` requiere borrar primero la fila de la subclase y después la de la base (Hibernate lo hace automáticamente, pero son dos `DELETE`).

### Ejercicio 36: ​Realice el mismo proceso ahora con la estrategia TABLE_PER_CLASS. Indique cuál le parece la mejor estrategia para este modelo concreto y justifique su elección.

Se crea una tabla por cada clase concreta de la jerarquía, usualmente `DriverUser` y `TourGuideUser` , y también una para `User` **si esta no es abstracta**. Cada tabla contiene todas las columnas, incluyendo las heredadas (id, username, password, etc.) y las propias (expedient o
education).

```java
@Entity
@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.TABLE)   // IDENTITY no es viable acá
    private Long id;
    // resto de los atributos comunes y código
}

@Entity
public class DriverUser extends User {
    @Column(nullable = false)
    private String expedient;
    // resto del código
}

@Entity
public class TourGuideUser extends User {
    @Column(nullable = false)
    private String education;
    // resto del código
}
```

>[!IMPORTANT]
> La estrategia de generación **no puede ser `IDENTITY`**. Cada subclase tiene su propia tabla y, si cada una usara su `AUTO_INCREMENT`, los **IDs se solaparían** (un `DriverUser` con `id = 1` y un `TourGuideUser` con `id = 1` coexistiendo) y romperían las FKs polimórficas (por ejemplo, `Purchase.user_id`). Por eso se usa `TABLE` (o `SEQUENCE` e1n motores que la soporten) para que el **contador de IDs sea único a nivel de toda la jerarquía**.

#### a)​ DDL generado

Hibernate genera **una tabla por cada clase concreta**, completa e independiente, replicando los atributos de la clase base en cada una. Como `User` es **concreta** , se generan **tres** tablas. Los usuarios planos (clientes) viven solo en `User`, los choferes en `DriverUser` y los guías en `TourGuideUser`

```sql
CREATE TABLE User (
    id          BIGINT       NOT NULL,
    username    VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    birthdate   DATETIME(6)  NOT NULL,
    phoneNumber VARCHAR(255) NOT NULL UNIQUE,
    active      BIT          NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE DriverUser (
    id          BIGINT       NOT NULL,
    username    VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    birthdate   DATETIME(6)  NOT NULL,
    phoneNumber VARCHAR(255) NOT NULL UNIQUE,
    active      BIT          NOT NULL,
    expedient   VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE TourGuideUser (
    id          BIGINT       NOT NULL,
    username    VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    birthdate   DATETIME(6)  NOT NULL,
    phoneNumber VARCHAR(255) NOT NULL UNIQUE,
    active      BIT          NOT NULL,
    education   VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);
```

>[!IMPORTANT]
> - Nada impide que un `User`, un `DriverUser` y un `TourGuideUser` compartan, por ejemplo, el mismo `username`, la **unicidad global se pierde** (el motor no puede garantizarla entre tablas distintas).
> - Como las tres tablas comparten el mismo generador (`TABLE`/`SEQUENCE`, nunca `IDENTITY`), un `id` no se repite entre `User`, `DriverUser` y `TourGuideUser`. Requisito para que `Purchase.user_id` pueda referenciar a cualquiera de los tres tipos.

#### b)​ SQL al cargar un `DriverUser`

```sql
SELECT id, username, password, name, email, birthdate, phoneNumber, active, expedient
  FROM DriverUser
 WHERE id = ?;
```

>[!NOTE]
> Una sola query a una sola tabla. Para este caso particular, `TABLE_PER_CLASS` es **tan rápida como `SINGLE_TABLE`** (incluso más, porque no hay columna discriminadora que filtrar). En cambio, una **consulta polimórfica** (`from User`) requiere `UNION ALL` y es la consulta más cara de las tres estrategias.

#### c)​ Ventajas y desventajas

- **Ventajas**:
  - Lecturas de subclases concretas sin `JOIN` ni filtro adicional.
  - `NOT NULL` sobre atributos de subclase declarativo, igual que `JOINED`.
  - Cada subclase es estructuralmente independiente. Si una evoluciona, no afecta el DDL de las otras.
- **Desventajas**:
  - Consultas polimórficas costosas (`UNION ALL` sobre todas las tablas).
  - `IDENTITY` no es viable, hay que usar `TABLE` o `SEQUENCE` para mantener IDs únicos a nivel jerarquía.
  - Cada tabla repite todas las columnas comunes. Si `User` crece, hay que tocar todas las tablas hijas.
  - FKs polimórficas imposibles, relaciones como `Purchase.user_id` no pueden representarse con una FK simple a nivel BD, la integridad pasa a depender del ORM.
  - `UNIQUE` global se pierde, la unicidad de `username`/`email` queda partida por subclase.

#### Estrategia elegida para este modelo: `SINGLE_TABLE`

Para este modelo, donde las **subclases agregan pocos atributos** (`expedient`, `education`), la **jerarquía es estable** y el **costo** (NULLs y pérdida del `NOT NULL`) **es acotado** `SINGLE_TABLE` es la mejor elección, ganando en **performance y simplicidad**. 

A pesar de que `JOINED` es la más íntegra a nivel BD y `TABLE_PER_CLASS` es competitiva en lecturas no polimórficas, la elección concreta para este TP es **`SINGLE_TABLE`**, ya que hay consultas polimórficas, que resolvemos solo con una `SELECT` simple. Además, cada subclase solo agrega un atributo, y no tenemos indicios de que se vayan a agregar en el futuro más tipos concretos de usuarios

>[!IMPORTANT]
> La única desventaja real de `SINGLE_TABLE` es no poder declarar `NOT NULL` sobre `expedient` y `education`. Esa restricción se valida igualmente a nivel aplicación (en los constructores de `DriverUser` y `TourGuideUser`) sin pérdida de garantías para la lógica de dominio. Sólo se pierde la validación declarativa en la BD, lo cual es un costo aceptable.

### Ejercicio 37: ​Route tiene relaciones muchos-a-muchos con DriverUser y TourGuideUser (subclases de User). Analizar el impacto de la estrategia de herencia sobre la tabla join:

#### a)​ Si la jerarquía es SINGLE_TABLE, ¿a qué tabla apunta la FK en la tabla join?

- Las tablas join `route_driver` y `route_tour_guide` tienen su FK apuntando a `User(id)`.
- A nivel BD, una fila en `route_driver` representa "una `Route` asociada a alguna fila de `User`", sin que la base pueda imponer por sí misma que esa fila sea efectivamente un `DriverUser`.
- La garantía de que el usuario referenciado sea de la subclase correcta queda **a cargo de Hibernate**, que al insertar/leer aplica el filtro por `user_type` automáticamente. Si un proceso externo (un `INSERT` manual a la tabla join, una migración por SQL nativo, etc.) saltea el ORM, podría introducir una asociación inválida y la BD no la detendría.

#### b)​ Si la jerarquía es JOINED, ¿cambia la tabla destino de esa FK?

Sí, cambia. Con `JOINED`, cada subclase tiene su propia tabla cuya PK es a la vez FK contra `User(id)`. Hibernate, al generar el DDL de las tablas join:

- Apunta la FK de `route_driver` directamente a **`DriverUser(id)`** (no a `User(id)`).
- Apunta la FK de `route_tour_guide` directamente a **`TourGuideUser(id)`**.

Esto refuerza la integridad referencial, ya que la base **garantiza por sí misma** que un `route_driver` sólo puede contener `DriverUser`s, porque la FK exige que el `id` exista en la tabla específica.

### Ejercicio 38: ​¿Qué estrategia resulta más robusta ante cambios futuros como agregar una nueva subclase de User? Justificar con al menos dos argumentos.

La estrategia más robusta ante la incorporación de nuevas subclases es **`JOINED`**:

1. **Aislamiento del esquema existente**: agregar una nueva subclase implica únicamente **crear una nueva tabla** con la PK como FK contra `User(id)` y las columnas propias de la subclase. La tabla base (`User`) **no se modifica**, ni tampoco las tablas de las otras subclases.
   - Por contraste, en **`SINGLE_TABLE`** la nueva subclase obliga a alterar la tabla `User` agregando columnas para sus atributos propios (todas `nullable = true`) y un nuevo valor en la columna discriminadora.
   - En **`TABLE_PER_CLASS`** la nueva subclase implica también una nueva tabla, pero además exige que **todas las consultas polimórficas existentes incorporen el nuevo `UNION ALL`** y más repetición de atributos.

2. **Integridad de datos y normalización**: los atributos propios de la nueva subclase se pueden declarar `NOT NULL` desde el primer momento (cosa que `SINGLE_TABLE` impide), y las FKs desde otras entidades hacia la nueva subclase son representables a nivel BD con garantía de tipo. Las FKs polimórficas hacia `User` siguen siendo válidas porque la tabla base existe y tiene PK propia. En `SINGLE_TABLE` esa integridad de tipo no es expresable y en `TABLE_PER_CLASS` ni siquiera existe la tabla base contra la que apuntar las FKs polimórficas, por lo que agregar subclases agrava un problema preexistente.

> [!NOTE]
> Hay una tensión entre las decisiones de `SINGLE_TABLE` por simplicidad y performance polimórfica en este TP y la de `JOINED` por robustez ante cambios futuros. No es una contradicción, son dos optimizaciones distintas. `SINGLE_TABLE` es la mejor para el modelo *actual y estable* del TP, y `JOINED` sería la mejor si se anticipara que la jerarquía va a crecer (más subclases, más atributos por subclase, restricciones de integridad más fuertes). La elección depende, en última instancia, del horizonte temporal y de la criticidad de la integridad declarativa frente al costo de los joins.
