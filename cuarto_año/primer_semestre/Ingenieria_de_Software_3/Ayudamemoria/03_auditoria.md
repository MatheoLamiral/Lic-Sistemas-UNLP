# 3. Auditoría de Sistemas

### Definición + 4 objetivos ❗
**Auditoría de SI**: proceso sistemático y planificado de **recolectar, analizar y evaluar evidencia** para determinar si se cumplen 4 objetivos:
1. **Preservar los activos**, 2. **Mantener la integridad/consistencia de los datos**, 3. **Usar los recursos con eficiencia**, 4. **Alcanzar los objetivos organizacionales con eficacia**.

### Tipos de opinión del auditor ❗❗
- **Sin calificación (limpia)**: no hubo pérdidas materiales ni registros incorrectos.
- **Con calificación**: hubo pérdidas/registros incorrectos pero **montos no considerables**.
- **Adversa**: hubo pérdidas materiales / estados financieros distorsionados (sí relevantes).
- **Excusada (abstención)**: **no se puede emitir opinión** con el trabajo realizado.

### Tipos de riesgo de auditoría ❗
- **Inherente**: riesgo propio de la actividad, sin considerar controles.
- **De control**: que los controles no prevengan/detecten un error.
- **De detección**: que el auditor no detecte un error existente.

### Controles ❗
- **Preventivo**: evita el evento *antes* (ej. validación de campos en un form).
- **Detectivo**: identifica el evento *después* (ej. log que detecta datos incorrectos).
- **Correctivo**: corrige/mitiga tras la detección (ej. bloqueo y reset tras N intentos).
**"Un control es un sistema"**: es un conjunto de componentes/procesos coordinados (no algo aislado) para prevenir/detectar/corregir eventos ilegales.

### Abuso informático vs Fraude comercial ❗
Se diferencian por: **Escalabilidad** (el abuso informático no está limitado por lo físico, es masivo y rápido) y **Trazabilidad** (deja huellas en logs, aunque pueden borrarse). El vector de ataque es vía sistemas de información.

### Gobernanza vs Administración de TI ❗
- **Gobernanza**: **quién** decide (autoridad, responsabilidad, rendición de cuentas); decisiones estratégicas al más alto nivel (junta directiva). Objetivo: valor, mitigar riesgos, alineación. Funciones: **Evaluar, Dirigir, Monitorear**.
- **Administración**: **ejecuta** las decisiones. Funciones: **Planificar, Construir, Ejecutar, Monitorear**.

### COBIT ❗ (en aumento)
Marco de **ISACA** para gobernanza/control de TI. **Separa Gobernanza de Administración**.
**5 principios**: satisfacer necesidades de los interesados; cubrir la empresa de extremo a extremo; aplicar un marco integrado único; habilitar un enfoque holístico; separar gobernanza de administración.
**37 procesos** en 2 dominios: Gobernanza (5) y Administración (32: **APO, BAI, DSS, MEA** ≈ plan/build/run/check).

### Procedimientos de auditoría
Para evaluar eficiencia/eficacia: **testeos de controles**, **revisión analítica**, testeos de detalle de transacciones, procedimientos para comprender los controles.

### Caso práctico: plan de evaluación incompleto
1º **contactar al cliente** para completar el plan según objetivos/intereses, antes de empezar. Para el **informe**: dejar claro objetivo, alcance, hallazgos, opinión y recomendaciones de mejora.
