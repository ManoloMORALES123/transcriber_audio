import os
import warnings
from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
AUDIO_DIR = PROJECT_DIR / "audio"
OUTPUT_DIR = PROJECT_DIR / "output"
SUPPORTED_FORMATS = {".mp3", ".m4a", ".wav", ".ogg", ".flac"}
MODEL_CHOICES = {"tiny", "base", "small", "medium", "large-v3"}


@dataclass(frozen=True)
class HardwareProfile:
    cpu_cores: int
    total_memory_gb: float
    available_memory_gb: float


@dataclass(frozen=True)
class TranscriptionConfig:
    model: str
    cpu_threads: int
    beam_size: int


def _read_integer(path: Path) -> int | None:
    try:
        value = path.read_text(encoding="ascii").strip()
    except OSError:
        return None

    if value == "max":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _memory_from_proc() -> tuple[int | None, int | None]:
    try:
        entries = Path("/proc/meminfo").read_text(encoding="ascii").splitlines()
    except OSError:
        return None, None

    values: dict[str, int] = {}
    for entry in entries:
        name, _, raw_value = entry.partition(":")
        if name in {"MemTotal", "MemAvailable"}:
            try:
                values[name] = int(raw_value.strip().split()[0]) * 1024
            except (IndexError, ValueError):
                continue
    return values.get("MemTotal"), values.get("MemAvailable")


def _cgroup_memory_limit() -> tuple[int | None, int | None]:
    """Return a finite cgroup memory limit and current usage, if present."""
    v2_limit = _read_integer(Path("/sys/fs/cgroup/memory.max"))
    v2_usage = _read_integer(Path("/sys/fs/cgroup/memory.current"))
    if v2_limit is not None and v2_usage is not None:
        return v2_limit, v2_usage

    v1_limit = _read_integer(Path("/sys/fs/cgroup/memory/memory.limit_in_bytes"))
    v1_usage = _read_integer(Path("/sys/fs/cgroup/memory/memory.usage_in_bytes"))
    if v1_limit is not None and v1_usage is not None:
        return v1_limit, v1_usage
    return None, None


def detect_hardware() -> HardwareProfile:
    """Detect CPU affinity and usable memory, including common Linux cgroups."""
    try:
        cpu_cores = len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        detected_cores = os.cpu_count()
        if detected_cores is None:
            warnings.warn(
                "No fue posible detectar los CPU; se usará un hilo.",
                RuntimeWarning,
                stacklevel=2,
            )
        cpu_cores = detected_cores or 1
    cpu_cores = max(1, cpu_cores)

    total_bytes, available_bytes = _memory_from_proc()
    if total_bytes is None:
        try:
            total_bytes = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
        except (AttributeError, OSError, ValueError):
            warnings.warn(
                "No fue posible detectar la memoria; se asumirá un límite de 4 GiB.",
                RuntimeWarning,
                stacklevel=2,
            )
            total_bytes = 4 * 1024**3
    if available_bytes is None:
        warnings.warn(
            "No fue posible detectar la memoria disponible; se usará la memoria total.",
            RuntimeWarning,
            stacklevel=2,
        )
        available_bytes = total_bytes

    limit_bytes, usage_bytes = _cgroup_memory_limit()
    if limit_bytes is not None and usage_bytes is not None:
        total_bytes = min(total_bytes, limit_bytes)
        available_bytes = min(available_bytes, max(0, limit_bytes - usage_bytes))

    return HardwareProfile(
        cpu_cores=cpu_cores,
        total_memory_gb=total_bytes / 1024**3,
        available_memory_gb=available_bytes / 1024**3,
    )


def select_transcription_config(
    hardware: HardwareProfile,
    model: str = "auto",
    beam_size: int = 5,
    cpu_threads: int | None = None,
) -> TranscriptionConfig:
    """Choose a conservative CPU configuration with explicit user overrides."""
    if model != "auto" and model not in MODEL_CHOICES:
        raise ValueError(f"Modelo no soportado: {model}")
    if beam_size < 1:
        raise ValueError("beam_size debe ser al menos 1.")
    if cpu_threads is not None and cpu_threads < 1:
        raise ValueError("cpu_threads debe ser al menos 1.")

    if model == "auto":
        if hardware.cpu_cores >= 4 and hardware.available_memory_gb >= 3.5:
            model = "small"
        elif hardware.cpu_cores >= 2 and hardware.available_memory_gb >= 2:
            model = "base"
        else:
            model = "tiny"

    return TranscriptionConfig(
        model=model,
        cpu_threads=cpu_threads or hardware.cpu_cores,
        beam_size=beam_size,
    )


def select_audio(audio_dir: Path = AUDIO_DIR) -> Path:
    """List supported audio files and ask the user to select one."""
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_files = sorted(
        file
        for file in audio_dir.iterdir()
        if file.is_file() and file.suffix.lower() in SUPPORTED_FORMATS
    )
    if not audio_files:
        raise FileNotFoundError(f"No se encontraron archivos de audio en {audio_dir}")

    print("\nAudios disponibles:\n")
    for index, audio in enumerate(audio_files, start=1):
        print(f"{index}. {audio.name}")

    while True:
        try:
            option = int(input("\nSelecciona un audio: "))
        except ValueError:
            print("Ingresa un número válido.")
            continue

        if 1 <= option <= len(audio_files):
            return audio_files[option - 1]
        print("Opción fuera de rango.")
