# 🤖 Jarvis AI — Bilingual Voice Desktop Assistant

> A production-grade, hands-free AI assistant that understands  Hindi & English,
> speaks with a neural female voice, and performs live desktop automation.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

- 🎙️ **Bilingual STT** — Groq Whisper (Hindi + English)
- 🧠 **AI Brain** — LLaMA 3.3-70B via Groq (ultra-fast inference)
- 🔊 **Neural TTS** — Microsoft Edge-TTS female voice
- 💬 **WhatsApp Automation** — sends messages via desktop GUI
- ▶️ **YouTube Control** — voice-activated browser playback
- ⚙️ **System Control** — shutdown, mute, close windows
- 🖥️ **Professional GUI** — CustomTkinter dark theme dashboard

---

#£# 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/himanshukumar/Jarvis-AI-Assistant
cd jarvis-ai-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.template .env
# Open .env and add your GROQ_API_KEY
```

### 4. Run
```bash
python main.py
```

---

### 🗂️ Project Structure

```text
jarvis-ai/
├── main.py              # Entry point
├── config.py            # Settings & prompts
├── core/
│   ├── stt_engine.py    # Speech-to-Text (Groq Whisper)
│   ├── llm_brain.py     # AI reasoning (LLaMA 3.3)
│   ├── tts_engine.py    # Text-to-Speech (Edge-TTS)
│   └── wake_word.py     # "Jarvis" trigger detection
├── automation/
│   ├── whatsapp_bot.py  # WhatsApp Desktop automation
│   ├── browser_bot.py   # Selenium web automation
│   └── system_control.py
├── gui/
│   ├── app_window.py    # Main dashboard
│   ├── waveform_widget.py
│   └── chat_log.py
└── utils/
    └── helpers.py
```

---

## 🔑 API Keys Required

| Service | Purpose | Get it at |
|---------|---------|-----------|
| Groq | LLM + STT | [console.groq.com](https://console.groq.com) |
| Picovoice *(optional)* | Wake word | [console.picovoice.ai](https://console.picovoice.ai) |

---

## 👥 Author & Creator

| Name | Role |
|------|------|
| **Himanshu Kumar** | Lead Developer & Creator |

---

## 📄 License

Copyright (c) 2026 **Himanshu Kumar**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

MIT License — Free to use, edit, and modify. Created with 🤖
 by **Himanshu Kumar**.
