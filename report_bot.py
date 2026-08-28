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
        print(f"Lỗi gửi tin nhắn Telegram: {e}")

def run_report(chat_id):
    if not GHN_USER or not GHN_PASS:
        send_message(chat_id, "❌ Lỗi: Chưa cài đặt GHN_USERNAME hoặc GHN_PASSWORD trên Render Environment!")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. Mở trang Đăng nhập GHN SSO
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            # 2. Điền tài khoản & mật khẩu
            page.fill("input[name='username'], input[type='text']", GHN_USER)
            page.fill("input[name='password'], input[type='password']", GHN_PASS)
            
            # Click Đăng nhập và chờ xử lý
            page.click("button[type='submit'], button:has-text('Đăng nhập')")
            page.wait_for_timeout(4000)

            # 3. Chuyển sang trang báo cáo Backlog
            page.goto(REPORT_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            title = page.title()
            body_text = page.inner_text("body")
            
            # Cắt ngắn văn bản thu thập được để gửi lên Telegram
            summary_text = body_text[:1000] if body_text else "Không lấy được nội dung."

            send_message(chat_id, f"📊 **BÁO CÁO BACKLOG GHN**\n\n📌 Trang: {title}\n\n📝 Nội dung:\n{summary_text}")

        except Exception as e:
            send_message(chat_id, f"❌ Lỗi khi đăng nhập hoặc lấy dữ liệu GHN: {e}")
            
        finally:
            browser.close()
