import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from software.daq_core.device_manager import DeviceManager
from software.daq_core.data_engine import DataEngine

def prueba_estres_una_hora():
    print("--- Iniciando Prueba de Estrés Continua (1 Hora) ---")
    manager = DeviceManager()
    # Búfer ampliado para a prova de longa duração
    engine = DataEngine(manager, buffer_capacity=50000, samples_per_read=100)

    try:
        engine.start()
        print("[+] DataEngine iniciado. Adquiriendo datos...")
        
        tiempo_inicio = time.monotonic()
        duracion_total = 3600.0  # 3600 segundos = 1 hora
        
        while time.monotonic() - tiempo_inicio < duracion_total:
            engine.raise_if_failed()
            
            # Consumir os dados continuamente para evitar que o búfer se encha
            _ = engine.read(max_samples=500)
            
            muestras_disponibles = engine.buffer.available_samples
            muestras_perdidas = engine.buffer.dropped_samples
            tiempo_transcurrido = time.monotonic() - tiempo_inicio
            
            print(f"  -> Tiempo: {tiempo_transcurrido:.0f}s / 3600s | Búfer: {muestras_disponibles} | Overflow: {muestras_perdidas}", end="\r")
            time.sleep(1.0)
            
        print("\n[+] Prueba de 1 hora completada sin errores.")
        
    except Exception as e:
        print(f"\n[ERROR] Falla durante la adquisición prolongada: {e}")
    finally:
        engine.close()
        print("[+] Motor detenido y recursos de hardware liberados.")

if __name__ == "__main__":
    prueba_estres_una_hora()