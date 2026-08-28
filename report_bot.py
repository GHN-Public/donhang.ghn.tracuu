import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GHN_USER = os.getenv("GHN_USERNAME")
GHN_PASS = os.getenv("GHN_PASSWORD")

LOGIN_API = "https://sso.ghn.vn/api/v1/auth/login"
REPORT_API = "https://nhanh.ghn.vn/api/v1/lastmile/report/backlog-lgt"

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
        send_message(chat_id, "❌ Chưa cấu hình GHN_USERNAME hoặc GHN_PASSWORD trên Render!")
        return

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }

    try:
        # 1. Đăng nhập qua API SSO GHN
        login_payload = {
            "username": GHN_USER,
            "password": GHN_PASS
        }
        login_res = session.post(LOGIN_API, json=login_payload, headers=headers, timeout=15)
        
        if login_res.status_code != 200:
            send_message(chat_id, f"❌ Đăng nhập GHN thất bại! Mã lỗi: {login_res.status_code}\nVui lòng kiểm tra lại tài khoản/mật khẩu.")
            return

        login_data = login_res.json()
        token = login_data.get("data", {}).get("token") or login_data.get("token")

        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 2. Gọi API lấy báo cáo Backlog
        report_res = session.get(REPORT_API, headers=headers, timeout=15)
        
        if report_res.status_code == 200:
            res_data = report_res.json()
            # Trích xuất dữ liệu trả về từ API
            msg = f"📊 **BÁO CÁO BACKLOG GHN**\n\n"
            msg += f"✅ Lấy dữ liệu thành công!\n"
            msg += f"Dữ liệu phản hồi: {str(res_data)[:800]}"
            send_message(chat_id, msg)
        else:
            send_message(chat_id, f"⚠️ Đã đăng nhập nhưng không thể lấy báo cáo Backlog (HTTP {report_res.status_code}).")

    except Exception as e:
        send_message(chat_id, f"❌ Lỗi kết nối hệ thống GHN: {e}")
