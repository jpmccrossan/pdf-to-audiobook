"""Tkinter desktop app."""

import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from .config import DEFAULT_SPEED, SPEED_MAX, SPEED_MIN, VOICES
from .converter import ConversionError, convert_pdf
from .device import detect_device, device_label
from .synth import Synthesizer

GREEN = "#27ae60"
RED = "#c0392b"
TEXT = "#333"
MUTED = "#999"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF to Audiobook")
        self.geometry("460x400")
        self.resizable(False, False)
        self.configure(padx=20, pady=20)

        self.pdf_path = None
        self.synth = Synthesizer()
        # Worker thread -> UI messages. Tk widgets must only be touched on the main thread.
        self._messages = queue.Queue()

        self._build_ui()
        self.after(100, self._drain_messages)

    # ---- layout ---------------------------------------------------------

    def _build_ui(self):
        tk.Label(self, text="PDF to Audiobook", font=("Helvetica", 18, "bold")).pack(anchor="w")
        on_gpu = detect_device() != "cpu"
        tk.Label(self, text=f"Local | {device_label()}", fg=GREEN if on_gpu else RED
                 ).pack(anchor="w", pady=(0, 14))

        file_row = tk.Frame(self)
        file_row.pack(fill="x", pady=4)
        self.file_label = tk.Label(file_row, text="No file selected", fg=MUTED, anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True)
        ttk.Button(file_row, text="Choose PDF...", command=self._pick_file).pack(side="right")

        tk.Label(self, text="Voice", anchor="w").pack(fill="x", pady=(14, 2))
        self.voice_var = tk.StringVar(value=next(iter(VOICES)))
        ttk.Combobox(self, textvariable=self.voice_var, values=list(VOICES),
                     state="readonly").pack(fill="x")

        self.speed_var = tk.DoubleVar(value=DEFAULT_SPEED)
        self.speed_label = tk.Label(self, anchor="w")
        self.speed_label.pack(fill="x", pady=(14, 2))
        ttk.Scale(self, from_=SPEED_MIN, to=SPEED_MAX, variable=self.speed_var,
                  orient="horizontal", command=lambda _v: self._update_speed_label()
                  ).pack(fill="x")
        self._update_speed_label()

        self.convert_btn = ttk.Button(self, text="Convert to MP3", command=self._start_convert)
        self.convert_btn.pack(fill="x", pady=(18, 6))

        self.status = tk.Label(self, text="", fg=TEXT, wraplength=420, justify="left")
        self.status.pack(anchor="w")

    # ---- UI helpers -----------------------------------------------------

    def _update_speed_label(self):
        self.speed_label.config(text=f"Speed  {self.speed_var.get():.2f}x")

    def _set_status(self, msg, colour=TEXT):
        self.status.config(text=msg, fg=colour)

    def _pick_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.pdf_path = path
            self.file_label.config(text=os.path.basename(path), fg=TEXT)

    def _drain_messages(self):
        try:
            while True:
                kind, payload = self._messages.get_nowait()
                if kind == "status":
                    self._set_status(payload)
                elif kind == "done":
                    self._set_status(f"Done -> {payload}", GREEN)
                    self.convert_btn.config(state="normal")
                elif kind == "error":
                    self._set_status(payload, RED)
                    self.convert_btn.config(state="normal")
        except queue.Empty:
            pass
        self.after(100, self._drain_messages)

    # ---- conversion -----------------------------------------------------

    def _start_convert(self):
        if not self.pdf_path:
            self._set_status("Pick a PDF first.", RED)
            return
        self.convert_btn.config(state="disabled")
        self._set_status("Working...")
        args = (self.pdf_path, VOICES[self.voice_var.get()], round(self.speed_var.get(), 2))
        threading.Thread(target=self._run_convert, args=args, daemon=True).start()

    def _run_convert(self, pdf_path, voice, speed):
        try:
            out = convert_pdf(pdf_path, voice, speed, synth=self.synth,
                              on_status=lambda m: self._messages.put(("status", m)))
            self._messages.put(("done", os.path.basename(out)))
        except ConversionError as e:
            self._messages.put(("error", str(e)))
        except Exception as e:  # surface anything unexpected in the UI
            self._messages.put(("error", f"Error: {e}"))


def run():
    App().mainloop()
