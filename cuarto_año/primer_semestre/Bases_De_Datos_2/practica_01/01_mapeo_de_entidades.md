# Mapeo de entidades

## Mapeo de una entidad simple: Service

### Ejercicio 12: ​¿Cuál es el conjunto mínimo de anotaciones que debe tener una clase para ser persistente con JPA?

El conjunto mínimo de anotaciones que debe tener una clase para ser persistente con JPA se compone de dos anotaciones:
- `@Entity`: Se coloca a nivel de la declaración de la clase para indicarle al framework que dicha clase es una entidad (POJO persistente) y que debe ser mapeada a la base de datos
- `@Id`: Se coloca sobre el atributo que servirá como identificador único o clave primaria, cumpliendo con la regla obligatoria de los POJOs persistentes de proveer un identificador

>[!NOTE]
> No es obligatorio agregar anotaciones adicionales para los demás atributos de la clase. Gracias al principio de "Convención sobre Configuración", JPA asume por defecto que todos los atributos declarados en la clase deben persistirse en la base de datos, a menos que se indique explícitamente lo contrario (por ejemplo, utilizando la anotación `@Transient` para que un campo sea ignorado)

### Ejercicio 13: ¿Qué significa que JPA use persistencia por alcance (persistence by reachability)? ¿Qué consecuencia tiene si un objeto referenciado no está todavía persistido?

La persistencia por alcance (o persistencia transitiva) significa que todo objeto al cual se pueda llegar navegando a partir de un objeto que ya es persistente, debe ser necesariamente persistente a su vez. Esto permite que, para almacenar un objeto en la base de datos, el desarrollador solamente necesite vincularlo orgánicamente (por ejemplo, agregándolo a una colección o asignándolo a un atributo) con algún otro objeto que ya exista en el repositorio, reduciendo de esta forma las operaciones explícitas de guardado y respetando el principio de independencia
- La consecuencia de que un objeto referenciado no esté todavía persistido (es decir,  que se encuentre en estado volátil o transitorio) depende de la configuración de cascada:
  - Si la persistencia por alcance está activa (por ejemplo, configurada con `CascadeType.PERSIST` o `ALL`): Al momento de realizar el commit de la transacción, el framework recorrerá el grafo de objetos modificados y, al encontrar este nuevo objeto volátil referenciado, lo insertará y persistirá automáticamente en la base de datos sin requerir ninguna acción adicional por parte del desarrollador
  - Si la persistencia por alcance NO está activa (el comportamiento por defecto de JPA): La operación de guardado no se propagará hacia la entidad asociada. Como consecuencia, el ORM intentará guardar en la base de datos una relación hacia un registro que físicamente aún no existe, lo cual desencadenará una excepción — típicamente `org.hibernate.TransientObjectException` o `TransientPropertyValueException` — o, si se llega al flush, una falla de integridad referencial a nivel de base de datos.

### Ejercicio 14: ¿Qué diferencia hay entre las estrategias IDENTITY, SEQUENCE y TABLE para la generación de IDs? ¿Cuál tiene mejor rendimiento en inserciones masivas y por qué?

En JPA la anotación `@GeneratedValue` permite definir cómo se crearán las claves primarias automáticamente, utilizando tres estrategias principales:

- `IDENTITY`:
  - **Delega la generación del identificador enteramente a la base de datos** utilizando columnas de tipo "**autoincremental**" (como `AUTO_INCREMENT` en MySQL o `IDENTITY` en PostgreSQL).
  - En Hibernate no conoce el ID del objeto hasta que la sentencia `INSERT` se ejecuta realmente en la base de datos.
- `SEQUENCE`:
  - Utiliza un objeto nativo de la base de datos llamado "Secuencia" (muy común en Oracle o PostgreSQL).
  - En Hibernate realiza una consulta a la base de datos para pedirle el próximo valor de la secuencia antes de ejecutar el `INSERT`. Esto le permite a Hibernate conocer el ID del objeto y asignárselo en memoria antes de guardar el registro.
- `TABLE`:
  - Es la estrategia más genérica. En lugar de usar características nativas del motor (como columnas autoincrementales o secuencias), crea una tabla auxiliar en la base de datos dedicada exclusivamente a llevar la cuenta de los identificadores.
  - En Hibernate para generar un nuevo ID, Hibernate debe hacer un `SELECT` en esta tabla auxiliar, bloquear la fila (lock), hacer un `UPDATE` para incrementar el valor, y liberar la fila.

En cuanto al **rendimiento en inserciones masivas**, la estrategia más eficiente es `SEQUENCE`. La razón es que Hibernate necesita conocer el ID de la entidad antes de insertarla para poder asignárselo en memoria. Con `SEQUENCE`, Hibernate puede pedir varios IDs de antemano (con `allocationSize` obtiene bloques completos en una sola consulta), lo que le permite agrupar múltiples `INSERT` en un **batch JDBC** y reducir los round-trips a la base. En cambio, con `IDENTITY` el ID sólo se conoce después de ejecutar el `INSERT`, por lo que Hibernate **deshabilita automáticamente el batch insert** y se ve obligado a ejecutar cada sentencia individualmente. La estrategia `TABLE` es la peor de las tres, porque cada generación implica un `SELECT ... FOR UPDATE` + `UPDATE` con bloqueo de fila sobre la tabla auxiliar, lo que agrega contención y sobrecarga.

### Ejercicio 15: Implementar el mapeo completo de la entidad Service según el diagrama. La implementación debe incluir:

#### a) Clave primaria con estrategia de generación automática. Elegir entre IDENTITY, SEQUENCE o TABLE y justificar la elección.

- Agregamos la anotación `@Entity` a la clase para marcarla como una entidad persistente
- Luego, definimos el atributo `id` como clave primaria utilizando la anotación `@Id` y configuramos la estrategia de generación automática con `@GeneratedValue`. En este caso, utilizaremos `IDENTITY`
  - La elección de `IDENTITY` se justifica porque estamos usando MySQL, motor que soporta nativamente columnas autoincrementales (`AUTO_INCREMENT`). Esto evita tener que crear y mantener objetos adicionales en el esquema (una `SEQUENCE` —que además MySQL no soporta de forma nativa— o una tabla auxiliar en el caso de `TABLE`) y mantiene la generación de IDs simple y transparente para el motor. Si bien para inserciones masivas `SEQUENCE` suele rendir mejor (ver ejercicio 14), el TP no contempla un escenario de carga masiva y las operaciones típicas son inserciones unitarias, donde el costo de `IDENTITY` es despreciable.

#### b) Atributos: name (no nulo, max. 100 caracteres), description (opcional), price (no nulo).

- Ahora sobre el atributo `name` agregamos las anotaciones `@Column(nullable = false, length = 100)` para indicar que no puede ser nulo y que su longitud máxima es de 100 caracteres
- Sobre el atributo `description` agregamos la anotación `@Column(nullable = true)` para indicar que es opcional (aunque esta anotación es redundante, ya que por defecto los campos son nullable)
- Sobre el atributo `price` agregamos la anotación `@Column(nullable = false)`

#### c) Al menos una restricción de unicidad a nivel de columna.

La opción natural sería agregar `@Column(unique = true)` sobre el atributo `name`, garantizando que no existan dos servicios con el mismo nombre.

> [!NOTE]
> En la **implementación final del TP** este `unique = true` se relajó: los datos provistos por `DBInitializer.prepareDB()` crean dos servicios llamados `"souvenir t-shirt"` (con descripciones distintas — "I love Buenos Aires" y "I love Argentina" — y proveedores distintos), lo cual viola la restricción. Por ese motivo, en `Service` queda únicamente `nullable = false` sobre `name` y `price`, sin restricciones de unicidad a nivel de columna. La regla de negocio "no repetir el mismo servicio para un mismo proveedor" se delega entonces a la capa de servicio (validación previa al `save`), no al esquema. El mismo criterio aplica a `User.phoneNumber`: el dominio sugería `unique = true`, pero los datos de prueba reúsan el mismo número entre usuarios y la columna queda con `nullable = false` sin unicidad.

## Relaciones entre entidades

### Ejercicio 16: Para la relación Purchase -> ItemService (composición uno-a-muchos):

#### a)​ ¿Qué anotaciones se necesitan en cada lado?

- En el lado de `Purchase` (lado "uno"), se necesita la anotación `@OneToMany` sobre el atributo que representa la colección de `ItemService`. Además, se debe especificar el atributo `mappedBy` para indicar que esta es la parte inversa de la relación y que el propietario es `ItemService`. Además, agregamos `cascade = {CascadeType.REMOVE, CascadeType.PERSIST}` para que se propaguen las operaciones de eliminación y persistencia, y por último `orphanRemoval = true` para eliminar objetos "sueltos" (sin referencias).
- En el lado de `ItemService` (lado "muchos"), se necesita la anotación `@ManyToOne` sobre el atributo que representa la referencia a `Purchase`. Este lado es el propietario de la relación, por lo que no se utiliza `mappedBy` aquí. Además, se puede agregar la anotación `@JoinColumn` para especificar el nombre de la columna que actuará como clave foránea en la base de datos. En este caso, utilizaremos `@JoinColumn(name = "purchase_id")` para indicar que la columna `purchase_id` en la tabla de `ItemService` será la clave foránea que referencia a `Purchase`.

#### b)​ ¿Qué columna o tabla aparece en la base de datos para representar esta relación?

- Aparece una columna llamada `purchase_id` en la tabla correspondiente a `ItemService`, que actúa como clave foránea y referencia a la tabla de `Purchase`. Esta columna se utiliza para establecer la relación entre cada registro de `ItemService` y su correspondiente registro de `Purchase`.

>[!NOTE]
> Esta columna se genera automáticamente por JPA debido a la anotación `@JoinColumn` en el lado de `ItemService`, y su nombre puede ser personalizado según las necesidades del desarrollador. En este caso, hemos elegido `purchase_id` para mantener una convención clara y descriptiva.

#### c)​ ¿Qué es mappedBy y en qué lado de la relación va? ¿Qué ocurre si se omite en ambos lados?

- `mappedBy` es un atributo de la anotación `@OneToMany` que se utiliza para indicar que esta parte de la relación es la inversa y que el propietario de la relación es el otro lado (en este caso, `ItemService`). Especifica el nombre del atributo en la clase del lado "muchos" que mantiene la referencia a la clase del lado "uno". En este caso, `mappedBy = "purchase"` indica que el atributo `purchase` en `ItemService` es el propietario de la relación.
- Si se omite `mappedBy` en ambos lados, JPA no podrá determinar cuál es el propietario de la relación, lo que resultará en la creación de una tabla intermedia adicional para gestionar la relación entre `Purchase` e `ItemService`, en lugar de utilizar una clave foránea directa en la tabla de `ItemService`. Esto puede llevar a una estructura de base de datos más compleja e ineficiente, ya que se requerirán operaciones adicionales para gestionar la relación entre las entidades.

#### d)​ ¿Es esta relación bidireccional o unidireccional según el diagrama? ¿Cómo se refleja en el código Java?

- Según el diagrama, esta relación es bidireccional, ya que tanto `Purchase` como `ItemService` mantienen referencias mutuas entre sí. En el código Java, esto se refleja mediante la presencia de un atributo en `Purchase` que es una colección de `ItemService` (con la anotación `@OneToMany`) y un atributo en `ItemService` que es una referencia a `Purchase` (con la anotación `@ManyToOne`). Esta configuración permite navegar desde una instancia de `Purchase` hacia sus `ItemService` asociados, así como desde una instancia de `ItemService` hacia su correspondiente `Purchase`.

### Ejercicio 17: ​Para las relaciones Route <-> DriverUser y Route <-> TourGuideUser (muchos-a-muchos):

#### a)​ ¿Qué anotaciones se usan?

- Las anotaciones que se utilizan son:
  - Del lado de `Route`, se utiliza la anotación `@ManyToMany` sobre los atributos que representan las colecciones de `DriverUser` y `TourGuideUser`. Además, utilizamos la anotación `@JoinTable` para definir explícitamente la tabla intermedia que gestionará la relación muchos-a-muchos, especificando los nombres de las columnas de clave foránea y declarando que no pueden ser nulos (`nullable = false`) ya que se especifica que la relación es obligatoria. 
  - Del lado de `DriverUser` y `TourGuideUser`, también se utiliza la anotación `@ManyToMany` sobre los atributos que representan las colecciones de `Route`. Además, utilizamos `mappedBy` para indicar que esta es la parte inversa de la relación y que el propietario es `Route`. En este lado, no utilizamos `@JoinTable` porque la tabla intermedia ya está definida en el lado de `Route`.

#### b)​ ¿Qué tabla adicional genera JPA? ¿Qué columnas tiene? Definirla explícitamente usando @JoinTable.

