---
titulo: "Plan de Trabajo de Prácticas Preprofesionales: Desarrollo de Sistema DAQ de 16 Canales para Sensores Geotécnicos de Presa con NI USB-6210 y Python"
proyecto: "Sistema de Adquisición, Calibración y Caracterización Metrológica de Sensores Geotécnicos en Python (NI USB-6210)"
codigo_proyecto: "RSA-PPP-2026-12"
area_tematica: "Instrumentación Virtual, Procesamiento Digital de Señales, Metrología Asistida por Computador, Python (NI-DAQmx) y Sensores Geotécnicos"
estado: "En Ejecución"
version: "1.0"
fecha_creacion: "2026-09-28"
fecha_actualizacion: "2026-09-28"

practicante:
  nombre: "Christopher Carchipulla"
  cedula: "N/D"
  correo: "christopher.carchipulla@ucuenca.edu.ec"
  carrera: "Ingeniería en Telecomunicaciones"
  institucion: "Universidad de Cuenca"

tutoria:
  tutor_institucional: "Ing. Milton Muñoz (Red Sísmica del Austro - RSA)"
  correo_tutor_institucional: "milton.munozc@ucuenca.edu.ec"

cronograma:
  duracion_total_horas: 144
  dedicacion_semanal_horas: 14
  duracion_semanas: 10.5
  fecha_inicio: "2026-10-01"
  fecha_fin_estimada: "2026-12-18"
  modalidad: "Presencial"

tecnologias:
  - "Hardware de Adquisición de Datos: National Instruments NI USB-6210 (16 entradas analógicas, resolución de 16 bits, hasta 250 kSPS, bus USB de alta velocidad)"
  - "Acondicionamiento Analógico Especializado: Amplificadores de instrumentación de precisión Burr-Brown/TI INA114AP para Puentes de Wheatstone"
  - "Sensores Geotécnicos e Instrumentación: 2 Canales de Puentes de Wheatstone (galgas extensométricas de deformación) y 14 Sensores potenciométricos lineales de desplazamiento"
  - "Entorno y Lenguaje de Programación: Python 3.10+ en entorno virtual (.venv), VS Code, Git/GitHub"
  - "Librerías de Control y Adquisición: NI-DAQmx (controlador oficial de National Instruments), PyDAQmx / nidaqmx-python"
  - "Procesamiento Numérico y Visualización: NumPy, SciPy (filtros digitales pasabajas Butterworth y media móvil), Matplotlib / PyQtGraph para monitoreo multicanal en tiempo real"
  - "Formatos de Datos y Configuración: YAML / JSON para desacoplamiento de parámetros y calibración; CSV estructurado y Parquet para series temporales"
  - "Instrumental de Calibración: Multímetro digital de banco de 6.5 dígitos, caja de décadas de resistencias patrón (precisión 0.05%), micrómetro digital de precisión sobre banco de desplazamiento"

repositorio:
  url: "https://github.com/RSA-PPP/ppp-2026-12-daq-ni6210-python"
  rama_base: "main"

topics:
  - rsa-ppp
  - ucuenca
  - dam-monitoring
  - daq
  - ni-usb-6210
  - strain-gauges
  - metrology
  - python
---

---

## 1. Antecedentes y Justificación Técnica

### 1.1. Contexto del Sistema y Estado Inicial del Artefacto
La Red Sísmica del Austro (RSA) dispone de instrumentación geotécnica especializada para la supervisión de deformaciones milimétricas y desplazamientos relativos en juntas, galerías y taludes de presas hidroeléctricas. Dentro de este instrumental, se cuenta con una tarjeta física de acondicionamiento de señales diseñada para conectar simultáneamente **16 transductores geotécnicos**:
* **2 canales para Puentes de Wheatstone:** Destinados a galgas extensométricas para medición de deformación inducida por esfuerzos estructurales. La señal diferencial de microvoltios producida por el desbalance del puente es amplificada por circuitos integrados de instrumentación de ultra bajo ruido **INA114AP**.
* **14 canales para sensores potenciométricos:** Diseñados para transductores lineales de desplazamiento de hilo o vástago, cuya variación resistiva genera una tensión proporcional a la posición relativa de bloques o fisuras.

