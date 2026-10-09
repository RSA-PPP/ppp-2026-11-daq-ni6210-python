import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from software.daq_core.device_manager import DeviceManager


class TestDeviceManager(unittest.TestCase):
    def setUp(self):
        self.loader = Mock()
        self.loader.device_name = "Dev1"
        self.loader.sampling_rate_hz = 100
        self.loader.channels = [
            SimpleNamespace(
                id="CH01",
                physical_name="ai0",
                terminal_config="DIFFERENTIAL",
                voltage_range=(-1.0, 1.0),
            ),
            SimpleNamespace(
                id="CH02",
                physical_name="ai1",
                terminal_config="RSE",
                voltage_range=(0.0, 10.0),
            ),
        ]
        self.task = Mock()
        self.system = SimpleNamespace(
            devices=[SimpleNamespace(name="Dev1")]
        )

        self.manager = DeviceManager(
            config_loader=self.loader,
            task_factory=lambda: self.task,
            system_factory=lambda: self.system,
            samples_per_channel=500,
        )

    def test_initialize_builds_and_reserves_task_from_configuration(self):
        self.manager.initialize()

        self.loader.load_and_validate.assert_called_once_with()
        self.task.ai_channels.add_ai_voltage_chan.assert_any_call(
            physical_channel="Dev1/ai0",
            name_to_assign_to_channel="CH01",
            terminal_config=unittest.mock.ANY,
            min_val=-1.0,
            max_val=1.0,
        )
        self.task.ai_channels.add_ai_voltage_chan.assert_any_call(
            physical_channel="Dev1/ai1",
            name_to_assign_to_channel="CH02",
            terminal_config=unittest.mock.ANY,
            min_val=0.0,
            max_val=10.0,
        )
        self.task.timing.cfg_samp_clk_timing.assert_called_once()
        timing = self.task.timing.cfg_samp_clk_timing.call_args.kwargs
        self.assertEqual(timing["rate"], 100)
        self.assertEqual(timing["samps_per_chan"], 500)
        self.task.control.assert_called_once()

    def test_context_manager_stops_and_closes_started_task(self):
        with self.manager:
            self.manager.start()

        self.task.start.assert_called_once_with()
        self.task.stop.assert_called_once_with()
        self.task.close.assert_called_once_with()
        self.assertIsNone(self.manager.task)

    def test_start_failure_closes_task(self):
        self.manager.initialize()
        self.task.start.side_effect = RuntimeError("start failure")

        with self.assertRaisesRegex(RuntimeError, "start failure"):
            self.manager.start()

        self.task.close.assert_called_once_with()
        self.assertIsNone(self.manager.task)

    def test_missing_device_is_reported_before_task_creation(self):
        self.system.devices = []

        with self.assertRaisesRegex(ValueError, "Dev1"):
            self.manager.initialize()

        self.loader.load_and_validate.assert_called_once_with()
        self.assertIsNone(self.manager.task)


if __name__ == "__main__":
    unittest.main()