- JPA genera una tabla adicional para cada relación muchos-a-muchos. Por convención por defecto, JPA la nombraría como `route_driver_user` / `route_tour_guide_user` (combinando los nombres de las entidades), pero en el proyecto se personalizan explícitamente mediante `@JoinTable(name = ...)`:
  - Para la relación entre `Route` y `DriverUser`, se genera la tabla `route_driver` con las siguientes columnas:
    - `route_id`: Clave foránea que referencia a la tabla de `Route`, con `nullable = false`.
    - `driver_id`: Clave foránea que referencia a la tabla de `DriverUser`, con `nullable = false`.
  - Para la relación entre `Route` y `TourGuideUser`, se genera la tabla `route_tour_guide` con las siguientes columnas:
    - `route_id`: Clave foránea que referencia a la tabla de `Route`, con `nullable = false`.
    - `tour_guide_id`: Clave foránea que referencia a la tabla de `TourGuideUser`, con `nullable = false`.

#### c)​ ¿Pueden ambas relaciones compartir la misma tabla join? ¿Por qué?

- No, ambas relaciones no pueden compartir la misma tabla join porque cada relación muchos-a-muchos representa una asociación distinta entre diferentes entidades. Cada tabla join debe ser específica para la relación que está gestionando, ya que contiene claves foráneas que hacen referencia a las entidades involucradas en esa relación particular. Compartir la misma tabla join para ambas relaciones podría generar confusión y problemas de integridad referencial, ya que no habría una forma clara de distinguir entre los registros que corresponden a la relación `Route`-`DriverUser` y los que corresponden a la relación `Route`-`TourGuideUser`. Por lo tanto, es necesario tener tablas join separadas para cada relación muchos-a-muchos.

### Ejercicio 18: ​La relación Purchase -> Review es opcional (0..1). Implementar el mapeo de ambos lados. ¿Cómo se representa la opcionalidad en JPA?

- Para mapear la relación opcional entre `Purchase` y `Review`, se utiliza la anotación `@OneToOne` en ambos lados de la relación. En el lado de `Purchase`, se puede agregar la anotación `@OneToOne(mappedBy = "purchase", cascade = CascadeType.REMOVE, optional = true, orphanRemoval = true)` para indicar que esta es la parte inversa de la relación y que el propietario es `Review`. En el lado de `Review`, se utiliza la anotación `@OneToOne` junto con `@JoinColumn(name = "purchase_id", nullable = false)` para establecer la clave foránea que referencia a `Purchase`.
- La opcionalidad se representa en JPA utilizando el atributo `optional = true` en la anotación de relación (`@OneToOne`, `@ManyToOne`, etc.) en el lado que es opcional.

>[!NOTE]
> Para que la relación sea realmente 1–1 (y no 1–*) a nivel de base de datos, la columna `purchase_id` en `review` debe tener una restricción `UNIQUE`. JPA la agrega de forma **implícita** cuando se combina `@OneToOne` + `@JoinColumn`, por lo que no es obligatorio declararla de forma explícita. Si se quiere dejarla visible en el código, puede escribirse `@JoinColumn(name = "purchase_id", nullable = false, unique = true)`.

### Ejercicio 19: ItemService referencia a Service (muchos-a-uno). Analizar el diagrama: ¿es navegable esta relación desde Service hacia ItemService? Justificar si conviene hacerla bidireccional o no.

- Es navegable, ya que `Service` tiene un atributo que es una colección de `ItemService`, por lo cual, se puede navegar desde una instancia de `Service` hacia sus `ItemService` asociados.
- Es conveniente hacerla bidireccional porque permite una mayor flexibilidad al momento de acceder a los datos. Al tener la relación bidireccional, se puede navegar tanto desde `ItemService` hacia `Service` como desde `Service` hacia `ItemService`, lo que facilita la consulta y manipulación de los datos relacionados. Además, al ser una relación muchos-a-uno, la cantidad de `ItemService` asociados a un `Service` puede ser significativa, por lo que tener la capacidad de navegar desde `Service` hacia `ItemService` puede mejorar la eficiencia y la claridad del código. También, deberíamos tener en cuenta que al ser bidireccional, se debe gestionar adecuadamente la sincronización de ambas partes de la relación para evitar inconsistencias en el modelo de datos, lo cual agrega cierta complejidad al código.
- Adicionalmente, el argumento no es meramente teórico: los tests provistos con el proyecto base asumen esta bidireccionalidad. Por ejemplo, en `ToursApplicationTests.removePurchaseAndItems` se valida `assertEquals(1, service1.getItemServiceList().size())`, es decir, se accede explícitamente a los `ItemService` desde el `Service`. Esto convierte la decisión en un requerimiento concreto del dominio dentro del TP, no en una simple comodidad.

### Ejercicio 20.​Implementar el mapeo completo de las siguientes entidades con todas sus relaciones, siguiendo las anotaciones y decisiones discutidas: Supplier, Purchase, ItemService, Route, Stop y Review. Para cada relación bidireccional, incluir las anotaciones en ambos lados.

Siguiendo las decisiones discutidas en los ejercicios 16–19, se mapearon las seis entidades. Para cada relación bidireccional se colocan las anotaciones en ambos lados, respetando que el lado dueño (el que tiene la FK/tabla join) no lleva `mappedBy` y el lado inverso sí. Respecto a las cascadas, se sigue el criterio de la cátedra: declarar únicamente los `CascadeType` que el dominio justifica y dejar explícito `cascade = {}` cuando no se necesita propagar nada (en lugar de usar `CascadeType.ALL` por defecto).

> [!NOTE]
> **Inicialización de colecciones inversas**: todas las colecciones que aparecen como lado inverso (`Supplier.services`, `Service.itemServiceList`, `User.purchaseList`, `DriverUser.routes`, `TourGuideUser.routes`) deben inicializarse en su declaración con `new ArrayList<>()`. Si quedan en `null`, los métodos helper como `addService(...)`, `addRoute(...)`, etc. fallan con `NullPointerException` la primera vez que el código intenta agregar un elemento. Hibernate sustituye estas listas por sus colecciones especiales (`PersistentBag`/`PersistentList`) sólo cuando la entidad pasa a managed; mientras esté en estado *transient* (recién instanciada con `new`), los helpers necesitan una lista real.

#### Supplier

- `@OneToMany(mappedBy = "supplier", cascade = {})` sobre `services`. Es el lado inverso de la relación con `Service`; el dueño es `Service` (ver abajo).
- `cascade = {}` porque el dominio no especifica aún qué debe pasar con los `Service` si se elimina un `Supplier` (tema a definir en el ejercicio 30). Hasta entonces, no se propaga ninguna operación.

#### Service

- Lado dueño de la relación con `Supplier`: `@ManyToOne` + `@JoinColumn(name = "supplier_id", nullable = false)`. La FK `supplier_id` es obligatoria porque todo servicio pertenece a un proveedor.
- Lado inverso de la relación con `ItemService`: `@OneToMany(mappedBy = "service")`. Se decidió bidireccional según el ejercicio 19 para habilitar la navegación desde `Service` hacia sus ítems; no se declara cascada porque los `ItemService` pertenecen al agregado `Purchase`, no a `Service`.

#### Purchase

- Lados dueños de las relaciones a `User` y `Route`: `@ManyToOne` + `@JoinColumn("user_id"/"route_id", nullable = false)`. Ambas FK son obligatorias: una compra siempre pertenece a un usuario y a una ruta.
- `@OneToOne(mappedBy = "purchase", cascade = CascadeType.REMOVE, optional = true, orphanRemoval = true)` sobre `review`. `optional = true` modela la cardinalidad `0..1` del diagrama; `REMOVE` + `orphanRemoval` propaga la baja del review al eliminar la compra o al desvincularlo (tiene sentido porque un review sin su compra no existe en el dominio).
- `@OneToMany(mappedBy = "purchase", cascade = {CascadeType.REMOVE, CascadeType.PERSIST}, orphanRemoval = true)` sobre `itemServiceList`. Es composición (diamante negro): `PERSIST` para poder agregar ítems a una compra nueva sin guardarlos manualmente, `REMOVE` y `orphanRemoval` para que al borrar o desvincular un ítem de la lista se elimine también de la base.
- `@Temporal(TemporalType.DATE)` sobre `date` para persistir sólo la fecha (sin hora).

#### ItemService

- Lado dueño de la relación con `Purchase`: `@ManyToOne` + `@JoinColumn("purchase_id", nullable = false)`. Obligatorio por la composición: todo ítem pertenece a una compra.
- Lado dueño de la relación con `Service`: `@ManyToOne` + `@JoinColumn("service_id", nullable = false)`. Todo ítem referencia obligatoriamente un servicio.
- No se declara cascada en ninguna de las dos porque la propagación se maneja desde el lado de `Purchase` (composición) y nunca desde el ítem.
- Atributos propios:
  - `quantity: int` — del diagrama original.
  - `price: float` con `@Column(nullable = false)` — **agregado en la implementación**. Actúa como *snapshot* del precio del `Service` al momento de la compra: si el `Service.price` cambia después, los `ItemService` históricos preservan el precio que efectivamente se cobró. Es información económica/contable que no puede recalcularse desde el catálogo actual.

#### Route

- `@ManyToMany` con `@JoinTable` sobre `stops`, `driverList` y `tourGuideList`. Se usa `@JoinTable` (y no `@JoinColumn`) porque son relaciones muchos-a-muchos: cada una necesita su propia tabla intermedia (`route_stop`, `route_driver`, `route_tour_guide`), con sus dos FK declaradas `nullable = false`.
- `cascade = {}` en las tres. Las paradas, choferes y guías existen de forma independiente a la ruta: se crean y se persisten antes de asociarse, así que no corresponde propagar persistencia ni baja desde la ruta.

#### Stop

- Entidad simple, sin referencias salientes. El lado dueño de la relación con `Route` es `Route` (a través del `@JoinTable` `route_stop`), por lo que `Stop` no necesita anotaciones de relación.

#### Review

- Lado dueño de la relación con `Purchase`: `@OneToOne` + `@JoinColumn("purchase_id", nullable = false)`. La FK es obligatoria porque un review no tiene sentido sin la compra que lo origina. La opcionalidad `0..1` se declara del lado inverso (`Purchase.review` con `optional = true`).

## Fetch Type: LAZY vs. EAGER

### Ejercicio 21: ¿Para qué sirve la propiedad `fetch` en las anotaciones de relación? ¿Cuáles son los valores posibles? ¿Cuál es el valor por defecto para `@OneToMany`, para `@ManyToOne` y para `@ManyToMany`?

- La propiedad `fetch` define la **estrategia de carga** de los objetos asociados en una relación: indica si las entidades relacionadas deben traerse de la base de datos en el mismo momento en que se carga la entidad principal, o recién cuando el código accede explícitamente a ellas por primera vez. Su configuración impacta directamente en la performance (cantidad de queries y volumen de datos transferidos) y en el consumo de memoria.
- Los valores posibles son dos, definidos por el enum `FetchType`:
  - `FetchType.EAGER`: La entidad asociada se carga **inmediatamente** junto con la entidad principal, típicamente mediante un `JOIN` o una consulta adicional automática.
  - `FetchType.LAZY`: La entidad asociada **no** se carga al traer la entidad principal. En su lugar, Hibernate coloca un proxy (o una colección "wrappeada") y sólo ejecuta la consulta cuando el código accede al atributo por primera vez.
- Los valores por defecto dependen del tipo de relación y están pensados según la cardinalidad del "otro lado":
  - `@OneToMany`: `LAZY` por defecto (la colección puede tener muchos elementos → traerlos siempre es costoso).
  - `@ManyToMany`: `LAZY` por defecto (mismo razonamiento).
  - `@ManyToOne`: `EAGER` por defecto (se asume que cargar un único objeto asociado es barato).
  - `@OneToOne`: `EAGER` por defecto (mismo razonamiento que `@ManyToOne`).

> [!NOTE]
> La regla general es: **las relaciones "a-muchos" son LAZY por defecto, las "a-uno" son EAGER por defecto**. Sin embargo, como se discute en el ejercicio 22, la recomendación práctica es configurar todas las relaciones como `LAZY` y traer explícitamente lo que se necesita con `JOIN FETCH` o `@EntityGraph`.

### Ejercicio 22: Describir ventajas y desventajas concretas de EAGER y LAZY, en términos de performance de acceso como de espacio en memoria. ¿Por qué configurar EAGER en todas las relaciones suele ser una mala idea en aplicaciones reales?

- **EAGER**:
  - *Ventajas*:
    - Al cargar la entidad principal, las entidades relacionadas ya están disponibles en memoria, evitando consultas adicionales al acceder a ellas posteriormente.
    - Los datos están garantizados fuera del contexto de persistencia (por ejemplo después de cerrar la `Session`), evitando `LazyInitializationException`.
  - *Desventajas*:
    - **Sobrecarga de memoria**: se cargan datos que quizá nunca se usen. Si una `Purchase` trae siempre su `User`, `Route`, `itemServiceList`, y cada ítem su `Service`, y cada `Service` su `Supplier`... una sola query termina arrastrando un grafo enorme.
    - **Consultas pesadas**: Hibernate debe realizar `JOIN`s adicionales o ejecutar queries extra (problema de *N+1 queries* si la relación EAGER es una colección y no se optimiza con fetch join).
    - **Acoplamiento del modelo a una estrategia de carga**: la decisión queda "cementada" en la anotación y no se puede relajar caso por caso.
