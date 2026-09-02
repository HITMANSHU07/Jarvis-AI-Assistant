# 🤖 Jarvis AI — Continuous Bilingual Voice Assistant & Desktop Automation

> A production-grade, continuous voice AI assistant that understands Hinglish & English, speaks with natural neural voice, and performs live desktop & web automation.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3-orange?style=flat-square)
![STT](https://img.shields.io/badge/STT-Whisper%20Large%20v3-green?style=flat-square)
![TTS](https://img.shields.io/badge/TTS-Edge--TTS%20Neural-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🚀 Repository & Live Demo Links

* 💻 **GitHub Repository:** [https://github.com/HITMANSHU07/Jarvis-AI-Assistant](https://github.com/HITMANSHU07/Jarvis-AI-Assistant)
* 🌐 **Web Voice Assistant Demo:** Run `python web_server.py` to open the Web Voice Assistant in any browser!
* 🌐 **GitHub Pages Live Demo:** [https://hitmanshu07.github.io/Jarvis-AI-Assistant](https://hitmanshu07.github.io/Jarvis-AI-Assistant)

---

## ✨ Features

* 🎙️ **Continuous Voice Listening Mode ("Always-On")** — Once turned on, Jarvis stays active continuously. Automatically pauses mic listening while speaking (TTS) to prevent feedback loops, then resumes listening immediately.
* 🌐 **Web & Desktop Dual Interface** — Use the rich Cyberpunk CustomTkinter Desktop GUI app or the browser Web Voice Assistant.
* ⚡ **High-Accuracy STT (Groq Whisper Large v3)** — Dynamic Voice Activity Detection (VAD) with ambient noise adjustment. Ultra-fast transcription of Hinglish, Hindi, and English with Google STT fallback.
* 🧠 **AI Brain (Groq LLaMA 3.3-70B)** — Ultra-fast response generation in natural, concise Hinglish.
* 🔊 **Neural TTS (Microsoft Edge-TTS)** — High-quality male neural voice (`en-US-GuyNeural` / `hi-IN-MadhurNeural`) with pyttsx3 fallback.
* 📱 **WhatsApp Automation** — Voice-controlled instant WhatsApp message sending.
* ▶️ **YouTube & Media Controls** — Search/play YouTube videos, exact volume percentage control (e.g. *"volume 40%"*), mute, play/pause, next/prev track.
* 🖥️ **App Launcher & System Controls** — Launch desktop apps (Chrome, Notepad, Calc, VS Code, Spotify, CMD, Explorer, Settings), take screenshots, lock screen, system status (CPU, RAM, Battery report), shutdown/restart timer.
* 🎨 **Cyberpunk Dashboard GUI** — CustomTkinter dark theme dashboard with real-time waveform audio monitor, status pill, and system metrics.

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/HITMANSHU07/Jarvis-AI-Assistant.git
cd Jarvis-AI-Assistant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the root directory and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

*(Get your free API key at [Groq Console](https://console.groq.com))*

---

## 🖥️ Running Jarvis

### Option A: Desktop AI Assistant GUI (Full System Controls)

```bash
python main.py
```
- Full desktop control (apps, volume %, screenshots, lock screen, WhatsApp, YouTube).
- Click the **🎤 Mic button** to toggle Continuous Voice Listening.

### Option B: Web AI Assistant Demo (Browser Voice AI)

```bash
python web_server.py
```
- Opens local Web Assistant server at `http://localhost:8000`.
- Works in Google Chrome, Microsoft Edge, Brave, and Opera with browser Web Speech API.

---

## 🗂️ Project Structure

```text
Jarvis-AI-Assistant/
├── main.py                    # Desktop Application entry point & core orchestrator
├── web_server.py              # Web Voice Assistant local server launcher
├── config.py                  # API keys, voice settings & prompts
├── requirements.txt           # Dependencies
├── web/
│   └── index.html             # Web AI Voice Assistant interface
├── core/
│   ├── stt_engine.py          # Speech-to-Text (Groq Whisper v3 + VAD + Google STT)
│   ├── tts_engine.py          # Text-to-Speech (Edge-TTS Neural + pyttsx3 fallback)
│   ├── llm_brain.py           # AI reasoning (LLaMA 3.3 70B via Groq)
│   └── wake_word.py           # Trigger word detector
├── automation/
│   ├── system_control.py      # App launcher, system metrics, volume & screenshot controls
│   ├── whatsapp_bot.py        # WhatsApp Web automation
│   └── browser_bot.py         # Browser automation
├── gui/
│   ├── app_window.py          # CustomTkinter main GUI dashboard
│   ├── waveform_widget.py     # Live audio waveform visualizer
│   └── chat_log.py            # Conversation log component
└── utils/
    └── helpers.py             # System stats, logging & time utilities
```

---

## 👥 Author & Creator

| Name | Role |
| :--- | :--- |
| **Himanshu Kumar** | Lead Developer & Creator |

---

## 📄 License

MIT License — Free to use, modify, and distribute.

Created with 🤖 by **Himanshu Kumar**.
