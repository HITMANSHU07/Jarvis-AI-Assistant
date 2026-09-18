import sys
import os
import re
import time
import threading
import difflib
import speech_recognition as sr
import pyautogui

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import config
from gui.app_window import JarvisApp
from core.stt_engine import SpeechToTextEngine
from core.tts_engine import speak, is_tts_speaking, set_tts_status_callback
from core.llm_brain import get_response, clear_history
from automation.system_control import (
    open_app, open_website, search_google, search_youtube,
    play_youtube_video, take_screenshot, lock_screen, shutdown_pc,
    restart_pc, cancel_shutdown, mute_volume, close_active_window,
    get_system_report
)

pyautogui.PAUSE = 0.15

# -------------------------------------------------------------
# WhatsApp Contact Resolver
# -------------------------------------------------------------
def find_contact(name: str):
    name = name.strip().lower()
    contacts = getattr(config, "CONTACTS", {})
    if not contacts:
        return None
    if name in contacts:
        return contacts[name]
    matches = difflib.get_close_matches(name, contacts.keys(), n=1, cutoff=0.5)
    if matches:
        return contacts[matches[0]]
    return None

def send_whatsapp_message(contact_name: str, message: str) -> str:
    """Sends WhatsApp message via pywhatkit (WhatsApp Web)."""
    number = find_contact(contact_name)
    if not number:
        return f"'{contact_name}' ka contact dictionary mein nahi mila. Config file check karein."
    try:
        import pywhatkit
        pywhatkit.sendwhatmsg_instantly(
            phone_no=f"+{number}",
            message=message,
            wait_time=15,
            tab_close=True,
            close_time=3,
        )
        return f"{contact_name.capitalize()} ko WhatsApp message bhej diya."
    except Exception as e:
        print("WhatsApp Error:", e)
        return "WhatsApp message bhejne mein error aaya. Login check karein."

# -------------------------------------------------------------
# System Volume Control via Pycaw
# -------------------------------------------------------------
def _get_volume_interface():
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return interface.QueryInterface(IAudioEndpointVolume)

def set_system_volume(percent: int) -> bool:
    try:
        vol = _get_volume_interface()
        target = max(0.0, min(1.0, percent / 100.0))
        vol.SetMasterVolumeLevelScalar(target, None)
        return True
    except Exception as e:
        print("Volume Set Error:", e)
        return False

def get_system_volume() -> int:
    try:
        vol = _get_volume_interface()
        return round(vol.GetMasterVolumeLevelScalar() * 100)
    except Exception as e:
        print("Volume Read Error:", e)
        return -1

def adjust_system_volume(delta: int) -> int:
    current = get_system_volume()
    if current == -1:
        return -1
    new_val = max(0, min(100, current + delta))
    set_system_volume(new_val)
    return new_val