- **LAZY**:
  - *Ventajas*:
    - **Menor consumo de memoria inicial**: sólo se carga lo que se pide.
    - **Mejor performance en consultas básicas**: la query de la entidad principal es más chica y más rápida.
    - **Flexibilidad**: cada caso de uso puede decidir qué traer explícitamente (con `JOIN FETCH`, `@EntityGraph`, etc.).
  - *Desventajas*:
    - Cada acceso a una asociación no cargada genera una **consulta adicional**, lo que puede derivar en el problema de *N+1 queries* si no se planifica bien.
    - Si se accede a la relación **fuera del contexto de persistencia** (con la `Session` cerrada), se produce la temida `LazyInitializationException` (ver ejercicio 24).
- **¿Por qué configurar EAGER en todas las relaciones es mala idea?**
  - En un modelo con relaciones transitivas como el de tours (`Purchase` → `User`, `Route`, `itemServiceList` → `Service` → `Supplier`, etc.), marcar todo como `EAGER` provoca que **cada consulta a una entidad termine arrastrando gran parte del grafo de dominio**, incluso cuando el caso de uso sólo necesita un par de campos.
  - Esto degrada gravemente la performance (queries largas con múltiples `JOIN`s o cascadas de *N+1*), agota la memoria de la JVM en listados grandes y hace imposible optimizar caso por caso.
  - La buena práctica es la opuesta: declarar **todo LAZY por defecto** y, cuando un caso de uso específico necesita traer más, pedirlo explícitamente con `JOIN FETCH` / `@EntityGraph`. Así la decisión de qué cargar vive en la consulta (cerca del caso de uso), no en el mapeo (cerca del esquema).

### Ejercicio 23: Para cada relación del modelo, elegir el FetchType más adecuado y justificar. Luego implementar su decisión en el proyecto tours.

Siguiendo la recomendación discutida en el ejercicio 22, se declaran **todas las relaciones como `LAZY`**, incluso aquellas que por defecto serían `EAGER` (`@ManyToOne` y `@OneToOne`). El razonamiento es: *la estrategia de carga debe ser una decisión de cada caso de uso, no del mapeo*. Si un caso particular necesita traer la asociación, se usa `JOIN FETCH` en el HQL del repositorio correspondiente.

| Relación | Tipo de anotación | FetchType elegido | Justificación |
| --- | --- | --- | --- |
| `Purchase` → `User` | `@ManyToOne` | `LAZY` | Aunque el default es `EAGER`, no todos los casos de uso sobre `Purchase` necesitan el `User` (listar compras por fecha, calcular totales, etc.). Forzar la carga siempre es un costo que se paga sin retorno garantizado. |
| `Purchase` → `Route` | `@ManyToOne` | `LAZY` | Mismo criterio: hay consultas sobre `Purchase` que no requieren la `Route` completa (con sus stops, drivers y tour guides). Si hace falta, se hace `JOIN FETCH p.route`. |
| `Purchase` → `itemServiceList` | `@OneToMany` | `LAZY` (default) | Una compra puede tener múltiples ítems; cargarlos siempre infla las queries aun cuando sólo se inspecciona el `totalPrice` o la `date`. Se mantiene el default. |
| `Purchase` → `Review` | `@OneToOne` | `LAZY` | El default es `EAGER`, pero la review es opcional y sólo se consulta en casos específicos (detalle de compra, reportes de rating). Dejarla `EAGER` forzaría una query extra en toda carga de `Purchase`. |
| `ItemService` → `Service` | `@ManyToOne` | `LAZY` | Si sólo se necesitan la cantidad y el precio del ítem (p.ej. para calcular un total), no hace falta traer el `Service`. Cuando sí se necesita, se pide con `JOIN FETCH`. |
| `Route` → `stops` | `@OneToMany` | `LAZY` (default) | Las paradas pueden ser muchas; en la mayoría de los listados de rutas basta con nombre, precio y km totales. |
| `Route` → `drivers` (`DriverUser`) | `@ManyToMany` | `LAZY` (default) | Lista potencialmente larga y que se accede sólo en casos específicos (asignar/desasignar choferes, reportes operativos). |
| `Route` → `tourGuides` (`TourGuideUser`) | `@ManyToMany` | `LAZY` (default) | Mismo criterio que con `drivers`. |
| `User` → `purchases` | `@OneToMany` | `LAZY` (default) | Un usuario puede tener muchísimas compras; traerlas todas en cada carga de `User` es prohibitivo. |
| `Service` → `supplier` | `@ManyToOne` | `LAZY` | El default es `EAGER`, pero no todos los casos de uso sobre `Service` (listar servicios, buscar por nombre, actualizar precio) necesitan conocer el `Supplier`. |

> [!NOTE]
> Forzar `LAZY` en un `@ManyToOne` o `@OneToOne` en Hibernate requiere habilitar *bytecode enhancement* para que el proxy funcione correctamente en todos los escenarios. Sin esta optimización, Hibernate puede ignorar el `LAZY` y ejecutar la query igualmente (típicamente en `@OneToOne` optional del lado inverso, donde no puede decidir si devolver un proxy o `null` sin consultar la base).

### Ejercicio 24: ¿Cómo podría producirse una `LazyInitializationException` en el modelo? Investigue de qué representa esta excepción y escribir un escenario concreto explicando al menos formas de resolverlo sin cambiar el FetchType a EAGER.

- La `org.hibernate.LazyInitializationException` es la excepción que se lanza cuando se intenta **acceder a una asociación marcada como `LAZY` una vez que el contexto de persistencia (la `Session`) que cargó la entidad ya está cerrado o desvinculado**. Como la colección o el proxy está "vacío" y necesita una `Session` abierta para ir a buscar los datos a la base, Hibernate no puede cumplir el acceso y falla con esta excepción.

- **Escenario concreto en el modelo tours**:
  - En la capa de servicio se abre una transacción, se llama al `PurchaseRepository` y se obtiene una `Purchase` por ID. La transacción finaliza y con ella se cierra la `Session`.
  - Posteriormente, en la capa de presentación (por ejemplo, un controller que serializa la respuesta a JSON), se ejecuta `purchase.getItemServiceList().size()` o `purchase.getRoute().getName()`.
  - Como `itemServiceList` y `route` están marcadas como `LAZY` y la `Session` que cargó la `Purchase` ya está cerrada, Hibernate lanza `LazyInitializationException` al intentar resolver el proxy.

- **Formas de resolverlo sin cambiar el FetchType a `EAGER`**:
  1. **`JOIN FETCH` en la consulta HQL/JPQL**: modificar la query del repositorio para que traiga explícitamente las asociaciones necesarias en la misma consulta. Por ejemplo:
     ```java
     @Query("SELECT p FROM Purchase p " +
            "LEFT JOIN FETCH p.itemServiceList " +
            "LEFT JOIN FETCH p.route " +
            "WHERE p.id = :id")
     Purchase findByIdWithDetails(@Param("id") Long id);
     ```
     De esta forma, la carga de la asociación se decide por caso de uso, no globalmente en el mapeo.
  2. **`@EntityGraph`**: declarar un grafo de carga reutilizable sobre la entidad o sobre la query del repositorio, listando los atributos a cargar de forma ansiosa *sólo para esa operación*. Combina las ventajas de `LAZY` por defecto con la flexibilidad de traer más datos cuando se necesita.
  3. **Ampliar el alcance transaccional (`@Transactional` en el servicio)**: mantener la `Session` abierta mientras dure la operación — envolver el caso de uso en `@Transactional` en la capa de servicio y realizar dentro del método todos los accesos a relaciones LAZY que la respuesta vaya a necesitar. No soluciona accesos posteriores (por ejemplo, en el controller), pero evita la excepción mientras la lógica permanezca dentro del contexto transaccional.
  4. **Inicializar explícitamente con `Hibernate.initialize(...)`**: dentro de la transacción, forzar la carga de la colección o del proxy antes de devolverlo (`Hibernate.initialize(purchase.getItemServiceList())`). Útil en casos puntuales, aunque suele ser preferible `JOIN FETCH`/`@EntityGraph` porque evita queries extra.
  5. **Mapear un DTO en la consulta**: en lugar de devolver la entidad al resto de la aplicación, proyectar directamente a un objeto plano (`new PurchaseDTO(p.id, p.code, ...)`) que contenga sólo los campos que se van a usar. Así nunca se accede a relaciones LAZY fuera del contexto de persistencia.

> [!NOTE]
> Cambiar el `FetchType` a `EAGER` "resuelve" el síntoma pero introduce los problemas descritos en el ejercicio 22 (sobrecarga de memoria, queries innecesarias, acoplamiento del mapeo a un caso de uso). La solución correcta es mantener el default `LAZY` y elegir la estrategia de carga adecuada por caso de uso, usando las herramientas listadas arriba.

## Operaciones en cascada

### Ejercicio 25: ​Enumerar todos los valores de CascadeType y explicar qué operación propaga cada uno sobre las entidades relacionadas.

JPA define el enum `javax.persistence.CascadeType` (en Jakarta EE: `jakarta.persistence.CascadeType`) que enumera las operaciones que pueden propagarse desde una entidad hacia las entidades asociadas. Sus valores son:

- `CascadeType.PERSIST`:
  - Propaga la operación `EntityManager.persist()` (en Hibernate, `Session.persist()`).
  - Al persistir la entidad principal, todas las entidades asociadas que estén en estado **transitorio** se insertan automáticamente en la base de datos.
  - Es la base de la *persistencia por alcance* (ver ejercicio 13): permite que el desarrollador no tenga que llamar manualmente a `persist()` sobre cada objeto del grafo.
- `CascadeType.MERGE`:
  - Propaga la operación `EntityManager.merge()`.
  - Al hacer merge de una entidad **detached** (devolviéndola al contexto de persistencia), también se mergean las entidades asociadas. Útil cuando un grafo entero viaja por la red (por ejemplo, desde un cliente) y vuelve para reconciliarse con la base.
- `CascadeType.REMOVE`:
  - Propaga la operación `EntityManager.remove()`.
  - Al eliminar la entidad principal, las entidades asociadas se eliminan también. Tiene sentido sólo en relaciones de *composición* (relación de "todo-parte", como `Purchase` → `ItemService`), donde la existencia de la parte depende del todo.
- `CascadeType.REFRESH`:
  - Propaga la operación `EntityManager.refresh()`.
  - Al refrescar la entidad principal con su estado actual de la base, las entidades asociadas también se vuelven a leer y se descartan los cambios pendientes en memoria sobre ellas.
- `CascadeType.DETACH`:
  - Propaga la operación `EntityManager.detach()`.
  - Al desvincular la entidad principal del contexto de persistencia (pasándola a estado *detached*), las entidades asociadas también se desvinculan. Útil cuando se quiere "sacar" un grafo entero del `PersistenceContext` para evitar flushes accidentales.
- `CascadeType.ALL`:
  - Atajo que equivale a declarar `{PERSIST, MERGE, REMOVE, REFRESH, DETACH}` simultáneamente.
  - Cómodo pero peligroso: rara vez una asociación justifica propagar **todas** las operaciones (especialmente `REMOVE`). Su uso indiscriminado es una de las causas más frecuentes de bajas en cascada no deseadas.

> [!NOTE]
> Hibernate define adicionalmente sus propios valores en `org.hibernate.annotations.CascadeType` para cubrir operaciones que no son parte del estándar JPA: `SAVE_UPDATE` (propaga `Session.saveOrUpdate()`), `LOCK` (propaga `Session.lock()`) y `REPLICATE` (propaga `Session.replicate()`). Sólo se utilizan cuando se trabaja con la API nativa de Hibernate vía `@Cascade(...)`; con anotaciones JPA puras no aparecen.

> [!NOTE]
> `orphanRemoval = true` (atributo de `@OneToMany` y `@OneToOne`) **no es un `CascadeType`** sino una propiedad independiente. Su comportamiento se discute en el ejercicio 27, pero conviene aclararlo aquí para evitar confundirlo con `CascadeType.REMOVE`: el primero elimina hijos desvinculados de la colección, el segundo propaga la baja del padre a los hijos.

### Ejercicio 26:  ​¿Cuál es el comportamiento por defecto cuando no se define cascade? ¿Cuál es la finalidad general de CASCADE? Proponga un caso del modelo donde definir un CASCADE inadecuado podría traer problemas a la consistencia de la base de datos.

- **Comportamiento por defecto**:
  - Cuando no se define el atributo `cascade` en una anotación de relación (`@OneToMany`, `@ManyToOne`, `@ManyToMany`, `@OneToOne`), JPA asume `cascade = {}` — es decir, **ninguna operación se propaga** desde la entidad principal hacia las asociadas.
  - En la práctica esto significa que si se invoca `persist()`, `remove()`, `merge()`, etc. sobre una entidad y sus asociaciones están en estado transitorio o requieren la operación, el desarrollador debe ejecutarlas manualmente sobre cada una. De lo contrario, según el caso, se obtendrá una `TransientObjectException` (al guardar) o simplemente no se reflejarán los cambios en las asociaciones.

