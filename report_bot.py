from playwright.sync_api import sync_playwright

URL = "https://nhanh.ghn.vn/lastmile/report/backlog-lgt"

def run_report():
    with sync_playwright() as p:
        # Khởi tạo Chromium headless tương thích hoàn toàn với môi trường Render Linux
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--single-process"
            ]
        )
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto(URL, wait_until="networkidle", timeout=60000)
            print("Da mo:", page.title())
        except Exception as e:
            print(f"Loi khi mo trang: {e}")
            
        browser.close()

if __name__ == "__main__":
    run_report()
