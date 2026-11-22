"""End-to-end PDF -> audio file conversion, shared by the GUI and CLI."""

import os
from typing import Callable, Optional

from .extract import extract_text
from .synth import Synthesizer, save_audio

StatusFn = Callable[[str], None]


class ConversionError(Exception):
    """A user-facing problem (e.g. scanned PDF with no text)."""


def default_output_path(pdf_path: str) -> str:
    return os.path.splitext(pdf_path)[0] + ".mp3"


def convert_pdf(pdf_path: str, voice: str, speed: float = 1.0,
                out_path: Optional[str] = None,
                synth: Optional[Synthesizer] = None,
                on_status: Optional[StatusFn] = None) -> str:
    """Convert a PDF to speech. Returns the path of the audio file written."""
    status = on_status or (lambda _msg: None)
    synth = synth or Synthesizer()
    out_path = out_path or default_output_path(pdf_path)

    status("Extracting text...")
    text = extract_text(pdf_path)
    if not text:
        raise ConversionError("No extractable text found (is it a scanned PDF?).")

    if not synth.is_loaded(voice):
        status("Loading voice model (first run downloads ~330 MB)...")

    audio = synth.synthesize(
        text, voice=voice, speed=speed,
        on_progress=lambda p: status(f"Synthesising... {p:.0%}"),
    )
    if audio.size == 0:
        raise ConversionError("Nothing was synthesised.")

    status("Saving audio...")
    return save_audio(audio, out_path)
