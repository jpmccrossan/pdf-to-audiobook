# PDF to Audiobook

Turn any PDF into an MP3 audiobook, entirely on your own machine, using the [Kokoro](https://github.com/hexgrad/kokoro) text-to-speech model. It runs offline and needs no API keys or accounts.

- Desktop app (Tkinter) and a command-line mode
- 8 built-in UK and US voices, plus adjustable speed
- Uses your GPU automatically: NVIDIA (CUDA), Apple Silicon (MPS), or falls back to CPU

## Quick start

You need **Python 3.10, 3.11 or 3.12** (Kokoro doesn't support 3.13 yet). The quick-start script creates a virtual environment, installs everything, and launches the app. The first run downloads PyTorch (a few GB) and the Kokoro voice model (about 330 MB), so give it a few minutes. Later runs start straight away.

### Linux (Ubuntu / Debian / Mint)

```bash
sudo apt install python3 python3-venv python3-tk git
git clone https://github.com/jpmccrossan/pdf-to-audiobook.git
cd pdf-to-audiobook
./run.sh
```

NVIDIA GPU: no extra steps needed. The standard Linux PyTorch build includes CUDA, so all you need is a working NVIDIA driver (`nvidia-smi` should list your card).

### macOS (Apple Silicon or Intel)

```bash
brew install python@3.12 python-tk@3.12 git
git clone https://github.com/jpmccrossan/pdf-to-audiobook.git
cd pdf-to-audiobook
./run.sh
```

On M-series Macs the Apple GPU (MPS) is used automatically.

### Windows

1. Install [Python 3.12](https://www.python.org/downloads/). In the installer, tick **"Add python.exe to PATH"** and leave **tcl/tk** selected.
2. Install [Git](https://git-scm.com/download/win), or use **Code → Download ZIP** on GitHub.
3. In a terminal:

```bat
git clone https://github.com/jpmccrossan/pdf-to-audiobook.git
cd pdf-to-audiobook
run.bat
```

Or just double-click `run.bat` in File Explorer.

If you have an NVIDIA GPU, `run.bat` detects it and installs the CUDA build of PyTorch for you, because the default Windows build is CPU-only.

## Using it

### Desktop app

Run `./run.sh` (Linux/macOS) or `run.bat` (Windows) with no arguments.

1. **Choose PDF...**
2. Pick a **Voice**
3. Set the **Speed** (1.0x sounds natural)
4. **Convert to MP3**: the file is saved next to your PDF

Under the title you'll see which device is in use, e.g. `Local | CUDA (NVIDIA GeForce RTX 3090)`. If it shows **CPU** in red, PyTorch can't see a GPU. It will still work, just more slowly.

### Command line

```bash
./run.sh book.pdf                         # -> book.mp3 next to the PDF
./run.sh book.pdf -v af_bella -s 1.2      # pick a voice and speed
./run.sh book.pdf -o ~/Audiobooks/out.mp3 # choose where to save
./run.sh --list-voices
./run.sh --help
```

On Windows, use `run.bat` the same way. If you've activated the venv yourself, `python -m pdf_to_audiobook ...` does the same thing.

## Voices

| ID            | Voice                 |
|---------------|-----------------------|
| `bm_george`   | George (UK, male)     |
| `bm_lewis`    | Lewis (UK, male)      |
| `bf_emma`     | Emma (UK, female)     |
| `bf_isabella` | Isabella (UK, female) |
| `am_michael`  | Michael (US, male)    |
| `am_adam`     | Adam (US, male)       |
| `af_bella`    | Bella (US, female)    |
| `af_nicole`   | Nicole (US, female)   |

The CLI also accepts any other English Kokoro voice ([full list](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)). To add a voice to the app's dropdown, edit `VOICES` in `pdf_to_audiobook/config.py`.

## Project layout

```text
pdf_to_audiobook/
  config.py     voices, sample rate, speed limits
  device.py     CUDA / MPS / CPU detection
  extract.py    PDF -> clean text (pdfplumber)
  synth.py      Kokoro text-to-speech + saving audio
  converter.py  end-to-end PDF -> MP3 pipeline (shared by GUI and CLI)
  gui.py        Tkinter desktop app
  cli.py        command-line interface / entry point
app.py          convenience launcher (python app.py)
run.sh          quick start for Linux / macOS
run.bat         quick start for Windows
```

## Troubleshooting

- **"No extractable text"**: the PDF is a scanned image with no text layer. Run it through OCR first (e.g. `ocrmypdf in.pdf out.pdf`).
- **Got a `.wav` instead of `.mp3`**: your libsndfile is too old to write MP3. Convert the file with `ffmpeg -i book.wav book.mp3`.
- **GUI won't open / `No module named tkinter`**: install Tk (`sudo apt install python3-tk` or `brew install python-tk@3.12`), then delete the `venv` folder and run the script again.
- **espeak errors**: Kokoro ships its own espeak-ng, but if you still get phonemizer errors, install it system-wide (`sudo apt install espeak-ng` / `brew install espeak-ng`).
- **Start fresh**: delete the `venv` folder and run the quick-start script again.
- **Different CUDA version on Windows**: set `TORCH_INDEX_URL` before running, e.g. `set TORCH_INDEX_URL=https://download.pytorch.org/whl/cu126`.

## License

MIT, see [LICENSE](LICENSE). Kokoro model weights are Apache 2.0.
