from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import os
import subprocess
import sys


# ==============================
# PATH FIX (IMPORTANT)
# ==============================
sys.path.append("/home/bitech-office/Sanwal/football_app")
from app.db.connection  import get_db

# ==============================
# CONFIG
# ==============================
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

    for _ in range(8):
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
# DOWNLOAD
# ==============================
def download_video(reel_url, shortcode):
    output_path = f"{VIDEO_DIR}/{shortcode}.mp4"

    try:
        print(f"⬇️ Processing {shortcode}")

        # STEP 1: Get direct video URL using yt-dlp
        result = subprocess.run([
            "yt-dlp",
            "-f", "best",
            "-g",
            reel_url
        ], capture_output=True, text=True, check=True)

        video_url = result.stdout.strip()

        if not video_url:
            print(f"❌ No video URL found for {shortcode}")
            return None

        # STEP 2: Download using FFmpeg
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", video_url,
            "-c:v", "copy",
            "-c:a", "copy",
            output_path
        ], check=True)

        return output_path

    except Exception as e:
        print(f"❌ Failed {shortcode}: {e}")
        return None
    
# ==============================
# PROCESS PROFILE
# ==============================
def process_profile(driver, profile_url):
    print(f"\n📌 Scraping: {profile_url}")

    conn = get_db()
    cur = conn.cursor()

    reels = collect_reels(driver, profile_url)
    print(f"🔎 Found {len(reels)} reels")

    for reel_url, shortcode in reels:
        try:
            # STEP 1: check status
            cur.execute("""
                SELECT status FROM instagram_reels WHERE shortcode=?
            """, (shortcode,))
            row = cur.fetchone()

            if row and row[0] == "done":
                print(f"⏭️ Already done: {shortcode}")
                continue

            # STEP 2: insert if new
            cur.execute("""
                INSERT OR IGNORE INTO instagram_reels (shortcode, reel_url, status)
                VALUES (?, ?, 'pending')
            """, (shortcode, reel_url))
            conn.commit()

            # STEP 3: mark downloading
            cur.execute("""
                UPDATE instagram_reels
                SET status='downloading'
                WHERE shortcode=?
            """, (shortcode,))
            conn.commit()

            # STEP 4: download
            path = download_video(reel_url, shortcode)

            # STEP 5: update result
            if path:
                cur.execute("""
                    UPDATE instagram_reels
                    SET status='done', video_path=?
                    WHERE shortcode=?
                """, (path, shortcode))
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
            print("❌ ERROR:", e)

    conn.close()


# ==============================
# MAIN LOOP
# ==============================
if __name__ == "__main__":
    profiles = [
        "https://www.instagram.com/futoreels/",
        "https://www.instagram.com/premierleague/",
        "https://www.instagram.com/fcbarcelona/reels/"
    ]

    driver = init_driver()

    try:
        while True:
            print("\n🚀 SCRAPER START\n")

            start_time = time.time()   # ⏱️ START TOTAL TIME

            for profile in profiles:
                process_profile(driver, profile)

            end_time = time.time()     # ⏱️ END TOTAL TIME

            print("\n==============================")
            print(f"⏱️ TOTAL EXECUTION TIME: {end_time - start_time:.2f} seconds")
            print("==============================\n")

            print("\n⏳ Sleeping...\n")
            time.sleep(RUN_INTERVAL)

    except KeyboardInterrupt:
        print("🛑 Stopped manually")

    finally:
        driver.quit()