- **Finalidad general de CASCADE**:
  - Permitir que el desarrollador trabaje con **grafos de objetos como una unidad lógica**, sin tener que invocar manualmente cada operación de persistencia sobre cada nodo del grafo.
  - Es la herramienta concreta con la que se implementa la *persistencia por alcance* (ejercicio 13) y se modelan relaciones de **composición** (donde el ciclo de vida de la parte está atado al del todo).
  - Reduce código repetitivo, alinea el modelo de datos con el modelo de dominio (un agregado se persiste/elimina entero) y centraliza la responsabilidad sobre las asociaciones en el mapeo, no en cada caso de uso.

- **Caso de CASCADE inadecuado en el modelo tours**:
  - **Escenario**: declarar `cascade = CascadeType.ALL` (o, lo que es peor, `cascade = CascadeType.REMOVE`) en la relación `Route` → `drivers` (`@ManyToMany`).
  - **Problema**: los `DriverUser` son entidades **independientes** del ciclo de vida de una `Route` — un mismo chofer puede participar en muchas rutas distintas a lo largo del tiempo (ver descripción del dominio en el TP). Si se elimina una `Route` con `CascadeType.REMOVE` activo sobre `drivers`, JPA intentará eliminar también a los choferes asociados.
  - **Consecuencia para la consistencia**:
    - Se borran usuarios `DriverUser` que **siguen siendo válidos en otras rutas**, dejando el sistema con choferes "fantasma" referenciados desde la tabla join `route_driver` de esas otras rutas → falla de integridad referencial o, si las FKs están con `ON DELETE CASCADE`, una **baja en cascada masiva e involuntaria** que limpia las asociaciones de rutas que no tenían nada que ver con la operación original.
    - Se pierden datos de antecedentes profesionales del chofer que el dominio explícitamente pide conservar (atributo `expedient`).
  - El mismo razonamiento aplica a `Route` → `tourGuides` y, en general, a cualquier `@ManyToMany`: en relaciones de asociación (no de composición), `CascadeType.REMOVE` es siempre sospechoso. Por esa razón, en el ejercicio 20 se declaró `cascade = {}` para estas relaciones, y se discute con más detalle en el ejercicio 31.

> [!NOTE]
> El error simétrico también existe: declarar `cascade = {}` (o no declarar nada) en una relación que sí es de composición — como `Purchase` → `itemServiceList` — obliga al desarrollador a persistir cada `ItemService` manualmente y a borrarlos uno por uno antes de poder eliminar la `Purchase`. No rompe la integridad de la base, pero rompe la coherencia del agregado a nivel de dominio y vuelve el código repetitivo y propenso a errores. La regla práctica es: **CASCADE donde haya composición; cascade vacío donde haya asociación**.


### Ejercicio 27: ​¿Cuál es la diferencia entre cascade = REMOVE y orphanRemoval = true? ¿Pueden usarse conjuntamente? Ejemplificar con el par Purchase -> ItemService.

- **Diferencia conceptual**:
  - `cascade = CascadeType.REMOVE`: propaga la operación `remove()` desde la **entidad principal hacia las asociadas**. Sólo se dispara cuando se elimina explícitamente la entidad principal con `entityManager.remove(padre)`. No reacciona a cambios dentro de la colección: si el padre sigue existiendo y simplemente se saca un hijo de la lista, ese hijo **no se borra** de la base, queda como un registro huérfano (con su FK apuntando al padre, pero ya sin referencia desde el lado Java).
  - `orphanRemoval = true`: propiedad disponible en `@OneToMany` y `@OneToOne` que actúa **a nivel de la colección/asociación**, no de la entidad padre. Cuando un hijo es **desvinculado** (`list.remove(item)` o `parent.setChild(null)`), Hibernate detecta que ese hijo se "quedó sin padre" y emite un `DELETE` sobre él en el siguiente flush. También se dispara, transitivamente, cuando se elimina el padre: si los hijos pierden su referencia, igual se borran.
  - Dicho de otra manera: `REMOVE` reacciona a "padre eliminado", `orphanRemoval` reacciona a "hijo desvinculado" (incluido el caso particular en que la desvinculación viene del padre eliminado).

- **¿Pueden usarse conjuntamente?**: sí, y es lo habitual en relaciones de composición. Son **complementarios**, no redundantes:
  - `CascadeType.REMOVE` cubre el caso "se elimina el padre" → propaga el `DELETE` a los hijos.
  - `orphanRemoval = true` cubre el caso "el padre sigue vivo pero un hijo se sacó de la colección" → elimina ese hijo huérfano.
  - Sin `orphanRemoval`, las modificaciones a la lista (sacar un ítem) no se reflejan como bajas; sin `CascadeType.REMOVE`, eliminar el padre falla por integridad referencial (a menos que la FK tenga `ON DELETE CASCADE` a nivel de base, lo que no es lo que se quiere desde el lado JPA).

- **Ejemplo con `Purchase` → `ItemService`** (tal como se mapeó en el ejercicio 20):

  ```java
  @OneToMany(
      mappedBy = "purchase",
      cascade = {CascadeType.PERSIST, CascadeType.REMOVE},
      orphanRemoval = true
  )
  private List<ItemService> itemServiceList = new ArrayList<>();
  ```

  - **Caso 1 — eliminar la compra entera**: `entityManager.remove(purchase)`. `CascadeType.REMOVE` propaga la baja y los `ItemService` asociados se eliminan automáticamente. Sin esta cascada, la operación fallaría porque la FK `purchase_id` en `item_service` quedaría apuntando a una `Purchase` inexistente.
  - **Caso 2 — quitar un ítem de la compra**: `purchase.getItemServiceList().remove(item)`. `CascadeType.REMOVE` **no se dispara** (no se eliminó ningún `Purchase`). Es `orphanRemoval = true` el que detecta que `item` quedó sin padre lógico y emite el `DELETE`. Sin esta opción, el ítem seguiría existiendo en la base como registro huérfano (e incluso podría reaparecer al recargar la entidad desde la base, según el caso).
  - **Caso 3 — reasignar un ítem a otra compra**: con `orphanRemoval = true`, sacar el ítem de `purchase1.itemServiceList` lo marca para eliminación. Si la intención era moverlo a `purchase2.itemServiceList`, se borra antes de poder reasignarlo, lo que normalmente es un *bug*. Es decir, `orphanRemoval` asume que la relación es **de composición estricta**: los hijos no se "transfieren" entre padres. En el modelo tours esto encaja perfectamente — un `ItemService` pertenece a una sola `Purchase` y tiene sentido sólo en su contexto.

> [!NOTE]
> La diferencia más sutil entre ambos: `CascadeType.REMOVE` se dispara una sola vez por borrado del padre. `orphanRemoval` está activo en cada flush de la transacción y observa los cambios sobre la colección de manera continua. Por eso `orphanRemoval` aplica también a la modificación gradual del agregado (ediciones), mientras que `REMOVE` aplica sólo al evento final de baja del padre.

### Ejercicio 28: ​Para la relación Purchase -> ItemService (composición):

#### a)​ ¿Qué tipos de cascade configurarías? Justificar cada uno.

Para esta relación, configuraría `cascade = {CascadeType.PERSIST, CascadeType.REMOVE}`:

- `CascadeType.PERSIST`:
  - **Justificación**: la composición implica que un `ItemService` no tiene sentido fuera de la `Purchase` que lo contiene; nace y se persiste **junto con** ella. Al construir una compra nueva en memoria, el código natural es agregar los ítems a la lista (`purchase.addItem(item, price)`) y persistir la `Purchase` una sola vez. `PERSIST` permite que Hibernate, gracias a la persistencia por alcance (ejercicio 13), recorra la colección y guarde cada `ItemService` automáticamente.
  - Sin esta cascada, intentar persistir una `Purchase` con ítems transitorios fallaría con `TransientObjectException` o forzaría al desarrollador a llamar `persist()` sobre cada ítem manualmente, rompiendo la abstracción del agregado.
- `CascadeType.REMOVE`:
  - **Justificación**: como los ítems pertenecen al ciclo de vida de la compra, eliminar la `Purchase` debe arrastrar la baja de todos sus `ItemService`. Sin esta cascada, el `DELETE` sobre `purchase` fallaría por integridad referencial (la FK `purchase_id` en `item_service` apuntaría a un padre inexistente) o, peor, dejaría registros huérfanos si la FK lo permitiera.
- **¿Por qué no `CascadeType.MERGE`, `DETACH` o `REFRESH`?**:
  - `MERGE`/`DETACH`/`REFRESH` no aportan valor concreto en este modelo: el TP no transfiere grafos detached de un lado a otro de la red, ni necesita refrescar/desvincular agregados completos como unidad. Declararlos sería sobre-permisivo y dificultaría razonar el modelo. En coherencia con el criterio de la cátedra (ejercicio 20: declarar sólo lo que el dominio justifica), se omiten.
- **¿Por qué no `CascadeType.ALL`?**:
  - `ALL` incluye los anteriores que sí necesitamos pero también los que no. No usar `ALL` mantiene visible la decisión y evita propagaciones futuras inadvertidas si la jerarquía cambiara.

#### b)​ ¿Usarías orphanRemoval? ¿Por qué?

Sí, configuraría `orphanRemoval = true`.

- La razón es estrictamente la naturaleza de **composición** de la relación: un `ItemService` que se quita de `purchase.itemServiceList` (por ejemplo, porque el usuario edita la compra y elimina una línea) deja de tener sentido en el dominio. No es un objeto que viva por su cuenta y pueda reasignarse a otra compra.
- `CascadeType.REMOVE` por sí solo **no cubre este caso**: sólo se dispara cuando se elimina la `Purchase` entera. Si el padre sigue vivo y simplemente se modifica la colección, `REMOVE` no actúa y el ítem quedaría como registro huérfano en la base.
- `orphanRemoval = true` cierra ese hueco: Hibernate detecta en cada flush los hijos que fueron desvinculados y emite el `DELETE` correspondiente.
- Coincide además con el comportamiento que asumen los tests provistos del proyecto base (`removePurchaseAndItems` y similares verifican que al eliminar un ítem de la lista, también desaparece de la base).

#### c)​ Describir qué ocurre a nivel de base de datos cuando se elimina un ItemService de la lista de una Purchase y Hibernate realiza el flush.

Asumiendo el mapeo del ejercicio 20 (`cascade = {PERSIST, REMOVE}`, `orphanRemoval = true`) y una operación del estilo:

```java
purchase.getItemServiceList().remove(item);   // dentro de una transacción activa
// ... fin de la transacción → flush
```

A nivel de base de datos, en el flush ocurre lo siguiente:

1. **Detección de la modificación en el `PersistenceContext`**: Hibernate, al hacer flush, compara el estado actual de la entidad gestionada `purchase` contra el snapshot que tenía cargado. Detecta que la colección `itemServiceList` perdió una referencia a un hijo que sí estaba en el snapshot.
2. **Identificación del huérfano por `orphanRemoval`**: como la relación tiene `orphanRemoval = true`, ese `ItemService` desvinculado se marca para eliminación. (Si sólo estuviera `CascadeType.REMOVE` y no `orphanRemoval`, **no pasaría nada** en este punto.)
3. **Emisión del SQL `DELETE`**: Hibernate ejecuta una sentencia `DELETE FROM item_service WHERE id = ?` sobre la fila correspondiente al ítem eliminado. La FK `purchase_id` se resuelve sin conflicto porque el ítem desaparece, no queda colgado.
4. **No se modifica la fila de `Purchase`**: la compra padre sigue existiendo en la tabla `purchase`; sólo cambia el conjunto de filas en `item_service` que la referencian. Tampoco se ejecuta `UPDATE` sobre `item_service` para "desasociar" el ítem (poner `purchase_id` en NULL), porque la columna está declarada `nullable = false` y, conceptualmente, en una composición no existe el estado intermedio "ítem sin compra".
5. **Commit**: al cerrar la transacción, los cambios se hacen permanentes. Si por algún motivo el `DELETE` falla (por ejemplo, una restricción adicional o un trigger), Hibernate hace rollback de toda la unidad de trabajo y la lista vuelve a su estado original en memoria al recargar.

> [!NOTE]
> Si `cascade = REMOVE` estuviera configurado **pero no** `orphanRemoval = true`, la operación `list.remove(item)` no produciría ningún SQL y, al recargar la `Purchase` desde la base, el ítem reaparecería en la colección porque su fila en `item_service` seguiría existiendo. Es un *bug* clásico que confunde a desarrolladores que asumen que `CascadeType.REMOVE` cubre las modificaciones de la colección — y es exactamente la razón por la que `orphanRemoval` se introdujo como concepto separado.

> [!NOTE]
> **Sobre `ItemService.price` como snapshot**: además de `quantity`, en la implementación final el `ItemService` tiene un atributo `price` (`@Column(nullable = false)`) que se setea al agregarse a la `Purchase` con el valor actual de `Service.price`. El `Purchase.totalPrice` se incrementa por `price * quantity` en el helper `addItem(item, price)`. Si `Service.price` cambia después, los `ItemService` ya persistidos preservan el precio que se cobró efectivamente — son información histórica/contable que no debe mutar con cambios posteriores en el catálogo. Esta es otra razón por la que la composición `Purchase` → `ItemService` está bien justificada: el ítem no puede transferirse a otra compra ni recalcularse a partir del catálogo actual.

### Ejercicio 29: ​Para la relación Purchase -> Review:

