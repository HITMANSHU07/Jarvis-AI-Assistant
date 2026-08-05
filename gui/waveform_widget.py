"""
gui/waveform_widget.py
----------------------
Animated audio waveform visualizer built on tkinter Canvas.
Updated for compatibility with latest customtkinter versions.
"""

import math
import random
import threading
import tkinter as tk
import customtkinter as ctk

# ---------------------------------------------------------------------------
# Colour constants
# ---------------------------------------------------------------------------
COLOUR_IDLE     = "#2A3A4A"
COLOUR_ACTIVE   = "#00D4FF"
COLOUR_SPEAKING = "#7B61FF"
COLOUR_ERROR    = "#FF4D6D"
COLOUR_BG       = "#0D1117"

class WaveformWidget(ctk.CTkFrame):
    BAR_COUNT = 40
    BAR_GAP = 3
    FRAME_RATE = 30

    def __init__(self, master, **kwargs):
        # Yahan width aur height ko kwargs se nikal kar pass karenge
        super().__init__(master, **kwargs)
        
        self._state = "idle"
        self._running = False
        self._lock = threading.Lock()
        self._phase = 0.0

        # Canvas ko frame ke andar adjust kar rahe hain
        self._canvas = tk.Canvas(
            self, bg="#0D1117", highlightthickness=0, bd=0
        )
        self._canvas.pack(fill="both", expand=True)

        self._bar_ids = []
        # Initial draw defer kar rahe hain taake size mil jaye
        self.after(100, self._setup_bars)

    def _setup_bars(self):
        w = self.winfo_width()
        h = self.winfo_height()
        bar_w = (w - (self.BAR_COUNT + 1) * self.BAR_GAP) / self.BAR_COUNT
        cx = h // 2
        for i in range(self.BAR_COUNT):
            x1 = self.BAR_GAP + i * (bar_w + self.BAR_GAP)
            bid = self._canvas.create_rectangle(x1, cx, x1 + bar_w, cx, fill="#2A3A4A", outline="")
            self._bar_ids.append(bid)
        self.start()

    def set_state(self, state):
        with self._lock: self._state = state

    def start(self):
        if not self._running:
            self._running = True
            self._animate()

    def _animate(self):
        if not self._running: return
        with self._lock: state = self._state
        
        # Simple animation logic
        cx = self.winfo_height() / 2
        for i, bid in enumerate(self._bar_ids):
            h = (math.sin(self._phase + i*0.5) * 20) + 20
            x1, _, x2, _ = self._canvas.coords(bid)
            self._canvas.coords(bid, x1, cx - h, x2, cx + h)
        
        self._phase += 0.2
        self.after(33, self._animate)

    def stop(self) -> None:
        self._running = False