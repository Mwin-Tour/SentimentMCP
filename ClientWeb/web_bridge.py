"""
web_bridge.py - Pont HTTP + serveur de fichiers
Lance avec: python web_bridge.py
Puis ouvre: http://localhost:8765
"""
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Dossier du script (ClientWeb)
CLIENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Dossier ServerMCP (dossier frère)
BASE_DIR = os.path.join(CLIENT_DIR, "..", "ServerMCP")
BASE_DIR = os.path.normpath(BASE_DIR)

PROMPT_FILE = os.path.join(BASE_DIR, "prompts", "sentiment.txt")
COMMENTS_FILE = os.path.join(BASE_DIR, "ressources", "commentaires_plat.json")

sys.path.insert(0, BASE_DIR)

# === DEBUG au démarrage ===
print(f"📂 CLIENT_DIR  : {CLIENT_DIR}")
print(f"📂 BASE_DIR    : {BASE_DIR}")
print(f"📄 PROMPT_FILE : {PROMPT_FILE} → existe={os.path.exists(PROMPT_FILE)}")
print(f"💬 COMMENTS    : {COMMENTS_FILE} → existe={os.path.exists(COMMENTS_FILE)}")

def analyze(text):
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_rules = f.read()
        from tools.sentiment_tools import analyze_sentiment
        result = analyze_sentiment(text, prompt_rules)
        try:
            start = result.find("{")
            end = result.rfind("}") + 1
            if start != -1 and end > start:
                parsed = json.loads(result[start:end])
                return {"success": True, "data": parsed}
        except:
            pass
        return {"success": True, "data": {"sentiment": "inconnu", "justification": result, "raw": result}}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_comments():
    try:
        print(f"📂 Lecture : {COMMENTS_FILE}")
        print(f"📂 Existe  : {os.path.exists(COMMENTS_FILE)}")
        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ {len(data)} commentaires chargés")
        return data
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return []

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            filepath = os.path.join(CLIENT_DIR, "index.html")
            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_cors()
                self.end_headers()
                self.wfile.write(content)
            except:
                self.send_response(404)
                self.end_headers()

        elif parsed.path == "/comments":
            data = get_comments()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors()
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

        elif parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/analyze":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body)
                text = payload.get("text", "").strip()
                if not text:
                    result = {"success": False, "error": "Texte vide"}
                else:
                    result = analyze(text)
            except Exception as e:
                result = {"success": False, "error": str(e)}
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_cors()
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    port = 8765
    print(f"\n✅ Serveur démarré !")
    print(f"👉 Ouvrez : http://localhost:{port}\n")
    server = HTTPServer(("localhost", port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")