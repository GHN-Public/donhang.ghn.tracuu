import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import report_bot

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_telegram_message(chat_id, text):
    if not BOT_TOKEN:
        print("Loi: Chưa cài đặt TELEGRAM_BOT_TOKEN trong Environment Variables!")
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
            text = message.get("text", "").strip()

            if text in ["/start"]:
                reply = "Chào bạn! Bot Tra Cứu GHN đã sẵn sàng. Hãy gõ /menu hoặc gửi mã đơn hàng để tra cứu."
                send_telegram_message(chat_id, reply)

            elif text in ["/report", "/menu", "menu"]:
                send_telegram_message(chat_id, "⏳ Đang kết nối hệ thống GHN để lấy dữ liệu, vui lòng đợi trong giây lát...")
                
                # Gọi hàm cào dữ liệu từ report_bot.py
                report_bot.run_report()
                
                send_telegram_message(chat_id, "✅ Đã tải và cập nhật xong báo cáo Dashboard GHN!")

            else:
                send_telegram_message(chat_id, f"Đã nhận mã/câu lệnh: {text}. Đang xử lý tra cứu...")

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
            # Xử lý tin nhắn trong luồng riêng để phản hồi Webhook ngay lập tức cho Telegram
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
