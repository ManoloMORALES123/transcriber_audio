# Audio Transcriber

Herramienta CLI desarrollada en Python para convertir archivos de audio a texto mediante **faster-whisper**, utilizando modelos de reconocimiento automático de voz (ASR).

El procesamiento se realiza localmente, sin necesidad de enviar archivos de audio a servicios externos ni consumir tokens de una API de inteligencia artificial.

## 1. Características

- Transcripción automática de audio en español.
- Soporte para archivos M4A, MP3, WAV, OGG y FLAC.
- Procesamiento local mediante Whisper.
- Selección interactiva de archivos disponibles.
- Generación de transcripciones en formato TXT.
- Marcas de tiempo para identificar la ubicación de cada segmento.
- Barra de progreso basada en los segundos de audio transcritos.
- Filtrado de silencios mediante VAD.
- Ejecución mediante CPU, utilizando cuantización INT8.

## 2. Tecnologías

| Tecnología | Propósito |
|---|---|
| Python 3.10+ (probado con Python 3.12) | Lenguaje de desarrollo |
| faster-whisper | Motor de transcripción |
| CTranslate2 | Ejecución optimizada de modelos |
| PyAV | Lectura y decodificación de audio |
| tqdm | Barra de progreso |

## 3. Estructura del proyecto

```text
transcriber_audio/
│
├── audio/
│   └── archivo.m4a
│
├── output/                 # Se crea si no existe
│
├── transcriber.py
├── requirements.txt
└── README.md
```

**Directorios:**

- `audio/`: contiene los archivos de audio que se desean transcribir.
- `output/`: almacena las transcripciones generadas.
- `transcriber.py`: script principal de ejecución.
- `requirements.txt`: dependencias de Python.

## 4. Requisitos previos

- Python 3.10 o superior (el proyecto se verificó con Python 3.12).
- Conexión a Internet durante la primera descarga del modelo Whisper.
- Espacio disponible en disco para almacenar el modelo y las transcripciones.

La dependencia `av` (PyAV), instalada desde `requirements.txt`, se encarga de decodificar los formatos de audio; no es necesario instalar el ejecutable FFmpeg por separado.

## 5. Instalación

Acceder al directorio del proyecto:

```bash
cd transcriber_audio
```

Crear un entorno virtual con Python 3:

```bash
python3 -m venv .venv
```

Activarlo en Linux o macOS:

```bash
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` instala `faster-whisper`, `av` (PyAV) y `tqdm`.

## 6. Configuración

Las principales configuraciones se encuentran al inicio de `transcriber.py`:

```python
AUDIO_DIR = Path("audio")
OUTPUT_DIR = Path("output")

MODEL_SIZE = "small"
LANGUAGE = "es"
```

| Parámetro | Descripción |
|---|---|
| `AUDIO_DIR` | Directorio de entrada de los audios. |
| `OUTPUT_DIR` | Directorio de salida de las transcripciones. |
| `MODEL_SIZE` | Modelo Whisper utilizado. |
| `LANGUAGE` | Idioma de la transcripción. |

### Modelos disponibles

| Modelo | Característica |
|---|---|
| `tiny` | Menor consumo de recursos, menor precisión. |
| `base` | Alternativa ligera. |
| `small` | Equilibrio entre velocidad y precisión. |
| `medium` | Mayor capacidad de reconocimiento, mayor consumo. |
| `large-v3` | Modelo de mayor tamaño, requiere más recursos. |

**Recomendación:** comenzar con `small` y evaluar `medium` si se requiere mejorar la precisión.

La primera ejecución descarga automáticamente el modelo seleccionado. Las siguientes ejecuciones reutilizan el modelo almacenado localmente.

## 7. Ejecución

Colocar los archivos de audio dentro del directorio `audio/`.

Formatos soportados:

- `.m4a`
- `.mp3`
- `.wav`
- `.ogg`
- `.flac`

Ejecutar:

```bash
python transcriber.py
```

El programa mostrará los archivos disponibles:

```text
Audios disponibles:

1. reunion_01.m4a
2. reunion_02.m4a
3. reunion_03.mp3

Selecciona un audio:
```

Ingresar el número correspondiente al archivo que se desea procesar.

Una vez seleccionado, comenzará la transcripción y se mostrará una barra de progreso en segundos de audio. La barra avanza al procesarse cada segmento y se completa cuando finaliza el proceso; no representa una estimación exacta del tiempo de cómputo restante.

## 8. Resultado

El resultado se almacena automáticamente en el directorio `output/`, utilizando el mismo nombre del archivo original y extensión `.txt`.

Ejemplo:

```text
audio/
└── reunion_01.m4a

output/
└── reunion_01.txt
```

### Formato de transcripción

```text
Idioma: es

[0000.00s - 0005.25s] Buenos días, vamos a comenzar con la reunión.

[0005.25s - 0012.80s] El objetivo de hoy es revisar los pendientes del proyecto.

[0012.80s - 0020.45s] Necesitamos validar los servicios desplegados.
```

Las marcas de tiempo permiten localizar cada segmento dentro del audio original.

## 9. Consideraciones técnicas

- La transcripción se realiza localmente, pero la primera descarga del modelo requiere Internet.
- El rendimiento depende del procesador, memoria RAM y modelo seleccionado.
- Los archivos de audio originales no se modifican.
- La transcripción automática puede contener errores en nombres propios, cifras o términos técnicos.
- El filtrado VAD puede omitir fragmentos detectados como silencio; si se sospecha pérdida de contenido, se recomienda comparar con `vad_filter=False`.
- La transcripción no identifica automáticamente a los participantes.
- No se realiza resumen, interpretación ni análisis semántico del contenido.

## 10. Solución de problemas

**Error: No se encontraron archivos de audio**

Verificar que los archivos estén dentro de `audio/` y tengan una extensión soportada.

**Primera ejecución demasiado lenta**

Es normal que la primera ejecución tarde más debido a la descarga del modelo Whisper.

**Consumo elevado de memoria**

Cambiar el modelo a `small`, `base` o `tiny`, dependiendo de los recursos disponibles.

## 11. Próximas mejoras

Funcionalidades consideradas para futuras versiones:

- Generación de archivos SRT.
- Validación para evitar sobrescribir resultados existentes.
- Identificación de participantes (Speaker Diarization).
- Segmentación y limpieza inteligente del texto.
- Integración con modelos LLM para generar resúmenes, acuerdos y tareas.

---

**Proyecto:** Audio Transcriber  
**Versión:** 1.0.0  
**Motor de transcripción:** faster-whisper  
**Formato de salida:** TXT