# Guía de Referencia Técnica y Material Heredado
## Proyecto: Sistema DAQ de 16 Canales para Sensores Geotécnicos (NI USB-6210 y Python)

Este documento establece el puente técnico y metodológico entre el desarrollo previo del hardware de acondicionamiento / prototipado de software y la ejecución de la pasantía actual (**`RSA-PPP-2026-12`**), llevada a cabo por **Christopher Carchipulla** bajo la tutoría del **Ing. Milton Muñoz**.

---

## 📌 Datos de Identificación del Proyecto

| Parámetro | Detalle |
| :--- | :--- |
| **Código Institucional** | `RSA-PPP-2026-12` |
| **Proyecto** | Sistema de Adquisición, Calibración y Caracterización Metrológica de Sensores Geotécnicos en Python (NI USB-6210) |
| **Pasante** | Christopher Carchipulla (`christopher.carchipulla@ucuenca.edu.ec`) |
| **Tutor Institucional** | Ing. Milton Muñoz (`milton.munozc@ucuenca.edu.ec`) — Red Sísmica del Austro (RSA) |
| **Repositorio** | [RSA-PPP/ppp-2026-12-daq-ni6210-python](https://github.com/RSA-PPP/ppp-2026-12-daq-ni6210-python) |
| **Plan Rector** | [docs/planificacion.md](file:///C:/Users/miltonrsa/Documents/git/ppp/ppp-2026-12-daq-ni6210-python/docs/planificacion.md) (144 horas) |

---

## 🔍 Resumen del Material Heredado (Qué está disponible y probado)

Se ha transferido al repositorio todo el desarrollo previo clasificado y depurado para servir de base en las distintas fases del proyecto:

1. **Tarjeta de Acondicionamiento Analógico Multicanal (KiCad V7+):**
   * **Esquemático del sistema (`Nidaq.kicad_sch`):** Diseño circuital completo que integra:
     * Conector principal de 32 pines (`J16`) para interfaz física con los bornes de la tarjeta **National Instruments NI USB-6210**.
     * 2 canales para puentes de Wheatstone instrumentados con amplificadores de instrumentación **INA114AP** (`J1` [Presión] y `J17` [Galgas]).
     * 14 canales para sensores de desplazamiento potenciométricos (`J3` a `J15` y `POT_10`) con resistencias de polarización/protección de $220\,\Omega$ (`R_02` a `R_18`).
     * Rieles de alimentación y filtrado con condensadores de $68\text{ nF}$ (`C15`, `C16`) y conectores de fuente (`J18`, `J19`).
     * Mapeo completo de redes: `AI0` a `AI15`, `AISN` (AI Sense), `AGND` (tierra analógica) y `DGND` (tierra digital).
   * **Placa de circuito impreso corregida (`Nidaq_corregido.kicad_pcb`):** Ruteo de 2 capas ($162.0\text{ mm} \times 207.4\text{ mm}$) que superó la verificación de reglas de diseño (DRC) para ensamble y fabricación.

2. **Diseño Mecánico y Envolventes 3D (OpenSCAD / STL):**
   * Carcasa protectora (`Nidaq_corregido_caja`), bandeja de montaje (`Nidaq_corregido_bandeja`) y blindaje electromagnético (`Nidaq_corregido_blindaje` en `.scad`, `.stl` y `.dxf`) diseñados a medida para acoplar la tarjeta física con la NI USB-6210.

3. **Estrategia de Fabricación y Lista de Materiales (BOM):**
   * Ficha técnica de cotización (`ficha_cotizacion_Nidaq_corregido.md`) y lista de componentes THT (`BOM_Nidaq_corregido_LCSC_Manual_THT.csv`), con especificaciones de conectores JST EH de 3 y 6 pines, resistencias axiales y capacitores.

4. **Prototipo de Software Inicial (`prototipo_gui_nidaqmx.py`):**
   * Interfaz gráfica preliminar desarrollada con **PySide6** y **PyQtGraph**.
   * Permite enumerar dispositivos NI-DAQ conectados, seleccionar canales analógicos (`AI`) o digitales (`DI`), configurar modos de terminal (`RSE`, `NRSE`, `DIFF`), rangos de tensión ($\pm 10\text{ V}$) y visualizar lecturas gráficas en tiempo real.

---

## ⚠️ Cuellos de Botella y Limitaciones Heredadas (¡Lectura Obligatoria!)

El material previo representa una base experimental de gran valor, pero **no constituye la solución de ingeniería final**. Presenta limitaciones técnicas críticas que debes resolver a lo largo de tu pasantía:

### 1. En el Hardware y la Circuitería
* **Ganancia y Rango Teórico sin Validación Experimental:**  
  La ganancia de los amplificadores de instrumentación INA114AP se rige teóricamente por la fórmula:
  $$G = 1 + \frac{50\,\text{k}\Omega}{R_G}$$
  En el esquemático no se dispone de la verificación en banco con multímetro patrón de 6.5 dígitos del valor real de $R_G$, de la ganancia efectiva resultante, ni de los límites dinámicos de entrada diferencial antes de alcanzar la saturación del amplificador operacional.
* **Topología de Tierra (RSE vs NRSE vs Diferencial):**  
  En el esquemático coexisten las etiquetas `AGND` y `AISN` (AI Sense). Al muestrear 14 potenciómetros simultáneamente junto a 2 canales de alta ganancia (galgas), existe un riesgo severo de bucles de masa (*ground loops*) e inducción cruzada (*cross-talk*). Debes analizar y justificar la configuración terminal en la NI USB-6210 para garantizar inmunidad electromagnética.

### 2. En el Software Prototipo (`prototipo_gui_nidaqmx.py`)
* **Adquisición por Polling vs Streaming Continuo por Hardware:**  
  El prototipo actual crea y destruye una tarea de `nidaqmx.Task()` en cada ciclo de un `QTimer` para leer una sola muestra de un único canal. Este esquema:
  * Genera una sobrecarga inaceptable en el bus USB y jitter temporal significativo.
  * No aprovecha el convertidor ADC de aproximaciones sucesivas de 250 kSPS ni el búfer FIFO interno de la tarjeta NI.
  * En la **Fase 2** debes reemplazar este enfoque por un motor de adquisición continuo basado en búfer circular (`software/daq_core/`), con temporización gobernada por el reloj de hardware de la NI USB-6210.
* **Muestreo Multicanal Inexistente:**  
  El prototipo solo lee un canal a la vez. El sistema final debe digitalizar los **16 canales analógicos sincronizadamente**.
* **Configuración Rígida (*Hardcoded*):**  
  No cuenta con un archivo externo desacoplado. En la **Fase 2** deberás implementar el parser para `sensors_config.yaml`.
* **Ausencia de Calibración, Cero de Software y Unidades de Ingeniería:**  
  El prototipo solo muestra voltios. No calcula tara dinámica, ni aplica las fórmulas de microdeformación ($\mu\varepsilon$) para galgas ni regresiones lineales para milímetros ($\text{mm}$).
* **Carencia de Filtrado Digital:**  
  Las lecturas presentan ruido directo de red eléctrica (60 Hz). En la **Fase 5** debes incorporar los filtros pasabajas Butterworth digitales ($f_c = 10\text{ Hz}$) mediante `scipy.signal`.
* **Concurrencia GUI / Adquisición:**  
  En el prototipo, la interfaz y la lectura comparten el hilo principal. En la **Fase 6**, el motor DAQ debe correr en un hilo/proceso independiente del renderizado de PyQtGraph para evitar pérdida de muestras.

---

## 🗺️ Mapa de Navegación del Material Proporcionado

Todo el material útil ha sido ubicado de forma limpia en el árbol de directorios del repositorio:

| Ruta en el Repositorio | Contenido | Propósito y Uso Recomendado |
| :--- | :--- | :--- |
| [`docs/hardware/kicad/`](file:///C:/Users/miltonrsa/Documents/git/ppp/ppp-2026-12-daq-ni6210-python/docs/hardware/kicad/) | • `Nidaq.kicad_pro`<br>• `Nidaq.kicad_sch`<br>• `Nidaq_corregido.kicad_pcb`<br>• `NIDAQ.kicad_mod`<br>• `sym-lib-table` / `fp-lib-table` | **Inspección circuital (Fases 1, 3 y 4):** Ábrelo en KiCad para auditar las conexiones del conector `J16`, los pines del INA114AP, las resistencias de ganancia y el ruteo de tierras. |
| [`docs/hardware/bom/`](file:///C:/Users/miltonrsa/Documents/git/ppp/ppp-2026-12-daq-ni6210-python/docs/hardware/bom/) | • `ficha_cotizacion_Nidaq_corregido.md`<br>• `BOM_Nidaq_corregido_JLCPCB.csv`<br>• `BOM_Nidaq_corregido_LCSC_Manual_THT.csv` | **Lista de partes y montaje (Fase 1):** Consulta los números de parte, conectores JST y tolerancias de componentes pasantes para la verificación en banco. |
| [`docs/hardware/3d_enclosure/`](file:///C:/Users/miltonrsa/Documents/git/ppp/ppp-2026-12-daq-ni6210-python/docs/hardware/3d_enclosure/) | • Modelos `.scad`, `.stl` y `.dxf` de caja, bandeja y blindaje | **Ensamble mecánico:** Utilízalo si se requiere fabricar o ajustar la carcasa protectora y el apantallamiento de la tarjeta física. |
| [`python/scripts/prototipo_gui_nidaqmx.py`](file:///C:/Users/miltonrsa/Documents/git/ppp/ppp-2026-12-daq-ni6210-python/python/scripts/prototipo_gui_nidaqmx.py) | Script funcional de prueba con interfaz gráfica PySide6 / PyQtGraph | **Banco de pruebas inicial (Fase 1 y 6):** Ejecútalo para validar rápidamente la detección de la NI USB-6210 y como referencia de componentes visuales en Qt. |

---

## 🚀 Guía de Aprovechamiento Paso a Paso según el Plan de Trabajo (144h)

### Semana 1: Fase 1 — Auditoría Circuital y Setup NI-DAQmx
1. Abre [`docs/hardware/kicad/Nidaq.kicad_sch`](file:///C:/Users/miltonrsa/Documents/git/ppp/ppp-2026-12-daq-ni6210-python/docs/hardware/kicad/Nidaq.kicad_sch) en KiCad.
2. Identifica los amplificadores `U0` y `U1` (INA114AP), ubica sus resistencias de ganancia $R_G$ y calcula la ganancia nominal teórica.
3. Contrasta con el conector `J16` qué pines van a las entradas analógicas de la NI USB-6210 (`ai0` a `ai15`).
4. Conecta la NI USB-6210 y ejecuta [`python/scripts/prototipo_gui_nidaqmx.py`](file:///C:/Users/miltonrsa/Documents/git/ppp/ppp-2026-12-daq-ni6210-python/python/scripts/prototipo_gui_nidaqmx.py) para confirmar que el sistema reconoce la tarjeta física y lee niveles de tensión seguros ($\pm 10\text{ V}$).

### Semanas 2–3: Fase 2 — Arquitectura Modular y Configuración Desacoplada
1. Extrae los patrones útiles de `nidaqmx` del script prototipo (métodos `add_ai_voltage_chan`, enumeraciones de modo terminal) y refactorízalos dentro de la arquitectura orientada a objetos en `software/daq_core/`:
   * `DeviceManager`: inicialización y liberación determinista de tareas `nidaqmx.Task`.
   * `ConfigLoader`: lectura de `sensors_config.yaml`.
   * `Channel`: abstracción con tipo de sensor, modo terminal y calibración.
   * `DataEngine`: adquisición continua multicanal con búfer circular (sustituyendo el `QTimer` del prototipo).

### Semana 4: Fase 3 — Procesamiento y Equilibrado de Puentes de Wheatstone
1. Utiliza el esquemático de KiCad para verificar el puente de galgas (`J17`) y presión (`J1`).
2. Diseña la rutina de tara dinámica (promediado de offset inicial) y programa la conversión a microdeformación ($\mu\varepsilon$) validando la linealidad con resistencias patrón.

### Semanas 5–6: Fase 4 — Calibración de los 14 Potenciómetros
1. Analiza el circuito de los divisores resistivos en KiCad (`R_02` a `R_18` de $220\,\Omega$).
2. Evalúa experimentalmente si el modo `NRSE` (usando `AISN`) ofrece mejor rechazo a ruido que `RSE`.
3. Conecta el potenciómetro al banco micrométrico y calcula regresión lineal ($R^2 \ge 0.9995$) para volcar los coeficientes a `sensors_config.yaml`.

### Semanas 7–8: Fase 5 — Filtrado Butterworth y Persistencia
1. Implementa en `software/daq_core/` el filtro pasabajas digital Butterworth ($f_c = 10\text{ Hz}$) de 4to orden con `scipy.signal`.
2. Establece detección automática de anomalías (saturación $|V| \ge 9.95\text{ V}$ o canal desconectado).
3. Genera la persistencia dual en CSV (`raw_voltages_*.csv` y `engineering_data_*.csv`).

### Semanas 9–10: Fase 6 — GUI en Tiempo Real y Ensayo de Estrés de 24h
1. Toma como inspiración visual los widgets de PyQtGraph de [`prototipo_gui_nidaqmx.py`](file:///C:/Users/miltonrsa/Documents/git/ppp/ppp-2026-12-daq-ni6210-python/python/scripts/prototipo_gui_nidaqmx.py) (`pg.PlotWidget`, barras de nivel, etiquetas de estado).
2. Construye el panel de supervisión completo de los 16 canales asegurando que la GUI corra en un hilo separado del motor de adquisición.
3. Ejecuta la prueba ininterrumpida de 24 a 48 horas registrando la estabilidad térmica y la ausencia de desbordamiento de memoria.
