from playwright.sync_api import sync_playwright

URL = "https://nhanh.ghn.vn/lastmile/report/backlog-lgt"

def run_report():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--blink-settings=imagesEnabled=false"  # Tắt tải ảnh để tăng tốc
            ]
        )
        context = browser.new_context()
        
        # Chặn tải các tài nguyên nặng như ảnh, CSS, media
        page = context.new_page()
        page.route("**/*.{png,jpg,jpeg,svg,gif,css,woff,woff2}", lambda route: route.abort())

        try:
            # Chờ DOM sẵn sàng thay vì chờ networkidle (tiết kiệm 5-10 giây)
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            print("Đã tải xong trang:", page.title())
        except Exception as e:
            print(f"Lỗi khi cào dữ liệu: {e}")
            
        browser.close()
