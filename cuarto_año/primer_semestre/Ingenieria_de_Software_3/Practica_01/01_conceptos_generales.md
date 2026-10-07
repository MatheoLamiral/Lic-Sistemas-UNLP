# Práctica 1 – Administración de Proyectos y Costos

## Parte I: Conceptos generales

### Ejercicio 1: Una startup de salud digital quiere lanzar una app de gestión de turnos médicos en un plazo de 4 meses, con el objetivo de comenzar a operar en una red de clínicas privadas. El sistema deberá permitir que los pacientes reserven turnos online, que los médicos gestionen su agenda y se enviarán recordatorios de forma automática.

#### a) Defina con sus palabras el *objetivo* del proyecto.

El objetivo es desarrollar una aplicación de gestión de turnos, reservas online, gestión de agenda y recordatorios automáticos, en un plazo de 4 meses para comenzar a utilizarla en una red de clínicas privadas

#### b) Identifique al menos 4 restricciones y explique cómo afectan al proyecto.

1. **Alcance**: El sistema debe tener tres funcionalidades, reserva de turnos online, gestión de agenda médica y recordatorios automáticos. Tenemos un alcance acotado, cualquier pedido extra que aparezca, se sale del alcance acordado y, para mantenerlo, obliga a renegociar tiempo, costo y/o recursos.
2. **Tiempo**: Se fijó un tiempo corto de 4 meses. Esto limita la capacidad de agregar funcionalidades extra y requiere una planificación muy rigurosa  
3. **Recursos**: No se especifica el tamaño del equipo. Si es chico, no alcanza para cubrir el alcance en 4 meses. Además se necesitar recurson técnicos (infraestructura/servidores), y si su disponibilidad es limitada condiciona cúanto se puede hacer.
4. **Costo**: No se especificó un presupuesto. Esto impide fijar los límites del desarrollo
5. **Calidad**: La reserva de turnos debe ser confiable y los recordatorios deben enviarse correctamente. Además, al tratar con salud, se deben cumplir normativas de protección de datos personales. Esto añade complejidad técnica y auditorías que pueden retrasar el desarrollo

#### c) Indique 3 riesgos concretos del proyecto y para cada uno de ellos indique la causa, el impacto y proponga un posible plan de mitigación.

1. **Incumplimiento del plazo de entrega**:
   - **Causa**: Plazo muy ajustado, posible equipo reducido o retrasos en el desarrollo.
   - **Impacto**: La startup no puede empezar a operar, implicaría pérdidas de credibilidad y oportunidades de negocio.
   - **mitigación**: Definir un MVP (producto mínimo viable) con lo esencial para salir a producción en la fecha pactada
2. **Baja en el equipo de desarrollo**
   - **causa**: Una enfermedad, licencia o renuncia reduce el equipo de desarrolladores.
   - **Impacto**: Se frena el avnce de las funcionalidades que esa persona manejaba y se pierde su conocimiento, lo que compromente la fecha de entrega. 
   - **mitigación**: Documentar el código y las decisiones técnicas para que no dependan de una sola persona.
3. **Baja adopción por parte de los usuarios**
   - **causa:** Interfaz comleja o difícil de integrar en la rutina de los usuarios.
   - **Impacto**: Implica el fracaso del proyecto y la planificación de una reentrega.
   - **mitigación**: Realizar prototipos y pruebas de usabilidad con médicos reales desde el segundo 1.

### Ejercicio 2: Elija dos proyectos reales (pueden ser conocidos o hipotéticos): uno exitoso y uno fallido.

#### a) Describa brevemente cada uno de los proyectos (objetivo, contexto, resultado final).

**Proyecto fallido - FBI Virtual Case File (VCF)**

- **Objetivo**: reemplazar el sistema de gestión de casos en el papel del FBI por uno digital que permitiera conectar información de distintas fuentes para investigaciones mas eficiente.
- **Contexto**: desarrollado entre 2001 y 2005 como parte del programa Trilogy, contratado a una empresa externa (SAIC). Los requerimientos estaban mal definidos y cambiaban constantemente durante el desarrollo. Se le aseguró al Congreso que avanzaba bien cuando en realidad estaba en problemas serios.
- **Resultado final**: el sistema fue declarado inutilizable y cancelado en 2005. Sobrecosto de ~89% (más de USD 200 millones perdidos). El FBI tuvo que empezar de cero con un proyecto nuevo.

**Proyecto exitoso - FBI Sentinel**

