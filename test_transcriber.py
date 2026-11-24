import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from transcriber import transcribe_audio
from transcriber_utils import HardwareProfile


class TranscribeAudioTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.audio_path = self.root / "sample.wav"
        self.output_dir = self.root / "output"
        self.hardware = HardwareProfile(4, 7.8, 4.6)

    def test_existing_transcript_is_preserved_without_overwrite(self):
        self.output_dir.mkdir()
        output_file = self.output_dir / "sample.txt"
        output_file.write_text("previous transcript", encoding="utf-8")

        with patch("transcriber.WhisperModel") as model:
            with self.assertRaises(FileExistsError):
                transcribe_audio(
                    self.audio_path,
                    self.output_dir,
                    self.hardware,
                    "small",
                    5,
                    4,
                )

        model.assert_not_called()
        self.assertEqual(
            output_file.read_text(encoding="utf-8"),
            "previous transcript",
        )

    def test_transcribes_with_selected_cpu_settings_and_writes_segments(self):
        segment = SimpleNamespace(start=0.0, end=1.5, text=" Hola.")
        info = SimpleNamespace(duration=60.0, language="es")
        model_instance = Mock()
        model_instance.transcribe.return_value = ([segment], info)

        with patch("transcriber.WhisperModel", return_value=model_instance) as model:
            output_file = transcribe_audio(
                self.audio_path,
                self.output_dir,
                self.hardware,
                "base",
                3,
                2,
            )

        model.assert_called_once_with(
            "base",
            device="cpu",
            compute_type="int8",
            cpu_threads=2,
        )
        model_instance.transcribe.assert_called_once_with(
            str(self.audio_path),
            language="es",
            beam_size=3,
            vad_filter=True,
            log_progress=True,
            initial_prompt=None,
        )
        self.assertEqual(
            output_file.read_text(encoding="utf-8"),
            "Idioma: es\n\n[0000.00s - 0001.50s] Hola.\n",
        )


if __name__ == "__main__":
    unittest.main()
