# Borrado lógico 

## Ejercicio 36: ¿Que es el borrado lógico (soft delete)? Pensar en el modelo de tours: si un usuario decide darse de baja del sistema, ¿tiene sentido eliminar físicamente su registro? ¿Qué ocurriría con todas las compras que ese usuario ha realizado? Describir por qué el borrado lógico resuelve este problema y qué ventaja ofrece frente al borrado físico en este caso concreto.

El **borrado lógico (soft delete)** es una estrategia de persistencia en la que **no se elimina físicamente el registro** de la base de datos, sino que se lo **marca como inactivo** mediante un campo adicional (típicamente un booleano `active`/`deleted` o un timestamp `deletedAt`). El registro sigue existiendo en la tabla, pero las consultas ordinarias lo filtran como si no estuviera. Lo opuesto, el **borrado físico (hard delete)**, sí ejecuta un `DELETE` que retira definitivamente la fila.

**¿Tiene sentido eliminar físicamente al usuario en el modelo de tours?**

No. En el modelo, `User` está referenciado por la entidad `Purchase` mediante una clave foránea (`purchase.user_id → user.id`), una relación que además forma parte del historial de negocio. Si se ejecutara un `DELETE` físico sobre el usuario, ocurriría una de dos cosas, dependiendo de la configuración del esquema:

1. **La base rechaza el borrado** por violación de integridad referencial (la restricción `FOREIGN KEY` impide eliminar un usuario si tiene compras asociadas).
2. **El borrado se propaga en cascada** (`ON DELETE CASCADE` o `CascadeType.REMOVE` en JPA), y junto con el usuario **desaparecen todas sus compras**, sus reviews, los `ItemService` ligados a ellas, etc.

Ambos resultados son indeseables: el primero impide cumplir con el pedido del usuario de darse de baja, el segundo destruye **información de negocio histórica** que la empresa necesita conservar (compras facturadas, reseñas usadas en promociones, métricas de demanda, auditoría contable).

**Por qué el borrado lógico resuelve el problema:**

Con soft delete, "dar de baja" un usuario se traduce en `UPDATE user SET active = false WHERE id = ?`. El registro permanece intacto, y con él:

- **Las compras siguen existiendo y siendo válidas:** `Purchase.user_id` sigue apuntando a un registro real, no quedan FKs colgadas.
- **El historial se preserva:** las consultas analíticas (`getTopNSuppliersInPurchases`, `getMostDemandedService`, `getCountOfPurchasesBetweenDates`, etc.) siguen funcionando porque las compras del usuario inactivo aún cuentan.
- **El usuario puede ser re-activado:** si vuelve a registrarse o se trata de un error, basta con `active = true`, sin necesidad de recrear ni adivinar datos perdidos.
- **Las consultas ordinarias lo ignoran:** un filtro global (`@Where(clause = "active = true")` en Hibernate, o un `WHERE` explícito en las queries) hace que `findById`, `findAll` y los Query Methods devuelvan solo usuarios activos, manteniendo la app limpia.

**Ventajas frente al borrado físico en este caso concreto:**

- **Integridad referencial garantizada por construcción**, no hay riesgo de FKs huérfanas ni de cascadas destructivas.
- **Cumplimiento normativo y contable**, en muchos sistemas (incluidos los de turismo) las compras y facturas no pueden borrarse aunque el cliente se vaya, hay obligaciones legales de retención.
- **Reversibilidad**, errores de operación o bajas accidentales se deshacen con un `UPDATE`, no con un restore de backup.
- **Trazabilidad y auditoría**, queda registro de quiénes hicieron qué y cuándo, útil para resolver disputas o analizar patrones.
- **Consultas históricas siguen funcionando** sin condiciones especiales, las compras antiguas no quedan "huérfanas" mostrando un `null` donde antes había un usuario.

>[!NOTE]
> En resumen, en un dominio como este, donde las entidades están **fuertemente acopladas por relaciones que reflejan transacciones reales**, el borrado físico **rompe la coherencia del modelo**. El soft delete preserva esa coherencia transformando "eliminar" en "marcar como inactivo".