- **Objetivo**: es el mismo que VCF, reemplazar el sistema de casos en papel del FBI por uno digital y moderno.
- **Contexto**: iniciado en 2006 con presupuesto de USD 425 millones. Arrancó también con demoras y problemas bajo el modelo tradicional (contratista Lockheed Martin). En 2010 el FBI tomó control directo del desarrollo y adoptó Scrum (Agile): redujo el equipo de 125 a 55 personas y organizó el trabajo en 670 user stories sobre sprints de 2 semanas.
- **Resultado final**: Sentinel se completó por debajo del presupuesto y entró en uso en todo el FBI el 1 de julio de 2012. Es un caso de estudio citado en libros de referencia de Scrum (Sutherland, Schwaber).

#### b) Identifique al menos 3 factores clave en cada caso que expliquen el éxito/fracaso del proyecto.

- **Tres factores clave del fracaso**
  - **Requerimientos mal definidos y cambiantes**: Se construyó sobre una base inestable.
  - **No se realizaron entregas intermedias**: Se delegó todo a un contratista externo para entregar el sistema completo de una sola vez. Recién al final se descubrió que era inutilizable.
  - **Falta de control/seguimiento honesto**: se informaba que avanzaba bien cuando estaba en crisis. Los desvíos se detectaron demasiado tarde.

- **Tres factores clave del éxito**
  - **Utilización de una metodología ágil**: Entregas incrementales en sprints de 2 semanas que permitieron validar y corregir temprano.
  - **Control directo del proyecto por parte del cliente**: El FBI tomó el control del desarrollo en vez de delegarlo en el contratista, con responsabilidad directa sobre el resultado.
  - **Equipo reducido y enfocado**: Se redujo el equipo de 125 a 55 personas, mejorando la comunicación y el foco.

#### c) Explique las diferencias entre ambos proyectos y proponga 3 acciones concretas que podrían haberse tomado para evitar los problemas del proyecto fallido.

Las diferencias residen en la planificación, el alcance y el control del proyecto. El proyecto exitoso definió bien los requerimientos y utilizó metodologías ágiles para una buena planificación, lo que derivó en un alcance claro y bien definido. Además, el cliente (FBI) tuvo control directo sobre el avance. En cambio, el proyecto fallido no se detuvo en dejar firmes las bases antes de construir, no aplicó ninguna metodología para gestionar las entregas y ocultó los desvíos hasta que fue demasiado tarde.

- Tres acciones que podría haberse tomado para evitar los problemas del proyecto fallido:
  - Realizar encuestas, entrevistas y prototipos para definir bien los requerimientos. 
  - Realizar una buena planificación para definir un alcance concreto y plazos de entrega rales.
  - Utilización de metodologías ágiles, con sprints semanales, para no tener sorpresas al momento de la entrega final.

### Ejercicio 3: Elija una organización y describa a qué se dedica (cuál es su misión). Formule un objetivo estratégico para el cual se necesite la ejecución de un programa y luego:

**Organizacion**: SuperFresh supermercados.

**Misión**: Ofrecer productos de calidad a precios accesibles, con la mejor experiencia de compra para sus clientes.

**Objetivo**: aumentar las ventas un 25% en 2 años impulsando la transformación digital de la empresa

>[!NOTE]
> Este objetivo es muy grande para un solo proyecto, por lo que se necesita un prorama que coordine varios proyectos

#### a) Identifique un programa para la implementación del objetivo estratégico que incluya al menos tres proyectos.

**Programa**: Transformación digital SuperFresh

- Incluye al menos 3 proyectos:
  - **App de e-commerce y deliver**: Permitir compras online con entregas a domicilio.
  - **Programa de fidelización digital**: App de puntos/cupones para retener clientes y conocer su hábitos de compra.
  - **Sistema de analítica de datos**: Centralizar y analizar los datos de ventas para optimizar stock y promociones.

#### b) Explique por qué los proyectos forman parte del programa.

**Comparten el mismo objetivo**: los tres apuntan a aumentar las ventas vía digitalización, ninguno por sí solo lo logra.

**Estan relacionados y se potencian entre sí**: la app de e-commerce genera datos que alimentan el sistema de BI, el BI mejora las promociones del programa de fidelización, la fidelización trae más usuarios a la app. El beneficio combinado es mayor que la suma de los proyectos por separado

>[!NOTE]
> Eso es lo que justifica gestionarlos como programa y no como proyectos sueltos

**Requieren coordinación**: comparten recursos, tecnología e infraestructura (ej. la misma base de clientes), por lo que conviene administrarlos de forma centralizada para evitar duplicar esfuerzos.
