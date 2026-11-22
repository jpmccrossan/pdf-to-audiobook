"""PDF to Audiobook - fully local text-to-speech for PDFs using Kokoro."""

import os

# Kokoro uses a few ops that Apple's MPS backend doesn't implement yet.
# This must be set before torch is imported anywhere.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

__version__ = "1.0.0"