#### a)​ ¿Qué cascades configurarías?

Configuraría `cascade = CascadeType.REMOVE` en el lado inverso (`Purchase.review`), acompañado de `orphanRemoval = true`. Tal como quedó en el ejercicio 20:

```java
@OneToOne(
    mappedBy = "purchase",
    cascade = CascadeType.REMOVE,
    optional = true,
    orphanRemoval = true
)
private Review review;
```

- `CascadeType.REMOVE`:
  - **Justificación**: la `Review` no es una entidad independiente del dominio; sólo existe en función de una `Purchase`. Eliminar la compra debe arrastrar la baja del review asociado, evitando inconsistencias en la base (review apuntando a una compra inexistente).
- `orphanRemoval = true`:
  - **Justificación**: cubre el caso "se desvincula el review sin borrar la compra" (`purchase.setReview(null)`). Sin esta opción, esa operación no produciría ningún `DELETE` y la fila quedaría huérfana — o, peor, fallaría al intentar guardar la nueva review por la restricción `UNIQUE` que JPA aplica implícitamente sobre `purchase_id` en una `@OneToOne` (ver nota del ejercicio 18).
- **¿Por qué no `CascadeType.PERSIST`?**:
  - Aunque sería razonable, en este modelo el flujo de creación pasa por `purchase.addReview(rating, comment)`, que se ejecuta sobre una `Purchase` ya persistida. Es decir, el review se crea **siempre con su padre ya managed**, no como parte de un grafo nuevo. Al estar el padre managed y la nueva entidad colgada de él, el flush la persistirá igual aunque no haya cascada de `PERSIST`, gracias a la persistencia por alcance estándar de JPA en relaciones bidireccionales con propietario claro. Aun así, agregar `PERSIST` no haría daño y daría más flexibilidad — es una decisión defendible en cualquiera de los dos sentidos; aquí se elige el set mínimo según el criterio de la cátedra.
- **¿Por qué no `CascadeType.ALL`?**:
  - Mismo motivo que en el ejercicio 28: `ALL` arrastra `MERGE`, `DETACH`, `REFRESH`, que no se justifican por el dominio del TP, y oculta la decisión.

#### b)​ Si se elimina una Purchase, ¿debería eliminarse también su Review? Justificar desde el modelo de negocio.

Sí, debería eliminarse también su `Review`. Justificación desde el dominio:

- El `Review` **no tiene existencia propia fuera de la compra que lo originó**. Conceptualmente es un *atributo enriquecido* de la compra: representa la opinión del usuario sobre **esa** experiencia concreta. Si la compra desaparece (cancelación administrativa, baja por requerimiento legal, depuración de datos antiguos, etc.), no queda nada a lo que la opinión refiera — un review sin compra es ruido en el sistema, no información.
- El propio modelo de datos lo refleja: la FK `purchase_id` en `review` está declarada `nullable = false` (ejercicio 20). Es decir, **no existe** el estado intermedio "review sin compra". Si se elimina la `Purchase` sin propagar la baja al `Review`, se viola la integridad referencial.
- Desde la perspectiva del negocio descripto en el TP, los reviews se utilizan para *promociones del emprendimiento* y para *captar más público*. Mantener reviews huérfanos (sin compra trazable) los vuelve inutilizables para esos fines, ya que no se puede vincular la opinión al recorrido, al usuario ni a la fecha de la experiencia.
- Adicionalmente, conservar reviews después de eliminar la compra puede ser problemático en términos de **privacidad/regulatorios**: si la baja de la compra responde a un derecho de supresión del usuario (p.ej. GDPR/Ley de Datos Personales), dejar el review con su `rating` y `comment` sin el contexto borrado puede convertirse en una *re-identificación* indirecta. Borrarlo en cascada es la opción consistente con la baja del usuario.

> [!NOTE]
> Es importante diferenciar este caso del de `Purchase` → `Route`: la `Route` también está referenciada por compras, pero **es independiente** de cualquier compra particular (existe antes y después de que se vendan recorridos sobre ella). Por eso allí no se configura `CascadeType.REMOVE`. La regla a aplicar es: la cascada de baja sigue al ciclo de vida del dominio, no a la dirección de la FK.

### Ejercicio 30: ​Para la relación Supplier -> Service:

#### a)​ ¿Qué cascades tienen sentido?

A diferencia de los ejercicios 28 y 29, esta no es una relación de composición sino de **asociación pura**: un `Service` referencia obligatoriamente a un `Supplier`, pero el `Supplier` y los `Service` tienen ciclos de vida independientes y, sobre todo, los `Service` están a su vez **referenciados desde fuera** del agregado del proveedor (los `ItemService` de cada `Purchase`). En este escenario, ningún `CascadeType` se justifica plenamente; pueden discutirse por separado:

- `CascadeType.PERSIST`:
  - Caso de uso típico: dar de alta un `Supplier` con su catálogo inicial de `Service` en una sola operación. Si el flujo de la aplicación crea ambos en el mismo momento, agregarlo evita persistir cada `Service` manualmente.
  - Si en cambio los `Service` se dan de alta uno por uno sobre proveedores ya existentes, no aporta nada y se descarta.
  - **Decisión defendible** según el flujo de creación. En este TP no hay un caso de uso documentado de "alta masiva del catálogo de un proveedor", por lo que se omite.
- `CascadeType.REMOVE`:
  - **Peligroso** y se descarta. Razón: borrar un `Supplier` arrastraría todos sus `Service`, y cada `Service` está referenciado desde `ItemService` con FK `nullable = false`. La cascada fallaría por integridad referencial o forzaría a Hibernate a borrar también los `ItemService` (lo que a su vez exigiría que esa cadena estuviera permitida, cosa que no se quiere — ver punto b).
  - Más profundo: **un `Service` ya vendido representa información histórica de compras pasadas**. Borrarlo en cascada implicaría mutilar el historial de la aplicación, que es información económica/contable y de relación con el cliente.
- `CascadeType.MERGE`, `DETACH`, `REFRESH`:
  - No se justifican por el dominio del TP (mismo razonamiento que en 28/29).
- `CascadeType.ALL`:
  - Descartado por incluir `REMOVE`.

**Configuración elegida**: `cascade = {}`, tal como se dejó en el ejercicio 20. Mantiene cada `Service` como una entidad gestionada explícitamente por su propio caso de uso, sin ataduras al ciclo de vida del proveedor.

#### b)​ Si se elimina un Supplier, ¿qué debería ocurrir con sus Service? ¿Y con las Purchase que los contienen a través de ItemService?

- **Qué debería ocurrir con sus `Service`**:
  - **No deberían eliminarse en cascada**. Un `Service` ya vendido (es decir, referenciado por algún `ItemService`) representa una transacción histórica que la aplicación necesita preservar para trazabilidad, contabilidad y soporte al cliente.
  - La estrategia correcta es **bloquear la baja del `Supplier`** mientras existan `Service` activos referenciados, o bien implementar una **baja lógica** (un `boolean active` o similar) que retire al proveedor del catálogo sin destruir su historia. La descripción del dominio en el TP no entra en este detalle, pero la cátedra deja explícito en el ejercicio 31 que las cascadas peligrosas (especialmente en `@ManyToMany` y `@OneToMany` no compositivos) no deben configurarse a la ligera.
  - Si por algún motivo se decidiera permitir la baja física del `Supplier`, el procedimiento debería ser: primero verificar/limpiar las dependencias en la capa de servicio (mover los `Service` a otro proveedor, o asegurarse de que ninguno está vendido), y recién después eliminar el `Supplier`. Eso es responsabilidad del **caso de uso**, no del mapeo.
- **Qué debería ocurrir con las `Purchase` que los contienen a través de `ItemService`**:
  - **Nada**. Las `Purchase` son hechos económicos cerrados: representan una operación comercial que ya ocurrió, fue cobrada y eventualmente abre derechos del usuario (refund, comprobante, factura, derivados contables). Que el proveedor del servicio adquirido haya dejado de operar **no afecta la validez de la compra**.
  - Tocar las compras al dar de baja al proveedor confundiría dos eventos que no tienen relación causal: la baja del proveedor (administrativa, presente) y la compra (transacción histórica). Sería un error de modelado severo y, en muchos contextos, también un problema regulatorio/contable.
  - Por eso el `ItemService` referencia al `Service`, y no al `Supplier`: la compra preserva exactamente lo que se vendió, independientemente de qué pase con quien lo proveyó.

> [!NOTE]
> Este ejercicio refuerza la regla del 26: **CASCADE donde haya composición; cascade vacío donde haya asociación**. `Supplier` → `Service` es asociación, no composición — son entidades autónomas que comparten una relación, pero ninguna depende de la otra para existir. La integridad ante la baja del `Supplier` se gestiona en la capa de servicio (validando precondiciones o aplicando baja lógica), no en el mapeo.

### Ejercicio 31: ​¿Por que CascadeType.REMOVE en una relación @ManyToMany (por ejemplo Route <-> DriverUser) suele ser peligroso? Describir un escenario donde su uso cause pérdida no deseada de datos.

- **Por qué es peligroso**:
  - Una relación `@ManyToMany` modela una **asociación entre entidades autónomas**, no una composición. Cada extremo existe independientemente del otro: una `Route` puede operar con distintos choferes a lo largo del tiempo, y un `DriverUser` puede participar en varias rutas distintas.
  - `CascadeType.REMOVE` propaga el `DELETE` desde la entidad que se borra **hacia el otro lado de la relación**. Cuando ese otro lado es una entidad compartida con muchos otros agregados, la cascada termina destruyendo datos que **no pertenecen** al ámbito de la operación que se quería realizar.
  - A diferencia de un `@OneToMany` compositivo (donde los hijos sólo viven en función del padre), aquí el "hijo" tiene su propia identidad, su propia historia, y suele estar referenciado desde otras tablas (otras rutas, registros de actividad, antecedentes laborales, etc.). Borrarlo en cascada produce un efecto dominó imposible de prever desde el lado en que se origina la operación.
  - Como agravante, si la cascada se declara **en ambos lados** (`Route` con `cascade = REMOVE` sobre `drivers` y `DriverUser` con `cascade = REMOVE` sobre `routes`), una sola baja puede dispararse recursivamente y arrastrar prácticamente toda la red de rutas y choferes conectados transitivamente.

- **Escenario concreto en el modelo tours**:
  - Supongamos que se configura `cascade = CascadeType.REMOVE` en `Route.drivers` (`@ManyToMany` con `DriverUser`).
  - El sistema tiene tres rutas activas:
    - `Route A` ("Tour tradicional de Bs. As.") con choferes `D1`, `D2`, `D3`.
    - `Route B` ("Tour del Delta") con choferes `D2`, `D4`.
    - `Route C` ("Recorrido nocturno") con choferes `D1`, `D5`.
  - Por una decisión administrativa, se decide retirar la `Route A` del catálogo y se ejecuta `routeRepository.delete(routeA)`.
  - **Lo que el desarrollador esperaba**: que se elimine la fila de `route` correspondiente a `A` y las filas de la tabla join `route_driver` que la vinculaban a `D1`, `D2` y `D3`. Los choferes deberían seguir intactos porque `D1` aún trabaja en `Route C`, `D2` en `Route B`, y `D3` puede ser reasignado en el futuro.
  - **Lo que ocurre con `CascadeType.REMOVE` activo**: Hibernate, al ejecutar el flush, propaga el `DELETE` a `D1`, `D2` y `D3` (todos los `DriverUser` referenciados desde la colección `drivers` de `Route A`).
    - `D1` desaparece de la tabla `user`/`driver_user`, pero `Route C` sigue teniendo en su tabla join `route_driver` una fila `(C, D1)`. Eso o **rompe la integridad referencial** (si la FK no permite huérfanos) y la transacción aborta dejando estado inconsistente, o **se borra también la fila de `route_driver` de `Route C`** si la FK está con `ON DELETE CASCADE`, despoblando silenciosamente la asignación de choferes de `Route C`.
    - `D2` desaparece, dejando a `Route B` sin uno de sus choferes asignados.
    - Se pierden, además, los **antecedentes laborales** (`expedient`) de los tres choferes — datos que la descripción del dominio del TP pide explícitamente conservar.
  - El usuario administrativo creyó que estaba dando de baja una ruta y terminó **rompiendo la operatoria diaria de otras dos rutas**, eliminando información histórica de personal y, según la configuración de las FKs, dejando a la base en un estado inconsistente o con datos silenciosamente perdidos.
  - El mismo razonamiento se replica simétricamente: si se diera de baja un chofer con `cascade = REMOVE` activo, se borrarían las rutas en las que participa (junto con sus stops, sus tour guides asociados, sus compras y reviews vía `Purchase`), arrastrando un grafo masivo y completamente involuntario.

- **Conclusión y solución**:
  - Por estas razones, en el ejercicio 20 se eligió `cascade = {}` para `Route` ↔ `DriverUser` y `Route` ↔ `TourGuideUser`. La gestión de las asociaciones (`addDriver`, `removeDriver`, etc.) se hace **modificando la colección**, lo que actualiza la tabla join sin tocar las entidades vinculadas.
  - Si en algún momento es necesario eliminar una `Route` que tiene choferes asignados, el procedimiento correcto es: limpiar la colección desde el lado dueño (`route.getDrivers().clear()` para que Hibernate borre las filas de `route_driver`), y recién después eliminar la `Route`. Esto se resuelve a nivel de **caso de uso en la capa de servicio**, no a nivel de mapeo.

