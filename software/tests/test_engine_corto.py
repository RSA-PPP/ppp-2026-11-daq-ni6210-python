import sys
import time
from pathlib import Path

# Asegurar que el directorio raíz está en el path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from software.daq_core.device_manager import DeviceManager
from software.daq_core.data_engine import DataEngine

def prueba_corta_adquisicion():
    print("--- Iniciando Prueba Corta de Adquisición Continua (10 segundos) ---")
    
    # Instanciamos los componentes del núcleo
    manager = DeviceManager()
    # Búfer de 10,000 muestras, leyendo bloques de 100 muestras a la vez
    engine = DataEngine(manager, buffer_capacity=10000, samples_per_read=100)
    
    try:
        engine.start()
        print("[+] DataEngine iniciado correctamente. Adquiriendo datos...")
        
        tiempo_inicio = time.monotonic()
        while time.monotonic() - tiempo_inicio < 10.0:
            # Revisar si el hilo trabajador reportó algún error crítico
            engine.raise_if_failed()
            
            muestras_disponibles = engine.buffer.available_samples
            muestras_perdidas = engine.buffer.dropped_samples
            
            print(f"  -> Búfer: {muestras_disponibles} muestras disponibles | Perdidas (overflow): {muestras_perdidas}", end="\r")
            time.sleep(1.0)
            
        print("\n[+] Tiempo de prueba completado. Extrayendo un bloque de lectura...")
        
        # Leer todo lo acumulado
        bloque_final = engine.read()
        print(f"[+] Bloque extraído exitosamente. Forma: {bloque_final.shape} (Canales, Muestras)")
        
    except Exception as e:
        print(f"\n[ERROR] Falla durante la adquisición: {e}")
    finally:
        engine.close()
        print("[+] Motor detenido y recursos de hardware liberados.")

if __name__ == "__main__":
    prueba_corta_adquisicion()