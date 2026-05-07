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
VIDEO_DIR = "/home/bitech-office/Sanwal/football_app/downloads/tiktok"
RUN_INTERVAL = 600

os.makedirs(VIDEO_DIR, exist_ok=True)


# ==============================
# UTILS
# ==============================
def extract_video_id(url):
    match = re.search(r"/video/(\d+)", url)
    return match.group(1) if match else None


# ==============================
# SCRAPE TIKTOK VIDEOS
# ==============================
def collect_videos(page, profile_url):
    print(f"📌 Opening: {profile_url}")
    page.goto(profile_url, wait_until="networkidle")
    page.wait_for_timeout(5000)

    videos = []
    seen = set()

    for _ in range(8):
        # TikTok video links
        elements = page.query_selector_all("a[href*='/video/']")

        for el in elements:
            href = el.get_attribute("href")
            if not href:
                continue

            full_url = "https://www.tiktok.com" + href.split("?")[0]
            video_id = extract_video_id(full_url)

            if video_id and video_id not in seen:
                videos.append((full_url, video_id))
                seen.add(video_id)

        # scroll
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)

    return videos


# ==============================
# DOWNLOAD VIDEO
# ==============================
def download_video(video_url, video_id):
    output_path = f"{VIDEO_DIR}/{video_id}.mp4"

    try:
        print(f"⬇️ Downloading {video_id}")

        # TikTok works very well with yt-dlp
        subprocess.run([
            "yt-dlp",
            "-f", "mp4",
            "-o", output_path,
            video_url
        ], check=True)

        return output_path

    except Exception as e:
        print(f"❌ Download failed {video_id}: {e}")
        return None


# ==============================
# PROCESS PROFILE
# ==============================
def process_profile(page, profile_url):
    conn = get_db()
    cur = conn.cursor()

    videos = collect_videos(page, profile_url)
    print(f"🔎 Found {len(videos)} videos")

    for video_url, video_id in videos:
        try:
            cur.execute("""
                SELECT status FROM tiktok_videos WHERE video_id=?
            """, (video_id,))
            row = cur.fetchone()

            if row and row[0] == "done":
                print(f"⏭️ Already done: {video_id}")
                continue

            cur.execute("""
                INSERT OR IGNORE INTO tiktok_videos (video_id, video_url, status)
                VALUES (?, ?, 'pending')
            """, (video_id, video_url))
            conn.commit()

            cur.execute("""
                UPDATE tiktok_videos
                SET status='downloading'
                WHERE video_id=?
            """, (video_id,))
            conn.commit()

            path = download_video(video_url, video_id)

            if path:
                cur.execute("""
                    UPDATE tiktok_videos
                    SET status='done', video_path=?
                    WHERE video_id=?
                """, (path, video_id))
                print(f"✅ DONE: {video_id}")
            else:
                cur.execute("""
                    UPDATE tiktok_videos
                    SET status='failed'
                    WHERE video_id=?
                """, (video_id,))
                print(f"❌ FAILED: {video_id}")

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
        "https://www.tiktok.com/@433",
        "https://www.tiktok.com/@brfootball",
        "https://www.tiktok.com/tag/football"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            while True:
                print("\n🚀 TIKTOK SCRAPER START\n")

                start_time = time.time()

                for profile in profiles:
                    process_profile(page, profile)

                end_time = time.time()

                print("\n==============================")
                print(f"⏱️ TIME: {end_time - start_time:.2f}s")
                print("==============================\n")

                print("⏳ Sleeping...\n")
                time.sleep(RUN_INTERVAL)

        except KeyboardInterrupt:
            print(" cccpped manually")

        finally:
            browser.close()


if __name__ == "__main__":
    main()