"""Pull readable text out of a PDF."""

import re

import pdfplumber


def extract_text(pdf_path: str) -> str:
    """Return the PDF's text layer as one clean string ('' if there is none)."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            if txt.strip():
                pages.append(txt)
    return clean_text("\n".join(pages))


def clean_text(text: str) -> str:
    text = re.sub(r"-\n", "", text)   # rejoin words hyphenated across lines
    text = re.sub(r"\s+", " ", text)  # collapse all whitespace to single spaces
    return text.strip()