## Ejercicio 37: Describir dos estrategias para implementar soft delete en JPA/Hibernate: campo booleano (active/deleted) y campo de fecha (deletedAt). ¿Qué diferencias hay entre ambas en cuanto a consultas y recuperación de datos?​

**Estrategia 1: campo booleano (`active` o `deleted`).**

Se agrega un campo `boolean` a la entidad que indica si el registro está activo. Es lo más simple y suele ser el caso por defecto.

```java
@Entity
public class User {
    @Column(nullable = false)
    private boolean active = true;
    // ...
}
```

- **"Borrar"** se traduce en `UPDATE user SET active = false WHERE id = ?`.
- **Las consultas ordinarias** agregan `WHERE active = true` (manual o con `@Where(clause = "active = true")` de Hibernate, que lo aplica globalmente).
- **Solo se sabe si está borrado o no.** No queda registro de *cuándo* ni de cuántas veces se borró/restauró.

**Estrategia 2: campo de fecha (`deletedAt`).**

Se agrega una columna `Date`/`Timestamp` que es `null` mientras la entidad está activa y toma el valor de la fecha de baja cuando se "borra".

```java
@Entity
public class User {
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;        // null = activo
    // ...
}
```

- **"Borrar"** se traduce en `UPDATE user SET deleted_at = NOW() WHERE id = ?`.
- **Las consultas ordinarias** agregan `WHERE deleted_at IS NULL`.
- Además del estado de borrado, **queda registrado *cuándo* ocurrió la baja**, lo que aporta información de auditoría sin estructura adicional.

**Diferencias en cuanto a consultas:**

- **Filtro:** el booleano se filtra con `WHERE active = true`, la fecha con `WHERE deleted_at IS NULL`. Ambos son equivalentes en cuanto a performance si la columna está indexada.
- **Información disponible:** con el booleano solo se sabe `activo` / `inactivo`. Con `deletedAt` se puede responder además **"¿cuándo se dio de baja?"**, "¿cuántos usuarios se dieron de baja el último mes?", "¿usuarios eliminados antes de tal fecha?", todo sin tablas auxiliares.
- **Re-activación:** con el booleano se hace `active = true` y se pierde el rastro del periodo de inactividad. Con `deletedAt`, restaurar es `deleted_at = NULL`, pero para conservar el historial conviene mover el valor anterior a una tabla de auditoría o usar otro campo (`reactivatedAt`), de lo contrario también se pierde el rastro.

**Diferencias en cuanto a recuperación de datos:**

- El **booleano** es mejor cuando el estado es realmente binario y solo importa saber si la fila "existe" o no para la aplicación.
- La **fecha** es mejor cuando el negocio necesita reportes de auditoría, retención por tiempo (por ejemplo, "borrar definitivamente todo lo que esté borrado lógicamente hace más de 5 años") o cumplimiento normativo que exige saber **cuándo** se eliminó un dato.

>[!NOTE]
> En este TP se eligió el enfoque del **campo booleano `active`** (ver ejercicio 39), porque la consigna pide simplemente que el usuario quede inhabilitado y las consultas ignoren los inactivos, no se necesita información temporal sobre la baja.

### Ejercicio 38: ¿Que es la anotación `@SQLDelete` de JPA? ¿Qué permite hacer? ¿Cómo se combina con `@Where` para que las consultas ordinarias ignoren los registros borrados? Mostrar un ejemplo de uso sobre la entidad User.

`@SQLDelete` y `@Where` son anotaciones de **Hibernate** (no JPA estándar, viven en `org.hibernate.annotations`) que permiten implementar **soft delete de forma transparente para el resto de la aplicación**, sin tocar repositorios ni servicios.

**Qué hace `@SQLDelete`:**

Reemplaza la sentencia `DELETE` que Hibernate generaría automáticamente al persistir una eliminación, por la **sentencia SQL que se le indique** (típicamente, un `UPDATE` que marca el registro como borrado). De esta forma, una llamada normal a `entityManager.remove(entity)` o `repository.delete(entity)` **no borra físicamente**, sino que ejecuta el `UPDATE` definido.

```java
@SQLDelete(sql = "UPDATE app_user SET active = false WHERE id = ?")
```

