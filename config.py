import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PICOVOICE_KEY = os.getenv("PICOVOICE_KEY", "")

LLM_MODEL = "llama-3.3-70b-versatile"
WHISPER_MODEL = "whisper-large-v3"
TTS_VOICE = "en-IN-PrabhatNeural"

SYSTEM_PROMPT = """
You are Jarvis, a fast, witty, and intelligent AI assistant.
- ALWAYS respond in short, conversational Hinglish (1-2 sentences max).
- If an action/command is required (like opening an app, YouTube search, volume control, etc.), append the action tag at the end in strict JSON format.

Action Schema:
<ACTION>{"type": "<ACTION_TYPE>", "target": "<APP_NAME_OR_QUERY>"}</ACTION>

Allowed ACTION_TYPE: "open_app", "web_search", "youtube_play"
"""
