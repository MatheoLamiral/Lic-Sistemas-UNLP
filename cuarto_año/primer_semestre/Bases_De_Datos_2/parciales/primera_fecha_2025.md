# BBDD2 — Parcial (TEMA 2) — 1era fecha 10/06/2026

## Enunciado: plataforma de cursos online

El siguiente diagrama modela una plataforma de cursos online. `Persona` es una clase **abstracta** de la que heredan `Alumno` e `Instructor`. Un `Alumno` puede inscribirse en muchos `Curso` y un `Curso` puede tener muchos alumnos inscriptos (relación **"inscripto", muchos-a-muchos**). Un `Instructor` **"dicta"** muchos cursos, mientras que cada `Curso` es dictado por un único instructor (relación **"dicta", uno-a-muchos**). Cada curso se compone de una o más lecciones (relación **"contiene", composición**).

Se sabe que un alumno **no puede ser instructor** o viceversa y que existen **pocas consultas sobre todas las personas**.

### Atributos

- **Persona** (abstracta): `id: Long`, `email: String` (no puede repetirse para distintas personas), `nombreCompleto: String`, `fechaNacimiento: Date`
- **Alumno**: `legajo: String` (no puede repetirse para distintos alumnos), `fechaInscripcion: Date`
- **Instructor**: `especialidad: String`, `biografia: String`, `valoracion: Double`
- **Curso**: `id: Long`, `titulo: String`, `codigo: String` (no puede repetirse para distintos cursos), `precio: BigDecimal`, `fechaPublicacion: Date`
- **Leccion**: `titulo: String`, `numeroOrden: int`, `duracionMin: int`

### Diagrama de clases (UML)

```
                 ┌──────────────────────────────┐
                 │ «abstract»  Persona          │
                 │  - id : Long                 │
                 │  - email : String            │
                 │  - nombreCompleto : String   │
                 │  - fechaNacimiento : Date    │
                 └──────────────▲───────────────┘
                                │ (herencia)
            ┌───────────────────┴────────────────────┐
┌───────────────────────────┐         ┌───────────────────────────────┐
│ Alumno                    │         │ Instructor                    │
│  - legajo : String        │         │  - especialidad : String      │
│  - fechaInscripcion : Date│         │  - biografia : String         │
└───────────┬───────────────┘         │  - valoracion : Double        │
            │ *        inscripto       └───────────────┬───────────────┘
            │ *  (muchos-a-muchos)                     │ 1   dicta
            │                                          │ *  (uno-a-muchos)
            └──────────────►┌──────────────────────────▼───┐
                            │ Curso                        │
                            │  - id : Long                 │
                            │  - titulo : String           │
                            │  - codigo : String           │
                            │  - precio : BigDecimal       │
                            │  - fechaPublicacion : Date   │
                            └──────────────┬───────────────┘
                                           │ 1   contiene (composición ◆)
                                           │ 1..*
                            ┌──────────────▼───────────────┐
                            │ Leccion                      │
                            │  - titulo : String           │
                            │  - numeroOrden : int         │
                            │  - duracionMin : int         │
                            └──────────────────────────────┘
```

---

## Hibernate / JPA

### 1. Estrategia de herencia (opción única)

Al mapear la jerarquía `Persona` / `Alumno` / `Instructor` a tablas relacionales, ¿qué estrategia de herencia de las posibles opciones de Hibernate/JPA utilizaría? Justificar la decisión teniendo en cuenta que las subclases poseen **atributos obligatorios propios** (por ejemplo `legajo` en Alumno y `especialidad` en Instructor) y **relaciones propias**. **Seleccione la única opción correcta:**

- a. ( ) `SINGLE_TABLE`
- b. (X) `JOINED`
- c. ( ) `TABLE_PER_CLASS`
- d. ( ) No es posible mapear esta jerarquía con JPA porque las subclases tienen relaciones propias; debe eliminarse la herencia y duplicar los atributos comunes.

Selecciono `JOINED` porque tenemos restricciones a nivel de la clase abstracta que hay que mantener (email único), restricción que no podemos mantener si seleccionamos `TABLE_PER_CLASS` no podemos mantener. Además, tenemos restricciones a nivel de las clases concretas (legajo único), restricción que no podemos mantener si seleccionamos `SINGLE_TABLE`, por lo que solo nos queda `JOINED` como opción viable para poder mantener todas las restricciones.

>[!NOTE]
> Tendremos que pagar el precio del JOIN extra en cada consulta

### 2. Mapeo JPA completo de la jerarquía

Definir el mapeo JPA completo de las tres clases de la jerarquía (`Persona`, `Alumno` e `Instructor`) según el diagrama. Tener en cuenta las **restricciones de los atributos**. Complete las anotaciones JPA sobre la siguiente estructura de clases, en los renglones indicados con `//`. Puede agregar los renglones que necesite.

