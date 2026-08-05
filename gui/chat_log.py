"""
gui/chat_log.py
---------------
Scrollable, styled conversation history widget.
Each message is rendered as a floating bubble with avatar,
timestamp, and role-specific colour scheme.
"""

import tkinter as tk
from datetime import datetime
from typing import Literal

import customtkinter as ctk

# ---------------------------------------------------------------------------
# Theme tokens
# ---------------------------------------------------------------------------
FONT_BODY   = ("Segoe UI", 13)
FONT_LABEL  = ("Segoe UI", 10)
FONT_NAME   = ("Segoe UI Semibold", 12)

BG_SURFACE  = "#12181F"
BG_USER     = "#1A2535"
BG_JARVIS   = "#141C27"
BG_SYSTEM   = "#0D1117"

ACCENT_CYAN   = "#00D4FF"
ACCENT_VIOLET = "#7B61FF"
ACCENT_GRAY   = "#4A5568"

TEXT_PRIMARY   = "#E2E8F0"
TEXT_SECONDARY = "#718096"
TEXT_MUTED     = "#4A5568"

Role = Literal["user", "jarvis", "system"]


# ---------------------------------------------------------------------------
# Single message bubble
# ---------------------------------------------------------------------------

class _MessageBubble(ctk.CTkFrame):
    """One chat message: avatar dot • name + timestamp • body text."""

    _AVATAR = {
        "user":   ("U", "#1A3A5C", ACCENT_CYAN),
        "jarvis": ("J", "#2D1B69", ACCENT_VIOLET),
        "system": ("S", "#1A1F2E", ACCENT_GRAY),
    }

    def __init__(self, master, role: Role, text: str, timestamp: str, **kw):
        bg = {"user": BG_USER, "jarvis": BG_JARVIS, "system": BG_SYSTEM}[role]
        super().__init__(
            master,
            fg_color=bg,
            corner_radius=10,
            **kw,
        )
        self.grid_columnconfigure(1, weight=1)

        letter, av_bg, av_fg = self._AVATAR[role]

        # ---- Avatar ----
        avatar = ctk.CTkLabel(
            self,
            text=letter,
            width=32,
            height=32,
            fg_color=av_bg,
            text_color=av_fg,
            corner_radius=16,
            font=("Segoe UI Semibold", 12),
        )
        avatar.grid(row=0, column=0, rowspan=2, padx=(10, 8), pady=10, sticky="n")

        # ---- Header row ----
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(8, 0))

        role_name = {"user": "You", "jarvis": "Jarvis AI", "system": "System"}[role]
        name_colour = {"user": ACCENT_CYAN, "jarvis": ACCENT_VIOLET, "system": ACCENT_GRAY}[role]

        ctk.CTkLabel(
            header,
            text=role_name,
            font=FONT_NAME,
            text_color=name_colour,
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=f"  {timestamp}",
            font=FONT_LABEL,
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(side="left")

        # ---- Message body ----
        body = ctk.CTkLabel(
            self,
            text=text,
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
            anchor="w",
            justify="left",
            wraplength=460,
        )
        body.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(2, 10))


# ---------------------------------------------------------------------------
# Separator
# ---------------------------------------------------------------------------

class _TimeSeparator(ctk.CTkFrame):
    def __init__(self, master, label: str, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.grid_columnconfigure((0, 2), weight=1)

        ctk.CTkFrame(self, height=1, fg_color=ACCENT_GRAY).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ctk.CTkLabel(
            self,
            text=label,
            font=FONT_LABEL,
            text_color=TEXT_MUTED,
        ).grid(row=0, column=1)
        ctk.CTkFrame(self, height=1, fg_color=ACCENT_GRAY).grid(
            row=0, column=2, sticky="ew", padx=(8, 0)
        )


# ---------------------------------------------------------------------------
# Main ChatLog widget
# ---------------------------------------------------------------------------

class ChatLog(ctk.CTkScrollableFrame):
    """
    Scrollable chat log. Drop into any CTk layout.

    Usage
    -----
    log = ChatLog(parent)
    log.add_message("user",   "Jarvis, mera mood nahi hai.")
    log.add_message("jarvis", "Koi baat nahi, Siraj ko message kar deta hoon!")
    log.add_system("Session started")
    log.clear()
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=BG_SURFACE,
            scrollbar_button_color="#1E2D3D",
            scrollbar_button_hover_color=ACCENT_CYAN,
            corner_radius=12,
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)
        self._row = 0
        self._last_date: str = ""

        # Welcome banner
        self._add_welcome()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_message(self, role: Role, text: str) -> None:
        """Append a user or Jarvis message bubble."""
        now = datetime.now()
        date_str = now.strftime("%B %d, %Y")
        time_str = now.strftime("%H:%M")

        if date_str != self._last_date:
            self._add_separator(date_str)
            self._last_date = date_str

        bubble = _MessageBubble(
            self,
            role=role,
            text=text,
            timestamp=time_str,
        )
        bubble.grid(
            row=self._row,
            column=0,
            sticky="ew",
            padx=8,
            pady=(4, 0),
        )
        self._row += 1
        self._scroll_to_bottom()

    def add_system(self, text: str) -> None:
        """Add a subtle system notification line."""
        now = datetime.now().strftime("%H:%M")
        bubble = _MessageBubble(self, role="system", text=text, timestamp=now)
        bubble.grid(row=self._row, column=0, sticky="ew", padx=8, pady=(4, 0))
        self._row += 1
        self._scroll_to_bottom()

    def clear(self) -> None:
        """Remove all messages."""
        for widget in self.winfo_children():
            widget.destroy()
        self._row = 0
        self._last_date = ""
        self._add_welcome()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _add_separator(self, label: str) -> None:
        sep = _TimeSeparator(self, label=label)
        sep.grid(row=self._row, column=0, sticky="ew", padx=16, pady=10)
        self._row += 1

    def _add_welcome(self) -> None:
        welcome = ctk.CTkLabel(
            self,
            text="✦  Jarvis AI is ready  ✦",
            font=("Segoe UI", 11),
            text_color=TEXT_MUTED,
        )
        welcome.grid(row=self._row, column=0, pady=(16, 8))
        self._row += 1

    def _scroll_to_bottom(self) -> None:
        """Force scroll to the newest message after a short delay."""
        self.after(80, lambda: self._parent_canvas.yview_moveto(1.0))
