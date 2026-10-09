import unittest
import sys
from pathlib import Path

# Asegurar que el directorio raíz está en el path para poder importar 'software'
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from software.daq_core.config_loader import ConfigLoader

class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        """Prepara el entorno antes de cada prueba."""
        # Apunta al archivo YAML real que creamos en el Paso 1
        self.config_path = "software/sensors_config.yaml"

    def test_load_and_validate_success(self):
        """Verifica que el YAML oficial se cargue y valide sin errores."""
        loader = ConfigLoader(config_path=self.config_path)
        
        # Si el YAML tiene errores, esto lanzará una excepción y la prueba fallará
        loader.load_and_validate()
        
        # Validaciones de integridad sobre los datos cargados
        self.assertEqual(loader.device_name, "Dev1", "El device_name no coincide.")
        self.assertEqual(loader.sampling_rate_hz, 100, "El sampling_rate_hz no coincide.")
        self.assertEqual(len(loader.channels), 16, "No se cargaron los 16 canales esperados.")
        
        print("\n[+] Prueba superada: ConfigLoader interpretó correctamente los 16 canales del YAML.")

if __name__ == "__main__":
    unittest.main()