> [!NOTE]
> En `@ManyToMany`, lo único que conviene "limpiar" en cascada son las **filas de la tabla join**, no las entidades del otro lado. Esa limpieza se logra automáticamente al eliminar la entidad dueña (la que tiene `@JoinTable`): Hibernate emite los `DELETE` correspondientes sobre la tabla intermedia sin necesidad de `CascadeType.REMOVE`. Por eso, en la inmensa mayoría de las relaciones muchos-a-muchos, **`cascade = {}` es lo correcto**.

### Ejercicio 32: ​Implemente las operaciones en cascada adecuada para todas las relaciones del modelo tours

Consolidando las decisiones tomadas en los ejercicios 28–31, la configuración de cascadas para todas las relaciones queda como sigue. La regla general es la enunciada en el ejercicio 26: **CASCADE donde haya composición; cascade vacío donde haya asociación**.

| Relación | Tipo | `cascade` | `orphanRemoval` | Justificación |
| --- | --- | --- | --- | --- |
| `Purchase` → `itemServiceList` | `@OneToMany` | `{PERSIST, REMOVE}` | `true` | Composición. `PERSIST` permite construir la compra como agregado; `REMOVE` arrastra los ítems al borrar la compra; `orphanRemoval` cubre las ediciones de la lista (ejercicio 28). |
| `Purchase` → `Review` | `@OneToOne` (inverso) | `{REMOVE}` | `true` | Composición funcional: el `Review` no tiene sentido sin la compra (ejercicio 29). |
| `ItemService` → `Purchase` | `@ManyToOne` (lado dueño) | `{}` | — | Lado dueño de la composición. La propagación se maneja desde `Purchase`, nunca desde el ítem. |
| `ItemService` → `Service` | `@ManyToOne` | `{}` | — | Asociación. El `Service` es independiente y compartido con otros ítems históricos. |
| `Service` → `Supplier` | `@ManyToOne` | `{}` | — | Asociación. Ver ejercicio 30. |
| `Supplier` → `services` | `@OneToMany` (inverso) | `{}` | — | Asociación: `Service` no es parte del agregado `Supplier`. Si se eliminara un `Supplier` sin `Service` activos, la baja se gestiona en el caso de uso (ejercicio 30). |
| `Service` → `itemServiceList` | `@OneToMany` (inverso) | `{}` | — | Asociación. Los `ItemService` pertenecen al agregado `Purchase`, no a `Service`. |
| `Purchase` → `User` | `@ManyToOne` | `{}` | — | Asociación. El `User` es independiente y vive más allá de cualquier compra particular. |
| `Purchase` → `Route` | `@ManyToOne` | `{}` | — | Asociación. La `Route` existe antes y después de cualquier compra. |
| `User` → `purchases` | `@OneToMany` (inverso) | `{}` | — | Asociación. Las `Purchase` son hechos económicos que sobreviven a la baja del usuario y se gestionan vía baja lógica si correspondiera. |
| `Route` ↔ `DriverUser` | `@ManyToMany` | `{}` | — | Asociación. `REMOVE` aquí causaría pérdida masiva de datos compartidos con otras rutas (ejercicio 31). |
| `Route` ↔ `TourGuideUser` | `@ManyToMany` | `{}` | — | Mismo razonamiento que `Route` ↔ `DriverUser`. |
| `Route` ↔ `Stop` | `@ManyToMany` | `{}` | — | Asociación. Las paradas existen de forma independiente y pueden ser reutilizadas por otras rutas. |

Concretamente, los fragmentos relevantes del mapeo (ya consolidados en el ejercicio 20 y reforzados aquí) quedan así:

```java
// Purchase
@OneToMany(
    mappedBy = "purchase",
    cascade = {CascadeType.PERSIST, CascadeType.REMOVE},
    orphanRemoval = true
)
private List<ItemService> itemServiceList = new ArrayList<>();

@OneToOne(
    mappedBy = "purchase",
    cascade = CascadeType.REMOVE,
    optional = true,
    orphanRemoval = true
)
private Review review;

@ManyToOne(cascade = {})
@JoinColumn(name = "user_id", nullable = false)
private User user;

@ManyToOne(cascade = {})
@JoinColumn(name = "route_id", nullable = false)
private Route route;

// ItemService
@ManyToOne(cascade = {})
@JoinColumn(name = "purchase_id", nullable = false)
private Purchase purchase;

@ManyToOne(cascade = {})
@JoinColumn(name = "service_id", nullable = false)
private Service service;

// Service
@ManyToOne(cascade = {})
@JoinColumn(name = "supplier_id", nullable = false)
private Supplier supplier;

@OneToMany(mappedBy = "service", cascade = {})
private List<ItemService> itemServiceList = new ArrayList<>();

// Supplier
@OneToMany(mappedBy = "supplier", cascade = {})
private List<Service> services = new ArrayList<>();

// Route (lado dueño de las @ManyToMany, con @JoinTable definido en el ej. 20)
@ManyToMany(cascade = {})
@JoinTable(name = "route_stop", /* ... */)
private List<Stop> stops = new ArrayList<>();

@ManyToMany(cascade = {})
@JoinTable(name = "route_driver", /* ... */)
private List<DriverUser> drivers = new ArrayList<>();

@ManyToMany(cascade = {})
@JoinTable(name = "route_tour_guide", /* ... */)
private List<TourGuideUser> tourGuides = new ArrayList<>();

// User
@OneToMany(mappedBy = "user", cascade = {})
private List<Purchase> purchases = new ArrayList<>();

// Review (lado dueño, OneToOne)
@OneToOne(cascade = {})
@JoinColumn(name = "purchase_id", nullable = false)
private Purchase purchase;

// DriverUser, TourGuideUser (lado inverso de las @ManyToMany con Route)
@ManyToMany(mappedBy = "drivers", cascade = {})       // o "tourGuides"
private List<Route> routes = new ArrayList<>();
```

> [!NOTE]
> Las cascadas declaradas explícitamente como `cascade = {}` no son redundantes en el sentido del default JPA (que también es vacío), pero **sí son una decisión documentada**: dejan visible en el código que se evaluó qué cascada correspondía y se resolvió no propagar nada. Esto sigue el criterio de la cátedra (ejercicio 20) de declarar la intención antes que confiar en defaults. Además, si después el estándar cambiara su default, el código seguiría siendo correcto.

> [!NOTE]
> Las dos únicas relaciones con cascadas activas en todo el modelo son las que parten de `Purchase` (`itemServiceList` y `review`), porque son **los únicos casos de composición real** del diagrama. Todo el resto son asociaciones — usuarios, rutas, paradas, choferes, guías, servicios y proveedores son entidades autónomas — y por lo tanto no llevan cascada de baja, ni `orphanRemoval`. La integridad ante eliminaciones de esas entidades se resuelve en la capa de servicio, no en el mapeo (ejercicios 30 y 31).

## Jerarquía de herencia: User, DriverUser y TourGuideUser

### Ejercicio 33: ​Describir las tres estrategias de mapeo de herencia. Para cada una indicar qué tablas se crean, si aparece columna discriminadora y cómo resuelve Hibernate una consulta polimórfica. Completar la tabla:

JPA define tres estrategias de mapeo de jerarquías de herencia, configurables con la anotación `@Inheritance(strategy = ...)` sobre la clase base:

- **`SINGLE_TABLE`** (default si no se especifica nada):
  - **Tablas creadas**: una **única tabla** que aglutina los atributos de la clase base y de **todas** las subclases.
  - **Columna discriminadora**: sí, obligatoria. Por defecto `DTYPE` (varchar) o configurable con `@DiscriminatorColumn`. Cada subclase declara su valor con `@DiscriminatorValue`.
  - **Consulta polimórfica**: una sola sentencia `SELECT * FROM user` (sin `JOIN`s); Hibernate filtra por la columna discriminadora si se quiere acotar a una subclase concreta.
- **`JOINED`** (estrategia "tabla por subclase normalizada"):
  - **Tablas creadas**: una tabla para la clase base con sus atributos comunes, y una tabla por **cada subclase** con sólo los atributos propios de esa subclase. Las tablas hijas tienen la PK como FK hacia la tabla base.
  - **Columna discriminadora**: opcional pero recomendable; Hibernate puede inferir el tipo a partir de la presencia de filas en las tablas hijas, pero declararla con `@DiscriminatorColumn` simplifica las consultas.
  - **Consulta polimórfica**: requiere un `JOIN` (típicamente `LEFT OUTER JOIN`) entre la tabla base y cada tabla de subclase para reconstruir cada entidad. Hibernate genera la query automáticamente.
- **`TABLE_PER_CLASS`**:
  - **Tablas creadas**: una tabla por **cada subclase concreta**, **independiente y completa** (incluyendo los atributos de la clase base, duplicados en cada tabla hija). La clase base sólo se mapea si es concreta; si es abstracta, no genera tabla.
  - **Columna discriminadora**: no se usa (cada tabla representa exactamente una subclase).
  - **Consulta polimórfica**: requiere un `UNION ALL` entre todas las tablas de las subclases para reconstruir el conjunto completo. Es la estrategia más costosa en consultas polimórficas.

Aplicado al modelo del TP (`User` como clase base, `DriverUser` con `expedient` y `TourGuideUser` con `education` como subclases):

| Aspecto | `SINGLE_TABLE` | `JOINED` | `TABLE_PER_CLASS` |
| --- | --- | --- | --- |
| Tablas creadas en la BD | Una sola: `user` con todas las columnas (`id`, `username`, …, `expedient`, `education`, `dtype`). | Tres: `user` (atributos comunes) + `driver_user` (`id` FK, `expedient`) + `tour_guide_user` (`id` FK, `education`). | Dos (si `User` es abstracta) o tres (si es concreta): `driver_user` y `tour_guide_user` con **todas** las columnas (`id`, `username`, …, atributos propios). Sin tabla para `User` si se la deja abstracta. |
| Columna discriminadora | Sí, obligatoria. Por defecto `DTYPE`; se configura con `@DiscriminatorColumn` y cada subclase con `@DiscriminatorValue`. | Opcional. Hibernate puede deducir el tipo por las filas en las tablas hijas, pero conviene declararla. | No aplica. La identidad de la subclase está implícita en la tabla en la que vive la fila. |
| NULLs en columnas de subclases | **Sí, inevitablemente**. Las columnas `expedient` y `education` deben declararse `nullable = true` aunque la lógica de negocio las requiera, porque las filas correspondientes a la otra subclase las dejan vacías. | **No**. Cada subclase guarda sus atributos en su propia tabla, donde pueden declararse `nullable = false` sin problema. | **No**. Cada tabla es completa para su subclase y no comparte filas con otra. |
| Consulta polimórfica `from User` | `SELECT * FROM user` — una sola query, sin `JOIN`s. La más rápida. | `SELECT … FROM user u LEFT JOIN driver_user d ON d.id = u.id LEFT JOIN tour_guide_user t ON t.id = u.id`. Más cara que `SINGLE_TABLE`. | `SELECT … FROM (SELECT … FROM driver_user UNION ALL SELECT … FROM tour_guide_user) sub`. La más cara. |
| Cargar un `DriverUser` por ID | `SELECT * FROM user WHERE id = ? AND dtype = 'DriverUser'`. | `SELECT … FROM user u INNER JOIN driver_user d ON d.id = u.id WHERE u.id = ?`. Necesita un `JOIN`. | `SELECT * FROM driver_user WHERE id = ?`. Una sola tabla, sin `JOIN`. La más rápida para este caso. |
| Integridad referencial (FK posibles) | Limitada. Como toda fila vive en `user`, una FK de otra tabla apuntando específicamente a "un `DriverUser`" no puede expresarse a nivel relacional; se necesita una restricción CHECK que combine `dtype` con la FK, o validación en aplicación. | **Buena**. Cada subclase tiene su propia tabla; otras tablas pueden definir FK hacia `driver_user` o `tour_guide_user` directamente. La FK de cada subclase contra `user` garantiza la herencia. | Pobre/ambigua. No hay tabla `user` (si es abstracta), por lo que FKs polimórficas a "un `User` cualquiera" no son representables en el esquema. |
| Performance en lecturas simples (de una entidad) | Excelente: una sola tabla, sin `JOIN`s ni `UNION`s. | Costo extra: cada carga de subclase requiere `JOIN` con la tabla base. | Excelente para subclases concretas (una sola tabla); pero costosa para consultas polimórficas (`UNION ALL`). |
| Qué implica agregar una nueva subclase | Agregar **columnas nuevas** a la tabla `user` (todas `nullable = true`) y un nuevo `@DiscriminatorValue`. Migración intrusiva sobre una tabla potencialmente grande. | Agregar **una nueva tabla** para la subclase con FK a `user` y columnas propias. La tabla base no se toca. La más amigable a la evolución. | Agregar una **nueva tabla independiente** con todas las columnas (incluidos los atributos de la clase base, duplicados). Las consultas polimórficas existentes deben actualizarse para incluir el nuevo `UNION`. |

