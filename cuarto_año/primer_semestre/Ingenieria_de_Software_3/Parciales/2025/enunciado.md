# Ingeniería de Software III — Parcial Primera Fecha (13/06/2025)

## 1. Administración de Proyectos

**a. Explique el concepto de "Triángulo de alcance" y la relación que existe entre todos los parámetros involucrados.**

El concepto de "triángulo de alcance" refiere a una representación visual de la interdependencia de los parámetros de un proyecto. En el centro del triángulo, se encuentra el alcance y la calidad, y en los vértices, el costo, el tiempo y los recursos. Al modificar uno de los vértices, se produce un impacto sobre la calidad y el alcance del proyecto, y genera una deformación sobre los otros dos. 

**b. Indique cuáles de los siguientes son enfoques de la gestión de los stakeholders.**
- [x] Estrategia de gestión de los stakeholders
- [x] Matriz de impacto 
- [x] Mantener el interés y el compromiso de los stakeholders
- [x] Mapa de los stakeholders
- [ ] Analizar los stakeholders
- [x] Canales de comunicación

**c. Indique de las siguientes cuáles son características de un programa y cuáles de un proyecto.**
- [ PROGRAMA ] Tienen un amplio alcance que puede cambiar para satisfacer las expectativas
- [ PROYECTO ] Se realiza una planificación detallada para administrar la entrega de productos y servicios
- [ PROGRAMA ] El estilo de liderazgo se centra en la gestión de las relaciones y la resolución de conflictos
- [ PROYECTO ] El éxito se mide por el presupuesto, el tiempo de entrega y los productos que cumplen las especificaciones

**d. Una empresa de seguros de vehículos cuenta con una planta de 50 empleados. En base a requerimientos de los directivos, se definió la ejecución de un proyecto para proveer un sistema de sueldos.**
- **i. Clasifique el proyecto según *Duración, Riesgo, Complejidad y Tecnología*. Justifique.**
	|Duración|Riesgo|Complejidad|Tecnología|
	|--------|------|-----------|----------|
	|3-6 meses|Medio|Media|Práctica|

	No tenemos información específica sobre los requerimientos, pero asumiendo por lo que se dice, que es un sistema solo para el cálculo de sueldos en base a políticas de la empresa, un plazo de 3-6 meses es un tiempo razonable. El riesgo lo considero medio, ya que trataremos datos sensibles de los empleados. La complejidad también media, ya que, debemos calcular el sueldo en base a unos determinados términos y condiciones de la empresa, y normativas generales, lo que implica varias reglas de negocio. En cuanto a la tecnología, utilizaría una práctica, ya que el sistema es pequeño, no se nos da indicios de futuros cambios, por lo que este tipo de tecnología cumplirá con los requerimientos y nos ahorrará complicaciones y tiempo.
- **ii. Enumere dos situaciones que puedan hacer fracasar el proyecto.**
  1. Pobre estimación: si se subestima el esfuerzo de implementar las normativas legales de liquidación, el proyecto se queda sin tiempo/fondos y se entrega incompleto.
  2. Falta de control de calidad: un error no detectado en el cálculo de sueldos genera un producto defectuoso y pérdida de confianza.

## 2. Calidad de Software

**a.** Describa el concepto de "Calidad de Producto de Software", mencione los modelos de calidad y formas de evaluación vistas en la materia.

La calidad de un producto de software hace referencia a las características propias de un Software y la capacidad de las mismas de satisfacer los requermientos de un cliente.

- Los modelos de calidad vistos en la materia son:
  - ISO/IEC 9126 (Calidad de Software), reemplazada por ISO/IEC 25010
- Las formas de evaluación vistas en la materia son:
  - ISO/IEC 14598, reemplazada por ISO/IEC 25040

**b.** Explique cómo aplicaría la ISO 9001 a un proceso de software.

Para aplicar la ISO 9001 a un proceso de software se utiliza la ISO/IEC 90003:2018 como directriz/guía. Esta norma está basada en la ISO 9001:2015 y sirve para interpretar sus requisitos en el contexto del Software

**c.** Clasifique las siguientes características del modelo de calidad de datos ISO/IEC 25012 considerando los puntos de vista.
- Exactitud [INHERENTE] 
- Completitud [INHERENTE] 
- Disponibilidad [DEPENDIENTE DEL SISTEMA] 
- Credibilidad [INHERENTE] 

**d.** Sistema de Gestión de la Calidad (SGC)
- **i.** Indique cuáles de las siguientes son características del Alcance del SGC (A) y cuáles de los Objetivos del SGC (O)
	- Ser comparables [O]
	- Ser medibles [O]
	- Indicar normas de certificación [A]
	- Ser específicos [A, O]
	- Ser realistas [O]
	- Indicar estado actual [O]
- **ii.** Seleccione *uno* de los siguientes procesos principales de desarrollo de una empresa y defina:
	`ANÁLISIS → DISEÑO → IMPLEMENTACIÓN → [PRUEBAS] → MANTENIMIENTO`
	- **a.** Alcance del SGC
    	- El SGC se aplica al proceso de pruebas del desarrollo de software de la organización, abarcando desde la planificación de las pruebas hasta la emisión del informe de resultados y el acta de aceptación. Aplica al equipo de la sede central. Se excluyen el diseño y la implementación del código, por corresponder a otros procesos. El alcance está documentado en el manual de calidad y se revisa periódicamente.
	- **b.** Dos objetivos del SGC
    	- Reducir en un 30% los errores que llegan a producción respecto del semestre anterior
    	- Alcanzar una cobertura de casos del 90% sobre los requerimientos funcionales, antes de fin de año

## 3. Auditoría de Sistemas

**a.** Defina, con sus palabras, qué es una "Auditoría de Sistemas de Información". Mencione cuáles son los cuatro objetivos.

La auditoría de sistemas de información es el proceso sistemático y planificado de recolectar y evaluar evidencia sobre los sistemas informáticos de una organización, para determinar si:
1. Preserva los activos
2. Mantiene la integridad de datos
3. Permite alcanzar los objetivos organizacionales con eficacia 
4. Usa los recursos con eficiencia 

**b.** Indique cuáles de los siguientes son tipos de riesgos de auditoría.
- [x] Riesgo de detección
- [ ] Riesgo preventivo
- [ ] Riesgo de contratación
- [x] Riesgo deseado
- [x] Riesgo inherente

**c.** Indique de qué tipo de opinión de auditoría se trata en cada uno de los siguientes casos:
- Se concluye que ocurrieron pérdidas materiales pero las cantidades no son considerables: Con calificación
- No puede emitirse una opinión en base al trabajo realizado: Excusada
- Se considera que no han ocurrido pérdidas materiales: Sin calificación
- Se concluye que han ocurrido pérdidas materiales: Adversa

**d.** Presente un ejemplo de cómo un mal procesamiento de información realizado por un sistema informático puede conducir a una toma de decisiones incorrecta para el gerente de una empresa vinculada a la industria hotelera.

## 4. Interfaces No Tradicionales

**a.** Indique cuáles de las siguientes son consideradas ejemplos de "Interfaces hápticas".
- Pantalla táctil de un teléfono móvil
- Guante que permite sentir objetos virtuales
- Cinturón de navegación para personas ciegas
- Casco de realidad virtual con vibración
- Joystick de simulador de vuelo con fuerza de resistencia
- Monitor de computadora