Para digitalizar estas variables con alto estándar metrológico, se dispone de una tarjeta de adquisición de datos **National Instruments NI USB-6210** (16 entradas analógicas, convertidor ADC de 16 bits de aproximaciones sucesivas con velocidad agregada de hasta 250 kSPS). Sin embargo, el sistema carece de una plataforma de software unificada, trazable y automatizada en **Python** que gobierne la digitalización multicanal, aplique el equilibrado y cero eléctrico, convierta voltajes a magnitudes de ingeniería ($\mu\varepsilon$ y mm) y audite continuamente la salud del cableado y los sensores.

### 1.2. Limitaciones Críticas o Cuellos de Botella Identificados
* **Cálculo Teórico Desvinculado de la Realidad del Circuito:** La ganancia real de los amplificadores INA114AP depende críticamente de la resistencia de ajuste $R_G$ ($G = 1 + 50\,\text{k}\Omega/R_G$). En los esquemas no se dispone de una validación experimental de dicha ganancia ni del cálculo de los umbrales de saturación analógica ante variaciones de la tensión de excitación.
* **Falta de Justificación en la Topología de Tierra (RSE, NRSE o Diferencial):** La tarjeta NI USB-6210 permite configurar los canales en modo referenciado (RSE/NRSE) o diferencial. Al usar 16 canales en modo de terminal común, existe un alto riesgo de acoplamiento de bucles de masa (*ground loops*) e interferencia cruzada (*cross-talk*) entre los potenciometros y las etapas de alta ganancia de los puentes si no se establece un esquema riguroso de puesta a tierra.
* **Configuración 'Hardcoded' sin Trazabilidad Metrológica:** Los parámetros de calibración (pendiente, intercepto, factor de galga, cero inicial) se encontraban dispersos o fijados rígidamente dentro del código, impidiendo sustituir sensores en campo o actualizar coeficientes sin recompilar la aplicación.
* **Inexistencia de Filtrado Digital y Monitoreo en Tiempo Real:** La presencia de ruido industrial de 60 Hz y transitorios electromagnéticos en los cables de instrumentación de presas exige el diseño de etapas de filtrado digital deterministas (filtros IIR Butterworth o promedios móviles) y una interfaz de supervisión gráfica ágil que no degrade el determinismo temporal del motor de adquisición.
* **Carencia de Diagnóstico de Salud de Canal:** No existía detección automática de saturación (voltaje fuera de rango $\pm 10\text{ V}$), desconexiones de cable (*open-circuit*) o derivas excesivas de cero durante registros continuos.

### 1.3. Desacoplamiento del Alcance y Propuesta de Solución
La presente pasantía de **144 horas** aborda el diseño, desarrollo, calibración metrológica y validación de una suite de instrumentación virtual completa en **Python** gobernando la tarjeta NI USB-6210:
1. **Auditoría Circuital y Mapeo Físico:** Análisis de los planos esquemáticos, deducción matemática de ganancias y comprobación experimental en banco de las tensiones de excitación y límites seguros para la NI USB-6210.
2. **Arquitectura de Software Desacoplada:** Desarrollo en Python orientado a objetos con la librería oficial `nidaqmx`, aislando la lógica de adquisición en un motor modular e implementando un archivo de configuración externo (YAML/JSON) para la asignación y calibración de los 16 canales.
3. **Calibración y Procesamiento de Señales:** Algoritmos de tara/cero de software, conversión a unidades físicas ($\mu\varepsilon$ y mm), filtrado digital en tiempo real contra ruido de 60 Hz y registro sincronizado en CSV con archivos de diagnóstico.
4. **Validación Metrológica:** Pruebas progresivas en banco (sin sensores, con resistencias patrón de precisión y con banco micrométrico de desplazamiento) culminando en un ensayo de estrés continuo de 24 a 48 horas.

---

## 2. Objetivos del Plan de Trabajo

### 2.1. Objetivo General
Desarrollar, caracterizar y validar experimentalmente un sistema de instrumentación virtual en Python para la tarjeta de adquisición National Instruments NI USB-6210, integrando el acondicionamiento analógico de 2 puentes de Wheatstone con amplificadores INA114AP y 14 sensores potenciométricos de desplazamiento, con el propósito de garantizar un registro continuo, filtrado, calibrado y metrológicamente trazable para la auscultación geotécnica de presas de la RSA.

