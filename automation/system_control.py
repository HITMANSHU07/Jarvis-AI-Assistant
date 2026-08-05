import os
import pyautogui
import pygetwindow as gw

def shutdown_pc():
   
    os.system("shutdown /s /t 1 /f")

def mute_volume():
    pyautogui.press('volumemute')

def close_active_window():
    
    pyautogui.hotkey('alt', 'f4')

def increase_volume():
    for _ in range(5):
        pyautogui.press('volumeup')

def decrease_volume():
    for _ in range(5):
        pyautogui.press('volumedown')
def close_all_windows():
    os.system("taskkill /F /FI \"WINDOWTITLE ne Jarvis*\" /FI \"STATUS eq running\"")
    os.system("taskkill /F /IM chrome.exe")
'''
if __name__ == "__main__":
    print("Testing Mute Function...")
    mute_volume()
    print("Testing Volume Increase...")
    increase_volume()
'''