#!/usr/bin/env python3
"""Convenience launcher: `python app.py` (GUI) or `python app.py book.pdf` (CLI).

Equivalent to `python -m pdf_to_audiobook`.
"""

import sys

from pdf_to_audiobook.cli import main

if __name__ == "__main__":
    sys.exit(main())