### 2.2. Objetivos Específicos
1. **Auditoría de Hardware y Entorno NI-DAQmx:** Analizar los esquemas de la tarjeta de acondicionamiento, calcular y verificar experimentalmente las ganancias de los amplificadores INA114AP, comprobar los límites seguros de tensión ($\pm 10\text{ V}$) y configurar el entorno de ejecución en Python con el controlador oficial `nidaqmx`.
2. **Arquitectura de Software y Configuración Externa:** Diseñar e implementar una arquitectura de software orientada a objetos desacoplada, gobernada por un archivo externo estructurado (YAML/JSON) que defina la correspondencia de canal físico, modo de conexión (RSE/NRSE/Diferencial), ganancias y coeficientes individuales de calibración.
3. **Módulo de Procesamiento para Puentes de Wheatstone:** Implementar el equilibrado eléctrico, ajuste dinámico de cero (tara) y las ecuaciones analíticas de conversión de microvoltios a microdeformación ($\mu\varepsilon$), validando la respuesta estática y linealidad con resistencias patrón.
4. **Módulo de Calibración de Desplazamiento Potenciométrico:** Desarrollar el pipeline de adquisición simultánea de los 14 canales potenciométricos, ejecutando el procedimiento metrológico de calibración en banco para determinar pendiente, intercepto, linealidad ($R^2$) y evaluar la diafonía (*cross-talk*) entre canales.
5. **Filtrado Digital, GUI en Tiempo Real y Ensayo de Estrés:** Implementar filtros digitales pasabajas para rechazo de armónicos de red (60 Hz), desarrollar una interfaz gráfica de monitoreo en tiempo real con detección de alarmas/saturación y validar la estabilidad temporal en un ensayo continuo de adquisición multicanal.

---

## 3. Plan de Trabajo Detallado y Checkpoints Cuantificables

### Fase 1: Auditoría Circuital, Cálculo de Ganancias y Setup del Entorno NI-DAQmx
* **Duración:** 15 horas (Semana 1)
* **Objetivo:** Inspeccionar los esquemas electrónicos de la tarjeta de acondicionamiento, calcular teóricamente las características de transferencia, comprobar los niveles eléctricos de seguridad y poner a punto el entorno de control con la NI USB-6210.
* **Actividades técnicas:**
  1. Análisis minucioso de los esquemas circuitales de la tarjeta analógica: identificación de reguladores de tensión, rieles de alimentación, referencias analógicas (AGND) y digitales (DGND).
  2. Cálculo analítico de la ganancia nominal de los dos amplificadores de instrumentación INA114AP en función de la resistencia $R_G$:
     $$G = 1 + \frac{50\,\text{k}\Omega}{R_G}$$
     y determinación teórica del rango admisible de tensión diferencial en la entrada antes de provocar saturación en los rieles de salida.
  3. Verificación instrumental en banco: medir tensiones de excitación para los puentes de Wheatstone y para los 14 divisores potenciométricos con multímetro de 6.5 dígitos, garantizando que ninguna salida supere el rango de $\pm 10\text{ V}$ admisible por la NI USB-6210.
  4. Configuración del entorno de software en Python 3.10+ (`.venv`), instalación de los drivers oficiales NI-DAQmx y verificación del reconocimiento del hardware mediante `nidaqmx.system.System.local().devices`.
* **Checkpoints medibles para revisión:**
  - [ ] **CP 1.1:** Memoria técnica de cálculo circuital elaborada con la deducción de ganancias de los INA114AP y la tabla de rangos esperados de tensión para los 16 canales.
  - [ ] **CP 1.2:** Mediciones de tensión y rizado de las fuentes de alimentación documentadas; verificación de que los voltajes entregados a los conectores de la NI USB-6210 son seguros.
  - [ ] **CP 1.3:** Script en Python ejecutado con éxito detectando el número de serie, modelo y canales disponibles de la NI USB-6210 conectada por USB.

---

