import os
from dotenv import load_dotenv
from pathlib import Path

# Setup environment
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# API Keys
GROQ_API_KEY = ""
PICOVOICE_KEY = ", "

# Model Settings
LLM_MODEL = "llama-3.3-70b-versatile"
WHISPER_MODEL = "whisper-large-v3"

# Voice Settings
TTS_VOICE = "en-US-GuyNeural" # Male voice

# Master Behavior Prompt
SYSTEM_PROMPT = """
You are Jarvis, a friendly and intelligent AI assistant. Always start with "Jai Shree Ram".
- ALWAYS communicate in simple and natural Hinglish.
- Be witty, natural, and use filler words like "Acha", "Hmm", "Bilkul!".
- Keep responses short.
- If an action (WhatsApp, YouTube, etc.) is needed, YOU MUST output the <ACTION>{...}</ACTION> tag at the end.
- Extract contact names and message content accurately. If information is missing, ask for it.
"""