import asyncio
import edge_tts
import pygame
import tempfile
import os
import time
from config import TTS_VOICE

if not pygame.mixer.get_init():
    pygame.mixer.init()

async def _speak_async(text: str):
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    # tempfile ka use sahi hai, lekin file close karna zaroori hai
    fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    await communicate.save(tmp_path)
    return tmp_path

def speak(text: str):
    print(f"🔊 Jarvis: {text}")
    
   
    try:
        tmp_path = asyncio.run(_speak_async(text))
    except Exception as e:
        print(f"TTS Generation Error: {e}")
        return 

    try:
        if os.path.exists(tmp_path):
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
           
            pygame.mixer.music.unload()
            time.sleep(0.2) 
            
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        print(f"TTS Playback Error (Ignore this): {e}")
        