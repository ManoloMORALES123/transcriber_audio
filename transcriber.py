import argparse
from pathlib import Path
from typing import Sequence

from faster_whisper import WhisperModel

from transcriber_utils import (
    AUDIO_DIR,
    MODEL_CHOICES,
    OUTPUT_DIR,
    SUPPORTED_FORMATS,
    HardwareProfile,
    detect_hardware,
    select_audio,
    select_transcription_config,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe audio files locally with faster-whisper."
    )
    parser.add_argument(
        "--audio",
        type=Path,
        help="Audio file to transcribe. If omitted, show the interactive list.",
    )
    parser.add_argument(
        "--audio-dir",
        type=Path,
        default=AUDIO_DIR,
        help=f"Directory used by the interactive selector (default: {AUDIO_DIR}).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Directory for transcript files (default: {OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--model",
        choices=("auto", *sorted(MODEL_CHOICES)),
        default="auto",
        help="Whisper model; auto selects one based on available CPU and memory.",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="Decoding beam size; larger values may improve quality but take longer.",
    )
    parser.add_argument(
        "--cpu-threads",
        type=int,
        help="CPU threads to use (default: detected logical CPUs available to WSL).",
    )
    parser.add_argument(
        "--initial-prompt",
        help="Spanish context or domain vocabulary to help recognize names and terms.",
    )
    parser.add_argument(
        "--vad-filter",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Filter silence (default: enabled); use --no-vad-filter if speech is lost.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing transcript with the same filename.",
    )
    return parser.parse_args(argv)


def transcribe_audio(
    audio_path: Path,
    output_dir: Path,
    hardware: HardwareProfile,
    model_name: str,
    beam_size: int,
    cpu_threads: int,
    overwrite: bool = False,
    initial_prompt: str | None = None,
    vad_filter: bool = True,
) -> Path:
    """Transcribe audio and save timestamped segments as UTF-8 text."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{audio_path.stem}.txt"
    if output_file.exists() and not overwrite:
        raise FileExistsError(
            f"El resultado ya existe: {output_file}. "
            "Usa --overwrite para reemplazarlo."
        )

    print(f"\nTranscribiendo: {audio_path.name}", flush=True)
    print(
        f"Recursos detectados: {hardware.cpu_cores} CPU(s), "
        f"{hardware.available_memory_gb:.1f} GB disponibles",
        flush=True,
    )
    print(
        f"Configuración: modelo={model_name}, CPU INT8, "
        f"{cpu_threads} hilo(s), beam_size={beam_size}",
        flush=True,
    )

    model = WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8",
        cpu_threads=cpu_threads,
    )
    segments, info = model.transcribe(
        str(audio_path),
        language="es",
        beam_size=beam_size,
        vad_filter=vad_filter,
        log_progress=True,
        initial_prompt=initial_prompt,
    )

    print(f"Duración del audio: {info.duration / 60:.1f} minutos", flush=True)

    with output_file.open("w", encoding="utf-8") as file:
        file.write(f"Idioma: {info.language}\n\n")
        for segment in segments:
            timestamp = f"[{segment.start:07.2f}s - {segment.end:07.2f}s]"
            file.write(f"{timestamp} {segment.text.strip()}\n")

    return output_file


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    hardware = detect_hardware()
    config = select_transcription_config(
        hardware,
        model=args.model,
        beam_size=args.beam_size,
        cpu_threads=args.cpu_threads,
    )

    if args.audio is None:
        audio_path = select_audio(args.audio_dir)
    else:
        audio_path = args.audio
        if not audio_path.is_file():
            raise FileNotFoundError(f"No se encontró el archivo: {audio_path}")
        if audio_path.suffix.lower() not in SUPPORTED_FORMATS:
            raise ValueError(f"Formato de audio no soportado: {audio_path.suffix}")

    result = transcribe_audio(
        audio_path=audio_path,
        output_dir=args.output_dir,
        hardware=hardware,
        model_name=config.model,
        beam_size=config.beam_size,
        cpu_threads=config.cpu_threads,
        overwrite=args.overwrite,
        initial_prompt=args.initial_prompt,
        vad_filter=args.vad_filter,
    )
    print(f"\nTranscripción finalizada: {result}")


if __name__ == "__main__":
    main()
