"""Static configuration: voices, audio settings, speed limits."""

# Label -> Kokoro voice ID.
# The ID prefix encodes accent and gender: a=American, b=British | f=female, m=male.
# Full voice list: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
VOICES = {
    "George (UK, male)":     "bm_george",
    "Lewis (UK, male)":      "bm_lewis",
    "Emma (UK, female)":     "bf_emma",
    "Isabella (UK, female)": "bf_isabella",
    "Michael (US, male)":    "am_michael",
    "Adam (US, male)":       "am_adam",
    "Bella (US, female)":    "af_bella",
    "Nicole (US, female)":   "af_nicole",
}

DEFAULT_VOICE = "bm_george"

SAMPLE_RATE = 24000  # Kokoro outputs 24 kHz mono

SPEED_MIN = 0.7
SPEED_MAX = 1.5
DEFAULT_SPEED = 1.0


def lang_for(voice_id: str) -> str:
    """Kokoro language code for a voice ('a' = US English, 'b' = UK English)."""
    return voice_id[0]
