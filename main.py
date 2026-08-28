import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import report_bot

class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot GHN is running!")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            update = json.loads(post_data.decode('utf-8'))
            # Đưa dữ liệu tin nhắn vào hàm xử lý của report_bot
            threading.Thread(target=report_bot.process_update, args=(update,)).start()
        except Exception as e:
            print(f"Loi xu ly Webhook: {e}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"Server webhook dang chay tai port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
