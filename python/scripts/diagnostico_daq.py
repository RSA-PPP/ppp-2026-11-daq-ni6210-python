"""Diagnose NI-DAQmx installation and enumerate connected devices."""

from __future__ import annotations

import platform
import sys
from collections.abc import Callable


IMPORT_ERROR = 1
DAQ_ACCESS_ERROR = 2
ENUMERATION_ERROR = 3
NO_DEVICE_ERROR = 4
PRODUCT_ERROR = 5
SELF_TEST_ERROR = 6


def _print_resource_group(
    label: str,
    getter: Callable[[], object],
) -> None:
    """Print a device resource group while reporting query errors."""
    try:
        resources = getter()
        names = list(resources)
    except Exception as error:
        print(f"  {label}: ERROR ({type(error).__name__}: {error})")
        return

    print(f"  {label}: {len(names)}")
    for resource in names:
        print(f"    - {getattr(resource, 'name', resource)}")


def main() -> int:
    print("NI-DAQmx diagnostic")
    print(f"Python: {platform.python_version()}")

    try:
        import nidaqmx
        from nidaqmx.errors import DaqNotFoundError
        from nidaqmx.system import System
    except ImportError as error:
        print(f"FAIL: importar nidaqmx ({error})", file=sys.stderr)
        return IMPORT_ERROR

    print("PASS: nidaqmx importable")
    print(f"nidaqmx: {getattr(nidaqmx, '__version__', 'unknown')}")

    try:
        system = System.local()
    except DaqNotFoundError as error:
        print(
            "FAIL: acceder a NI-DAQmx (no se encontro NI-DAQmx en este equipo). "
            f"Detalle: {error}",
            file=sys.stderr,
        )
        return DAQ_ACCESS_ERROR
    except Exception as error:
        print(
            f"FAIL: acceder a NI-DAQmx ({type(error).__name__}: {error})",
            file=sys.stderr,
        )
        return DAQ_ACCESS_ERROR

    try:
        devices = list(system.devices)
    except Exception as error:
        print(
            f"FAIL: enumerar dispositivos ({type(error).__name__}: {error})",
            file=sys.stderr,
        )
        return ENUMERATION_ERROR

    if not devices:
        print("Dispositivos detectados: 0")
        print("FAIL: dispositivo detectado (no hay dispositivos enumerados)")
        return NO_DEVICE_ERROR

    print("PASS: NI-DAQmx accesible")
    print("PASS: dispositivo detectado")
    print(f"Dispositivos detectados: {len(devices)}")
    usb_6210_devices = []

    for device in devices:
        print(f"\nDispositivo: {device.name}")
        try:
            product_type = device.product_type
            print(f"  Tipo de producto: {product_type}")
            if "USB-6210" in product_type.upper():
                usb_6210_devices.append(device)
                print("  PASS: producto identificado como NI USB-6210")
            else:
                print("  INFO: producto distinto de NI USB-6210")
        except Exception as error:
            print(
                "  FAIL: identificar producto "
                f"({type(error).__name__}: {error})",
                file=sys.stderr,
            )

        for label, getter in (
            ("Numero de serie", lambda: device.serial_num),
            ("AI fisicas", lambda: device.ai_physical_chans),
            ("AO fisicas", lambda: device.ao_physical_chans),
            ("CI fisicas", lambda: device.ci_physical_chans),
            ("Lineas DO", lambda: device.do_lines),
        ):
            if label.endswith("fisicas") or label == "Lineas DO":
                _print_resource_group(label, getter)
                continue

            try:
                print(f"  {label}: {getter()}")
            except Exception as error:
                print(
                    f"  {label}: ERROR "
                    f"({type(error).__name__}: {error})"
                )

    if not usb_6210_devices:
        print(
            "FAIL: producto identificado "
            "(no se detecto una NI USB-6210)",
            file=sys.stderr,
        )
        return PRODUCT_ERROR

    for device in usb_6210_devices:
        try:
            device.self_test_device()
        except Exception as error:
            print(
                f"FAIL: self-test de {device.name} "
                f"({type(error).__name__}: {error})",
                file=sys.stderr,
            )
            return SELF_TEST_ERROR
        print(f"PASS: self-test exitoso ({device.name})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
