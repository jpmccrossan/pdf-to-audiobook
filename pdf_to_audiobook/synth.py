"""Text-to-speech with Kokoro, and writing the result to disk."""

import os
from typing import Callable, Optional

import numpy as np
import soundfile as sf

from .config import SAMPLE_RATE, lang_for
from .device import detect_device

ProgressFn = Callable[[float], None]  # receives 0.0 .. 1.0


class Synthesizer:
    """Wraps Kokoro, caching one pipeline per language so the model loads once."""

    def __init__(self, device: Optional[str] = None):
        self.device = device or detect_device()
        self._pipelines = {}

    def _pipeline(self, lang_code: str):
        if lang_code not in self._pipelines:
            from kokoro import KPipeline  # heavy import, defer until needed
            self._pipelines[lang_code] = KPipeline(
                lang_code=lang_code, repo_id="hexgrad/Kokoro-82M", device=self.device)
        return self._pipelines[lang_code]

    def is_loaded(self, voice: str) -> bool:
        return lang_for(voice) in self._pipelines

    def synthesize(self, text: str, voice: str, speed: float = 1.0,
                   on_progress: Optional[ProgressFn] = None) -> np.ndarray:
        """Return the spoken text as a float32 mono array at SAMPLE_RATE."""
        pipeline = self._pipeline(lang_for(voice))
        total = max(len(text), 1)
        done = 0
        parts = []

        # Kokoro yields one result per sentence-ish segment.
        for result in pipeline(text, voice=voice, speed=speed):
            if result.audio is not None:
                parts.append(_to_numpy(result.audio))
            done += len(result.graphemes or "")
            if on_progress:
                on_progress(min(done / total, 1.0))

        if not parts:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(parts)


def save_audio(audio: np.ndarray, out_path: str) -> str:
    """Write audio to out_path. If MP3 isn't supported, falls back to .wav.

    Returns the path actually written.
    """
    try:
        sf.write(out_path, audio, SAMPLE_RATE)
        return out_path
    except Exception:
        # MP3 needs libsndfile >= 1.1 (bundled with recent soundfile wheels).
        wav_path = os.path.splitext(out_path)[0] + ".wav"
        sf.write(wav_path, audio, SAMPLE_RATE)
        return wav_path


def _to_numpy(audio) -> np.ndarray:
    if hasattr(audio, "detach"):  # torch tensor
        audio = audio.detach().cpu().numpy()
    return np.asarray(audio, dtype=np.float32)