### Fase 2: Arquitectura del Software en Python y Módulo de Configuración Desacoplado
* **Duración:** 30 horas (Semanas 2–3)
* **Objetivo:** Diseñar e implementar la estructura del software modular orientada a objetos y el esquema de configuración externa desacoplada para los 16 canales de adquisición.
* **Actividades técnicas:**
  1. Diseño de la arquitectura de clases en Python:
     * `DeviceManager`: Encargado de la inicialización, reserva de tareas (`nidaqmx.Task`) y liberación determinista de recursos DAQ.
     * `ConfigLoader`: Parser y validador de esquema de configuración externa.
     * `Channel`: Abstracción de canal físico con atributos de modo de conexión, unidades, ganancias y coeficientes de calibración.
     * `DataEngine`: Motor de muestreo continuo basado en buffers y callbacks asíncronos.
  2. Creación del archivo de configuración desacoplado `sensors_config.yaml` estructurado con la especificación de los 16 canales:
     ```yaml
     device_name: "Dev1"
     sampling_rate_hz: 100
     channels:
       - id: "CH01"
         physical_name: "ai0"
         sensor_type: "strain_gauge_bridge"
         terminal_config: "DIFFERENTIAL" # o RSE / NRSE
         voltage_range: [-1.0, 1.0]
         gauge_factor: 2.1
         excitation_voltage_v: 5.0
         amplifier_gain: 501.0
         engineering_unit: "ue"
       - id: "CH03"
         physical_name: "ai2"
         sensor_type: "potentiometer_displacement"
         terminal_config: "RSE"
         voltage_range: [0.0, 10.0]
         calibration:
           slope_mm_per_v: 10.0
           intercept_mm: 0.0
         engineering_unit: "mm"
     ```
  3. Implementación de validaciones de integridad: comprobar que los canales físicos solicitados no excedan la capacidad del dispositivo ni existan solapamientos de recursos.
  4. Ensayos de adquisición continua de prueba en bucle durante 1 hora sobre canales flotantes/referenciados evaluando consumo de memoria y ausencia de desbordamiento de búfer (*buffer overflow*).
* **Checkpoints medibles para revisión:**
  - [ ] **CP 2.1:** Archivo `sensors_config.yaml` definido y validado contra un esquema estricto; el código carga dinámicamente cualquier modificación sin tocar el código fuente.
  - [ ] **CP 2.2:** Tarea de adquisición multicanal de NI-DAQmx generada dinámicamente a partir del archivo YAML con asignación correcta de rangos y modos de terminal.
  - [ ] **CP 2.3:** Prueba de estabilidad del motor de adquisición superada: 1 hora de captura continua sin fugas de memoria (*memory leaks*) ni excepciones en el hilo principal.

---

### Fase 3: Adquisición, Equilibrado y Calibración de Puentes de Wheatstone (INA114AP)
* **Duración:** 15 horas (Semana 4)
* **Objetivo:** Implementar la lógica de equilibrado, tara de software y conversión analítica de microvoltios a microdeformación ($\mu\varepsilon$) para los canales basados en INA114AP.
* **Actividades técnicas:**
  1. Conexión de resistencias patrón de precisión ($350.0\,\Omega \pm 0.05\%$) en la tarjeta analógica para simular un puente de Wheatstone perfectamente equilibrado.
  2. Implementación de la rutina de tara automática (*Zero Calibration*): capturar una ventana temporal (ej. 100 muestras), promediar la tensión residual de offset del amplificador y almacenar dicho valor como referencia cero.
  3. Caracterización de ganancia real experimental: introducir desequilibrios conocidos mediante resistencias calibradas en paralelo (resistencia de shunt) y medir la tensión de salida para contrastar la ganancia efectiva frente a la ganancia teórica de diseño.
  4. Implementación de la ecuación de conversión de voltaje a deformación mecánica:
     $$\Delta\varepsilon = \frac{4 \cdot (V_{out} - V_{zero})}{V_{ex} \cdot G \cdot GF} \cdot 10^6\quad [\mu\varepsilon]$$
     donde $V_{ex}$ es la tensión de excitación real, $G$ la ganancia del INA114AP y $GF$ el factor de galga (*Gauge Factor*).
  5. Evaluación de linealidad, estabilidad térmica del cero y umbral antes de la saturación del amplificador operacional.
