"""
gui/waveform_widget.py
----------------------
High-tech Holographic Canvas Visualizer & Audio Monitor for Tkinter GUI.
"""

import math
import random
import threading
import tkinter as tk
import customtkinter as ctk

COLOUR_IDLE     = "#00D4FF"
COLOUR_ACTIVE   = "#10B981"
COLOUR_SPEAKING = "#8B5CF6"
COLOUR_THINKING = "#F59E0B"
COLOUR_OFFLINE  = "#EF4444"
COLOUR_BG       = "#0D1117"

class WaveformWidget(ctk.CTkFrame):
    BAR_COUNT = 36
    BAR_GAP = 3

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._state = "idle"
        self._running = False
        self._lock = threading.Lock()
        self._phase = 0.0

        self._canvas = tk.Canvas(
            self, bg=COLOUR_BG, highlightthickness=0, bd=0, height=80
        )
        self._canvas.pack(fill="both", expand=True)

        self._bar_ids = []
        self.after(100, self._setup_bars)

    def _setup_bars(self):
        w = self.winfo_width() or 280
        h = self.winfo_height() or 80
        bar_w = max(2, (w - (self.BAR_COUNT + 1) * self.BAR_GAP) / self.BAR_COUNT)
        cx = h // 2

        for i in range(self.BAR_COUNT):
            x1 = self.BAR_GAP + i * (bar_w + self.BAR_GAP)
            bid = self._canvas.create_rectangle(x1, cx - 2, x1 + bar_w, cx + 2, fill=COLOUR_IDLE, outline="")
            self._bar_ids.append(bid)
        self.start()

    def set_state(self, state):
        with self._lock:
            self._state = state

    def start(self):
        if not self._running:
            self._running = True
            self._animate()

    def _animate(self):
        if not self._running:
            return
        with self._lock:
            state = self._state

        color = COLOUR_IDLE
        if state == "listening": color = COLOUR_ACTIVE
        elif state == "speaking": color = COLOUR_SPEAKING
        elif state == "thinking": color = COLOUR_THINKING
        elif state == "offline": color = COLOUR_OFFLINE

        h_center = (self.winfo_height() or 80) / 2
        for i, bid in enumerate(self._bar_ids):
            if state == "offline":
                amp = 2
            elif state in ["listening", "speaking"]:
                amp = (math.sin(self._phase + i * 0.4) * 22) + random.randint(5, 18)
            elif state == "thinking":
                amp = (math.sin(self._phase * 2 + i * 0.8) * 15) + 10
            else:
                amp = (math.sin(self._phase + i * 0.2) * 8) + 6

            x1, _, x2, _ = self._canvas.coords(bid)
            self._canvas.coords(bid, x1, h_center - amp, x2, h_center + amp)
            self._canvas.itemconfig(bid, fill=color)

        self._phase += 0.25
        self.after(33, self._animate)

    def stop(self) -> None:
        self._running = False