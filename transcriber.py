
from pathlib import Path
from faster_whisper import WhisperModel

AUDIO_DIR = Path("audio")
OUTPUT_DIR = Path("output")

MODEL_SIZE = "small"
LANGUAGE = "es"

SUPPORTED_FORMATS = {".mp3", ".m4a", ".wav", ".ogg", ".flac"}


def select_audio() -> Path:
    """Muestra los audios disponibles y permite seleccionar uno."""

    AUDIO_DIR.mkdir(exist_ok=True)

    audio_files = sorted(
        file for file in AUDIO_DIR.iterdir()
        if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS
    )

    if not audio_files:
        raise FileNotFoundError(
            f"No se encontraron archivos de audio en {AUDIO_DIR}"
        )

    print("\nAudios disponibles:\n")

    for index, audio in enumerate(audio_files, start=1):
        print(f"{index}. {audio.name}")

    while True:
        try:
            option = int(input("\nSelecciona un audio: "))

            if 1 <= option <= len(audio_files):
                return audio_files[option - 1]

            print("Opción fuera de rango.")

        except ValueError:
            print("Ingresa un número válido.")


def transcribe_audio(audio_path: Path) -> Path:
    """Transcribe el audio y guarda el resultado en TXT."""

    OUTPUT_DIR.mkdir(exist_ok=True)

    output_file = OUTPUT_DIR / f"{audio_path.stem}.txt"

    print(f"\nTranscribiendo: {audio_path.name}", flush=True)

    model = WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type="int8"
    )

    segments, info = model.transcribe(
        str(audio_path),
        language=LANGUAGE,
        beam_size=5,
        vad_filter=True,
        log_progress=True
    )

    print(
        f"Duración del audio: {info.duration / 60:.1f} minutos",
        flush=True
    )

    with output_file.open("w", encoding="utf-8") as file:
        file.write(f"Idioma: {info.language}\n\n")

        for segment in segments:
            timestamp = (
                f"[{segment.start:07.2f}s - "
                f"{segment.end:07.2f}s]"
            )

            file.write(
                f"{timestamp} {segment.text.strip()}\n"
            )

    return output_file



def main():
    audio = select_audio()
    result = transcribe_audio(audio)

    print(f"\nTranscripción finalizada: {result}")


if __name__ == "__main__":
    main()
