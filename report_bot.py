import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://nhanh.ghn.vn/lastmile/report/backlog-lgt"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_message(chat_id, text):
    if not BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def run_report(chat_id):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            title = page.title()
            
            # Gửi tin nhắn kết quả thực tế thu thập được về Telegram
            send_message(chat_id, f"✅ Đã truy cập trang thành công!\nTiêu đề trang: {title}")
            
        except Exception as e:
            send_message(chat_id, f"❌ Không thể lấy dữ liệu (Lỗi: {e})")
            
        browser.close()