```java
//
//

@Entity
@Inheritance(strategy = InheritanceType.JOINED)
public abstract class Persona {

    //
    //
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    //
    @Column(unique = true)
    private String email;

    //
    @Column
    private String nombreCompleto;

    //
    @Temporal(TemporalType.Date)
    private Date fechaNacimiento;

    // (getters y setters omitidos)
}


//
@Entity
public class Alumno extends Persona {

    //
    @Column(nulleable = false, unique = true)
    private String legajo;

    //
    @Temporal(TemporalType.Date)
    private Date fechaInscripcion;
}


//
@Entity
public class Instructor extends Persona {

    //
    @Column(nulleable = false)
    private String especialidad;

    //
    @Column
    private String biografia;

    //
    @Column
    private Double valoracion;
}
```

### 3. Relación `dicta` entre Instructor y Curso

Analizar la relación **`dicta`** entre `Instructor` y `Curso` y responda las siguientes preguntas:

- a. ¿Qué anotaciones se utilizan en cada lado? ¿Dónde se ubica `mappedBy` y en qué tabla aparece la clave foránea?
- b. ¿Qué `FetchType` elegiría en cada extremo de la relación? Justificar.
- c. ¿Qué operaciones en cascada configuraría desde `Instructor` hacia `Curso`? En particular, ¿tiene sentido `CascadeType.REMOVE`? Justificar a partir del modelo de negocio.

```java
public class Instructor extends Persona {

    // ... atributos propios ya mapeados (especialidad, biografia, valoracion)

    //
    @ManyToOne(mappedBy = instructor, fetch = FetchType.Lazy, cascade = {CascadeType.MERGE, CascadeType.PERSIST}, orphanRemoval = false)
    private List<Curso> cursos = new ArrayList<>();

    // getters y setters
}


public class Curso {

    // ... atributos ya mapeados (id, titulo, codigo, precio, fechaPublicacion)

    //
    @OneToMany(fetch = FetchType.EAGER, cascade = {}, orphanRemoval = false)
    @JoinColumn(name = "instructor_id", nulleable = false)
    private Instructor instructor;

    // getters y setters
}
```

---

## Spring Data JPA

### 4. ¿Qué es Spring Data JPA? (múltiple opción)

¿Qué es Spring Data JPA y qué problema resuelve respecto de usar Hibernate directamente? **Seleccione todas las opciones correctas (puede haber más de una):**

- a. [X] Es una capa de abstracción sobre JPA/Hibernate que reduce el código repetitivo (boilerplate) de la capa de acceso a datos.
- b. [X] Genera automáticamente, en tiempo de ejecución, la implementación de los repositorios definidos como interfaces.
- c. [X] Permite derivar consultas a partir del nombre del método.
- d. [ ] Reemplaza por completo a Hibernate: al usar Spring Data JPA ya no interviene otro ORM por debajo.
- e. [X] Provee soporte de paginación y ordenamiento mediante `Pageable` y `Sort`.
- f. [ ] Es el componente encargado de generar el SQL y de mapear el `ResultSet` a objetos Java por sí mismo, sin intervención del ORM.

### 5. Simplificaciones de Spring Data JPA

Describir **dos situaciones/implementaciones concretas** de este modelo donde Spring Data JPA simplifica código en comparación con la implementación manual requerida en Hibernate puro.

### 6. Cabecera del repositorio

Definir la cabecera (interfaz) de repositorio de **una** de las tres entidades mapeadas.

```java
// Repositorio de una de las entidades mapeadas (Persona, Alumno o Instructor)
public interface ____________________ extends ____________________<________, ____> {

    // Método(s) de consulta (punto siguiente):
    //
    //
}
```

### 7. Método de consulta

Sobre ese repositorio, agregar un método que devuelva los **cursos dictados por instructores cuya valoración sea mayor a un valor dado**. Indicar y justificar la estrategia elegida para escribir la consulta.

---

## MongoDB

### 8. Aggregation Framework

Suponiendo una colección `"cursos"` en la que cada documento referencia a su instructor mediante un campo `"instructorId"`, resolver con **Aggregation Framework**: por cada instructor, calcular la **cantidad de cursos que dicta** y el **precio promedio** de esos cursos; devolver únicamente los instructores con **valoración mayor a 8**, ordenados por **precio promedio de forma descendente**.

### 9. Embebido vs referencia

Suponiendo que este modelo se va a persistir a MongoDB, seleccionar **una relación** del modelo que convenga modelar como **documento embebido** y **otra** que convenga modelar como **referencia**. Justificar cada una de las elecciones.

---

## Redis

### 10. Almacenamiento y persistencia

¿Dónde almacena Redis los datos? ¿Qué implicancias tiene esto en términos de **velocidad** y de **persistencia**? ¿Es posible persistir estos datos? Explique al menos una de las posibles estrategias.
