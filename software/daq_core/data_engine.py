"""Continuous multichannel acquisition and bounded circular buffering."""

from __future__ import annotations

from collections import deque
from threading import Event, Lock, Thread, current_thread
from typing import Optional

import numpy as np

from software.daq_core.device_manager import DeviceManager


class CircularSampleBuffer:
    """Thread-safe sample ring with a fixed capacity per channel."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity debe ser mayor que cero.")
        self.capacity = capacity
        self._samples: deque[np.ndarray] = deque(maxlen=capacity)
        self._channel_count: Optional[int] = None
        self._dropped_samples = 0
        self._lock = Lock()

    @property
    def available_samples(self) -> int:
        with self._lock:
            return len(self._samples)

    @property
    def channel_count(self) -> Optional[int]:
        with self._lock:
            return self._channel_count

    @property
    def dropped_samples(self) -> int:
        with self._lock:
            return self._dropped_samples

    def append(self, block: np.ndarray) -> None:
        """Append a block shaped as ``[channels, samples]``."""
        values = np.asarray(block, dtype=float)
        if values.ndim != 2:
            raise ValueError("El bloque debe tener forma [canales, muestras].")
        if values.shape[1] == 0:
            return

        with self._lock:
            if self._channel_count is None:
                self._channel_count = values.shape[0]
            elif values.shape[0] != self._channel_count:
                raise ValueError(
                    "El bloque no coincide con el número de canales del búfer."
                )

            for sample_index in range(values.shape[1]):
                if len(self._samples) == self.capacity:
                    self._dropped_samples += 1
                self._samples.append(values[:, sample_index].copy())

    def read(self, max_samples: Optional[int] = None) -> np.ndarray:
        """Remove and return samples as ``[channels, samples]``."""
        with self._lock:
            if not self._samples:
                channel_count = self._channel_count or 0
                return np.empty((channel_count, 0), dtype=float)

            count = len(self._samples)
            if max_samples is not None:
                if max_samples <= 0:
                    raise ValueError("max_samples debe ser mayor que cero.")
                count = min(count, max_samples)

            samples = [self._samples.popleft() for _ in range(count)]
            return np.stack(samples, axis=1)


class DataEngine:
    """Read continuous blocks from one ``DeviceManager`` in a worker thread."""

    def __init__(
        self,
        device_manager: DeviceManager,
        *,
        buffer_capacity: int = 10_000,
        samples_per_read: int = 100,
        read_timeout: float = 1.0,
    ) -> None:
        if samples_per_read <= 0:
            raise ValueError("samples_per_read debe ser mayor que cero.")
        if read_timeout <= 0:
            raise ValueError("read_timeout debe ser mayor que cero.")

        self.device_manager = device_manager
        self.samples_per_read = samples_per_read
        self.read_timeout = read_timeout
        self.buffer = CircularSampleBuffer(buffer_capacity)
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._error: Optional[Exception] = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def error(self) -> Optional[Exception]:
        return self._error

    def start(self) -> None:
        """Initialize, start, and launch the continuous reader."""
        if self.is_running:
            raise RuntimeError("El DataEngine ya está ejecutándose.")

        self._error = None
        self._stop_event.clear()
        self.device_manager.initialize()
        try:
            self.device_manager.start()
            self._thread = Thread(
                target=self._acquisition_loop,
                name="daq-data-engine",
                daemon=True,
            )
            self._thread.start()
        except Exception:
            self.device_manager.close()
            raise

    def stop(self) -> None:
        """Request termination and wait for the reader to finish."""
        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread is not current_thread():
            thread.join(timeout=self.read_timeout + 1.0)
            if thread.is_alive():
                raise TimeoutError(
                    "El hilo de adquisición no terminó dentro del tiempo esperado."
                )
        self._thread = None
        self.device_manager.stop()

    def close(self) -> None:
        """Stop acquisition and release the NI-DAQmx task."""
        try:
            self.stop()
        finally:
            self.device_manager.close()

    def read(self, max_samples: Optional[int] = None) -> np.ndarray:
        """Consume buffered samples without exposing internal storage."""
        return self.buffer.read(max_samples)

    def raise_if_failed(self) -> None:
        """Raise the worker error in the consumer thread, if any."""
        if self._error is not None:
            raise RuntimeError("La adquisición continua falló.") from self._error

    def _acquisition_loop(self) -> None:
        task = self.device_manager.task
        if task is None:
            self._error = RuntimeError(
                "El DeviceManager no expone una tarea inicializada."
            )
            return

        try:
            while not self._stop_event.is_set():
                raw_block = task.read(
                    number_of_samples_per_channel=self.samples_per_read,
                    timeout=self.read_timeout,
                )
                block = self._normalize_block(raw_block)
                self.buffer.append(block)
        except Exception as error:
            self._error = error
            self._stop_event.set()
        finally:
            self.device_manager.stop()

    @staticmethod
    def _normalize_block(raw_block: object) -> np.ndarray:
        values = np.asarray(raw_block, dtype=float)
        if values.ndim == 1:
            values = values.reshape(1, -1)
        if values.ndim != 2 or values.shape[1] == 0:
            raise ValueError(
                "La lectura NI-DAQmx debe contener datos con forma "
                "[canales, muestras]."
            )
        return values