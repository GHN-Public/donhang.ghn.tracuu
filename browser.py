from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = Path("chrome_profile")

URL = "https://nhanh.ghn.vn/lastmile/report/backlog-lgt"

with sync_playwright() as p:

context = p.chromium.launch_persistent_context(
    user_data_dir=str(PROFILE),
    channel="chrome",
    headless=False,
    viewport=None,
    args=[
        "--start-maximized"
    ]
)

    pages = context.pages

    if pages:
        page = pages[0]
    else:
        page = context.new_page()

    if "nhanh.ghn.vn" not in page.url:
        page.goto(URL)

    page.wait_for_load_state("networkidle")

    print("Đã mở Dashboard")

    input("Nhấn Enter để kết thúc...")

    context.close()
