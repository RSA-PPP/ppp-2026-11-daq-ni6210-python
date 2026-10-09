"""Lifecycle management for NI-DAQmx analog acquisition tasks."""

from __future__ import annotations

from typing import Any, Callable, Optional

import nidaqmx
from nidaqmx.constants import AcquisitionType, TaskMode, TerminalConfiguration
from nidaqmx.system import System

from software.daq_core.channel import Channel
from software.daq_core.config_loader import ConfigLoader


TaskFactory = Callable[[], Any]
SystemFactory = Callable[[], Any]


class DeviceManager:
    """Create, configure, reserve, start, and release a DAQmx task.

    The manager does not read samples. That responsibility belongs to
    ``DataEngine``. It only owns the NI-DAQmx task and its lifecycle.
    """

    _TERMINAL_CONFIGURATIONS = {
        "RSE": TerminalConfiguration.RSE,
        "NRSE": TerminalConfiguration.NRSE,
        "DIFFERENTIAL": TerminalConfiguration.DIFF,
    }

    def __init__(
        self,
        config_loader: Optional[ConfigLoader] = None,
        *,
        config_path: str = "software/sensors_config.yaml",
        samples_per_channel: int = 1000,
        task_factory: TaskFactory = nidaqmx.Task,
        system_factory: SystemFactory = System.local,
    ) -> None:
        if samples_per_channel <= 0:
            raise ValueError("samples_per_channel debe ser mayor que cero.")

        self.config_loader = config_loader or ConfigLoader(config_path)
        self.samples_per_channel = samples_per_channel
        self._task_factory = task_factory
        self._system_factory = system_factory
        self._task: Optional[Any] = None
        self._device: Optional[Any] = None
        self._started = False

    @property
    def task(self) -> Optional[Any]:
        """Return the managed task, or ``None`` before initialization."""
        return self._task

    @property
    def device(self) -> Optional[Any]:
        """Return the resolved NI device, or ``None`` before initialization."""
        return self._device

    def initialize(self) -> None:
        """Load configuration and create a reserved multichannel task."""
        if self._task is not None:
            raise RuntimeError("El DeviceManager ya está inicializado.")

        self.config_loader.load_and_validate()
        self._device = self._resolve_device(self.config_loader.device_name)

        try:
            task = self._task_factory()
            self._configure_channels(task, self.config_loader.channels)
            task.timing.cfg_samp_clk_timing(
                rate=self.config_loader.sampling_rate_hz,
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=self.samples_per_channel,
            )
            task.control(TaskMode.TASK_RESERVE)
        except Exception as error:
            self._close_task_after_initialization_failure(locals().get("task"), error)
            self._device = None
            raise

        self._task = task

    def start(self) -> None:
        """Start the configured hardware-clocked task."""
        if self._task is None:
            raise RuntimeError("Debe inicializar el DeviceManager antes de iniciarlo.")
        if self._started:
            raise RuntimeError("La tarea NI-DAQmx ya está iniciada.")

        try:
            self._task.start()
        except Exception:
            self.close()
            raise
        self._started = True

    def stop(self) -> None:
        """Stop acquisition while keeping the task available for reuse."""
        if self._task is None or not self._started:
            return

        try:
            self._task.stop()
        finally:
            self._started = False

    def close(self) -> None:
        """Stop and close the task, releasing NI-DAQmx resources."""
        task = self._task
        if task is None:
            return

        stop_error: Optional[Exception] = None
        close_error: Optional[Exception] = None
        try:
            self.stop()
        except Exception as error:
            stop_error = error
        finally:
            try:
                task.close()
            except Exception as error:
                close_error = error
            finally:
                self._task = None
                self._device = None
                self._started = False

        if stop_error is not None:
            if close_error is not None:
                raise RuntimeError(
                    "No se pudo detener ni cerrar la tarea NI-DAQmx."
                ) from stop_error
            raise stop_error
        if close_error is not None:
            raise close_error

    def __enter__(self) -> "DeviceManager":
        self.initialize()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        self.close()
        return False

    def _resolve_device(self, device_name: str) -> Any:
        """Resolve the configured device before creating any task."""
        system = self._system_factory()
        for device in system.devices:
            if getattr(device, "name", None) == device_name:
                return device
        raise ValueError(
            f"El dispositivo configurado '{device_name}' no está disponible."
        )

    def _configure_channels(self, task: Any, channels: list[Channel]) -> None:
        for channel in channels:
            try:
                terminal_config = self._TERMINAL_CONFIGURATIONS[
                    channel.terminal_config.upper()
                ]
            except KeyError as error:
                raise ValueError(
                    f"Configuración terminal no soportada para {channel.id}: "
                    f"{channel.terminal_config}"
                ) from error

            task.ai_channels.add_ai_voltage_chan(
                physical_channel=self._qualify_channel(channel),
                name_to_assign_to_channel=channel.id,
                terminal_config=terminal_config,
                min_val=channel.voltage_range[0],
                max_val=channel.voltage_range[1],
            )

    def _qualify_channel(self, channel: Channel) -> str:
        if "/" in channel.physical_name:
            return channel.physical_name
        return f"{self.config_loader.device_name}/{channel.physical_name}"

    @staticmethod
    def _close_task_after_initialization_failure(
        task: Any,
        original_error: Exception,
    ) -> None:
        if task is not None:
            try:
                task.close()
            except Exception:
                raise RuntimeError(
                    "La inicialización falló y tampoco se pudo cerrar la tarea."
                ) from original_error