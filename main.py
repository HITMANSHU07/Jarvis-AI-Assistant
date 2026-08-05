import os
import threading
import time
import speech_recognition as sr
import pyttsx3
import config
import requests
from gui.app_window import JarvisApp

def speak(text: str):
    """Male Voice Speaker Function"""
    def _speak():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 165)
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
            print("TTS Error:", e)

    threading.Thread(target=_speak, daemon=True).start()

def get_ai_response(prompt: str) -> str:
    """Gets dynamic response from Groq LLM API"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": config.LLM_MODEL,
            "messages": [
                {"role": "system", "content": "You are Jarvis, a helpful, fast, and highly intelligent AI voice assistant. Keep answers concise, natural, and friendly."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150
        }
        response = requests.post(url, json=data, headers=headers, timeout=6)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("API Error:", e)
    return f"I processed your command: {prompt}"

class JarvisEngine:
    def __init__(self, app: JarvisApp):
        self.app = app
        self.recognizer = sr.Recognizer()
        
        # High Accuracy Mic Tuning
        self.recognizer.energy_threshold = 200      # Sensitive to normal speaking voice
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6         # Fast response (doesn't wait long after you stop speaking)
        
        self.is_listening_active = False

    def start_background_listening(self):
        """Non-stop background listening loop"""
        with sr.Microphone(device_index=1) as source:
            # Calibrate once for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            
            while self.is_listening_active:
                self.app.set_status("listening")
                try:
                    # Listen continuously in background
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                    
                    self.app.set_status("thinking")
                    text = self.recognizer.recognize_google(audio, language="en-IN")
                    
                    if text and len(text.strip()) > 0:
                        self.app.add_user_message(text)
                        self.process_command(text)
                except sr.UnknownValueError:
                    pass  # Ignore unrecognized noise quietly
                except Exception as e:
                    print("Background listener error:", e)
                    time.sleep(0.5)

    def toggle_mic(self):
        """Toggle Always-On Mic Mode"""
        if not self.is_listening_active:
            self.is_listening_active = True
            self.app.add_system("Jarvis is now continuously listening in background...")
            threading.Thread(target=self.start_background_listening, daemon=True).start()
        else:
            self.is_listening_active = False
            self.app.add_system("Continuous listening stopped.")
            self.app.set_status("idle")

    def process_command(self, text: str):
        command = text.lower()
        
        # 1. Open Instagram
        if "instagram" in command:
            msg = "Instagram khul raha hai"
            self.app.add_jarvis_message(msg)
            speak(msg)
            import webbrowser
            webbrowser.open("https://instagram.com")

        # 2. Open WhatsApp
        elif "whatsapp" in command:
            msg = "WhatsApp khul raha hai"
            self.app.add_jarvis_message(msg)
            speak(msg)
            import webbrowser
            webbrowser.open("https://web.whatsapp.com")

        # 3. YouTube Song / Search
        elif "play" in command or ("youtube" in command and len(command) > 10):
            search_query = command.replace("open", "").replace("play", "").replace("on youtube", "").strip()
            msg = f"YouTube par {search_query} chala raha hu"
            self.app.add_jarvis_message(msg)
            speak(msg)
            import webbrowser
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")

        elif "youtube" in command:
            msg = "YouTube khul raha hai"
            self.app.add_jarvis_message(msg)
            speak(msg)
            import webbrowser
            webbrowser.open("https://youtube.com")

        # 4. Google Search
        elif "google" in command:
            msg = "Google khul raha hai"
            self.app.add_jarvis_message(msg)
            speak(msg)
            import webbrowser
            webbrowser.open("https://google.com")

        # 5. Smart AI Chat (Groq API)
        else:
            reply = get_ai_response(text)
            self.app.add_jarvis_message(reply)
            speak(reply)
        
        # Auto-return to listening status
        if self.is_listening_active:
            self.app.set_status("listening")
        else:
            self.app.set_status("idle")

def start_assistant():
    app = JarvisApp()
    engine = JarvisEngine(app)

    # Attach Handlers
    app._on_text_command = engine.process_command
    app._on_mic_command = engine.toggle_mic

    app.run()

if __name__ == "__main__":
    start_assistant()