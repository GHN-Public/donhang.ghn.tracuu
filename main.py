import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram_sender import send_message

# 1. Khởi tạo Web Server giả lập để Render nhận diện dịch vụ thành công
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot GHN is running!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# 2. Luồng chạy chính của Bot
if __name__ == "__main__":
    # Chạy Web Server ở luồng phụ (background)
    threading.Thread(target=run_server, daemon=True).start()
    
    print("Bắt đầu chạy main.py")
    
    # Gửi tin nhắn thông báo khởi động thành công
    send_message("Bot GHN Report đã khởi chạy thành công trên Render 24/7!")
    
    # Giữ cho chương trình luôn chạy không bị thoát
    while True:
        time.sleep(3600)
