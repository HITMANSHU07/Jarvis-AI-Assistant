from core.stt_engine import record_audio, transcribe
from core.llm_brain import get_response
from core.tts_engine import speak
from automation.whatsapp_bot import send_whatsapp_message
from automation.browser_bot import play_youtube, open_website
from automation.system_control import shutdown_pc, mute_volume, close_active_window
from gui.app_window import JarvisApp

def execute_action(action: dict):
    """Executes the parsed action from the AI brain."""
    if not action or action.get("type") == "none":
        return
    
    atype = action.get("type")
    
    if atype == "whatsapp":
        send_whatsapp_message(action["contact"], action["message"])
    
    elif atype == "youtube":
        play_youtube(action["query"])
    
    elif atype == "browser":
        open_website(action.get("url", f"https://google.com/search?q={action.get('query','')}"))
    
    elif atype == "system":
        cmd = action.get("command")
        if cmd == "shutdown":   shutdown_pc()
        elif cmd == "mute":     mute_volume()
        elif cmd == "close":    close_active_window()

def jarvis_loop():
    """Main voice assistant loop."""
    speak("Assalam o Alaikum! Main Jarvis hoon. Aap ki kya madad kar sakta hoon?")
    
    while True:
        audio = record_audio(duration=6)
        user_text = transcribe(audio)
        
        if not user_text.strip():
            continue
        
        print(f"👤 You: {user_text}")
        
        if any(w in user_text.lower() for w in ["goodbye", "khuda hafiz", "bye jarvis"]):
            speak("Khuda Hafiz! Take care!")
            break
        
        reply, action = get_response(user_text)
        speak(reply)
        execute_action(action)

if __name__ == "__main__":
    # To run without GUI:
    # jarvis_loop()
    
    # To run with GUI:
    app = JarvisApp(assistant_loop=jarvis_loop)
    app.run()