> [!NOTE]
> Resumen de trade-offs:
> - `SINGLE_TABLE` favorece **performance** y simplicidad pero **sacrifica integridad** (NULLs forzados, FKs por subclase imposibles a nivel BD).
> - `JOINED` es la más **normalizada e íntegra**, paga el costo de los `JOIN`s y es la más amigable a evoluciones del modelo.
> - `TABLE_PER_CLASS` rinde bien para consultas no polimórficas pero degrada las polimórficas y rompe la unicidad del ID a nivel global (cada tabla genera IDs por su cuenta, complicando estrategias `IDENTITY`).
> Para este TP, donde `User` es referenciada por `Purchase` y `Route` (vía `DriverUser`/`TourGuideUser`), la decisión razonable suele ser `SINGLE_TABLE` por simplicidad y performance, o `JOINED` si se prioriza limpieza del esquema. La cátedra pide implementar `SINGLE_TABLE` en el ejercicio 34, `JOINED` en el 35 y `TABLE_PER_CLASS` en el 36, para comparar.

### Ejercicio 34: ​Implementar el mapeo de la jerarquía User/DriverUser/TourGuideUser usando la estrategia SINGLE_TABLE. Especificar @Inheritance, @DiscriminatorColumn y @DiscriminatorValue para cada clase. Incluir todos los atributos.

El mapeo concreto sobre las tres clases queda así:

```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "user_type", discriminatorType = DiscriminatorType.STRING)
public class User {
    // atributos comunes: id, username, password, name, email, birthdate, phoneNumber, active
}

@Entity
@DiscriminatorValue("DRIVER")
public class DriverUser extends User {
    private String expedient;
}

@Entity
@DiscriminatorValue("TOUR_GUIDE")
public class TourGuideUser extends User {
    private String education;
}
```

#### a)​ Ejecutar los tests provistos y analizar el DDL generado: ¿cuántas tablas aparecen? ¿Qué columnas tiene la tabla? ¿Dónde están los atributos expedient y education?

Con `@Inheritance(strategy = InheritanceType.SINGLE_TABLE)`, Hibernate genera una sola tabla (`User`) que aloja a las tres entidades. El DDL es similar a:

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

- **¿Cuántas tablas?** Una sola: `User`.
- **¿Qué columnas tiene?** Las de `User` (atributos comunes) + la columna discriminadora `user_type` + las columnas de **todas** las subclases (`expedient` y `education`).
- **¿Dónde están `expedient` y `education`?** Aplanadas en la misma tabla `User`, como columnas opcionales (nullables). No existen tablas separadas `DriverUser` ni `TourGuideUser`.

#### b)​ ¿Qué ocurre con las columnas de subclase cuando se inserta un TourGuideUser? ¿Y cuando se inserta un DriverUser?

- Al insertar un `TourGuideUser`:
  - `user_type = 'TOUR_GUIDE'`.
  - `education` recibe el valor cargado.
  - `expedient` queda en `NULL` (la columna existe en la tabla pero el `TourGuideUser` no tiene ese atributo).
- Al insertar un `DriverUser`:
  - Mismo `INSERT` sobre la tabla `User`.
  - `user_type = 'DRIVER'`.
  - `expedient` recibe el valor cargado.
  - `education` queda en `NULL`.

> [!NOTE]
> Por esta razón, JPA/Hibernate no permite declarar `nullable = false` (`NOT NULL`) sobre las columnas exclusivas de subclase: el DDL fallaría o las inserciones de la otra subclase violarían la restricción. La validación de obligatoriedad debe hacerse a nivel **aplicación** (por ejemplo, exigiendo el atributo en el constructor de `DriverUser`/`TourGuideUser`).

#### c)​ ¿Cuáles son las ventajas y desventajas de esta estrategia para este modelo concreto?

- **Ventajas**:
  - **Lecturas y polimorfismo muy rápidos**: consultar `from User` o `from DriverUser` no requiere `JOIN` — sólo un filtro `WHERE user_type = ...`. Útil porque en `Route` hay relaciones `@ManyToMany` tanto a `DriverUser` como a `TourGuideUser` (`driverList`, `tourGuideList`), y este esquema las resuelve sin joins extra.
  - **Inserciones simples**: un único `INSERT` por usuario, sin coordinación entre tablas.
  - **Claves foráneas estables**: cualquier FK hacia `User` (por ejemplo desde `Purchase.user_id`) apunta a una sola tabla, sea el usuario común, conductor o guía.
  - **DDL más simple** y menor cantidad de objetos en la base.
- **Desventajas**:
  - **Sin `NOT NULL` sobre atributos de subclase**: no se pueden usar restricciones `NOT NULL` sobre `expedient` ni `education` aunque conceptualmente sean obligatorios para sus subclases — se pierde integridad declarativa en la BD.
  - **Tabla "ancha" con muchas columnas en NULL**: si las subclases crecen con más atributos, la tabla acumula columnas que la mayoría de las filas dejan en `NULL` (desperdicio de espacio y lecturas más anchas).
  - **Acoplamiento del esquema a la jerarquía**: agregar un nuevo tipo de usuario implica agregar columnas a la misma tabla, afectando a todas las filas existentes.
  - **Mezcla semántica**: filas de tipos distintos conviven, lo que dificulta poner constraints específicos de subclase (CHECKs, índices únicos parciales, etc.) salvo con sintaxis específica del motor.

Para este modelo, donde las subclases agregan pocos atributos (`expedient`, `education`) y la jerarquía es estable, `SINGLE_TABLE` es una elección razonable: gana en performance y simplicidad, y el costo (NULLs y pérdida del `NOT NULL`) es acotado.

### Ejercicio 35: ​Reimplementar el mapeo de la misma jerarquía usando la estrategia JOINED.

El cambio frente al ejercicio 34 es mínimo a nivel código: se reemplaza la estrategia y se omite la columna discriminadora (es opcional en `JOINED` y Hibernate puede inferir el tipo a partir de la presencia de la fila en la tabla de la subclase):

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

Nótese que ahora sí podemos declarar `nullable = false` sobre `expedient` y `education`, porque cada uno vive en su propia tabla y no hay filas de otras subclases que dejen la columna en NULL (ver nota del PDF al final de la sección 2.5).

#### a)​ Ejecutar los tests y analizar el DDL: ¿cuantas tablas aparecen? ¿Qué FK existe entre ellas?

Con `@Inheritance(strategy = InheritanceType.JOINED)`, Hibernate genera **tres tablas**: una para la clase base con los atributos comunes, y una por cada subclase con sólo sus atributos propios:

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

- **Cantidad de tablas**: tres — `User`, `DriverUser`, `TourGuideUser`.
- **FK entre ellas**: cada tabla de subclase tiene una **FK desde su PK hacia `User(id)`**. Es decir, la clave primaria de `DriverUser` y `TourGuideUser` no es autoincremental propia: reusa el `id` asignado en `User` y lo "extiende" con los atributos específicos de la subclase.
- No hay columna discriminadora explícita: la pertenencia a una subclase queda determinada por la presencia de la fila en `DriverUser` o `TourGuideUser`.

#### b)​ Comparar el SQL generado por Hibernate al cargar un DriverUser en JOINED vs. en SINGLE_TABLE. ¿Cómo difiere?

- En **`SINGLE_TABLE`**:
  ```sql
  SELECT id, username, password, name, email, birthdate, phoneNumber, active, expedient
    FROM User
   WHERE id = ?
     AND user_type = 'DRIVER';
  ```
  Una sola query a una sola tabla, filtrando por la columna discriminadora. No hay `JOIN`s.
- En **`JOINED`**:
  ```sql
  SELECT u.id, u.username, u.password, u.name, u.email, u.birthdate, u.phoneNumber, u.active, d.expedient
    FROM User u
   INNER JOIN DriverUser d ON d.id = u.id
   WHERE u.id = ?;
  ```
  Hibernate hace un `INNER JOIN` entre la tabla base y la de la subclase para reconstruir la entidad. Si no se conoce el tipo concreto de antemano (consulta polimórfica `from User`), suma `LEFT OUTER JOIN` también con `TourGuideUser` y deduce el tipo a partir de cuál de los dos joins encontró fila.

**Diferencia concreta**: `JOINED` paga un `JOIN` extra en cada lectura de subclase, mientras que `SINGLE_TABLE` lee siempre de una sola tabla. Para cargas frecuentes y polimorfismo intensivo, `SINGLE_TABLE` es más rápida; `JOINED` es más cara en lectura pero más limpia en almacenamiento e integridad.

#### c)​ ¿Cuáles son las ventajas y desventajas de JOINED para este modelo?

- **Ventajas**:
  - **Esquema normalizado**: cada tabla guarda sólo lo que le corresponde. No hay columnas "muertas" en NULL.
  - **`NOT NULL` declarativo sobre atributos de subclase**: `expedient` y `education` pueden declararse `nullable = false` a nivel BD, alineando la integridad declarativa con la regla de negocio (la cátedra lo señala explícitamente en el PDF: *"Con JOINED, esa restricción puede aplicarse en la tabla de la subclase"*).
  - **FKs específicas por subclase**: si en el futuro otra entidad necesitara apuntar específicamente a un `DriverUser` (por ejemplo, un registro de "horas trabajadas por chofer"), puede declararse una FK contra `DriverUser(id)` con garantía de tipo a nivel BD.
  - **Evolutividad**: agregar una nueva subclase implica crear una nueva tabla; **no se modifica `User`** ni las tablas existentes.
- **Desventajas**:
  - **Lecturas más caras**: cada carga de subclase requiere `JOIN` con la tabla base; las consultas polimórficas (`from User`) requieren `LEFT JOIN` con todas las subclases.
  - **Inserciones más caras**: dar de alta un `DriverUser` implica **dos `INSERT`** (uno en `User` y otro en `DriverUser`), coordinados por Hibernate dentro de la misma transacción.
  - **Borrados más caros**: eliminar un `DriverUser` requiere borrar primero la fila de la subclase y después la de la base (Hibernate lo hace automáticamente, pero son dos `DELETE`).
  - **`@ManyToMany` con subclases**: en este modelo `Route` tiene `@ManyToMany` separadas hacia `DriverUser` y `TourGuideUser`. La FK de la tabla join apunta a la tabla específica de la subclase (`DriverUser` o `TourGuideUser`), lo cual es semánticamente más fuerte que `SINGLE_TABLE` (donde apuntaría a `User` y la subclase quedaría como invariante implícita), pero implica que si el día de mañana un mismo `User` debe poder ser chofer y guía simultáneamente, esta estructura no lo permite (un `User` sólo puede tener fila en una de las dos tablas hijas).

Para este TP, `JOINED` es la elección **más íntegra** y prolija a nivel BD: respeta las restricciones de obligatoriedad de los atributos de subclase y normaliza el esquema. El precio que paga (joins extra y dobles `INSERT`/`DELETE`) es modesto en el orden de magnitud del proyecto y suele compensarse con la claridad estructural.

### Ejercicio 36: ​Realice el mismo proceso ahora con la estrategia TABLE_PER_CLASS. Indique cuál le parece la mejor estrategia para este modelo concreto y justifique su elección.

El mapeo con `TABLE_PER_CLASS` queda así:

```java
@Entity
@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)
public abstract class User {
    @Id
    @GeneratedValue(strategy = GenerationType.TABLE)   // IDENTITY no es viable acá
    private Long id;
    // resto de los atributos comunes
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

Hay que destacar dos detalles propios de esta estrategia:

- `User` se marca **abstracta**: si fuera concreta, JPA generaría también una tabla `User` para usuarios "comunes", multiplicando el `UNION` polimórfico. Como en el modelo no hay un usuario que no sea ni chofer ni guía dentro de los flujos del TP, conviene dejarla abstracta.
- La estrategia de generación **no puede ser `IDENTITY`**: cada subclase tiene su propia tabla y, si cada una usara su `AUTO_INCREMENT`, los IDs se solaparían (un `DriverUser` con `id = 1` y un `TourGuideUser` con `id = 1` coexistiendo) y romperían las FKs polimórficas (por ejemplo, `Purchase.user_id`). Por eso se usa `TABLE` (o `SEQUENCE` en motores que la soporten) para que el contador de IDs sea único a nivel de toda la jerarquía.

#### a)​ DDL generado

Hibernate genera **una tabla por cada subclase concreta**, completa e independiente — replica los atributos de la clase base en cada una:

```sql
-- No se genera tabla User (es abstracta)

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

- **Cantidad de tablas**: dos (no hay tabla `User` por ser abstracta).
- **FK entre ellas**: ninguna. Cada tabla es autónoma y replica las columnas comunes de `User`.
- **Restricciones `UNIQUE` sobre `username`/`email`/`phoneNumber`**: sólo dentro de cada tabla. Nada impide que un `DriverUser` y un `TourGuideUser` compartan el mismo `username` — la unicidad global se pierde.

#### b)​ SQL al cargar un `DriverUser`

```sql
SELECT id, username, password, name, email, birthdate, phoneNumber, active, expedient
  FROM DriverUser
 WHERE id = ?;
```

