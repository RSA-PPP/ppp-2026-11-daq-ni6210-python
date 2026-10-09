import yaml
from pathlib import Path
from typing import List, Dict, Any

# Ajusta la ruta de importación según la estructura de tu proyecto
from software.daq_core.channel import Channel, PotentiometerCalibration

class ConfigLoader:
    """
    Carga, parsea y valida la configuración del sistema DAQ desde un archivo YAML.
    Garantiza que la configuración externa sea íntegra antes de inicializar el hardware.
    """
    def __init__(self, config_path: str = "software/sensors_config.yaml"):
        self.config_path = Path(config_path)
        self.device_name = ""
        self.sampling_rate_hz = 0
        self.channels: List[Channel] = []

    def load_and_validate(self) -> None:
        """Ejecuta el flujo completo de lectura y validación estricta."""
        raw_data = self._read_yaml()
        self._parse_global_settings(raw_data)
        self._parse_channels(raw_data)
        self._validate_global_integrity()

    def _read_yaml(self) -> Dict[str, Any]:
        """Abre el archivo YAML y reporta errores de existencia o sintaxis."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"[ERROR] El archivo de configuración no existe en: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as file:
            try:
                return yaml.safe_load(file) or {}
            except yaml.YAMLError as exc:
                raise ValueError(f"[ERROR] Sintaxis inválida en el archivo YAML:\n{exc}")

    def _parse_global_settings(self, data: Dict[str, Any]) -> None:
        """Extrae y valida los parámetros generales del sistema."""
        self.device_name = data.get("device_name")
        if not self.device_name:
            raise ValueError("[ERROR] Falta el parámetro obligatorio 'device_name' en la raíz del YAML.")
        
        self.sampling_rate_hz = data.get("sampling_rate_hz", 0)
        if not isinstance(self.sampling_rate_hz, (int, float)) or self.sampling_rate_hz <= 0:
            raise ValueError("[ERROR] El 'sampling_rate_hz' debe ser un número positivo mayor a 0.")

    def _parse_channels(self, data: Dict[str, Any]) -> None:
        """Transforma la lista de diccionarios YAML en objetos Channel tipados."""
        channels_data = data.get("channels", [])
        if not channels_data:
            raise ValueError("[ERROR] No se encontraron canales en la configuración ('channels').")

        for ch_dict in channels_data:
            # Extraer y estructurar el bloque de calibración si existe
            cal_data = ch_dict.pop("calibration", None)
            calibration_obj = PotentiometerCalibration(**cal_data) if cal_data else None
            
            try:
                # Inyectar datos en nuestro modelo y ejecutar la validación individual
                channel = Channel(**ch_dict, calibration=calibration_obj)
                channel.validate()
                self.channels.append(channel)
            except TypeError as exc:
                raise ValueError(f"[ERROR] Atributos inválidos en el canal {ch_dict.get('id', 'Desconocido')}: {exc}")

    def _validate_global_integrity(self) -> None:
        """Valida reglas arquitectónicas, como la prevención de canales duplicados."""
        seen_ids = set()
        seen_physical = set()

        for ch in self.channels:
            if ch.id in seen_ids:
                raise ValueError(f"[ERROR] Conflicto: El identificador lógico '{ch.id}' está duplicado.")
            if ch.physical_name in seen_physical:
                raise ValueError(f"[ERROR] Conflicto Hardware: El puerto físico '{ch.physical_name}' está asignado a múltiples canales.")
            
            seen_ids.add(ch.id)
            seen_physical.add(ch.physical_name)