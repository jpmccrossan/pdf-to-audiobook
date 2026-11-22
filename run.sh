#!/usr/bin/env bash
# Quick start for Linux and macOS.
#   ./run.sh                 -> opens the desktop app
#   ./run.sh book.pdf [...]  -> converts from the command line (see --help)
# First run creates a virtual environment and installs dependencies.
set -euo pipefail

cd "$(dirname "$0")"
VENV_DIR="${VENV_DIR:-venv}"
OS="$(uname -s)"

say()  { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31merror:\033[0m %s\n' "$*" >&2; exit 1; }

# --- find a supported Python (Kokoro needs 3.10-3.12) ---------------------
find_python() {
    for cmd in python3.12 python3.11 python3.10 python3; do
        if command -v "$cmd" >/dev/null 2>&1 &&
           "$cmd" -c 'import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,12) else 1)' 2>/dev/null; then
            echo "$cmd"; return 0
        fi
    done
    return 1
}

if [ ! -x "$VENV_DIR/bin/python" ]; then
    PY="$(find_python)" || {
        if [ "$OS" = "Darwin" ]; then
            fail "Python 3.10-3.12 not found. Install it with: brew install python@3.12 python-tk@3.12"
        else
            fail "Python 3.10-3.12 not found. Install it with: sudo apt install python3.12 python3.12-venv python3-tk"
        fi
    }

    "$PY" -c 'import tkinter' 2>/dev/null || {
        if [ "$OS" = "Darwin" ]; then
            echo "warning: tkinter missing - the GUI won't open (CLI still works). Fix: brew install python-tk@3.12" >&2
        else
            echo "warning: tkinter missing - the GUI won't open (CLI still works). Fix: sudo apt install python3-tk" >&2
        fi
    }

    say "Creating virtual environment with $PY in ./$VENV_DIR"
    "$PY" -m venv "$VENV_DIR" || fail "venv creation failed. On Debian/Ubuntu/Mint: sudo apt install python3-venv"
fi

PYTHON="$VENV_DIR/bin/python"
STAMP="$VENV_DIR/.installed-requirements"

# --- install deps (only when requirements.txt changes) --------------------
if ! cmp -s requirements.txt "$STAMP" 2>/dev/null; then
    say "Installing dependencies (first run pulls PyTorch - a few GB, be patient)"
    "$PYTHON" -m pip install --upgrade pip --quiet
    "$PYTHON" -m pip install -r requirements.txt
    cp requirements.txt "$STAMP"
fi

exec "$PYTHON" -m pdf_to_audiobook "$@"
