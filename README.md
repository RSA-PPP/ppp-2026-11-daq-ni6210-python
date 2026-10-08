# ppp-2026-12-daq-ni6210-python

> **Red Sísmica del Austro (RSA) — Universidad de Cuenca**  
> Prácticas Preprofesionales (PPP) • Instrumentación Virtual, Procesamiento Digital de Señales y Metrología

---

## 📋 Ficha Técnica del Proyecto

| Campo | Detalle |
| :--- | :--- |
| **Código Institucional** | `RSA-PPP-2026-12` |
| **Nombre del Proyecto** | Sistema de Adquisición, Calibración y Caracterización Metrológica de Sensores Geotécnicos en Python (NI USB-6210) |
| **Pasante** | Christopher Carchipulla (`christopher.carchipulla@ucuenca.edu.ec`) |
| **Carrera / Institución** | Ingeniería en Telecomunicaciones — Universidad de Cuenca |
| **Tutor Institucional** | Ing. Milton Muñoz (`milton.munozc@ucuenca.edu.ec`) — RSA |
| **Duración / Horas** | 144 horas (10.5 semanas) • Presencial |
| **Fecha de Ejecución** | 2026-10-01 al 2026-12-18 |
| **Estado** | `En Ejecución` |

---

## 🎯 Descripción General y Objetivos

La Red Sísmica del Austro (RSA) dispone de instrumental geotécnico para la supervisión de deformaciones milimétricas y desplazamientos relativos en presas hidroeléctricas. Este proyecto implementa una suite de instrumentación virtual completa y trazable en **Python 3.10+** gobernando una tarjeta de adquisición de datos **National Instruments NI USB-6210** (16 entradas analógicas, resolución de 16 bits hasta 250 kSPS).

El sistema digitaliza simultáneamente **16 transductores geotécnicos**:
* **2 canales para Puentes de Wheatstone:** Destinados a galgas extensométricas de deformación estructural, con acondicionamiento analógico de ultra bajo ruido mediante amplificadores de instrumentación **INA114AP**.
* **14 canales para sensores potenciométricos:** Destinados a transductores lineales de desplazamiento relativo (vástago/hilo).

La solución desacopla la configuración de los transductores mediante archivos estructurados (`YAML`/`JSON`), aplica equilibrado y cero eléctrico de software (tara dinámica), ejecuta filtrado digital en tiempo real contra ruido de red industrial (60 Hz), genera persistencia dual en CSV/Parquet y ofrece un panel de supervisión gráfica continuo y reactivo en **PyQtGraph**.

### Objetivos Clave
1. **Auditoría de Hardware y Entorno NI-DAQmx:** Validar circuitalmente las ganancias de los amplificadores INA114AP, verificar límites de tensión ($\pm 10\text{ V}$) y configurar el entorno de ejecución en Python con el driver oficial `nidaqmx`.
2. **Arquitectura de Software y Configuración Desacoplada:** Diseñar una arquitectura orientada a objetos modular gobernada por un archivo de configuración externo (`sensors_config.yaml`) para asignar canales, modos de conexión (RSE/NRSE/Diferencial) y parámetros de calibración.
3. **Módulo de Procesamiento para Puentes de Wheatstone:** Implementar equilibrado eléctrico, ajuste dinámico de cero y conversión analítica de microvoltios a microdeformación ($\mu\varepsilon$) con validación por resistencias patrón.
4. **Módulo de Calibración de Desplazamiento Potenciométrico:** Implementar el muestreo síncrono de los 14 canales, evaluando diafonía (*cross-talk*) y ejecutando regresiones lineales metrológicas en banco micrométrico.
5. **Filtrado Digital y Persistencia Segura:** Diseñar filtros digitales pasabajas Butterworth (10 Hz) contra armónicos de 60 Hz, supervisión proactiva de anomalías (saturación y desconexión) y almacenamiento sincronizado en CSV con logs de diagnóstico.
6. **Interfaz Gráfica en Tiempo Real y Ensayo de Estrés:** Desarrollar un panel reactivo en `PyQtGraph` desacoplado del hilo de muestreo y validar la estabilidad en una prueba continua ininterrumpida de 24 a 48 horas.
7. **Documentación Metrológica e Informe Final:** Elaborar manuales de calibración metrológica, guía de troubleshooting e Informe Técnico Final.

> 📄 Para consultar el cronograma detallado semana a semana, la carga horaria y los checkpoints verificables, revisa el [Plan de Trabajo Oficial](docs/planificacion.md).

---

## 🏗️ Arquitectura del Sistema y Flujo de Trabajo

