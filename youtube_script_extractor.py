#!/usr/bin/env python3
"""Extrae un guion/transcripción de un video de YouTube.

Estrategia:
1. Intenta obtener subtítulos/transcripción disponibles en YouTube.
2. Si no existen, descarga audio y usa Whisper local para transcribir.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlparse


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


def extract_video_id(url_or_id: str) -> str:
    """Extrae el ID de video de una URL de YouTube o devuelve el valor si ya es un ID."""
    raw = url_or_id.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", raw):
        return raw

    parsed = urlparse(raw)
    host = parsed.netloc.lower().replace("www.", "")

    if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_ids = parse_qs(parsed.query).get("v")
            if video_ids and re.fullmatch(r"[A-Za-z0-9_-]{11}", video_ids[0]):
                return video_ids[0]
        if parsed.path.startswith("/shorts/"):
            maybe_id = parsed.path.split("/shorts/")[-1].split("/")[0]
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", maybe_id):
                return maybe_id

    if host == "youtu.be":
        maybe_id = parsed.path.strip("/").split("/")[0]
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", maybe_id):
            return maybe_id

    raise ValueError("No se pudo extraer un ID de video válido.")


def fetch_youtube_transcript(video_id: str, language_priority: Iterable[str]) -> list[TranscriptSegment]:
    """Intenta recuperar subtítulos con youtube-transcript-api."""
    from youtube_transcript_api import YouTubeTranscriptApi

    transcript = YouTubeTranscriptApi().fetch(video_id, languages=list(language_priority))
    return [
        TranscriptSegment(start=float(item.start), end=float(item.start) + float(item.duration), text=item.text.strip())
        for item in transcript
    ]


def transcribe_audio_with_whisper(video_id: str, model_size: str, language: str | None) -> list[TranscriptSegment]:
    """Descarga audio y transcribe localmente con faster-whisper."""
    from faster_whisper import WhisperModel
    import yt_dlp

    with tempfile.TemporaryDirectory(prefix="yt_transcript_") as temp_dir:
        temp_path = Path(temp_dir)
        audio_path = temp_path / f"{video_id}.m4a"

        opts = {
            "format": "bestaudio/best",
            "outtmpl": str(audio_path),
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "192"}],
        }

        url = f"https://www.youtube.com/watch?v={video_id}"
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        wav_path = audio_path.with_suffix(".wav")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments_iter, _ = model.transcribe(str(wav_path), language=language, vad_filter=True)

        return [
            TranscriptSegment(start=seg.start, end=seg.end, text=seg.text.strip())
            for seg in segments_iter
        ]


def render_plain_script(segments: list[TranscriptSegment], with_timestamps: bool) -> str:
    lines: list[str] = []
    for seg in segments:
        if not seg.text:
            continue
        if with_timestamps:
            lines.append(f"[{seg.start:8.2f}s - {seg.end:8.2f}s] {seg.text}")
        else:
            lines.append(seg.text)
    return "\n".join(lines)


def extract_script(
    video_input: str,
    languages: list[str] | None = None,
    fallback_model: str = "small",
    whisper_language: str | None = None,
    timestamps: bool = False,
) -> str:
    """Obtiene la transcripción completa de un video y la devuelve como texto formateado."""
    video_id = extract_video_id(video_input)
    languages = languages or ["es", "en"]

    try:
        segments = fetch_youtube_transcript(video_id, languages)
        source = "youtube_subtitles"
    except Exception:
        segments = transcribe_audio_with_whisper(video_id, fallback_model, whisper_language)
        source = f"whisper:{fallback_model}"

    script = render_plain_script(segments, timestamps)
    header = f"# Video: {video_id}\n# Fuente: {source}\n\n"
    return header + script + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extrae transcripción de YouTube (subtítulos o Whisper local)."
    )
    parser.add_argument("video", nargs="?", help="URL o ID del video de YouTube")
    parser.add_argument("--langs", nargs="+", default=["es", "en"], help="Idiomas preferidos para subtítulos")
    parser.add_argument("--fallback-model", default="small", help="Modelo Whisper de respaldo")
    parser.add_argument("--whisper-language", default=None, help="Idioma forzado para Whisper")
    parser.add_argument("--timestamps", action="store_true", help="Incluir marcas de tiempo")
    parser.add_argument("--output", default=None, help="Archivo de salida")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    video_input = args.video
    if not video_input:
        video_input = input("Pega aquí la URL (o ID) del video de YouTube: ").strip()

    try:
        full_output = extract_script(
            video_input=video_input,
            languages=args.langs,
            fallback_model=args.fallback_model,
            whisper_language=args.whisper_language,
            timestamps=args.timestamps,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"No se pudo obtener transcripción: {exc}", file=sys.stderr)
        return 1

    if args.output:
        Path(args.output).write_text(full_output, encoding="utf-8")
        print(f"Transcripción guardada en: {args.output}")
    else:
        print(full_output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
