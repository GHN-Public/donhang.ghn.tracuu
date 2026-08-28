import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import report_bot

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_telegram_message(chat_id, text):
    if not BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Lỗi gửi tin nhắn: {e}")

def handle_update(update):
    try:
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()

            # Nhận lệnh /start hoặc /help
            if text in ["/start", "/help"]:
                reply = "👋 Chào mừng bạn! Gửi mã đơn hàng GHN hoặc dùng lệnh /report để lấy báo cáo."
                send_telegram_message(chat_id, reply)

            # Nhận lệnh /menu
            elif text in ["/menu", "menu"]:
                reply = "📋 **MENU TRA CỨU GHN**\n\n1. Gõ `/report` để tải báo cáo Backlog.\n2. Gửi mã đơn hàng để tra cứu trực tiếp."
                send_telegram_message(chat_id, reply)

            # Xử lý tất cả các dạng lệnh báo cáo (/report, /report@ghn_kpi_bot, ...)
            elif text.startswith("/report"):
                send_telegram_message(chat_id, "⏳ Đang kết nối GHN để lấy dữ liệu, vui lòng đợi trong giây lát...")
                
                # Chạy Playwright trong Thread riêng để tránh làm nghẽn Telegram
                thread = threading.Thread(target=report_bot.run_report, args=(chat_id,))
                thread.start()

            else:
                send_telegram_message(chat_id, f"🔍 Đã nhận yêu cầu: {text}. Tính năng đang cập nhật.")

    except Exception as e:
        print(f"Lỗi handle_update: {e}")

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
            threading.Thread(target=handle_update, args=(update,)).start()
        except Exception as e:
            print(f"Lỗi parse webhook: {e}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
