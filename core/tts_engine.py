import asyncio
import edge_tts
import pygame
import tempfile
import os
import time
import threading
import pyttsx3
import config
from utils.helpers import clean_text_for_tts

# Global speaking lock and state flag
_speaking_lock = threading.Lock()
is_tts_speaking = False
status_callback = None

if not pygame.mixer.get_init():
    try:
        pygame.mixer.init()
    except Exception as e:
        print(f"Pygame mixer init warning: {e}")

def set_tts_status_callback(cb):
    """Sets a callback function (state_name: str) -> None for GUI status updates."""
    global status_callback
    status_callback = cb

def _update_status(state: str):
    if status_callback:
        try:
            status_callback(state)
        except Exception:
            pass

async def _generate_edge_tts_audio(text: str, voice: str) -> str:
    communicate = edge_tts.Communicate(text, voice)
    fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    await communicate.save(tmp_path)
    return tmp_path

def _speak_pyttsx3(text: str):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        voices = engine.getProperty('voices')
        for v in voices:
            if "david" in v.name.lower() or "male" in v.name.lower():
                engine.setProperty('voice', v.id)
                break
        else:
            if len(voices) > 0:
                engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"pyttsx3 Fallback Error: {e}")

def speak(text: str, voice: str = None) -> None:
    """
    Speaks text naturally using Edge-TTS with pyttsx3 fallback.
    Thread-safe and manages TTS state so mic listening is safely paused during speech.
    """
    global is_tts_speaking
    cleaned_text = clean_text_for_tts(text)
    if not cleaned_text.strip():
        return

    selected_voice = voice or getattr(config, "TTS_VOICE", "en-US-GuyNeural")
    print(f"🔊 Jarvis: {cleaned_text}")

    with _speaking_lock:
        is_tts_speaking = True
        _update_status("speaking")
        tmp_path = None

        try:
            # Attempt Edge-TTS
            try:
                tmp_path = asyncio.run(_generate_edge_tts_audio(cleaned_text, selected_voice))
            except Exception as e:
                print(f"Edge-TTS Error ({e}), falling back to pyttsx3...")
                _speak_pyttsx3(cleaned_text)
                return

            if tmp_path and os.path.exists(tmp_path):
                try:
                    pygame.mixer.music.load(tmp_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(15)
                    pygame.mixer.music.unload()
                except Exception as play_err:
                    print(f"Pygame playback error: {play_err}")
                    _speak_pyttsx3(cleaned_text)
                finally:
                    time.sleep(0.15)
                    if os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
        finally:
            is_tts_speaking = False
            _update_status("idle")