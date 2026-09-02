import json
import re
import logging
from groq import Groq
import config

logger = logging.getLogger(__name__)

conversation_history = []

SYSTEM_PROMPT = """
You are Jarvis, an ultra-fast, intelligent, and polite AI voice assistant. Always start with "Jai Shree Ram" if greeted.
STRICT RULES:
1. Always communicate in simple, concise, and natural Hinglish (mix of Hindi & English written in Latin script).
2. Keep responses very short (maximum 1-2 sentences) so voice synthesis is quick and conversational.
3. If the user asks you to perform an action (e.g. WhatsApp message, YouTube search, open app, volume control, etc.), output a JSON action inside <ACTION> tags at the end of your response.
   Example formats:
   - "Mummy ko WhatsApp message bhej raha hu. <ACTION>{"type": "whatsapp", "contact": "mummy", "message": "mai aa raha hu"}</ACTION>"
   - "YouTube par lofi songs search kar raha hu. <ACTION>{"type": "youtube", "query": "lofi songs"}</ACTION>"
   - "Volume 50 percent set kar diya. <ACTION>{"type": "volume", "value": 50}</ACTION>"
   - "Calculator khol raha hu. <ACTION>{"type": "open_app", "app": "calculator"}</ACTION>"
4. If no specific action tag is needed, respond naturally without <ACTION> tags.
"""

def clear_history():
    global conversation_history
    conversation_history = []

def get_response(user_input: str) -> tuple[str, dict | None]:
    global conversation_history

    api_key = getattr(config, "GROQ_API_KEY", "")
    if not api_key:
        return "Groq API key `.env` file mein config nahi hai. Kripya API key add karein.", None

    conversation_history.append({"role": "user", "content": user_input})
    if len(conversation_history) > 12:
        conversation_history = conversation_history[-12:]
    
    try:
        client = Groq(api_key=api_key)
        model_name = getattr(config, "LLM_MODEL", "llama-3.3-70b-versatile")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            temperature=0.3,
            max_tokens=256
        )
        
        full_reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": full_reply})
        
        # Parse Action
        action = None
        action_match = re.search(r'<ACTION>(.*?)</ACTION>', full_reply, re.DOTALL)
        
        if action_match:
            try:
                json_str = action_match.group(1).strip()
                action = json.loads(json_str)
            except Exception as e:
                logger.error(f"Action JSON parse error: {e}")
        
        spoken_reply = re.sub(r'<ACTION>.*?</ACTION>', '', full_reply, flags=re.DOTALL).strip()
        return spoken_reply, action
        
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return "Abhi server connection error aa raha hai, thodi der baad try karein.", None