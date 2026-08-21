import os
import re
import json
import time
import threading
import webbrowser
import speech_recognition as sr
import requests
import pyttsx3
import config
from gui.app_window import JarvisApp

is_speaking = False

def speak(text: str):
    global is_speaking
    def _speak():
        global is_speaking
        is_speaking = True
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 165)
            voices = engine.getProperty('voices')
            for v in voices:
                if "david" in v.name.lower() or "male" in v.name.lower():
                    engine.setProperty('voice', v.id)
                    break
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("[TTS Error]:", e)
        finally:
            time.sleep(0.3)
            is_speaking = False

    threading.Thread(target=_speak, daemon=True).start()

def get_ai_response(prompt: str):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": config.LLM_MODEL,
            "messages": [
                {"role": "system", "content": config.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "max_tokens": 150
        }
        response = requests.post(url, json=data, headers=headers, timeout=8)
        if response.status_code == 200:
            raw_reply = response.json()['choices'][0]['message']['content'].strip()
            action_data = None
            action_match = re.search(r"<ACTION>(.*?)</ACTION>", raw_reply, re.DOTALL)
            if action_match:
                try:
                    action_data = json.loads(action_match.group(1).strip())
                except Exception:
                    pass
                clean_reply = re.sub(r"<ACTION>.*?</ACTION>", "", raw_reply).strip()
            else:
                clean_reply = raw_reply
            return clean_reply, action_data
    except Exception as e:
        print("[API Error]:", e)
    return "Command process karne me dikkat aayi.", None

class JarvisEngine:
    def __init__(self, app: JarvisApp):
        self.app = app
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.is_listening_active = False

    def start_background_listening(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                while self.is_listening_active:
                    if is_speaking:
                        time.sleep(0.2)
                        continue
                    self.app.set_status("listening")
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                        if is_speaking:
                            continue
                        self.app.set_status("thinking")
                        text = self.recognizer.recognize_google(audio, language="en-IN")
                        if text and len(text.strip()) > 0:
                            self.app.add_user_message(text)
                            self.process_command(text)
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        pass
                    except Exception as e:
                        print("[Listener Error]:", e)
                        time.sleep(0.5)
        except Exception as mic_err:
            print("[Mic Error]:", mic_err)

    def toggle_mic(self):
        if not self.is_listening_active:
            self.is_listening_active = True
            self.app.add_system("Jarvis listening shuru kar chuka hai...")
            threading.Thread(target=self.start_background_listening, daemon=True).start()
        else:
            self.is_listening_active = False
            self.app.add_system("Listening band kar di gayi.")
            self.app.set_status("idle")

    def execute_action(self, action: dict):
        if not action:
            return
        act_type = action.get("type", "")
        target = action.get("target", "")

        if act_type == "open_app":
            apps = {"chrome": "start chrome", "notepad": "notepad", "calculator": "calc"}
            os.system(apps.get(target.lower(), f"start {target}"))
        elif act_type == "web_search":
            webbrowser.open(f"https://www.google.com/search?q={target}")
        elif act_type == "youtube_play":
            webbrowser.open(f"https://www.youtube.com/results?search_query={target}")

    def process_command(self, text: str):
        command = text.lower().strip()
        if "instagram" in command:
            self.app.add_jarvis_message("Instagram khol raha hu.")
            speak("Instagram khol raha hu.")
            webbrowser.open("https://instagram.com")
        elif "whatsapp" in command:
            self.app.add_jarvis_message("WhatsApp khol raha hu.")
            speak("WhatsApp khol raha hu.")
            webbrowser.open("https://web.whatsapp.com")
        else:
            reply, action = get_ai_response(text)
            if reply:
                self.app.add_jarvis_message(reply)
                speak(reply)
            if action:
                self.execute_action(action)

        if self.is_listening_active:
            self.app.set_status("listening")
        else:
            self.app.set_status("idle")

def start_assistant():
    app = JarvisApp()
    engine = JarvisEngine(app)
    app._on_text_command = engine.process_command
    app._on_mic_command = engine.toggle_mic
    app.run()

if __name__ == "__main__":
    start_assistant()
