"""
gui/app_window.py
-----------------
Ultra-professional Jarvis AI dashboard built with CustomTkinter.
Dark cyberpunk-minimal aesthetic: deep navy blacks, cyan & violet accents,
clean grid layout, smooth status transitions, and real-time feedback.

Layout
------
┌─────────────────────────────────────────────────────────────┐
│   Header: Logo · Title · Status pill · Session timer        │
├──────────────────────────┬──────────────────────────────────┤
│                          │  Right sidebar                   │
│   Chat log               │  ┌──────────────────────────┐   │
│   (scrollable)           │  │  Waveform visualizer     │   │
│                          │  └──────────────────────────┘   │
│                          │  ┌──────────────────────────┐   │
│                          │  │  System metrics panel    │   │
│                          │  └──────────────────────────┘   │
│                          │  ┌──────────────────────────┐   │
│                          │  │  Quick action buttons    │   │
│                          │  └──────────────────────────┘   │
├──────────────────────────┴──────────────────────────────────┤
│   Input bar: text field · Send · Mic button · Wake toggle    │
└─────────────────────────────────────────────────────────────┘
"""

import threading
import time
import tkinter as tk
from typing import Callable, Optional

import customtkinter as ctk

from gui.waveform_widget import WaveformWidget
from gui.chat_log import ChatLog
from utils.helpers import get_system_stats, format_uptime

# ---------------------------------------------------------------------------
# Global appearance
# ---------------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
C_BG_ROOT    = "#0A0F16"
C_BG_SURFACE = "#0D1117"
C_BG_CARD    = "#12181F"
C_BG_INPUT   = "#161D27"

C_CYAN       = "#00D4FF"
C_CYAN_DIM   = "#004D5E"
C_VIOLET     = "#7B61FF"
C_VIOLET_DIM = "#2D1B69"
C_GREEN      = "#00FF87"
C_RED        = "#FF4D6D"
C_AMBER      = "#FFB02E"

C_TEXT_1     = "#E2E8F0"
C_TEXT_2     = "#718096"
C_TEXT_3     = "#4A5568"

C_BORDER     = "#1E2D3D"

FONT_H1      = ("Segoe UI Semibold", 18)
FONT_H2      = ("Segoe UI Semibold", 14)
FONT_BODY    = ("Segoe UI", 13)
FONT_SMALL   = ("Segoe UI", 11)
FONT_MONO    = ("Consolas", 11)
FONT_LOGO    = ("Segoe UI Black", 22)

STATUS_COLOURS = {
    "idle":      (C_TEXT_3,  "●  Idle"),
    "listening": (C_GREEN,   "◉  Listening"),
    "thinking":  (C_AMBER,   "◌  Processing"),
    "speaking":  (C_VIOLET,  "◈  Speaking"),
    "executing": (C_CYAN,    "◆  Executing"),
    "error":     (C_RED,     "✕  Error"),
}


# ---------------------------------------------------------------------------
# Main application window
# ---------------------------------------------------------------------------

