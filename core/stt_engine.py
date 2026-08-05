import sounddevice as sd
import numpy as np
import io
import wave
from groq import Groq
from config import GROQ_API_KEY, WHISPER_MODEL

client = Groq(api_key=GROQ_API_KEY)

def record_audio(duration=5, sample_rate=16000):
    """Records audio from microphone and returns WAV bytes."""
    print("🎤 Listening...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )
    sd.wait()
    
    # Convert to WAV bytes
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    buf.seek(0)
    return buf

def transcribe(audio_bytes) -> str:
    """Sends audio to Groq Whisper and returns transcribed text."""
    transcription = client.audio.transcriptions.create(
        file=("audio.wav", audio_bytes.read()),
        model=WHISPER_MODEL,
        language="ur",       # Urdu — handles Roman Urdu + English mix
        response_format="text"
    )
    return transcription.strip()
'''
if __name__ == "__main__":
    audio_data = record_audio(duration=5)
    text = transcribe(audio_data)
    print(f"Transcription Result: {text}")
'''