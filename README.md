# YouTube Script Extractor

Aplicación en Python para extraer el guion/transcripción de un video de YouTube incluso cuando el video no tiene subtítulos publicados.

Incluye:
- **CLI** para usar desde terminal.
- **UI web** para pegar URL y ejecutar desde navegador.

## Cómo funciona

1. **Primera opción**: intenta leer subtítulos/transcripción de YouTube con `youtube-transcript-api`.
2. **Fallback automático**: si no hay subtítulos, descarga el audio del video y lo transcribe con **Whisper local** (`faster-whisper`).

## Requisitos

- Python 3.10+
- `ffmpeg` instalado en el sistema (necesario para extraer audio)

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso CLI

### ¿Dónde pongo la URL de YouTube?

1. **Directamente en el comando** (recomendado):

```bash
python youtube_script_extractor.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

2. **Sin argumento**: ejecuta el script y te pedirá que pegues la URL:

```bash
python youtube_script_extractor.py
```

Con timestamps:

```bash
python youtube_script_extractor.py "dQw4w9WgXcQ" --timestamps
```

Guardar a archivo:

```bash
python youtube_script_extractor.py "dQw4w9WgXcQ" --output guion.txt
```

## Uso Web UI

Ejecuta la app web:

```bash
python web_app.py
```

Luego abre en tu navegador:

- `http://localhost:8000`

En la UI puedes:
- Pegar URL o ID del video.
- Elegir idiomas de subtítulos preferidos.
- Elegir modelo Whisper de fallback.
- Activar timestamps.
- Ver la transcripción en pantalla.

## Notas

- Si YouTube bloquea la extracción directa de subtítulos, el fallback de Whisper suele resolverlo.
- Modelos Whisper más grandes mejoran precisión, pero consumen más CPU/RAM.