* **Checkpoints medibles para revisión:**
  - [ ] **CP 3.1:** Ganancia real de los dos amplificadores INA114AP medida experimentalmente y contrastada con el valor teórico, con discrepancia documentada inferior al $2\%$.
  - [ ] **CP 3.2:** Subrutina de equilibrado y cero eléctrico ejecutada en menos de 2 segundos, reduciendo el offset residual a $< 0.1\,\mu\varepsilon$.
  - [ ] **CP 3.3:** Curva de calibración de deformación vs resistencia de shunt con coeficiente $R^2 \ge 0.999$ para ambos canales de puente.

---

### Fase 4: Adquisición y Calibración Metrológica de Sensores Potenciométricos (14 Canales)
* **Duración:** 30 horas (Semanas 5–6)
* **Objetivo:** Implementar la adquisición paralela de los 14 canales analógicos potenciométricos y ejecutar el protocolo metrológico de calibración en banco de desplazamiento.
* **Actividades técnicas:**
  1. Conexión de los 14 canales potenciométricos a las entradas analógicas de la NI USB-6210, justificando técnicamente la elección del modo de terminal (RSE vs NRSE) para minimizar bucles de tierra.
  2. Evaluación experimental de diafonía (*cross-talk*): excitar un canal con una señal de gran amplitud (ej. escalón 0 a 10 V) y medir con osciloscopio y con el ADC si se inducen tensiones espurias en los canales adyacentes.
  3. Montaje del banco de calibración de desplazamiento: acoplar potenciómetros de prueba a un micrómetro digital de precisión sobre base rígida.
  4. Ejecución del ensayo metrológico en 10 puntos de desplazamiento conocidos a lo largo de todo el rango útil (recorrido de ida y vuelta para evaluar histeresis).
  5. Algoritmo de regresión lineal por mínimos cuadrados en Python (`scipy.optimize` / `numpy.polyfit`) para determinar automáticamente la pendiente ($k$), el intercepto ($b$) y el coeficiente de determinación ($R^2$), actualizando los valores calculados en el archivo `sensors_config.yaml`.
* **Checkpoints medibles para revisión:**
  - [ ] **CP 4.1:** Adquisición síncrona de los 14 canales analógicos sin interferencia cruzada detectable (aislamiento de diafonía $> 60\text{ dB}$).
  - [ ] **CP 4.2:** Curvas de calibración generadas para los sensores potenciométricos con coeficiente de determinación $R^2 \ge 0.9995$ e histeresis inferior al $0.5\%$ del fondo de escala.
  - [ ] **CP 4.3:** Actualización automática y desacoplada de los coeficientes de calibración en el archivo de configuración sin alterar el código ejecutable.

---

### Fase 5: Filtrado Digital en Tiempo Real, Detección de Anomalías y Persistencia Segura
* **Duración:** 24 horas (Semanas 7–8)
* **Objetivo:** Desarrollar los módulos de acondicionamiento digital de señales, supervisión de fallos de hardware y almacenamiento sincronizado de alta integridad.
* **Actividades técnicas:**
  1. Diseño e implementación de filtros digitales en Python utilizando `scipy.signal`:
     * Filtro pasabajas IIR Butterworth de 4to orden (frecuencia de corte $f_c = 10\text{ Hz}$) para eliminar armónicos de la red eléctrica ($60\text{ Hz}$) y ruido electromagnético.
     * Opción de filtro de media móvil configurable para estabilización de lecturas estáticas de alta resolución.
  2. Implementación del módulo de diagnóstico y detección proactiva de anomalías:
     * Alerta de saturación: Detección si $|V| \ge 9.95\text{ V}$ indicando desborde del ADC o fallo de amplificador.
     * Alerta de circuito abierto / desconexión de sensor: Detección de canales flotantes o lecturas fijas atípicas.
     * Alerta de deriva térmica excesiva en puentes.
  3. Desarrollo del subsistema de almacenamiento de datos:
     * Generación de archivos CSV fechados con doble flujo: datos brutos en voltios (`raw_voltages_YYYYMMDD.csv`) y datos convertidos a unidades de ingeniería (`engineering_data_YYYYMMDD.csv`).
     * Archivo de log de auditoría de sesión (`session_diagnostic.log`) registrando eventos de tara, constantes de calibración aplicadas y errores detectados.
