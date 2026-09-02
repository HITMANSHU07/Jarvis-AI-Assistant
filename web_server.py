import http.server
import socketserver
import webbrowser
import os

PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(__file__), "web")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run_server():
    print(f"🚀 Jarvis Web Assistant Server starting at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
