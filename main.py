import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_telegram_message(chat_id, text):
    if not BOT_TOKEN:
        print("Lỗi: Chưa cài đặt TELEGRAM_BOT_TOKEN trong Environment Variables!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Loi gui tin nhan Telegram: {e}")

def handle_update(update):
    try:
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            if text in ["/start", "/menu", "menu"]:
                reply = "Chào bạn! Bot Tra Cứu GHN đã sẵn sàng hoạt động trên Render 24/7."
            else:
                reply = f"Đã nhận câu lệnh: {text}. Đang xử lý dữ liệu..."

            send_telegram_message(chat_id, reply)
    except Exception as e:
        print(f"Loi xu ly update: {e}")

class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot GHN is running!")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            update = json.loads(post_data.decode('utf-8'))
            # Xu ly tin nhắn trong luong rieng de phan hoi Webhook ngay lap tuc cho Telegram
            threading.Thread(target=handle_update, args=(update,)).start()
        except Exception as e:
            print(f"Loi xu ly Webhook: {e}")

        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"Server webhook dang chay tai port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