* **Checkpoints medibles para revisión:**
  - [ ] **CP 5.1:** Filtro digital en tiempo real validado; atenuación comprobada superior a $40\text{ dB}$ para la componente de ruido de 60 Hz sin generar latencia perceptible en la adquisición.
  - [ ] **CP 5.2:** Sistema de diagnóstico detectando con éxito la desconexión intencional de un sensor o la saturación por sobreesfuerzo en menos de 100 ms con registro en log.
  - [ ] **CP 5.3:** Archivos de datos generados con estructura tabular perfecta, incluyendo cabeceras de metadatos, marcas de tiempo ISO 8601 y sin pérdida de muestras durante ráfagas de escritura en disco.

---

### Fase 6: Interfaz Gráfica de Monitoreo en Tiempo Real y Ensayo Continuo de Estrés
* **Duración:** 18 horas (Semanas 9–10)
* **Objetivo:** Construir una interfaz visual para inspección de los 16 canales y someter al sistema completo a una prueba de estabilidad prolongada de 24 a 48 horas continuas.
* **Actividades técnicas:**
  1. Desarrollo de una interfaz gráfica de usuario (GUI) ligera y reactiva (utilizando `PyQtGraph` o `matplotlib` integrado en ventana GUI) con:
     * Panel general tipo cuadrícula (*grid*) con barras de nivel y semáforos de estado para los 16 canales.
     * Visor temporal tipo osciloscopio multicanal para inspeccionar ondas y transitorios en canales seleccionados.
     * Indicadores numéricos instantáneos con unidades físicas claras ($\mu\varepsilon$ y mm).
     * Botón de calibración de cero / tara en caliente y botón de exportación rápida.
  2. Optimización de concurrencia: asegurar que la GUI se ejecute en un hilo secundario independiente del hilo de adquisición de NI-DAQmx para garantizar que el renderizado gráfico jamás ralentice el muestreo por hardware.
  3. Ejecución de la **Prueba Integral de Estrés Continuo (24 a 48 horas)** en laboratorio:
     * Monitoreo ininterrumpido de los 2 puentes y 14 potenciómetros.
     * Análisis de deriva del cero a lo largo del ciclo diurno/nocturno.
     * Verificación de estabilidad del driver USB y ausencia total de fugas de memoria o congelamientos.
* **Checkpoints medibles para revisión:**
  - [ ] **CP 6.1:** Interfaz gráfica operativa con refresco fluido ($\ge 25\text{ FPS}$) manteniendo una carga de CPU inferior al $15\%$ en el equipo de cómputo.
  - [ ] **CP 6.2:** Prueba de 24 horas continuas de adquisición completada sin un solo error de búfer, reconexión de USB ni pérdida de paquetes.
  - [ ] **CP 6.3:** Reporte cuantitativo de deriva de cero generado demostrando la estabilidad metrológica del acondicionamiento a lo largo de un ciclo térmico completo.

---

### Fase 7: Manual de Metrología, Guía de Troubleshooting e Informe Técnico Final
* **Duración:** 12 horas (Semanas 10–11)
* **Objetivo:** Elaborar la documentación institucional de ingeniería, el manual de calibración para técnicos y el Informe Técnico Final de prácticas preprofesionales.
* **Actividades técnicas:**
  1. Elaboración del Manual de Operación y Calibración Metrológica: guía paso a paso para el equilibrado de puentes INA114AP, conexión de potenciómetros, edición de `sensors_config.yaml` y ejecución de ensayos en campo.
  2. Redacción de la Guía de Solución de Problemas (*Troubleshooting*) con catálogo de fallas comunes: resolución de bucles de tierra, ruidos de 60 Hz, reemplazo de transductores y códigos de excepción del driver NI-DAQmx.
  3. Redacción del Informe Técnico Final bajo el formato formal institucional de la RSA y la Universidad de Cuenca, compilando la formulación matemática, diagramas de bloques, curvas de calibración y análisis de resultados.
  4. Revisión técnica con el tutor institucional, incorporación de observaciones y entrega del repositorio de código en GitHub debidamente documentado.