class JarvisApp:
    """
    Main Jarvis GUI.  Instantiate, then call .run() on the main thread.

    Parameters
    ----------
    assistant_loop : callable
        The blocking function that runs the STT → LLM → TTS loop.
        It will be executed in a daemon thread so the GUI stays responsive.
    """

    def __init__(self, assistant_loop: Optional[Callable] = None):
        self._assistant_loop = assistant_loop
        self._assistant_thread: Optional[threading.Thread] = None
        self._session_start  = time.time()
        self._message_count  = 0
        self._mic_active     = False

        self._build_root()
        self._build_header()
        self._build_content()
        self._build_input_bar()
        self._start_clock()
        self._start_stats_updater()
        
        # Initial greeting set to Jai Shree Ram
        self.add_jarvis_message("Jai Shree Ram! I am Jarvis.")

    # ===================================================================
    # Public API (called from the assistant core)
    # ===================================================================
    def waveform_set_state(self, state: str) -> None:
        """Helper to sync main.py with the waveform widget."""
        self._waveform.set_state(state)
        
    def run(self) -> None:
        """Block on the Tk main loop. Call from the main thread only."""
        if self._assistant_loop:
            self._assistant_thread = threading.Thread(
                target=self._assistant_loop,
                daemon=True,
                name="AssistantCore",
            )
            self._assistant_thread.start()
        self._root.mainloop()

    def add_user_message(self, text: str) -> None:
        """Thread-safe: append a user bubble to the chat log."""
        self._root.after(0, lambda: self._chat.add_message("user", text))
        self._root.after(0, self._inc_message_count)

    def add_jarvis_message(self, text: str) -> None:
        """Thread-safe: append a Jarvis bubble to the chat log."""
        self._root.after(0, lambda: self._chat.add_message("jarvis", text))
        self._root.after(0, self._inc_message_count)

    def add_system(self, text: str) -> None:
        self._root.after(0, lambda: self._chat.add_system(text))

    def set_status(self, state: str) -> None:
        """
        Update the status pill and waveform.
        States: idle | listening | thinking | speaking | executing | error
        """
        self._root.after(0, lambda: self._apply_status(state))

    # ===================================================================
    # Build helpers
    # ===================================================================

    def _build_root(self) -> None:
        self._root = ctk.CTk()
        self._root.title("Jarvis AI  —  Voice Desktop Assistant")
        self._root.geometry("1100x720")
        self._root.minsize(900, 600)
        self._root.configure(fg_color=C_BG_ROOT)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Main grid: header / content / input
        self._root.grid_rowconfigure(1, weight=1)
        self._root.grid_columnconfigure(0, weight=1)

    # -------------------------------------------------------------------
    def _build_header(self) -> None:
        header = ctk.CTkFrame(
            self._root, fg_color=C_BG_SURFACE,
            corner_radius=0, height=64,
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        # Logo mark
        logo_dot = ctk.CTkLabel(
            header, text="◈", font=("Segoe UI", 22),
            text_color=C_CYAN, width=40,
        )
        logo_dot.grid(row=0, column=0, padx=(16, 4), pady=14)

        # Title
        ctk.CTkLabel(
            header, text="JARVIS", font=FONT_LOGO,
            text_color=C_TEXT_1,
        ).grid(row=0, column=1, sticky="w", padx=4)

        ctk.CTkLabel(
            header, text="AI Desktop Assistant",
            font=FONT_SMALL, text_color=C_TEXT_2,
        ).grid(row=0, column=2, sticky="w", padx=(0, 24))

        # Spacer
        ctk.CTkFrame(header, fg_color="transparent").grid(
            row=0, column=3, sticky="ew"
        )
        header.grid_columnconfigure(3, weight=1)

        # Status pill
        self._status_pill = ctk.CTkLabel(
            header,
            text="●  Idle",
            font=FONT_SMALL,
            text_color=C_TEXT_3,
            fg_color=C_BG_CARD,
            corner_radius=20,
            padx=12, pady=4,
        )
        self._status_pill.grid(row=0, column=4, padx=8)

        # Session timer
        self._timer_label = ctk.CTkLabel(
            header, text="00:00:00",
            font=FONT_MONO, text_color=C_TEXT_3,
        )
        self._timer_label.grid(row=0, column=5, padx=(0, 16))

        # Thin bottom border
        ctk.CTkFrame(self._root, fg_color=C_BORDER, height=1).grid(
            row=0, column=0, sticky="sew"
        )

    # -------------------------------------------------------------------
    def _build_content(self) -> None:
        content = ctk.CTkFrame(self._root, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        # ---- Chat log (left / main column) ----
        self._chat = ChatLog(content, width=580)
        self._chat.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)

        # ---- Right sidebar ----
        sidebar = ctk.CTkFrame(content, fg_color="transparent", width=320)
        sidebar.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(3, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        self._build_waveform_card(sidebar)
        self._build_metrics_card(sidebar)
        self._build_actions_card(sidebar)

    # -------------------------------------------------------------------
    def _build_waveform_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color=C_BG_CARD, corner_radius=12)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="AUDIO MONITOR",
            font=("Segoe UI Semibold", 10), text_color=C_TEXT_3,
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 4))

        self._waveform = WaveformWidget(card)
        self._waveform.grid(row=1, column=0, padx=14, pady=(0, 12))
        self._waveform.start()

        # State indicator row
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))

        self._wave_state_label = ctk.CTkLabel(
            row, text="Waiting for wake word…",
            font=FONT_SMALL, text_color=C_TEXT_3,
        )
        self._wave_state_label.pack(side="left")

    # -------------------------------------------------------------------
    def _build_metrics_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color=C_BG_CARD, corner_radius=12)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            card, text="SYSTEM",
            font=("Segoe UI Semibold", 10), text_color=C_TEXT_3,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(10, 6))

        # Metric tiles
        metrics = [
            ("CPU", "cpu_val"),
            ("RAM", "ram_val"),
            ("Uptime", "uptime_val"),
            ("Messages", "msg_val"),
        ]
        self._metric_labels: dict[str, ctk.CTkLabel] = {}
        for idx, (label, key) in enumerate(metrics):
            col = idx % 2
            row = 1 + idx // 2
            tile = ctk.CTkFrame(card, fg_color=C_BG_SURFACE, corner_radius=8)
            tile.grid(row=row, column=col, padx=(14 if col == 0 else 4, 4 if col == 0 else 14), pady=3, sticky="ew")
            ctk.CTkLabel(
                tile, text=label, font=FONT_SMALL, text_color=C_TEXT_3,
            ).pack(pady=(6, 0))
            val = ctk.CTkLabel(
                tile, text="—", font=("Segoe UI Semibold", 14), text_color=C_CYAN,
            )
            val.pack(pady=(0, 6))
            self._metric_labels[key] = val

        ctk.CTkFrame(card, fg_color="transparent", height=4).grid(
            row=3, column=0, columnspan=2
        )

    # -------------------------------------------------------------------
    def _build_actions_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color=C_BG_CARD, corner_radius=12)
        card.grid(row=2, column=0, sticky="ew", pady=(0, 0))
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            card, text="QUICK ACTIONS",
            font=("Segoe UI Semibold", 10), text_color=C_TEXT_3,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(10, 8))

        actions = [
            ("▶  YouTube",   self._cmd_youtube),
            ("💬  WhatsApp", self._cmd_whatsapp),
            ("🔇  Mute",     self._cmd_mute),
            ("✕  Close Win", self._cmd_close_win),
            ("🗑  Clear Log", self._cmd_clear),
            ("⏻  Shutdown",  self._cmd_shutdown),
        ]
        for idx, (label, cmd) in enumerate(actions):
            col = idx % 2
            row = 1 + idx // 2
            btn = ctk.CTkButton(
                card,
                text=label,
                font=FONT_SMALL,
                height=32,
                fg_color=C_BG_INPUT,
                hover_color=C_BG_SURFACE,
                text_color=C_TEXT_2,
                border_width=1,
                border_color=C_BORDER,
                corner_radius=8,
                command=cmd,
            )
            btn.grid(
                row=row, column=col,
                padx=(14 if col == 0 else 4, 4 if col == 0 else 14),
                pady=3, sticky="ew",
            )

        ctk.CTkFrame(card, fg_color="transparent", height=4).grid(
            row=4, column=0, columnspan=2
        )

    # -------------------------------------------------------------------
    def _build_input_bar(self) -> None:
        bar = ctk.CTkFrame(
            self._root, fg_color=C_BG_SURFACE,
            corner_radius=0, height=64,
        )
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        # Top divider
        ctk.CTkFrame(bar, fg_color=C_BORDER, height=1).place(x=0, y=0, relwidth=1)

        # Wake-word toggle
        self._wake_var = ctk.BooleanVar(value=True)
        wake_toggle = ctk.CTkSwitch(
            bar,
            text="",
            variable=self._wake_var,
            width=44,
            progress_color=C_CYAN,
            button_color=C_TEXT_1,
            button_hover_color=C_CYAN,
            fg_color=C_BG_INPUT,
            command=self._toggle_wake,
        )
        wake_toggle.grid(row=0, column=0, padx=(14, 4), pady=14)
        ctk.CTkLabel(
            bar, text="Wake", font=FONT_SMALL, text_color=C_TEXT_3,
        ).grid(row=0, column=0, padx=(56, 0))

        # Text input
        self._text_input = ctk.CTkEntry(
            bar,
            placeholder_text="Type a command or speak after saying 'Jarvis'…",
            font=FONT_BODY,
            fg_color=C_BG_INPUT,
            border_color=C_BORDER,
            text_color=C_TEXT_1,
            placeholder_text_color=C_TEXT_3,
            height=38,
            corner_radius=10,
        )
        self._text_input.grid(row=0, column=1, sticky="ew", padx=8, pady=13)
        self._text_input.bind("<Return>", self._on_text_send)

        # Send button
        send_btn = ctk.CTkButton(
            bar,
            text="Send",
            font=FONT_SMALL,
            width=72,
            height=38,
            fg_color=C_CYAN_DIM,
            hover_color="#006070",
            text_color=C_CYAN,
            corner_radius=10,
            command=self._on_text_send,
        )
        send_btn.grid(row=0, column=2, padx=(0, 6), pady=13)

        # Mic button
        self._mic_btn = ctk.CTkButton(
            bar,
            text="🎤",
            font=("Segoe UI", 16),
            width=42,
            height=38,
            fg_color=C_BG_INPUT,
            hover_color=C_VIOLET_DIM,
            text_color=C_TEXT_1,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
            command=self._on_mic_press,
        )
        self._mic_btn.grid(row=0, column=3, padx=(0, 14), pady=13)

    # ===================================================================
    # Status & clock
    # ===================================================================

    def _apply_status(self, state: str) -> None:
        colour, label = STATUS_COLOURS.get(state, (C_TEXT_3, "● Unknown"))
        self._status_pill.configure(text=label, text_color=colour)
        self._waveform.set_state(
            "listening" if state == "listening" else
            "speaking"  if state == "speaking"  else
            "idle"
        )
        wave_msg = {
            "idle":      "Waiting for wake word…",
            "listening": "Listening…",
            "thinking":  "Processing request…",
            "speaking":  "Speaking…",
            "executing": "Running automation…",
            "error":     "An error occurred.",
        }.get(state, "")
        self._wave_state_label.configure(text=wave_msg, text_color=colour)

    def _start_clock(self) -> None:
        def tick():
            elapsed = int(time.time() - self._session_start)
            h, rem  = divmod(elapsed, 3600)
            m, s    = divmod(rem, 60)
            self._timer_label.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
            self._root.after(1000, tick)
        tick()

    def _start_stats_updater(self) -> None:
        def update():
            stats = get_system_stats()
            self._metric_labels["cpu_val"].configure(text=f"{stats['cpu']}%")
            self._metric_labels["ram_val"].configure(text=f"{stats['ram']}%")
            self._metric_labels["uptime_val"].configure(
                text=format_uptime(int(time.time() - self._session_start))
            )
            self._metric_labels["msg_val"].configure(text=str(self._message_count))
            self._root.after(2000, update)
        update()

    def _inc_message_count(self) -> None:
        self._message_count += 1

    # ===================================================================
    # Button callbacks
    # ===================================================================

    def _on_text_send(self, _event=None) -> None:
        text = self._text_input.get().strip()
        if not text:
            return
        self._text_input.delete(0, "end")
        self.add_user_message(text)
        # Pass to assistant brain if available
        if hasattr(self, "_on_text_command"):
            threading.Thread(
                target=self._on_text_command,
                args=(text,),
                daemon=True,
            ).start()

    def _on_mic_press(self) -> None:
        if not self._mic_active:
            self._mic_active = True
            self._mic_btn.configure(fg_color=C_VIOLET_DIM, text_color=C_VIOLET)
            self.add_system("Manual mic triggered — speak now.")
            if hasattr(self, "_on_mic_command"):
                threading.Thread(
                    target=self._on_mic_command,
                    daemon=True,
                ).start()
        else:
            self._mic_active = False
            self._mic_btn.configure(fg_color=C_BG_INPUT, text_color=C_TEXT_1)
            self.set_status("idle")   

    def _toggle_wake(self) -> None:
        state = self._wake_var.get()
        msg = "Wake-word detection enabled." if state else "Wake-word detection paused."
        self.add_system(msg)

    def _cmd_youtube(self):
        self.add_system("Opening YouTube browser automation…")

    def _cmd_whatsapp(self):
        self.add_system("Opening WhatsApp Desktop automation…")

    def _cmd_mute(self):
        from automation.system_control import mute_volume
        mute_volume()
        self.add_system("Volume muted.")

    def _cmd_close_win(self):
        from automation.system_control import close_active_window
        close_active_window()
        self.add_system("Active window closed.")

    def _cmd_clear(self):
        self._chat.clear()
        self._message_count = 0

    def _cmd_shutdown(self):
        self.add_system("Shutdown initiated in 5 seconds…")
        self._root.after(1500, lambda: __import__(
            "automation.system_control", fromlist=["shutdown_pc"]
        ).shutdown_pc())

    def _on_close(self) -> None:
        self._waveform.stop()
        self._root.destroy()