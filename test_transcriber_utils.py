import unittest

from transcriber_utils import (
    HardwareProfile,
    detect_hardware,
    select_transcription_config,
)


class TranscriptionConfigTests(unittest.TestCase):
    def test_auto_selects_small_model_for_four_cores_and_eight_gb_class_machine(self):
        hardware = HardwareProfile(
            cpu_cores=4,
            total_memory_gb=7.8,
            available_memory_gb=4.6,
        )

        config = select_transcription_config(hardware)

        self.assertEqual(config.model, "small")
        self.assertEqual(config.cpu_threads, 4)
        self.assertEqual(config.beam_size, 5)

    def test_auto_reduces_model_when_resources_are_limited(self):
        hardware = HardwareProfile(
            cpu_cores=2,
            total_memory_gb=4.0,
            available_memory_gb=1.5,
        )

        self.assertEqual(select_transcription_config(hardware).model, "tiny")

    def test_manual_options_override_detected_defaults(self):
        hardware = HardwareProfile(
            cpu_cores=4,
            total_memory_gb=7.8,
            available_memory_gb=4.6,
        )

        config = select_transcription_config(
            hardware,
            model="base",
            beam_size=3,
            cpu_threads=2,
        )

        self.assertEqual(config.model, "base")
        self.assertEqual(config.cpu_threads, 2)
        self.assertEqual(config.beam_size, 3)

    def test_rejects_invalid_tuning_values(self):
        hardware = HardwareProfile(4, 7.8, 4.6)

        with self.assertRaises(ValueError):
            select_transcription_config(hardware, beam_size=0)
        with self.assertRaises(ValueError):
            select_transcription_config(hardware, cpu_threads=0)

    def test_detects_positive_cpu_and_memory_values(self):
        hardware = detect_hardware()

        self.assertGreaterEqual(hardware.cpu_cores, 1)
        self.assertGreater(hardware.total_memory_gb, 0)
        self.assertGreaterEqual(hardware.available_memory_gb, 0)


if __name__ == "__main__":
    unittest.main()
