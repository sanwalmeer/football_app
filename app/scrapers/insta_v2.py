import os
import re
import sys
import time
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By

# ==============================
# PATH FIX
# ==============================
sys.path.append("/home/bitech-office/Sanwal/football_app")

from app.db.connection import get_db

# ==============================
# CONFIG
# ==============================
BASE_MEDIA_DIR = "/home/bitech-office/Sanwal/football_app/media"

VIDEO_DIR = f"{BASE_MEDIA_DIR}/reels"
THUMB_DIR = f"{BASE_MEDIA_DIR}/thumbnails"

RUN_INTERVAL = 600  # 10 min

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

# ==============================
# UTILS
# ==============================
def extract_shortcode(url):
    match = re.search(r"/reel/([^/]+)/", url)
    return match.group(1) if match else None


# ==============================
# DRIVER
# ==============================
def init_driver():
    options = webdriver.ChromeOptions()

    # ✅ HEADLESS MODE (NOW SAFE)
    options.add_argument("--headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # 🔥 CRITICAL: persistent session (THIS FIXES LOGIN)
    options.add_argument("--user-data-dir=/home/bitech-office/.chrome-instagram")

    # reduce detection
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    return driver


# ==============================
# COLLECT REELS
# ==============================
def collect_reels(driver, profile_url):

    driver.get(profile_url)
    time.sleep(8)

    reels = []
    seen = set()

    for _ in range(6):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    links = driver.find_elements(By.TAG_NAME, "a")

    for a in links:
        try:
            href = a.get_attribute("href")
            if not href or "/reel/" not in href:
                continue

            clean = href.split("?")[0]
            shortcode = extract_shortcode(clean)

            if not shortcode or shortcode in seen:
                continue

            seen.add(shortcode)
            reels.append((clean, shortcode))

        except:
            continue

    return reels


# ==============================
# DOWNLOAD VIDEO + THUMBNAIL
# ==============================
def download_video(reel_url, shortcode):

    video_path = f"{VIDEO_DIR}/{shortcode}.mp4"
    thumb_path = f"{THUMB_DIR}/{shortcode}.jpg"

    try:
        print(f"⬇️ Downloading: {shortcode}")

        # VIDEO DOWNLOAD (stable format)
        subprocess.run([
            "yt-dlp",
            "-f", "mp4/best",
            "-o", video_path,
            reel_url
        ], check=True)

        # THUMBNAIL (safe ffmpeg)
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-ss", "1",
            "-frames:v", "1",
            thumb_path
        ], check=True)

        return video_path, thumb_path

    except Exception as e:
        print(f"❌ DOWNLOAD FAILED {shortcode}: {e}")
        return None, None


# ==============================
# PROCESS PROFILE
# ==============================
def process_profile(driver, profile_url):

    print(f"\n📌 SCRAPING: {profile_url}")

    conn = get_db()
    cur = conn.cursor()

    reels = collect_reels(driver, profile_url)
    print(f"🎥 FOUND {len(reels)} REELS")

    for reel_url, shortcode in reels:

        try:
            cur.execute("""
                SELECT status FROM instagram_reels WHERE shortcode=?
            """, (shortcode,))

            row = cur.fetchone()

            if row and row[0] in ("done", "downloading", "pending"):
                print(f"⏭️ SKIPPED: {shortcode}")
                continue

            cur.execute("""
                INSERT OR IGNORE INTO instagram_reels
                (shortcode, reel_url, status)
                VALUES (?, ?, 'pending')
            """, (shortcode, reel_url))

            conn.commit()

            cur.execute("""
                UPDATE instagram_reels
                SET status='downloading'
                WHERE shortcode=?
            """, (shortcode,))

            conn.commit()

            video_path, thumb_path = download_video(reel_url, shortcode)

            if video_path:

                # ONLY update existing columns (safe with your DB)
                cur.execute("""
                    UPDATE instagram_reels
                    SET status='done',
                        video_path=?
                    WHERE shortcode=?
                """, (video_path, shortcode))

                print(f"✅ DONE: {shortcode}")

            else:

                cur.execute("""
                    UPDATE instagram_reels
                    SET status='failed'
                    WHERE shortcode=?
                """, (shortcode,))

                print(f"❌ FAILED: {shortcode}")

            conn.commit()
            time.sleep(2)

        except Exception as e:
            print(f"❌ ERROR {shortcode}: {e}")

    conn.close()


# ==============================
# MAIN LOOP
# ==============================
if __name__ == "__main__":

    profiles = [
        "https://www.instagram.com/futoreels/",
        "https://www.instagram.com/premierleague/",
        "https://www.instagram.com/fcbarcelona/"
    ]

    driver = init_driver()

    try:
        while True:

            print("\n🚀 SCRAPER STARTED\n")

            start_time = time.time()

            for profile in profiles:
                process_profile(driver, profile)

            end_time = time.time()

            print("\n==============================")
            print(f"⏱️ TOTAL TIME: {end_time - start_time:.2f}s")
            print("==============================\n")

            print("😴 SLEEPING...\n")
            time.sleep(RUN_INTERVAL)

    except KeyboardInterrupt:
        print("🛑 STOPPED MANUALLY")

    finally:
        driver.quit()