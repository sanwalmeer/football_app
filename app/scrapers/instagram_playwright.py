import re
import time
import os
import subprocess
import sys
from playwright.sync_api import sync_playwright

# ==============================
# PATH FIX
# ==============================
sys.path.append("/home/bitech-office/Sanwal/football_app")
from app.db.connection import get_db

# ==============================
# CONFIG
# ==============================
VIDEO_DIR = "/home/bitech-office/Sanwal/football_app/downloads"
RUN_INTERVAL = 600

os.makedirs(VIDEO_DIR, exist_ok=True)


# ==============================
# UTILS
# ==============================
def extract_shortcode(url):
    match = re.search(r"/reel/([^/]+)/", url)
    return match.group(1) if match else None


# ==============================
# SCRAPE REELS (PLAYWRIGHT)
# ==============================
def collect_reels(page, profile_url):
    page.goto(profile_url, wait_until="networkidle")
    page.wait_for_timeout(4000)

    reels = []
    seen = set()

    for _ in range(8):
        elements = page.query_selector_all("a[href*='/reel/']")

        for el in elements:
            href = el.get_attribute("href")
            if not href:
                continue

            clean = href.split("?")[0]
            shortcode = extract_shortcode(clean)

            if shortcode and shortcode not in seen:
                reels.append((clean, shortcode))
                seen.add(shortcode)

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

    return reels


# ==============================
# DOWNLOAD
# ==============================
def download_video(reel_url, shortcode):
    output_path = f"{VIDEO_DIR}/{shortcode}.mp4"

    try:
        print(f"⬇️ Downloading {shortcode}")

        subprocess.run([
            "yt-dlp",
            "-f", "best",
            "-o", output_path,
            reel_url
        ], check=True)

        return output_path

    except Exception as e:
        print(f"❌ Download failed {shortcode}: {e}")
        return None


# ==============================
# PROCESS PROFILE
# ==============================
def process_profile(page, profile_url):
    print(f"\n📌 Scraping: {profile_url}")

    conn = get_db()
    cur = conn.cursor()

    reels = collect_reels(page, profile_url)
    print(f"🔎 Found {len(reels)} reels")

    for reel_url, shortcode in reels:
        try:
            cur.execute("""
                SELECT status FROM instagram_reels WHERE shortcode=?
            """, (shortcode,))
            row = cur.fetchone()

            if row and row[0] == "done":
                print(f"⏭️ Already done: {shortcode}")
                continue

            cur.execute("""
                INSERT OR IGNORE INTO instagram_reels (shortcode, reel_url, status)
                VALUES (?, ?, 'pending')
            """, (shortcode, reel_url))
            conn.commit()

            cur.execute("""
                UPDATE instagram_reels
                SET status='downloading'
                WHERE shortcode=?
            """, (shortcode,))
            conn.commit()

            path = download_video(reel_url, shortcode)

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
def main():
    profiles = [
        "https://www.instagram.com/futoreels/",
        "https://www.instagram.com/premierleague/",
        "https://www.instagram.com/fcbarcelona/reels/"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            while True:
                print("\n🚀 PLAYWRIGHT SCRAPER START\n")

                start_time = time.time()

                for profile in profiles:
                    process_profile(page, profile)

                end_time = time.time()

                print("\n==============================")
                print(f"⏱️ TOTAL EXECUTION TIME: {end_time - start_time:.2f} seconds")
                print("==============================\n")

                print("\n⏳ Sleeping...\n")
                time.sleep(RUN_INTERVAL)

        except KeyboardInterrupt:
            print("🛑 Stopped manually")

        finally:
            browser.close()


if __name__ == "__main__":
    main()