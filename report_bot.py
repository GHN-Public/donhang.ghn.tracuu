import os
import requests
from playwright.sync_api import sync_playwright

LOGIN_URL = "https://sso.ghn.vn/sso/login"
REPORT_URL = "https://nhanh.ghn.vn/lastmile/report/backlog-lgt"

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GHN_USER = os.getenv("GHN_USERNAME")
GHN_PASS = os.getenv("GHN_PASSWORD")

def send_message(chat_id, text):
    if not BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"Lỗi gửi tin nhắn: {e}")

def send_photo(chat_id, photo_path, caption=""):
    if not BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(photo_path, "rb") as photo:
            requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"photo": photo}, timeout=30)
    except Exception as e:
        print(f"Lỗi gửi ảnh Telegram: {e}")

def run_report(chat_id):
    if not GHN_USER or not GHN_PASS:
        send_message(chat_id, "❌ Chưa cấu hình GHN_USERNAME hoặc GHN_PASSWORD trên Render Environment!")
        return

    screenshot_path = "report.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 1. Mở trang đăng nhập
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            # 2. Điền thông tin đăng nhập
            inputs = page.query_selector_all("input")
            if len(inputs) >= 2:
                inputs[0].fill(GHN_USER)
                inputs[1].fill(GHN_PASS)
            else:
                page.fill("input[type='text'], input[placeholder*='Điện thoại']", GHN_USER)
                page.fill("input[type='password']", GHN_PASS)

            # Click Đăng nhập
            page.click("button[type='submit'], button:has-text('Đăng nhập')")
            page.wait_for_timeout(5000)

            # 3. Mở trang Báo cáo
            page.goto(REPORT_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000)

            # Chụp ảnh màn hình báo cáo
            page.screenshot(path=screenshot_path, full_page=True)

            # Gửi ảnh về Telegram
            send_photo(chat_id, screenshot_path, caption="📊 **BÁO CÁO BACKLOG GHN**")

        except Exception as e:
            send_message(chat_id, f"❌ Lỗi lấy báo cáo GHN: {e}")
            
        finally:
            browser.close()
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
