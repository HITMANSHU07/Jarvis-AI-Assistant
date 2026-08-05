"""
core/wake_word.py
-----------------
Fixed Wake Word Detector with Shared Microphone Access.
"""
import threading
import logging
import time
from enum import Enum, auto
from typing import Callable, Optional
import speech_recognition as sr

logger = logging.getLogger(__name__)

WAKE_WORDS = {"jarvis", "aura", "hey jarvis", "hey aura", "ok jarvis"}
ENERGY_THRESHOLD = 1200
PAUSE_THRESHOLD = 0.6
PHRASE_LIMIT = 8.0
COOLDOWN_SECONDS = 1.5

class ListenerState(Enum):
    IDLE = auto(); WAITING = auto(); TRIGGERED = auto(); PAUSED = auto(); STOPPED = auto()

class WakeWordDetector:
    def __init__(self, on_wake=None, on_command=None, on_error=None):
        self.on_wake = on_wake or (lambda: None)
        self.on_command = on_command or (lambda _: None)
        self.on_error = on_error or (lambda e: logger.error(e))
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = ENERGY_THRESHOLD
        self._recognizer.pause_threshold = PAUSE_THRESHOLD
        self._microphone = sr.Microphone()
        self._state = ListenerState.IDLE
        self._state_lock = threading.Lock()
        self._thread = None
        self._last_trigger = 0.0

    def start(self):
        with self._state_lock:
            if self._state != ListenerState.IDLE: return
            self._state = ListenerState.WAITING
        self._thread = threading.Thread(target=self._listener_loop, name="WakeWordListener", daemon=True)
        self._thread.start()

    def stop(self):
        with self._state_lock: self._state = ListenerState.STOPPED
        if self._thread: self._thread.join(timeout=3)

    def _listener_loop(self):
        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=1)
            while True:
                with self._state_lock:
                    if self._state == ListenerState.STOPPED: break
                
                try:
                    # Timeout ko None karo taake mic hamesha sunta rahe
                    audio = self._recognizer.listen(source, timeout=None, phrase_time_limit=5)
                    text = self._recognise(audio)
                    if text and any(w in text for w in WAKE_WORDS):
                        self._handle_wake(source) 
                except:
                    time.sleep(0.1)
                    continue

    def _handle_wake(self, source):
        # State ko pause karein taake loop conflict na kare
        with self._state_lock: self._state = ListenerState.PAUSED
        try:
            self.on_wake()
            audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=8)
            text = self._recognise(audio)
            if text: self.on_command(text)
        except Exception as e:
            logger.error(f"Command Error: {e}")
        finally:
            with self._state_lock: self._state = ListenerState.WAITING

    def _recognise(self, audio):
        try: return self._recognizer.recognize_google(audio).lower()
        except: return None