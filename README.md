# 🤖 Jarvis AI — Bilingual Voice Desktop Assistant

> A production-grade, hands-free AI assistant that understands Hindi & English, speaks with a neural female voice, and performs live desktop automation.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square\&logo=python)
![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🚀 Project Links

* 💻 **[GitHub Repository](https://github.com/HITMANSHU07/Jarvis-AI-Assistant)**
* 🎥 **Demo Video:** Coming Soon
* 🌐 **Live Demo:** Not available yet — Jarvis is currently a desktop application.

---

## ✨ Features

* 🎙️ **Bilingual STT** — Groq Whisper (Hindi + English)
* 🧠 **AI Brain** — LLaMA 3.3-70B via Groq (ultra-fast inference)
* 🔊 **Neural TTS** — Microsoft Edge-TTS female voice
* 💬 **WhatsApp Automation** — sends messages via desktop GUI
* ▶️ **YouTube Control** — voice-activated browser playback
* ⚙️ **System Control** — shutdown, mute, close windows
* 🖥️ **Professional GUI** — CustomTkinter dark theme dashboard

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

Create a `.env` file and add your API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run Jarvis

```bash
python main.py
```

---

## 🗂️ Project Structure

```text
Jarvis-AI-Assistant/
├── main.py                    # Application entry point
├── config.py                  # Settings & system prompts
├── core/
│   ├── stt_engine.py          # Speech-to-Text (Groq Whisper)
│   ├── llm_brain.py           # AI reasoning (LLaMA 3.3)
│   ├── tts_engine.py          # Text-to-Speech (Edge-TTS)
│   └── wake_word.py           # "Jarvis" trigger detection
├── automation/
│   ├── whatsapp_bot.py        # WhatsApp desktop automation
│   ├── browser_bot.py         # Browser automation
│   └── system_control.py      # System-level controls
├── gui/
│   ├── app_window.py          # Main dashboard
│   ├── waveform_widget.py     # Voice waveform UI
│   └── chat_log.py            # Conversation history
└── utils/
    └── helpers.py             # Utility functions
```

---

## 🔑 API Keys Required

| Service                | Purpose   | Get it at                                         |
| ---------------------- | --------- | ------------------------------------------------- |
| Groq                   | LLM + STT | [Groq Console](https://console.groq.com)          |
| Picovoice *(optional)* | Wake Word | [Picovoice Console](https://console.picovoice.ai) |

> ⚠️ Never commit your `.env` file or expose your API keys publicly.

---

## 🎯 How Jarvis Works

```text
🎙️ User Voice
      ↓
🎧 Speech Recognition
      ↓
🧠 Groq LLaMA AI
      ↓
⚙️ Intent / Command Processing
      ↓
💻 Desktop Automation
      ↓
🔊 Neural Voice Response
```

---

## 🖥️ Application

Jarvis is designed as a **desktop AI assistant** rather than a traditional web application.

It can listen to voice commands, understand Hindi and English, process requests using an LLM, speak responses, and perform supported desktop and browser automation tasks.

---

## 👥 Author & Creator

| Name               | Role                     |
| ------------------ | ------------------------ |
| **Himanshu Kumar** | Lead Developer & Creator |

---

## 📄 License

Copyright (c) 2026 **Himanshu Kumar**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

MIT License — Free to use, edit, and modify.

Created with 🤖 by **Himanshu Kumar**.
