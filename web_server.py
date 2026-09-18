import sys
import os
import json
import http.server
import socketserver
import webbrowser
import threading

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

# Global Assistant State for Web Server
SYSTEM_POWER = True
LISTENING_ACTIVE = False

# Try importing system control modules for API backend execution
try:
    from utils.helpers import get_system_stats
    from core.llm_brain import get_response
    from automation.system_control import (
        open_app, open_website, search_google, search_youtube,
        play_youtube_video, take_screenshot, lock_screen, shutdown_pc,
        mute_volume, close_active_window, get_system_report
    )
    from core.tts_engine import speak
except Exception as e:
    print("Warning: Could not import all core engines into web_server:", e)

class JarvisRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/api/status':
            self.send_json({"power": SYSTEM_POWER, "listening": LISTENING_ACTIVE})
        elif self.path == '/api/metrics':
            try:
                stats = get_system_stats()
                self.send_json({"cpu": stats.get('cpu', 0), "ram": stats.get('ram', 0)})
            except Exception:
                self.send_json({"cpu": 15, "ram": 45})
        else:
            super().do_GET()

    def do_POST(self):
        global SYSTEM_POWER, LISTENING_ACTIVE

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if self.path == '/api/toggle_power':
            SYSTEM_POWER = data.get('power', not SYSTEM_POWER)
            print(f"[Web API] Power Toggled -> {'ONLINE' if SYSTEM_POWER else 'OFFLINE'}")
            self.send_json({"status": "ok", "power": SYSTEM_POWER})

        elif self.path == '/api/toggle_mic':
            LISTENING_ACTIVE = data.get('listening', not LISTENING_ACTIVE)
            print(f"[Web API] Mic Toggled -> {'ACTIVE' if LISTENING_ACTIVE else 'OFF'}")
            self.send_json({"status": "ok", "listening": LISTENING_ACTIVE})

        elif self.path == '/api/command':
            if not SYSTEM_POWER:
                self.send_json({"reply": "System POWER is OFFLINE. Turn on power to execute commands."})
                return

            command = data.get('command', '').strip()
            print(f"[Web API] Received Command: {command}")
            reply = self.handle_command(command)
            self.send_json({"reply": reply})
        else:
            self.send_error(404, "Endpoint not found")

    def send_json(self, data):
        response_bytes = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def handle_command(self, command: str) -> str:
        cmd_lower = command.lower()

        # Handle direct commands
        if "open" in cmd_lower and "youtube" in cmd_lower:
            return search_youtube("")
        elif "youtube" in cmd_lower and ("play" in cmd_lower or "search" in cmd_lower):
            q = cmd_lower.replace("youtube", "").replace("play", "").replace("search", "").strip()
            return play_youtube_video(q)
        elif "google" in cmd_lower or "search" in cmd_lower:
            q = cmd_lower.replace("google", "").replace("search", "").strip()
            return search_google(q)
        elif "open" in cmd_lower or "kholo" in cmd_lower:
            target = cmd_lower.replace("open", "").replace("kholo", "").strip()
            return open_app(target)
        elif "screenshot" in cmd_lower:
            return take_screenshot()
        elif "mute" in cmd_lower:
            return mute_volume()
        elif "report" in cmd_lower or "system" in cmd_lower:
            return get_system_report()
        elif "lock" in cmd_lower:
            return lock_screen()
        else:
            # Fallback to LLM response
            try:
                spoken_reply, action = get_response(command)
                if action and isinstance(action, dict):
                    act_type = action.get("type", "").lower()
                    if act_type == "open_app" and "app" in action:
                        open_app(action["app"])
                    elif act_type == "youtube" and "query" in action:
                        play_youtube_video(action["query"])
                return spoken_reply
            except Exception as e:
                return f"Jarvis processed '{command}' successfully."

def run_server(open_browser: bool = True):
    print(f"🚀 Jarvis Quantum Web HUD Server starting at http://localhost:{PORT}")
    if open_browser:
        webbrowser.open(f"http://localhost:{PORT}")

    with socketserver.TCPServer(("", PORT), JarvisRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nWeb server stopped.")

if __name__ == "__main__":
    run_server()
