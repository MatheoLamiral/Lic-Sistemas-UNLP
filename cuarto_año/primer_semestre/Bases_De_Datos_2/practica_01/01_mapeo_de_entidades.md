# Mapeo de entidades

## Mapeo de una entidad simple: Service

### Ejercicio 12: ​¿Cuál es el conjunto mínimo de anotaciones que debe tener una clase para ser persistente con JPA?

El conjunto mínimo de anotaciones que debe tener una clase para ser persistente con JPA se compone de dos anotaciones:
- `@Entity`: Se coloca a nivel de la declaración de la clase par aindicarle al framework que dicha clase es uina entidad (POJO persistente) y que debe ser mapeada a la base de datos
- `@Id`: Se coloca sobre el atributo que servirá como identificador único o clave primaria, cumpliendo con la regla obligatoria de los POJOs persistentes de proveer un identificador

>[!NOTE]
> No es obligatorio agregar anotaciones adicionales para los demás atributos de la clase. Gracias al principio de "Convención sobre Configuración", JPA asume por defecto que todos los atributos declarados en la clase deben persistirse en la base de datos, a menos que se indique explícitamente lo contrario (por ejemplo, utilizando la anotación `@Transient` para que un campo sea ignorado)

### Ejercicio 13: ¿Qué significa que JPA use persistencia por alcance (persistence by reachability)? ¿Qué consecuencia tiene si un objeto referenciado no está todavía persistido?

La persistencia por alcance (o persistencia transitiva) significa que todo objeto al cual se pueda llegar navegando a partir de un objeto que ya es persistente, debe ser necesariamente persistente a su vez. Esto permite que, para almacenar un objeto en la base de datos, el desarrollador solamente necesite vincularlo orgánicamente (por ejemplo, agregándolo a una colección o asignándolo a un atributo) con algún otro objeto que ya exista en el repositorio, reduciendo de esta forma las operaciones explícitas de guardado y respetando el principio de independencia
- La consecuencia de que un objeto referenciado no esté todavía persistido (es decir,  que se encuentre en estado volátil o transitorio) depende de la configuración de cascada:
  - Si la persistencia por alcance está activa (por ejemplo, configurada con `CascadeType.PERSIST` o `ALL`): Al momento de realizar el commit de la transacción, el framework recorrerá el grafo de objetos modificados y, al encontrar este nuevo objeto volátil referenciado, lo insertará y persistirá automáticamente en la base de datos sin requerir ninguna acción adicional por parte del desarrollador
  - Si la persistencia por alcance NO está activa (el comportamiento por defecto de JPA): La operación de guardado no se propagará hacia la entidad asociada. Como consecuencia, el ORM intentará guardar en la base de datos una relación hacia un registro que físicamente aún no existe, lo cual desencadenará una excepción o falla de integridad referencial.

### Ejercicio 14: ¿Qué diferencia hay entre las estrategias IDENTITY, SEQUENCE y TABLE para la generación de IDs? ¿Cuál tiene mejor rendimiento en inserciones masivas y por qué?

En JPA la anotación `@GeneratedValue` permite definir cómo se crerán las claves primarias automáticamente, utilizando tres estrategias principales:

- `IDENTITY`:
  - Delega la generación del identificador enteramente a la base de datos utilizando columnas de tipo "autoincremental" (como `AUTO_INCREMENT` en MySQL o `IDENTITY` en PostgreSQL).
  - En Hibernate no conoce el ID del objeto hasta que la sentencia `INSERT` se ejecuta realmente en la base de datos.
- `SEQUENCE`:
  - Utiliza un objeto nativo de la base de datos llamado "Secuencia" (muy común en Oracle o PostgreSQL).
  - En Hibernate realiza una consulta a la base de datos para pedirle el próximo valor de la secuencia antes de ejecutar el `INSERT`. Esto le permite a Hibernate conocer el ID del objeto y asignárselo en memoria antes de guardar el registro.
- `TABLE`:
  - Es la estrategia más genérica. En lugar de usar características nativas del motor (como columnas autoincrementales o secuencias), crea una tabla auxiliar en la base de datos dedicada exclusivamente a llevar la cuenta de los identificadores.
  - En Hibernate para generar un nuevo ID, Hibernate debe hacer un `SELECT` en esta tabla auxiliar, bloquear la fila (lock), hacer un `UPDATE` para incrementar el valor, y liberar la fila.

### Ejercicio 15: Implementar el mapeo completo de la entidad Service según el diagrama. La implementación debe incluir:

#### a) Clave primaria con estrategia de generación automática. Elegir entre IDENTITY, SEQUENCE o TABLE y justificar la elección.

#### b) Atributos: name (no nulo, max. 100 caracteres), description (opcional), price (no nulo).

#### c) Al menos una restricción de unicidad a nivel de columna.

## Relaciones entre entidades