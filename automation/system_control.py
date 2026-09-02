import os
import sys
import ctypes
import datetime
import subprocess
import webbrowser
import pyautogui
from utils.helpers import get_system_stats, get_battery_status

pyautogui.PAUSE = 0.15

# App mappings for Windows system execution
APP_COMMANDS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "chrome": "start chrome",
    "browser": "start chrome",
    "cmd": "start cmd",
    "terminal": "start cmd",
    "command prompt": "start cmd",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "this pc": "explorer.exe",
    "my computer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "vscode": "code",
    "vs code": "code",
    "code": "code",
    "spotify": "start spotify",
    "control panel": "control",
    "settings": "start ms-settings:",
}

def open_app(app_name: str) -> str:
    """Launches a desktop application by name."""
    clean_name = app_name.lower().strip()
    
    # Direct match in registry
    for key, cmd in APP_COMMANDS.items():
        if key in clean_name:
            try:
                if cmd.startswith("start "):
                    os.system(cmd)
                else:
                    subprocess.Popen(cmd, shell=True)
                return f"{app_name.capitalize()} khol diya hai."
            except Exception as e:
                return f"{app_name} kholne mein error aaya: {e}"
                
    # Fallback to Windows search / start command
    try:
        os.system(f"start {clean_name}")
        return f"{app_name.capitalize()} launch kar raha hu."
    except Exception as e:
        return f"App '{app_name}' nahi mila."

def open_website(url_or_domain: str) -> str:
    """Opens a website in the default browser."""
    url = url_or_domain.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return f"Website khul rahi hai."
    except Exception as e:
        return f"Website open error: {e}"

def search_google(query: str) -> str:
    """Searches Google for query."""
    q = query.strip()
    if q:
        url = f"https://www.google.com/search?q={q}"
        webbrowser.open(url)
        return f"Google par '{q}' search kar raha hu."
    return "Kya search karna hai bataiye."

def search_youtube(query: str) -> str:
    """Searches YouTube for query."""
    q = query.strip()
    if q:
        url = f"https://www.youtube.com/results?search_query={q}"
        webbrowser.open(url)
        return f"YouTube par '{q}' search kar raha hu."
    return "YouTube khul raha hai."

def play_youtube_video(query: str) -> str:
    """Plays video on YouTube using pywhatkit or webbrowser."""
    q = query.strip()
    if not q:
        webbrowser.open("https://youtube.com")
        return "YouTube open kar raha hu."
    try:
        import pywhatkit
        pywhatkit.playonyt(q)
        return f"YouTube par {q} play kar raha hu."
    except Exception:
        url = f"https://www.youtube.com/results?search_query={q}"
        webbrowser.open(url)
        return f"YouTube par {q} dhundh raha hu."

def take_screenshot() -> str:
    """Takes a screenshot and saves to Pictures/Screenshots folder."""
    try:
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(pictures_dir, exist_ok=True)
        filename = f"Screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(pictures_dir, filename)
        
        img = pyautogui.screenshot()
        img.save(filepath)
        return f"Screenshot save ho gaya: Pictures/Screenshots me."
    except Exception as e:
        return f"Screenshot lene mein error: {e}"

def lock_screen() -> str:
    """Locks Windows screen."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Screen lock kar diya hai."
    except Exception as e:
        return f"Screen lock error: {e}"

def shutdown_pc(delay_seconds=5) -> str:
    """Initiates PC shutdown."""
    os.system(f"shutdown /s /f /t {delay_seconds}")
    return f"System {delay_seconds} seconds me shutdown ho raha hai."

def restart_pc(delay_seconds=5) -> str:
    """Initiates PC restart."""
    os.system(f"shutdown /r /f /t {delay_seconds}")
    return f"System {delay_seconds} seconds me restart ho raha hai."

def cancel_shutdown() -> str:
    """Cancels shutdown/restart timer."""
    os.system("shutdown /a")
    return "Shutdown cancel kar diya gaya hai."

def mute_volume():
    """Toggles system audio mute."""
    pyautogui.press('volumemute')
    return "Sound toggle kar diya hai."

def close_active_window():
    """Closes current active window."""
    pyautogui.hotkey('alt', 'f4')
    return "Active window close kar diya."

def get_system_report() -> str:
    """Returns human readable CPU, RAM and battery status."""
    stats = get_system_stats()
    batt = get_battery_status()
    
    report = f"System Report: CPU usage {stats['cpu']} percent, RAM usage {stats['ram']} percent."
    if batt:
        status = "charging" if batt["charging"] else "on battery"
        report += f" Battery level is {batt['percent']} percent ({status})."
    return report