Una sola query a una sola tabla. Para este caso particular, `TABLE_PER_CLASS` es **tan rápida como `SINGLE_TABLE`** (incluso más, porque no hay columna discriminadora que filtrar).

En cambio, una **consulta polimórfica** (`from User`) requiere `UNION ALL`:

```sql
SELECT … FROM (
  SELECT id, username, …, NULL AS expedient, NULL AS education, 'DriverUser'    AS clazz_ FROM DriverUser
  UNION ALL
  SELECT id, username, …, NULL AS expedient, NULL AS education, 'TourGuideUser' AS clazz_ FROM TourGuideUser
) sub;
```

Es la consulta más cara de las tres estrategias.

#### c)​ Ventajas y desventajas

- **Ventajas**:
  - Lecturas de subclases concretas sin `JOIN` ni filtro adicional (más rápidas que `JOINED`).
  - `NOT NULL` sobre atributos de subclase declarativo, igual que `JOINED`.
  - Cada subclase es estructuralmente independiente: si una evoluciona, no afecta el DDL de las otras.
- **Desventajas**:
  - **Consultas polimórficas costosas** (`UNION ALL` sobre todas las tablas).
  - **`IDENTITY` no es viable**: hay que usar `TABLE` o `SEQUENCE` para mantener IDs únicos a nivel jerarquía, lo que choca con la decisión del ejercicio 15 sobre el resto del modelo (donde se eligió `IDENTITY` por simplicidad y por usar MySQL).
  - **Duplicación masiva del esquema**: cada tabla repite todas las columnas comunes. Si `User` crece (por ejemplo, agregando `address`, `country`, etc.), hay que tocar todas las tablas hijas.
  - **FKs polimórficas imposibles**: relaciones como `Purchase.user_id` no pueden representarse con una FK simple a nivel BD; la integridad pasa a depender del ORM.
  - **`UNIQUE` global se pierde**: la unicidad de `username`/`email` queda partida por subclase.

#### Estrategia elegida para este modelo: `SINGLE_TABLE`

A pesar de que `JOINED` es la más íntegra a nivel BD y `TABLE_PER_CLASS` es competitiva en lecturas no polimórficas, la elección concreta para este TP es **`SINGLE_TABLE`**. La justificación se apoya en las características concretas del modelo:

- **Consultas polimórficas reales**: `Purchase.user` es un `@ManyToOne` hacia la jerarquía completa de `User`, sin distinguir subclase. Con `SINGLE_TABLE`, `purchaseRepository.findById(...)` resuelve el `User` con un único `SELECT` adicional sobre una sola tabla. Con `JOINED` se suman `LEFT JOIN`s con `DriverUser` y `TourGuideUser`; con `TABLE_PER_CLASS`, un `UNION ALL`. La frecuencia con la que las compras se cargan junto con su usuario hace que el costo polimórfico se pague constantemente, y `SINGLE_TABLE` es la única estrategia que lo evita.
- **Subclases simples y estables**: cada subclase agrega un único atributo (`expedient` y `education`). El "costo" de `SINGLE_TABLE` (columnas en NULL para la otra subclase) es despreciable: dos columnas extra opcionales en una tabla por demás chica. Si las subclases tuvieran muchos atributos propios, el balance cambiaría.
- **`@ManyToMany` hacia subclases concretas**: `Route` mantiene `@ManyToMany` separadas a `DriverUser` y `TourGuideUser`. Con `SINGLE_TABLE`, las tablas join (`route_driver`, `route_tour_guide`) apuntan a `User(id)`, y la pertenencia a la subclase se valida con la columna discriminadora a nivel aplicación. Esto es semánticamente más débil que en `JOINED` (donde la FK apuntaría directamente a `DriverUser(id)`/`TourGuideUser(id)`), pero el TP no exige esa garantía a nivel BD.
- **Coherencia con el resto del modelo**: el ejercicio 15 eligió `IDENTITY` para la generación de IDs. `SINGLE_TABLE` permite mantener `IDENTITY` para `User` sin problema; `TABLE_PER_CLASS` lo prohibiría y obligaría a cambiar la estrategia, rompiendo la coherencia interna del proyecto.
- **Costo del trade-off contenido**: la única desventaja real de `SINGLE_TABLE` es no poder declarar `NOT NULL` sobre `expedient` y `education`. Esa restricción se valida igualmente a nivel aplicación (en los constructores de `DriverUser` y `TourGuideUser`) sin pérdida de garantías para la lógica de dominio — sólo se pierde la validación declarativa en la BD, lo cual es un costo aceptable.
- **Aparición de otros tipos de usuarios**: no se nos da un indicio de que la jerarquía de usuarios vaya a crecer con nuevos tipos (por ejemplo, `AdminUser`, `CustomerUser`, etc.). Si ese fuera el caso, `JOINED` sería más amigable a la evolución. Pero dado el modelo actual, esa posibilidad es especulativa y no justifica el costo extra de los joins.

> [!NOTE]
> La cátedra deja constancia explícita en el PDF de que la decisión es un trade-off real: *"Con SINGLE_TABLE, los atributos propios de subclases (expedient, education) deben declararse `nullable=true` a nivel de columna aunque la lógica de negocio los requiera. Con JOINED, esa restricción puede aplicarse en la tabla de la subclase."* La elección de `SINGLE_TABLE` aquí asume ese costo a cambio de los beneficios de performance polimórfica y simplicidad estructural.

### Ejercicio 37: ​Route tiene relaciones muchos-a-muchos con DriverUser y TourGuideUser (subclases de User). Analizar el impacto de la estrategia de herencia sobre la tabla join:

#### a)​ Si la jerarquía es SINGLE_TABLE, ¿a qué tabla apunta la FK en la tabla join?

Con `SINGLE_TABLE`, las tres clases de la jerarquía (`User`, `DriverUser`, `TourGuideUser`) viven en la misma tabla — `User` — distinguidas únicamente por la columna discriminadora (`user_type`). Por lo tanto:

- Las tablas join `route_driver` y `route_tour_guide` tienen su FK apuntando a **`User(id)`**, no a tablas específicas de subclase (que ni siquiera existen en la base con esta estrategia).
- A nivel BD, una fila en `route_driver` representa "una `Route` asociada a alguna fila de `User`", sin que la base pueda imponer por sí misma que esa fila sea efectivamente un `DriverUser`.
- La garantía de que el usuario referenciado sea de la subclase correcta queda **a cargo de Hibernate**, que al insertar/leer aplica el filtro por `user_type` automáticamente. Si un proceso externo (un `INSERT` manual a la tabla join, una migración por SQL nativo, etc.) saltea el ORM, podría introducir una asociación inválida y la BD no la detendría.

Esquemáticamente:

```sql
CREATE TABLE route_driver (
    route_id BIGINT NOT NULL,
    driver_id BIGINT NOT NULL,                       -- FK -> User(id)
    PRIMARY KEY (route_id, driver_id),
    CONSTRAINT FK_route_driver_route FOREIGN KEY (route_id)  REFERENCES Route(id),
    CONSTRAINT FK_route_driver_user  FOREIGN KEY (driver_id) REFERENCES User(id)
);
```

#### b)​ Si la jerarquía es JOINED, ¿cambia la tabla destino de esa FK?

Sí, cambia. Con `JOINED`, cada subclase tiene su propia tabla (`DriverUser`, `TourGuideUser`) cuya PK es a la vez FK contra `User(id)`. Hibernate, al generar el DDL de las tablas join:

- Apunta la FK de `route_driver` directamente a **`DriverUser(id)`** (no a `User(id)`).
- Apunta la FK de `route_tour_guide` directamente a **`TourGuideUser(id)`**.

Esto refuerza la integridad referencial: la base **garantiza por sí misma** que un `route_driver` sólo puede contener `DriverUser`s, porque la FK exige que el `id` exista en la tabla específica. Insertar un `id` que pertenezca únicamente a un `TourGuideUser` (o a un `User` puro) falla a nivel BD. La validación deja de depender exclusivamente del ORM.

Esquemáticamente:

```sql
CREATE TABLE route_driver (
    route_id BIGINT NOT NULL,
    driver_id BIGINT NOT NULL,                       -- FK -> DriverUser(id)
    PRIMARY KEY (route_id, driver_id),
    CONSTRAINT FK_route_driver_route  FOREIGN KEY (route_id)  REFERENCES Route(id),
    CONSTRAINT FK_route_driver_driver FOREIGN KEY (driver_id) REFERENCES DriverUser(id)
);
```

> [!NOTE]
> Este ejercicio explicita una de las razones por las que `JOINED` se considera "más íntegra" que `SINGLE_TABLE` (ver ejercicio 35). Con `JOINED`, las relaciones a subclases concretas se traducen a FKs específicas a nivel BD; con `SINGLE_TABLE`, todas las FKs hacia la jerarquía aterrizan en la misma tabla y la garantía de tipo queda fuera del esquema relacional. En el TP se aceptó este costo (ejercicio 36) a cambio de la simplicidad y la performance polimórfica que ofrece `SINGLE_TABLE`.

> [!NOTE]
> Con `TABLE_PER_CLASS` la situación es aún más compleja: como no existe una tabla `User`, una FK polimórfica que apunte a "cualquier subclase" no puede expresarse a nivel BD. Las tablas join sí pueden apuntar a las tablas concretas (`DriverUser`/`TourGuideUser`), pero la unicidad global del `id` (necesaria para FKs hacia `User` desde otras entidades como `Purchase.user_id`) deja de estar garantizada por el motor — depende del generador de IDs (`TABLE`/`SEQUENCE`) que la aplicación configure.

### Ejercicio 38: ​¿Qué estrategia resulta más robusta ante cambios futuros como agregar una nueva subclase de User? Justificar con al menos dos argumentos.

La estrategia más robusta ante la incorporación de nuevas subclases es **`JOINED`**. Los argumentos concretos son:

1. **Aislamiento del esquema existente**: agregar una nueva subclase de `User` (por ejemplo, `OperatorUser` con un atributo `shift`) implica únicamente **crear una nueva tabla** (`operator_user`) con la PK como FK contra `User(id)` y las columnas propias de la subclase. La tabla base (`User`) **no se modifica**, ni tampoco las tablas de las otras subclases ya existentes (`driver_user`, `tour_guide_user`). Es una migración aditiva pura: el riesgo sobre los datos ya cargados es mínimo y la operación se puede aplicar incluso en caliente sobre tablas grandes sin reorganización física.
   - Por contraste, en **`SINGLE_TABLE`** la nueva subclase obliga a alterar la tabla `User` agregando columnas para sus atributos propios (todas `nullable = true`) y un nuevo valor en la columna discriminadora. La operación `ALTER TABLE` toca **todas las filas existentes** de la jerarquía y, en tablas grandes, suele requerir downtime, locks largos o migraciones por lotes.
   - En **`TABLE_PER_CLASS`** la nueva subclase implica también una nueva tabla, pero además exige que **todas las consultas polimórficas existentes incorporen el nuevo `UNION ALL`** y que el generador de IDs (compartido entre todas las tablas hijas vía `TABLE`/`SEQUENCE`) siga garantizando unicidad global. Las consultas armadas con la jerarquía vieja se vuelven, sutilmente, incorrectas el día que aparece la nueva subclase.

2. **Integridad declarativa preservada y FKs específicas estables**: con `JOINED`, los atributos propios de la nueva subclase se pueden declarar `NOT NULL` desde el primer momento (cosa que `SINGLE_TABLE` impide), y las FKs desde otras entidades hacia la nueva subclase (por ejemplo, una hipotética tabla "asignaciones operativas" apuntando a `operator_user.id`) son representables a nivel BD con garantía de tipo. Las FKs polimórficas hacia `User` siguen siendo válidas porque la tabla base existe y tiene PK propia. En `SINGLE_TABLE` esa integridad de tipo no es expresable; en `TABLE_PER_CLASS` ni siquiera existe la tabla base contra la que apuntar las FKs polimórficas, por lo que agregar subclases agrava un problema preexistente.

3. **Separación entre cambios de subclase y cambios del núcleo común**: si en el futuro hay que evolucionar atributos *propios de una subclase específica* (cambiar `expedient` por una FK a una entidad nueva, por ejemplo), la migración con `JOINED` afecta sólo la tabla de esa subclase. Con `SINGLE_TABLE` el cambio se mezcla con la tabla `User` que comparte filas con las demás subclases, y el riesgo de tocar de más es mayor. Esta propiedad — que los cambios localizados se mantengan localizados — es la que hace a `JOINED` más estable a lo largo del tiempo.

> [!NOTE]
> Hay una tensión entre las decisiones del ejercicio 36 (`SINGLE_TABLE` por simplicidad y performance polimórfica en este TP) y la del ejercicio 38 (`JOINED` por robustez ante cambios futuros). No es una contradicción: son dos optimizaciones distintas. `SINGLE_TABLE` es la mejor para el modelo *actual y estable* del TP; `JOINED` sería la mejor si se anticipara que la jerarquía va a crecer (más subclases, más atributos por subclase, restricciones de integridad más fuertes). La elección depende, en última instancia, del horizonte temporal y de la criticidad de la integridad declarativa frente al costo de los joins.
