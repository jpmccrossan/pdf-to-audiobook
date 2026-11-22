"""Pick the best available torch device: NVIDIA GPU, Apple Silicon GPU, or CPU."""

from functools import lru_cache


@lru_cache(maxsize=1)
def detect_device() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def device_label() -> str:
    """Human-readable description, e.g. 'CUDA (NVIDIA GeForce RTX 3090)'."""
    device = detect_device()
    if device == "cuda":
        import torch
        return f"CUDA ({torch.cuda.get_device_name(0)})"
    if device == "mps":
        return "MPS (Apple Silicon GPU)"
    return "CPU"
