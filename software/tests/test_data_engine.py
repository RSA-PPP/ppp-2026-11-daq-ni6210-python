import time
import unittest
from unittest.mock import Mock

import numpy as np

from software.daq_core.data_engine import CircularSampleBuffer, DataEngine


class TestCircularSampleBuffer(unittest.TestCase):
    def test_preserves_channel_sample_shape(self):
        buffer = CircularSampleBuffer(capacity=4)
        buffer.append(np.array([[1, 2], [10, 20]], dtype=float))

        np.testing.assert_array_equal(
            buffer.read(),
            np.array([[1, 2], [10, 20]], dtype=float),
        )

    def test_drops_oldest_samples_and_counts_overflow(self):
        buffer = CircularSampleBuffer(capacity=2)
        buffer.append(np.array([[1, 2, 3]], dtype=float))

        np.testing.assert_array_equal(
            buffer.read(),
            np.array([[2, 3]], dtype=float),
        )
        self.assertEqual(buffer.dropped_samples, 1)


class TestDataEngine(unittest.TestCase):
    def setUp(self):
        self.task = Mock()
        self.task.read.side_effect = [
            [[1, 2], [10, 20]],
            RuntimeError("lectura fallida"),
        ]
        self.manager = Mock()
        self.manager.task = self.task
        self.engine = DataEngine(
            self.manager,
            buffer_capacity=10,
            samples_per_read=2,
            read_timeout=0.1,
        )

    def test_reads_blocks_and_reports_worker_error(self):
        self.engine.start()
        deadline = time.monotonic() + 1.0
        while self.engine.is_running and time.monotonic() < deadline:
            time.sleep(0.01)

        self.assertFalse(self.engine.is_running)
        with self.assertRaisesRegex(RuntimeError, "adquisición continua falló"):
            self.engine.raise_if_failed()

    def test_read_returns_buffered_multichannel_samples(self):
        self.task.read.side_effect = lambda **kwargs: [[1, 2], [10, 20]]
        self.engine.start()
        deadline = time.monotonic() + 1.0
        while self.engine.buffer.available_samples < 2 and time.monotonic() < deadline:
            time.sleep(0.01)

        result = self.engine.read(max_samples=2)
        self.assertEqual(result.shape, (2, 2))
        np.testing.assert_array_equal(
            result,
            np.array([[1, 2], [10, 20]], dtype=float),
        )
        self.engine.close()

    def test_close_stops_and_releases_manager(self):
        self.task.read.side_effect = lambda **kwargs: [[1], [2]]
        self.engine.start()
        time.sleep(0.02)
        self.engine.close()

        self.manager.stop.assert_called()
        self.manager.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