* **Checkpoints medibles para revisión:**
  - [ ] **CP 7.1:** Borrador consolidado del Informe Técnico Final, Manual de Calibración y Guía de Troubleshooting entregado al tutor para revisión.
  - [ ] **CP 7.2:** Repositorio en GitHub estructurado con código modular, entorno virtual reproducible (`requirements.txt`), archivo de configuración ejemplo y documentación en Markdown.
  - [ ] **CP 7.3:** Aprobación definitiva del informe por los tutores y suscripción de las actas de culminación de prácticas.

---

## 4. Resumen de Fases y Cronograma Semanal (144 Horas)

El trabajo se organiza en bloques semanales de **14 horas** (a lo largo de **10.5 semanas**) estructurado con checkpoints cuantificables para garantizar una ejecución técnica rigurosa:

| Fase | Semanas | Horas | Enfoque Principal |
| :---: | :---: | :---: | :--- |
| **Fase 1** | Semana 1 | **15 h** | Auditoría circuital, cálculo de ganancias de INA114AP, seguridad eléctrica y conexión NI-DAQmx. |
| **Fase 2** | Semanas 2–3 | **30 h** | Arquitectura modular en Python (POO), archivo de configuración YAML desacoplado y buffer DAQ. |
| **Fase 3** | Semana 4 | **15 h** | Equilibrado, tara de cero y ecuaciones analíticas de microdeformación para puentes de Wheatstone. |
| **Fase 4** | Semanas 5–6 | **30 h** | Adquisición de 14 potenciómetros, análisis de diafonía (*cross-talk*) y calibración micrométrica. |
| **Fase 5** | Semanas 7–8 | **24 h** | Filtro pasabajas contra 60 Hz, detección proactiva de fallas/saturación y persistencia CSV/log. |
| **Fase 6** | Semanas 9–10 | **18 h** | Interfaz gráfica en tiempo real (PyQtGraph) y ensayo continuo de estrés de 24 horas. |
| **Fase 7** | Semanas 10–11 | **12 h** | Manual de calibración metrológica, guía de troubleshooting, repositorio e Informe Final. |
| **Total** | **~10.5 Semanas** | **144 h** | **Planificación Global de Prácticas Preprofesionales** |

---

## 5. Entregables y Criterios de Éxito de la Pasantía

1. **Memoria de Cálculo y Auditoría de Hardware:**
   * Documento técnico justificando el cálculo de ganancia de los amplificadores INA114AP, análisis de márgenes de saturación y asignación de topologías de conexión analógica (RSE/NRSE/Diferencial) para los 16 canales.
2. **Suite de Software Modular en Python:**
   * Código fuente completo, orientado a objetos y documentado, utilizando la librería oficial `nidaqmx`.
   * Archivo de configuración desacoplado (`sensors_config.yaml`) que permite modificar la calibración y comportamiento de los sensores sin tocar el código ejecutable.
   * Pipeline de filtrado digital con rechazo probado a ruido de red eléctrica de 60 Hz y rutinas de calibración de cero de software.
3. **Módulo de Diagnóstico y Persistencia de Datos:**
   * Sistema de detección y registro de fallos en tiempo real (saturación de canal, desconexión de sensor y deriva).
   * Almacenamiento continuo con doble volcado (voltajes crudos y unidades de ingeniería en CSV) con registros de auditoría de sesión fechados.
4. **Interfaz de Monitoreo Gráfico en Tiempo Real:**
   * Panel interactivo multicanal en `PyQtGraph` mostrando lecturas instantáneas, tendencias temporales y semáforos de advertencia sin introducir latencias en la adquisición de datos.
5. **Evidencia Experimental y Validación Metrológica:**
   * Curvas de calibración de deformación y desplazamiento con coeficientes de correlación $R^2 \ge 0.999$.
   * Registro continuo de la prueba de estrés de 24 horas demostrando estabilidad temporal, determinismo y ausencia de desbordamiento de búfer.
6. **Manual de Operación, Guía de Troubleshooting e Informe Final:**
   * Manual práctico de uso y calibración metrológica para los investigadores y técnicos de la RSA.
   * Guía de resolución de problemas (*troubleshooting*) de conectividad DAQ y ruidos de instrumentación.
   * Informe Técnico Final formal en el estándar institucional de la RSA y la Universidad de Cuenca.
