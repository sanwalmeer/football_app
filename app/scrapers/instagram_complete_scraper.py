from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import sqlite3
import os
import subprocess

DB_PATH = "/home/bitech-office/Sanwal/football_app/football.db"
VIDEO_DIR = "/home/bitech-office/Sanwal/football_app/downloads"

RUN_INTERVAL = 600  # 10 min

os.makedirs(VIDEO_DIR, exist_ok=True)


# ==============================
# UTILS
# ==============================

def extract_shortcode(url):
    match = re.search(r"/reel/([^/]+)/", url)
    return match.group(1) if match else None


# ==============================
# DB
# ==============================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn, conn.cursor()


def insert_reel(shortcode, reel_url):
    conn, cur = get_db()

    cur.execute("""
        INSERT OR IGNORE INTO instagram_reels (shortcode, reel_url, status)
        VALUES (?, ?, 'pending')
    """, (shortcode, reel_url))

    conn.commit()
    conn.close()


def update_status(shortcode, status, path=None):
    conn, cur = get_db()

    if path:
        cur.execute("""
            UPDATE instagram_reels
            SET status=?, video_path=?
            WHERE shortcode=?
        """, (status, path, shortcode))
    else:
        cur.execute("""
            UPDATE instagram_reels
            SET status=?
            WHERE shortcode=?
        """, (status, shortcode))

    conn.commit()
    conn.close()


# ==============================
# DRIVER
# ==============================

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


# ==============================
# SCRAPE REELS
# ==============================

def collect_reels(driver, profile_url):
    driver.get(profile_url)
    time.sleep(5)

    reels = []
    seen = set()

    for _ in range(10):
        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")

        for el in elements:
            href = el.get_attribute("href")
            if not href:
                continue

            clean = href.split("?")[0]
            shortcode = extract_shortcode(clean)

            if not shortcode or shortcode in seen:
                continue

            reels.append((clean, shortcode))
            seen.add(shortcode)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    return reels


# ==============================
# DOWNLOAD (yt-dlp preferred)
# ==============================

def download_video(reel_url, shortcode):
    output_path = f"{VIDEO_DIR}/{shortcode}.mp4"

    try:
        print(f"⬇️ Downloading {shortcode}")

        # 🔥 BEST METHOD
        subprocess.run([
            "yt-dlp",
            "-f", "mp4",
            "-o", output_path,
            reel_url
        ], check=True)

        return output_path

    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


# ==============================
# MAIN PIPELINE (ONE BY ONE)
# ==============================

def process_profile(driver, profile_url):
    print(f"\n📌 Scraping: {profile_url}")

    reels = collect_reels(driver, profile_url)

    print(f"🔎 Found {len(reels)} reels")

    for reel_url, shortcode in reels:

        # 1. insert
        insert_reel(shortcode, reel_url)

        # 2. mark downloading
        update_status(shortcode, "downloading")

        # 3. download
        path = download_video(reel_url, shortcode)
        # 4. update DB
        if path:
            update_status(shortcode, "done", path)
            print(f"✅ DONE: {shortcode}")
        else:
            update_status(shortcode, "failed")
            print(f"❌ FAILED: {shortcode}")
        # 🔥 IMPORTANT: one-by-one delay
        time.sleep(2)
# ==============================
# RUN LOOP
# ==============================
if __name__ == "__main__":
    profiles = [
        "https://www.instagram.com/futoreels/",
        "https://www.instagram.com/premierleague/"
    ]
    driver = init_driver()
    try:
        while True:
            print("\n🚀 SCRAPER START\n")

            for profile in profiles:
                process_profile(driver, profile)

            print("\n⏳ Sleeping...\n")
            time.sleep(RUN_INTERVAL)

    except KeyboardInterrupt:
        print("Stopped")

    finally:
        driver.quit()