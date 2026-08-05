import pyautogui
import time
import subprocess
import threading

bot_lock = threading.Lock()
pyautogui.PAUSE = 1.0
pyautogui.FAILSAFE = True

def send_whatsapp_message(contact: str, message: str) -> bool:
    with bot_lock:
        try:
            print(f"DEBUG: Attempting to send message to {contact}")
            
            # 1. Force Open WhatsApp using Subprocess
            subprocess.Popen([r"start", "whatsapp://"], shell=True)
            time.sleep(10) # 10 sec ka wait lazmi hai load hone ke liye
            
            # 2. Automation Flow
            pyautogui.press('esc')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(1.5)
            
            # Contact Search
            pyautogui.write(contact, interval=0.1)
            time.sleep(2.0)
            pyautogui.press('enter')
            time.sleep(1.5)

            # 3. Message Send
            pyautogui.typewrite(message, interval=0.05)
            pyautogui.press('enter')
            time.sleep(3.0)

            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.5)
            
            print("DEBUG: Task successfully completed.")
            return True

        except Exception as e:
            print(f"DEBUG: Critical Error: {e}")
            return False