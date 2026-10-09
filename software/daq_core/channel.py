from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class PotentiometerCalibration:
    """Almacena los coeficientes metrológicos experimentales del banco de desplazamiento."""
    slope_mm_per_v: float
    intercept_mm: float

@dataclass
class Channel:
    """
    Abstracción de un canal de adquisición geotécnico.
    Responsabilidad exclusiva: Representar y validar parámetros de calibración y hardware
    antes de interactuar con la tarjeta NI-DAQmx.
    """
    id: str
    physical_name: str
    sensor_type: str
    terminal_config: str
    voltage_range: Tuple[float, float]
    engineering_unit: str
    
    # Parámetros exclusivos para Puentes de Wheatstone (Galgas)
    gauge_factor: Optional[float] = None
    excitation_voltage_v: Optional[float] = None
    amplifier_gain: Optional[float] = None
    
    # Parámetros exclusivos para sensores potenciométricos
    calibration: Optional[PotentiometerCalibration] = None

    def validate(self) -> None:
        """
        Ejecuta todas las reglas de validación estructural y metrológica del canal.
        Actúa como barrera de contención por software para proteger el hardware.
        """
        # 1. Validación de nombre físico
        if not self.physical_name.lower().startswith("ai"):
            raise ValueError(f"Nombre físico inválido ({self.physical_name}) en {self.id}. Debe ser 'aiX'.")

        # 2. Validación de rangos (Protección del Hardware)
        if len(self.voltage_range) != 2:
            raise ValueError(f"El rango de voltaje debe tener exactamente dos valores en {self.id}.")
        if self.voltage_range[0] >= self.voltage_range[1]:
            raise ValueError(f"Límite inferior de voltaje debe ser menor al superior en {self.id}.")

        # 3. Validación de configuración de terminal
        valid_terminals = ["RSE", "NRSE", "DIFFERENTIAL"]
        if self.terminal_config.upper() not in valid_terminals:
            raise ValueError(f"Configuración terminal '{self.terminal_config}' no admitida en {self.id}.")

        # 4. Validación de campos obligatorios por tipo de sensor
        if self.sensor_type == "strain_gauge_bridge":
            if None in (self.gauge_factor, self.excitation_voltage_v, self.amplifier_gain):
                raise ValueError(f"Faltan parámetros metrológicos obligatorios para el puente en {self.id}.")
        elif self.sensor_type == "potentiometer_displacement":
            if not self.calibration:
                raise ValueError(f"Faltan coeficientes de calibración para el potenciómetro en {self.id}.")
        else:
            raise ValueError(f"Tipo de sensor '{self.sensor_type}' desconocido en {self.id}.")