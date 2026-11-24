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
├── transcriber_utils.py    # Detección de recursos y utilidades de selección
├── test_transcriber_utils.py
├── requirements.txt
└── README.md
```

**Directorios:**

- `audio/`: contiene los archivos de audio que se desean transcribir.
- `output/`: almacena las transcripciones generadas.
- `transcriber.py`: CLI y coordinación de la transcripción.
- `transcriber_utils.py`: detección de recursos y funciones auxiliares.
- `test_transcriber_utils.py`: pruebas de la configuración automática.
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

Por defecto, el programa detecta los CPU disponibles para el proceso y la memoria disponible (incluyendo límites habituales de cgroup en Linux/WSL). Selecciona un modelo conservador para esos recursos:

| Recursos detectados | Modelo automático |
|---|---|
| 4 o más CPU y al menos 3.5 GB disponibles | `small` |
| 2 o más CPU y al menos 2 GB disponibles | `base` |
| Menos recursos | `tiny` |

En una sesión WSL con 4 CPU y 8 GB de RAM, normalmente seleccionará `small`, usará INT8 y asignará un hilo por CPU disponible. La detección usa memoria disponible, por lo que puede elegir un modelo menor si otros procesos están consumiendo RAM. `beam_size=5` se mantiene para no sacrificar calidad automáticamente; puede reducirse manualmente para priorizar velocidad.

Las carpetas `audio/` y `output/` se resuelven desde la ubicación del script, no desde el directorio actual. Se pueden cambiar con `--audio-dir` y `--output-dir`. Si se modifica el modelo o los parámetros, se puede comprobar la selección con `--help`.

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

También se puede indicar directamente el archivo:

```bash
python transcriber.py --audio audio/reunion_01.m4a
```

Opciones habituales:

```bash
python transcriber.py --help
python transcriber.py --model base
python transcriber.py --beam-size 3
python transcriber.py --cpu-threads 2
python transcriber.py --output-dir transcripciones
```

`--model auto` es el valor predeterminado. `--model` admite `tiny`, `base`, `small`, `medium` y `large-v3`. Para evitar reemplazos accidentales, si ya existe un TXT con el mismo nombre, el programa se detiene; pasar `--overwrite` para reemplazarlo intencionalmente.

Para ayudar con nombres propios y vocabulario especializado, se puede proporcionar contexto con `--initial-prompt "..."`. Si el filtro de silencios parece omitir voz, probar `--no-vad-filter`; por defecto permanece habilitado.

Para ejecutar las pruebas de la configuración automática:

```bash
python -m unittest -v test_transcriber_utils
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

Usar `--model base` o `--model tiny`, o cerrar otras aplicaciones para liberar memoria. `--model auto` también reduce el modelo según los recursos disponibles detectados.

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