>[!NOTE]
> El `?` es un placeholder posicional que Hibernate completa con el `id` de la entidad que se está "borrando".

**Qué hace `@Where`:**

Aplica una **cláusula `WHERE` adicional implícita** a **todas las consultas** que Hibernate genere para esa entidad: `findById`, `findAll`, los Query Methods derivados, las consultas `@Query`, las relaciones navegadas desde otras entidades, etc. La condición se agrega de forma automática, sin que el código tenga que mencionarla.

```java
@Where(clause = "active = true")
```

**Cómo se combinan:**

`@SQLDelete` se encarga del *write side* (que un borrado deje el registro marcado) y `@Where` se encarga del *read side* (que todas las consultas ignoren los marcados). Juntas, hacen que la app trate al soft delete **como si fuera un borrado real**: cuando se llama a `userRepository.delete(user)`, el usuario "desaparece" de todas las consultas posteriores, aunque la fila siga en la tabla.

**Ejemplo aplicado a `User`:**

```java
import jakarta.persistence.*;
import org.hibernate.annotations.SQLDelete;
import org.hibernate.annotations.Where;

@Entity
@Table(name = "app_user")
@SQLDelete(sql = "UPDATE app_user SET active = false WHERE id = ?")
@Where(clause = "active = true")
public class User {

    @Id @GeneratedValue
    private Long id;

    private String username;
    private String password;
    private String fullName;

    @Column(nullable = false)
    private boolean active = true;        // por defecto, activo

    // resto del modelo...
}
```

Con esta configuración:

- **`userRepository.delete(user)`** ejecuta `UPDATE app_user SET active = false WHERE id = ?` en lugar del `DELETE` físico.
- **`userRepository.findById(id)`** devuelve `Optional.empty()` si el usuario está marcado como inactivo, como si nunca hubiera existido.
- **`userRepository.findAll()`** y los Query Methods (`findByUsername`, etc.) solo retornan usuarios activos.
- **Las relaciones navegadas** (por ejemplo, acceder a `purchase.getUser()`) también respetan el filtro de `@Where`.

>[!NOTE]
> `@Where` se aplica **globalmente** a todas las consultas que Hibernate genera para esa entidad. Si en algún caso particular se necesita listar también los usuarios inactivos (por ejemplo, en un panel de administración), hay que usar **SQL nativo** (`@Query(value = "...", nativeQuery = true)`) o una consulta JPQL explícita que evite el filtro, ya que JPQL ordinario lo aplicará igual.

## Implementación en el modelo

### Ejercicio 39: Implementar soft delete para la entidad User usando @SQLDelete y @Where. La implementación debe:

#### a)​ Agregar el campo necesario a la entidad User (campo y anotaciones).

El campo se modela como un `boolean active`, anotado con `@Column(nullable = false)` y con valor por defecto `true` en el constructor para que todo `User` recién creado quede activo.

```java
@Column(nullable = false)
private boolean active;

public User(String username, String password, String name, String email, Date birthdate, String phoneNumber) {
    // ...
    this.active = true;
}
```

#### b)​ Redefinir el comportamiento de delete para que marque el registro en lugar de eliminarlo.

Se anota la entidad con `@SQLDelete`, indicando la sentencia que Hibernate debe ejecutar cada vez que se invoca `delete(...)` sobre un `User`. Como el modelo usa herencia `SINGLE_TABLE` con discriminador `user_type`, la tabla real se llama `user` (la default que Hibernate da a la clase raíz):

```java
import org.hibernate.annotations.SQLDelete;

@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "user_type", discriminatorType = DiscriminatorType.STRING)
@DiscriminatorValue("USER")
@SQLDelete(sql = "UPDATE user SET active = false WHERE id = ?")
public class User { ... }
```

Con esto, `userRepository.delete(user)` deja de ejecutar `DELETE FROM user WHERE id = ?` y pasa a ejecutar el `UPDATE` que marca el usuario como inactivo. El servicio puede mantener la firma `delete(user)` sin saber que internamente es soft delete.

#### c)​ Asegurar que todas las consultas ordinarias (findAll, findById, Query Methods) excluyan automáticamente los usuarios borrados.