```text
+-----------------------------------------------------------------------------------+
|                        DIAGRAMA DE ARQUITECTURA DEL SISTEMA                       |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Sensores Geotécnicos en Presa]                                                  |
|  ├── 2x Puentes de Wheatstone (Galgas) ---> [Amplificadores INA114AP]            |
|  └── 14x Potenciómetros de Desplazamiento -> [Divisores / Acondicionamiento]      |
|                                                     |                             |
|                                                     v                             |
|                                        [NI USB-6210 DAQ Hardware]                 |
|                                        (16 AI, 16 bits, hasta 250 kSPS)           |
|                                                     |                             |
|                                                     v (USB Bus / NI-DAQmx Driver) |
|  [Software DAQ en Python 3.10+]                     |                             |
|  ├── DeviceManager & ConfigLoader (YAML) <----------+                             |
|  ├── DataEngine (Buffers circulares & Callbacks)                                  |
|  ├── Filtros Digitales Butterworth (fc=10 Hz) & Rutinas de Tara                   |
|  ├── Conversión Metrológica (uε y mm) & Detección de Fallos / Saturación          |
|  └── Persistencia Dual: raw_voltages.csv + engineering_data.csv                   |
|                                                     |                             |
|                                                     v                             |
|  [Interfaz Gráfica en Tiempo Real - PyQtGraph] <----+                             |
|  ├── Cuadrícula de 16 canales con barras de nivel y semáforos de alarma           |
|  └── Osciloscopio multicanal para inspección de tendencias dinámicas              |
+-----------------------------------------------------------------------------------+
```

---

## 📂 Estructura del Repositorio

> [!IMPORTANT]
> **Estructura Raíz Inmutable:** Para mantener la coherencia con los lineamientos institucionales de la RSA, la estructura de carpetas raíz no debe ser alterada ni renombrada sin previa coordinación con el tutor.

```text
ppp-2026-12-daq-ni6210-python/
├── data/
│   ├── evidence/              # Gráficas de calibración, capturas de osciloscopio y logs
│   └── raw_samples/           # Volcados de datos brutos (.csv de prueba, series temporales)
│
├── docs/
│   ├── hardware/              # Esquemáticos del acondicionador, memorias de cálculo INA114AP
│   ├── troubleshooting/       # Bitácora de problemas técnicos, ruidos y soluciones
│   └── planificacion.md       # Documento rector del plan de trabajo (144h) y checkpoints
│
├── software/
│   ├── common/                # Constantes, enumeraciones y estructuras de datos compartidas
│   ├── drivers/               # Envoltorios de bajo nivel para NI-DAQmx
│   ├── daq_core/              # Motor de adquisición, DeviceManager, ConfigLoader y filtros
│   └── tests/                 # Scripts de prueba unitaria, benchmarks y simulación
│
├── python/
│   ├── scripts/               # Scripts de ejecución rápida, calibración y exportación
│   ├── utils/                 # Funciones auxiliares matemáticas, de log y persistencia
│   └── requirements.txt       # Dependencias de software en Python
│
├── README.md                  # Este documento
└── .gitignore                 # Exclusiones de Git
```

---

## 🛠️ Herramientas y Requisitos de Desarrollo

* **Hardware / Instrumental:**
  - Tarjeta de Adquisición de Datos National Instruments **NI USB-6210**.
  - Tarjeta de Acondicionamiento Analógico con amplificadores Burr-Brown / TI **INA114AP**.
  - Multímetro digital de banco de 6.5 dígitos y caja de décadas de resistencias patrón (precisión $\pm 0.05\%$).
  - Banco de desplazamiento micrométrico con micrómetro digital de precisión.
* **Controladores y Drivers:**
  - Controlador oficial **NI-DAQmx** instalado en el sistema operativo.
* **Entorno de Programación:**
  - Python 3.10+ en entorno virtual (`.venv`).
  - Dependencias listadas en `python/requirements.txt`:
    ```bash
    pip install -r python/requirements.txt
    ```

---

## 🚀 Puesta en Marcha

### 1. Clonar el Repositorio
```bash
git clone git@github.com-rsa:RSA-PPP/ppp-2026-12-daq-ni6210-python.git
cd ppp-2026-12-daq-ni6210-python
```

### 2. Configuración del Entorno Virtual de Python
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r python/requirements.txt
```

### 3. Verificación del Hardware DAQ
Ejecutar el diagnóstico rápido para comprobar la detección de la tarjeta NI USB-6210:
```powershell
python -c "import nidaqmx.system; print(nidaqmx.system.System.local().devices)"
```

---

## 🛡️ Reglas de Trabajo y Control de Versiones

Para asegurar la calidad y trazabilidad del proyecto durante las prácticas:

1. **Rama Principal:** La rama activa de trabajo es **`main`**. Realiza commits frecuentes y atómicos al finalizar cada bloque o jornada de trabajo.
2. **Formato de Commits:** Utiliza la convención estándar en minúsculas:
   - `feat: [nueva funcionalidad, clase o módulo de adquisición implementado]`
   - `fix: [corrección de bug en cálculo, filtrado, calibración o script]`
   - `docs: [actualización de documentación técnica, esquemas o bitácora]`
   - `test: [incorporación o ejecución de pruebas de estrés y calibración]`
   - `refactor: [optimización de código sin cambio de comportamiento]`
3. **Integridad de Datos:** No subas archivos temporales pesados de pruebas o series temporales masivas sin comprimir. Apóyate en las reglas definidas en `.gitignore`.

---

## 📞 Contacto y Soporte Institucional

* **Tutor Institucional:** Ing. Milton Muñoz (`milton.munozc@ucuenca.edu.ec`)
* **Institución:** [Red Sísmica del Austro (RSA)](https://redsismicaaustro.github.io/RSA-Metodologias) — Universidad de Cuenca
