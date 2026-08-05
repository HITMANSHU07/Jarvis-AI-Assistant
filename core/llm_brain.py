import json
import re
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

client = Groq(api_key=GROQ_API_KEY)
conversation_history = []

# DYNAMIC PROMPT: Naam fix nahi hai, AI ab logic seekhega
SYSTEM_PROMPT = """
You are Jarvis, a professional and extremely concise AI assistant.
STRICT RULES:
1. Always reply in Roman Urdu.
2. LIMIT: Maximum 1 sentence. 
3. If the user gives a CLEAR COMMAND, you MUST output a JSON object inside <ACTION> tags.
4. Format: "Reply text here <ACTION>{"type": "...", "contact": "...", "message": "...", "query": "..."}</ACTION>"
5. If the user says "message [NAME] [TEXT]", identify [NAME] as contact and [TEXT] as message.
6. If the user says "play [SONG] on YouTube", identify [SONG] as query and set type to "youtube".
"""

def get_response(user_input: str) -> tuple[str, dict | None]:
    conversation_history.append({"role": "user", "content": user_input})
    if len(conversation_history) > 10:
        conversation_history.pop(0)
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            temperature=0.1, 
            max_tokens=512
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
                print(f"DEBUG: JSON Parse Error: {e}")
        
        spoken_reply = re.sub(r'<ACTION>.*?</ACTION>', '', full_reply, flags=re.DOTALL).strip()
        return spoken_reply, action
        
    except Exception as e:
        print(f"DEBUG: LLM Error: {e}")
        return "Main abhi thora busy hoon, thori der mein baat karte hain.", None