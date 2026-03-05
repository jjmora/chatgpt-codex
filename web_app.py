#!/usr/bin/env python3
"""Interfaz web para extraer guion/transcripción de videos de YouTube."""

from __future__ import annotations

from flask import Flask, render_template, request

from youtube_script_extractor import extract_script

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/extract")
def extract():
    video = request.form.get("video", "").strip()
    langs_raw = request.form.get("langs", "es en")
    langs = [lang.strip() for lang in langs_raw.replace(",", " ").split() if lang.strip()]
    fallback_model = request.form.get("fallback_model", "small")
    whisper_language = request.form.get("whisper_language", "").strip() or None
    timestamps = request.form.get("timestamps") == "on"

    if not video:
        return render_template(
            "index.html",
            error="Debes pegar una URL o ID de YouTube.",
            previous=request.form,
        )

    try:
        result = extract_script(
            video_input=video,
            languages=langs or ["es", "en"],
            fallback_model=fallback_model,
            whisper_language=whisper_language,
            timestamps=timestamps,
        )
    except Exception as exc:
        return render_template(
            "index.html",
            error=f"No se pudo obtener la transcripción: {exc}",
            previous=request.form,
        )

    return render_template(
        "index.html",
        transcript=result,
        previous=request.form,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
