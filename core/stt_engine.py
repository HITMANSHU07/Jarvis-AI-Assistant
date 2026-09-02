import io
import time
import logging
import speech_recognition as sr
from groq import Groq
import config

logger = logging.getLogger(__name__)

# Initialize Groq client safely
_groq_client = None
if getattr(config, "GROQ_API_KEY", ""):
    try:
        _groq_client = Groq(api_key=config.GROQ_API_KEY)
    except Exception as e:
        logger.warning(f"Could not initialize Groq client for STT: {e}")

class SpeechToTextEngine:
    """
    High-accuracy Speech-To-Text Engine supporting dynamic VAD (Voice Activity Detection),
    Groq Whisper Large v3, and Google STT fallback.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8  # Seconds of silence to consider speech finished
        self.recognizer.phrase_threshold = 0.3
        self.microphone = None
        self._is_calibrated = False

    def calibrate_microphone(self, source, duration=1.0):
        """Calibrates microphone for ambient noise level."""
        try:
            print("🎤 Calibrating microphone for background noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            self._is_calibrated = True
            print(f"🎤 Calibration complete. Energy threshold set to: {self.recognizer.energy_threshold}")
        except Exception as e:
            logger.error(f"Microphone calibration error: {e}")

    def listen_once(self, source, timeout=None, phrase_time_limit=10) -> str:
        """
        Listens for a single utterance using VAD and returns transcribed text.
        Uses Groq Whisper Large v3 with Google STT fallback.
        """
        if not self._is_calibrated:
            self.calibrate_microphone(source, duration=0.8)

        print("🎤 Listening...")
        try:
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            logger.error(f"Listening error: {e}")
            return ""

        return self.transcribe_audio(audio)

    def transcribe_audio(self, audio: sr.AudioData) -> str:
        """
        Transcribes SpeechRecognition AudioData using Groq Whisper Large v3.
        Falls back to Google STT if Groq fails or API key is not configured.
        """
        wav_bytes = audio.get_wav_data()

        # Method 1: Groq Whisper Large v3
        if _groq_client and getattr(config, "GROQ_API_KEY", ""):
            try:
                buf = io.BytesIO(wav_bytes)
                buf.name = "audio.wav"
                transcription = _groq_client.audio.transcriptions.create(
                    file=buf,
                    model=getattr(config, "WHISPER_MODEL", "whisper-large-v3"),
                    prompt="The user is speaking Hinglish, Hindi, or English commands to Jarvis AI assistant.",
                    response_format="text"
                )
                text = str(transcription).strip()
                if text:
                    print(f"⚡ [Whisper STT]: {text}")
                    return text
            except Exception as e:
                print(f"Whisper STT Error ({e}), falling back to Google STT...")

        # Method 2: Google Speech Recognition fallback
        try:
            text = self.recognizer.recognize_google(audio, language="en-IN")
            text = text.strip()
            print(f"🌐 [Google STT]: {text}")
            return text
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            logger.error(f"Google STT Error: {e}")
            return ""

# Module-level convenience functions
_stt_instance = SpeechToTextEngine()

def record_and_transcribe(duration=None) -> str:
    """Convenience helper to open mic, record once with VAD, and transcribe."""
    with sr.Microphone() as source:
        return _stt_instance.listen_once(source, phrase_time_limit=duration or 10)

def transcribe_wav_bytes(wav_bytes: bytes) -> str:
    audio = sr.AudioData(wav_bytes, 16000, 2)
    return _stt_instance.transcribe_audio(audio)