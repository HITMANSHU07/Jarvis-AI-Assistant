"""
utils/helpers.py
----------------
Shared utility functions used across all Jarvis modules:
  - System metrics (CPU, RAM, disk)
  - Structured logging setup
  - Time / uptime formatting
  - Text cleaning & sanitisation
  - Safe thread-pool task execution
  - Config validation helper
"""

import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

# Optional psutil — gracefully degrade if not installed
try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)-28s  %(message)s"
_LOG_DATE   = "%H:%M:%S"

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configure root logger with a clean formatter.
    Call once at startup (main.py).

    Parameters
    ----------
    level    : logging level (default INFO)
    log_file : optional path; if given, also writes to a rotating file
    """
    root = logging.getLogger()
    root.setLevel(level)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE))
    root.addHandler(ch)

    # File handler (optional)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        from logging.handlers import RotatingFileHandler
        fh = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=3)
        fh.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE))
        root.addHandler(fh)

    return logging.getLogger("jarvis")


# ---------------------------------------------------------------------------
# System metrics
# ---------------------------------------------------------------------------

def get_system_stats() -> dict[str, Any]:
    """
    Returns a dict with cpu, ram, disk (all 0–100 percentages) and
    the platform string. Falls back to zeroes if psutil is absent.
    """
    if _PSUTIL:
        return {
            "cpu":      round(psutil.cpu_percent(interval=None), 1),
            "ram":      round(psutil.virtual_memory().percent, 1),
            "disk":     round(psutil.disk_usage("/").percent, 1),
            "platform": platform.system(),
        }
    return {"cpu": 0.0, "ram": 0.0, "disk": 0.0, "platform": platform.system()}


def get_battery_status() -> Optional[dict]:
    """Returns battery percent and charging status, or None if no battery."""
    if _PSUTIL:
        batt = psutil.sensors_battery()
        if batt:
            return {
                "percent":  round(batt.percent, 1),
                "charging": batt.power_plugged,
            }
    return None


# ---------------------------------------------------------------------------
# Time & uptime formatting
# ---------------------------------------------------------------------------

def format_uptime(seconds: int) -> str:
    """
    Converts raw seconds to a compact human-readable string.
    Examples: 45 → "45s"   3750 → "1h 2m"   90 → "1m 30s"
    """
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(seconds, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


def timestamp_now(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return datetime.now().strftime(fmt)


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def clean_text_for_tts(text: str) -> str:
    """
    Strips markdown symbols, action tags, and excess whitespace
    before sending text to the TTS engine.
    """
    # Remove <ACTION>...</ACTION> blocks
    text = re.sub(r"<ACTION>.*?</ACTION>", "", text, flags=re.DOTALL)
    # Remove markdown bold / italic
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    # Remove markdown headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Collapse whitespace
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def truncate(text: str, max_chars: int = 120, suffix: str = "…") -> str:
    """Truncate a string for display labels."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars - len(suffix)] + suffix


def sanitise_filename(name: str) -> str:
    """Remove characters unsafe for file names."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", name).strip()


# ---------------------------------------------------------------------------
# Config / environment validation
# ---------------------------------------------------------------------------

REQUIRED_ENV_KEYS = ["GROQ_API_KEY"]
OPTIONAL_ENV_KEYS = ["PICOVOICE_KEY", "OPENAI_API_KEY"]

def validate_env() -> tuple[bool, list[str]]:
    """
    Checks that required .env keys are present.
    Returns (all_ok: bool, missing_keys: list[str]).
    """
    missing = [k for k in REQUIRED_ENV_KEYS if not os.getenv(k)]
    return (len(missing) == 0, missing)


def check_dependencies() -> dict[str, bool]:
    """
    Verifies that key system dependencies are available on PATH.
    Returns a dict { tool: available }.
    """
    tools = {
        "ffmpeg":  shutil.which("ffmpeg") is not None,
        "chrome":  (
            shutil.which("google-chrome") is not None or
            shutil.which("chromedriver") is not None or
            os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        ),
        "whatsapp": os.path.exists(
            os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe")
        ),
    }
    return tools


# ---------------------------------------------------------------------------
# Thread pool executor (for fire-and-forget async tasks)
# ---------------------------------------------------------------------------

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="jarvis-worker")


def run_async(fn: Callable, *args, **kwargs) -> Future:
    """
    Submit a callable to the shared thread pool.
    Returns a Future — caller can .result() if they need the return value.

    Usage
    -----
    run_async(send_whatsapp_message, "Siraj", "Be right there")
    """
    return _executor.submit(fn, *args, **kwargs)


def shutdown_executor() -> None:
    """Call on application exit to cleanly drain pending tasks."""
    _executor.shutdown(wait=True, cancel_futures=False)


# ---------------------------------------------------------------------------
# Safe subprocess launcher
# ---------------------------------------------------------------------------

def launch_app(path: str, timeout: float = 5.0) -> bool:
    """
    Launch an external application by path and wait briefly.
    Returns True if process started without immediate error.
    """
    try:
        if platform.system() == "Windows":
            subprocess.Popen(
                path,
                creationflags=subprocess.DETACHED_PROCESS,
                close_fds=True,
            )
        else:
            subprocess.Popen(path, start_new_session=True, close_fds=True)
        time.sleep(timeout)
        return True
    except FileNotFoundError:
        logging.getLogger("jarvis.helpers").error("App not found: %s", path)
        return False
    except Exception as exc:
        logging.getLogger("jarvis.helpers").error("Launch error: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Debounce decorator (prevents rapid repeated calls)
# ---------------------------------------------------------------------------

def debounce(wait: float):
    """
    Decorator: delays function execution by `wait` seconds and cancels
    it if called again within that window.

    Usage
    -----
    @debounce(0.5)
    def on_mic_button_click():
        ...
    """
    def decorator(fn):
        timer: list[Optional[threading.Timer]] = [None]

        def debounced(*args, **kwargs):
            if timer[0] is not None:
                timer[0].cancel()
            timer[0] = threading.Timer(wait, fn, args=args, kwargs=kwargs)
            timer[0].start()

        return debounced
    return decorator
