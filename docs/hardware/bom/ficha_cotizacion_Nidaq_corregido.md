# Ficha Técnica y Estrategia de Cotización JLCPCB

**Proyecto**: `Nidaq_corregido`  
**Estrategia de Fabricación**: Ensamblaje Mixto RSA (SMD Robotizado por JLCPCB + THT Conectores sueltos en LCSC).

---

## 1. 📐 Fabricación del PCB (Calculadora JLCPCB)

| Parámetro | Valor Recomendado |
| :--- | :--- |
| **Dimensiones** | `162.0 mm × 207.4 mm` |
| **Capas** | `2 capas` |
| **Cantidad** | `5 piezas` |
| **Material** | `FR-4 Standard Tg 130-140°C` |
| **Espesor de Placa** | `1.6 mm` |
| **Grosor de Cobre** | `1 oz (35 µm)` |
| **Acabado Superficial** | `HASL Lead-Free` o `ENIG` |
| **Color Máscara** | `Verde` (económico y rápido) |
| **Archivo Gerber** | `gerbers_Nidaq_corregido.zip` |

---

## 2. 🤖 Ensamblaje SMT Robotizado (PCBA JLCPCB)

| Parámetro SMT | Valor |
| :--- | :--- |
| **Tipo de Ensamble** | `Single-sided (Top side)` |
| **BOM para el Robot** | `BOM_Nidaq_corregido_JLCPCB_SMD_Robot.csv` |
| **CPL para el Robot** | `CPL_Nidaq_corregido_JLCPCB.csv` |
| **Optimización de Costo** | Solo piezas SMD básicas (\$0 USD tarifa de feeder). |

---

## 3. 📦 Piezas Sueltas para Envío Consolidado (LCSC)

| Archivo de Piezas | Acción |
| :--- | :--- |
| **Lista THT / Conectores** | `BOM_Nidaq_corregido_LCSC_Manual_THT.csv` |
| **Método de Compra** | Agregar al carrito de LCSC y marcar *"Combine with JLCPCB order"*. |
| **Montaje** | Llegan sueltos en la misma caja para soldar a mano con cautín. |
