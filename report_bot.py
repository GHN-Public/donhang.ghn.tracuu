from playwright.sync_api import sync_playwright

URL = "https://nhanh.ghn.vn/lastmile/report/backlog-lgt"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")

    context = browser.contexts[0]

    if context.pages:
        page = context.pages[0]
    else:
        page = context.new_page()

    page.goto(URL, wait_until="networkidle")

    print("Đã mở:", page.title())

    input("Kiểm tra rồi nhấn Enter...")