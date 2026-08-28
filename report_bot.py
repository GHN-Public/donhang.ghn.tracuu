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
        send_message(chat_id, "❌ Chưa cấu hình GHN_USERNAME hoặc GHN_PASSWORD trên Render Environment!")
        return

    with sync_playwright() as p:
        # Giả lập trình duyệt chuẩn để vượt qua rào cản 403
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # 1. Mở trang đăng nhập SSO GHN
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(2000)

            # 2. Tìm và điền ô tài khoản/mật khẩu
            inputs = page.query_selector_all("input")
            if len(inputs) >= 2:
                inputs[0].fill(GHN_USER)
                inputs[1].fill(GHN_PASS)
            else:
                page.fill("input[type='text'], input[name*='user'], input[placeholder*='Điện thoại']", GHN_USER)
                page.fill("input[type='password'], input[name*='pass']", GHN_PASS)

            # Click Đăng nhập
            page.click("button[type='submit'], button:has-text('Đăng nhập')")
            page.wait_for_timeout(4000)

            # 3. Điều hướng tới trang báo cáo Backlog
            page.goto(REPORT_URL, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(3000)

            title = page.title()
            body_text = page.inner_text("body")
            summary_text = body_text[:800] if body_text else "Không lấy được nội dung."

            send_message(chat_id, f"📊 **BÁO CÁO BACKLOG GHN**\n\n📌 Trang: {title}\n\n📝 Nội dung:\n{summary_text}")

        except Exception as e:
            send_message(chat_id, f"❌ Lỗi xử lý: {e}")
            
        finally:
            browser.close()