# -------------------------------------------------------------
# Jarvis Core Engine
# -------------------------------------------------------------
class JarvisEngine:
    def __init__(self, app: JarvisApp):
        self.app = app
        self.stt = SpeechToTextEngine()
        self.is_listening_active = False
        self._listener_thread = None

        # Bind TTS status callbacks to update GUI pill state
        set_tts_status_callback(self._on_tts_status_change)

    def _on_tts_status_change(self, state: str):
        if state == "speaking":
            self.app.set_status("speaking")
        elif state == "idle":
            if self.is_listening_active:
                self.app.set_status("listening")
            else:
                self.app.set_status("idle")

    def toggle_mic(self):
        """Toggles continuous mic listening mode."""
        if not self.is_listening_active:
            self.is_listening_active = True
            self.app.set_mic_active(True)
            self.app.add_system("Continuous voice listening turned ON.")
            msg = "Continuous listening on ho gaya hai. Aap bolo, main sun raha hu."
            self.app.add_jarvis_message(msg)
            speak(msg)
            
            self._listener_thread = threading.Thread(target=self._background_listening_loop, daemon=True)
            self._listener_thread.start()
        else:
            self.is_listening_active = False
            self.app.set_mic_active(False)
            self.app.set_status("idle")
            self.app.add_system("Continuous voice listening turned OFF.")
            msg = "Continuous listening off kar diya hai."
            self.app.add_jarvis_message(msg)
            speak(msg)

    def _background_listening_loop(self):
        """Continuous background listening loop with self-mute protection."""
        with sr.Microphone() as source:
            self.stt.calibrate_microphone(source, duration=0.8)
            
            while self.is_listening_active:
                # 1. Self-listening protection: Pause listening while TTS audio is playing
                if is_tts_speaking:
                    time.sleep(0.15)
                    continue

                self.app.set_status("listening")
                
                # 2. Listen for speech using VAD
                text = self.stt.listen_once(source, phrase_time_limit=10)
                
                # Re-check active state after listening delay
                if not self.is_listening_active:
                    break

                if text and len(text.strip()) > 0:
                    cmd_lower = text.lower().strip()
                    
                    # 3. Check for voice commands to stop continuous listening
                    stop_keywords = [
                        "stop listening", "stop mic", "jarvis stop", "turn off mic",
                        "listening off", "mic band karo", "chup karo", "bye jarvis", "bye"
                    ]
                    if any(w in cmd_lower for w in stop_keywords):
                        self.app.add_user_message(text)
                        msg = "Continuous listening stop kar raha hu. Baad me milte hain!"
                        self.app.add_jarvis_message(msg)
                        self.is_listening_active = False
                        self.app.set_mic_active(False)
                        self.app.set_status("idle")
                        speak(msg)
                        break
                    
                    # 4. Process valid command
                    self.app.add_user_message(text)
                    self.app.set_status("thinking")
                    self.process_command(text)
                else:
                    time.sleep(0.1)

    def process_command(self, text: str):
        command = text.lower().strip()

        # -------------------------------------------------------------
        # STEP 1: Volume Controls
        # -------------------------------------------------------------
        if "volume" in command or "sound" in command or "aawaaz" in command:
            numbers = re.findall(r'\d+', command)
            if numbers:
                vol_num = int(numbers[0])
                set_system_volume(vol_num)
                msg = f"Volume {vol_num} percent set kar diya hai."
                self.app.add_jarvis_message(msg)
                speak(msg)
            elif any(w in command for w in ["increase", "up", "raise", "badhao", "badha do", "tez"]):
                new_val = adjust_system_volume(+10)
                msg = f"Volume badha diya, ab {new_val}% hai." if new_val != -1 else "Volume badha raha hu."
                self.app.add_jarvis_message(msg)
                speak(msg)
            elif any(w in command for w in ["decrease", "down", "kam", "ghatao", "dheere"]):
                new_val = adjust_system_volume(-10)
                msg = f"Volume kam kar diya, ab {new_val}% hai." if new_val != -1 else "Volume kam kar raha hu."
                self.app.add_jarvis_message(msg)
                speak(msg)
            elif "mute" in command or "unmute" in command:
                msg = mute_volume()
                self.app.add_jarvis_message(msg)
                speak(msg)
            else:
                msg = "Volume percentage bolo (jaise 'volume 40%') ya 'volume badhao' bolo."
                self.app.add_jarvis_message(msg)
                speak(msg)

        # -------------------------------------------------------------
        # STEP 2: System & Screen Commands
        # -------------------------------------------------------------
        elif any(w in command for w in ["screenshot", "screen shot", "photo lo"]):
            msg = take_screenshot()
            self.app.add_jarvis_message(msg)
            speak(msg)

        elif "system status" in command or "system report" in command or "battery" in command or "cpu" in command:
            msg = get_system_report()
            self.app.add_jarvis_message(msg)
            speak(msg)

        elif "lock screen" in command or command == "lock" or "lock kar do" in command:
            msg = lock_screen()
            self.app.add_jarvis_message(msg)
            speak(msg)

        elif "cancel shutdown" in command:
            msg = cancel_shutdown()
            self.app.add_jarvis_message(msg)
            speak(msg)

        elif "shutdown" in command or "band kar do pc" in command:
            msg = shutdown_pc(10)
            self.app.add_jarvis_message(msg)
            speak(msg)

        elif "restart" in command:
            msg = restart_pc(10)
            self.app.add_jarvis_message(msg)
            speak(msg)

        # -------------------------------------------------------------
        # STEP 3: Media & Keyboard Controls
        # -------------------------------------------------------------
        elif command in ["pause", "stop", "ruk jau", "roko"]:
            pyautogui.press('k')
            msg = "Playback pause kar diya."
            self.app.add_jarvis_message(msg)
            speak(msg)

        elif command in ["play", "resume", "chalao"] and len(command.split()) == 1:
            pyautogui.press('k')
            msg = "Playback resume kar raha hu."
            self.app.add_jarvis_message(msg)
            speak(msg)

        elif "next" in command or "agla" in command:
            pyautogui.hotkey('shift', 'n')
            msg = "Agla track play kar raha hu."
            self.app.add_jarvis_message(msg)
            speak(msg)

        elif "previous" in command or "pichla" in command:
            pyautogui.hotkey('shift', 'p')
            msg = "Pichla track play kar raha hu."
            self.app.add_jarvis_message(msg)
            speak(msg)

        # -------------------------------------------------------------
        # STEP 4: WhatsApp Message
        # -------------------------------------------------------------
        elif "whatsapp" in command and any(w in command for w in ["bhejo", "message", "bolo", "send"]):
            match = re.search(
                r"(?:whatsapp\s*(?:par|pe|message)?\s*)?(.+?)\s*ko\s*(?:message\s*)?(?:bolo|bhejo|likho)?\s*(?:ki|:)?\s*(.+)",
                command,
            )
            if match:
                c_name = match.group(1).replace("whatsapp", "").replace("par", "").replace("pe", "").replace("message", "").strip()
                c_msg = match.group(2).strip()
                if c_name and c_msg:
                    res = send_whatsapp_message(c_name, c_msg)
                    self.app.add_jarvis_message(res)
                    speak(res)
                else:
                    msg = "Contact aur message clear boliye."
                    self.app.add_jarvis_message(msg)
                    speak(msg)
            else:
                msg = "Example: 'whatsapp par mummy ko bolo main 10 min me aa raha hu'."
                self.app.add_jarvis_message(msg)
                speak(msg)

        # -------------------------------------------------------------
        # STEP 5: App Launcher
        # -------------------------------------------------------------
        elif any(w in command for w in ["open", "kholo", "launch", "start"]) and not any(w in command for w in ["youtube", "google", "website"]):
            target = command
            for kw in ["open", "kholo", "launch", "start", "app"]:
                target = target.replace(kw, "")
            target = target.strip()
            if target:
                res = open_app(target)
                self.app.add_jarvis_message(res)
                speak(res)
            else:
                msg = "Konsa app kholna hai bataiye."
                self.app.add_jarvis_message(msg)
                speak(msg)

        # -------------------------------------------------------------
        # STEP 6: Web Search & YouTube
        # -------------------------------------------------------------
        elif "youtube" in command:
            if "search" in command:
                q = command.replace("youtube", "").replace("search", "").replace("par", "").replace("karo", "").strip()
                res = search_youtube(q)
            else:
                q = command.replace("youtube", "").replace("play", "").replace("chalao", "").replace("par", "").replace("on", "").strip()
                res = play_youtube_video(q)
            self.app.add_jarvis_message(res)
            speak(res)

        elif "google" in command or "search" in command:
            q = command.replace("google", "").replace("search", "").replace("par", "").replace("karo", "").replace("dhoondo", "").strip()
            res = search_google(q)
            self.app.add_jarvis_message(res)
            speak(res)

        # -------------------------------------------------------------
        # STEP 7: Dynamic LLM Brain (Groq Llama 3.3 70B)
        # -------------------------------------------------------------
        else:
            spoken_reply, action = get_response(text)
            self.app.add_jarvis_message(spoken_reply)
            speak(spoken_reply)
            
            if action and isinstance(action, dict):
                act_type = action.get("type", "").lower()
                if act_type == "open_app" and "app" in action:
                    open_app(action["app"])
                elif act_type == "youtube" and "query" in action:
                    play_youtube_video(action["query"])
                elif act_type == "whatsapp" and "contact" in action and "message" in action:
                    send_whatsapp_message(action["contact"], action["message"])
                elif act_type == "volume" and "value" in action:
                    set_system_volume(int(action["value"]))

        # Restore status
        if self.is_listening_active:
            self.app.set_status("listening")
        else:
            self.app.set_status("idle")

def start_assistant():
    # Launch Web Server HUD in background daemon thread
    try:
        from web_server import run_server
        web_thread = threading.Thread(target=run_server, kwargs={"open_browser": True}, daemon=True)
        web_thread.start()
        print("🌐 Web Assistant HUD server running on http://localhost:8000")
    except Exception as e:
        print("Web server auto-start warning:", e)

    app = JarvisApp()
    engine = JarvisEngine(app)

    # Attach UI handlers
    app._on_text_command = engine.process_command
    app._on_mic_command = engine.toggle_mic

    welcome_msg = "Jai Shree Ram! Jarvis is online. Desktop Window & Web HUD (http://localhost:8000) are both active."
    app.add_jarvis_message(welcome_msg)
    threading.Thread(target=speak, args=(welcome_msg,), daemon=True).start()

    app.run()

if __name__ == "__main__":
    start_assistant()