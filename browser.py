import os
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://nhanh.ghn.vn/lastmile/report/backlog-lgt"

def run_browser():
    with sync_playwright() as p:
        # Khởi chạy Chromium headless hoàn toàn phù hợp với môi trường Linux Render
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
            page.goto(URL, timeout=60000)
            page.wait_for_load_state("networkidle")
            print("Da mo Dashboard thanh cong!")
        except Exception as e:
            print(f"Loi truy cap URL: {e}")
            
        browser.close()

if __name__ == "__main__":
    run_browser()