Se anota la entidad con `@Where`, indicando la cláusula que Hibernate va a agregar a **todas** las consultas que devuelven `User`:

```java
import org.hibernate.annotations.Where;

@Entity
// ... resto de anotaciones
@SQLDelete(sql = "UPDATE user SET active = false WHERE id = ?")
@Where(clause = "active = true")
public class User { ... }
```

Con esto:

- `userRepository.findById(id)` devuelve `Optional.empty()` si el usuario fue marcado como inactivo.
- `userRepository.findAll()` y `findByUsername(...)` solo devuelven usuarios activos.
- Las relaciones que navegan al `User` desde otras entidades (por ejemplo, `purchase.getUser()`) también respetan el filtro.

**Implementación completa de la entidad `User`:**

```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "user_type", discriminatorType = DiscriminatorType.STRING)
@DiscriminatorValue("USER")
@SQLDelete(sql = "UPDATE user SET active = false WHERE and id = ?")
@Where(clause = "active = true")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // ... resto de los campos como ya están ...

    @Column(nullable = false)
    private boolean active;

    public User(String username, String password, String name, String email,
                Date birthdate, String phoneNumber) {
        this.username = username;
        this.password = password;
        this.name = name;
        this.email = email;
        this.birthdate = birthdate;
        this.phoneNumber = phoneNumber;
        this.active = true;
    }

    // getters/setters omitidos
}
```

**Simplificación del servicio:**

El método `deleteUser` actual implementa el soft delete manualmente borrando físicamente si el usuario no tiene compras, sino setea `active = false`. Con `@SQLDelete` activo, **toda esa lógica condicional ya no es necesaria**, basta con invocar `delete(...)` y Hibernate hace el `UPDATE` automáticamente:

```java
@Override
@Transactional
public void deleteUser(User user) throws ToursException {
    User persisted = userRepository.findById(user.getId())
            .orElseThrow(() -> new ToursException("El usuario no existe"));
    if (persisted.hasAssignedRoutes()) {
        throw new ToursException("El usuario no puede ser desactivado");
    }
    userRepository.delete(persisted);
}
```

Se conservan las validaciones de negocio (existencia y rutas asignadas), pero la decisión "borrado físico vs soft delete" deja de ser responsabilidad del servicio y queda contenida en el mapeo de la entidad.

### Ejercicio 40: La implementacion actual muestra el metodo `canBeDeactivate()` en `User`, `DriverUser` y `TourGuideUser`. El objetivo de estos métodos es evitar que se eliminen usuarios que poseen compras o asignaciones y, por tanto queden inconsistencias en la base de datos. Describa como esta nueva implementación afecta dichos métodos.

En la implementación, este rol lo cumple `hasAssignedRoutes()` (en `User` devuelve `false`; redefinido en `DriverUser`/`TourGuideUser`, devuelve `true` si tienen rutas asignadas). La nueva implementación afecta a estos métodos de forma **parcial**, distinta según la relación:

- **Respecto de las compras:** el chequeo **deja de ser necesario**. Antes había que evitar borrar usuarios con compras para no romper la FK; ahora el `@SQLDelete` preserva la fila y el `@Where` esconde al inactivo automáticamente, así que esa protección la da el propio mecanismo de soft delete, no el método.

- **Respecto de las asignaciones de ruta:** el método **sigue siendo necesario**. `@Where` solo filtra inactivos en las lecturas; **no impide desactivar** a un conductor/guía que aún tiene rutas, lo que dejaría rutas apuntando a un usuario "fantasma" (y como ya no hay `DELETE` físico, tampoco salta ninguna FK). Por eso `deleteUser` mantiene la guarda `hasAssignedRoutes()` y lanza la excepción, tal como exige el test (`deleteUserTest` espera `ToursException` al borrar un guía con ruta).

>[!NOTE]
> **En resumen:** el `@Where`/`@SQLDelete` **absorbe** la parte del control ligada a las *compras* (la integridad se garantiza por construcción), pero **no** la ligada a las *asignaciones de ruta*: esa verificación se conserva, ya que el soft delete no limpia la `@ManyToMany` ni evita la inconsistencia. El método no se elimina; queda reducido a su responsabilidad sobre las rutas.

