import requests
import subprocess
import time
import os
import re
import sys
import sqlite3

# ==============================
# PATH FIX
# ==============================
sys.path.append("/home/bitech-office/Sanwal/football_app")
from app.db.connection import get_db

# ==============================
# CONFIG
# ==============================
VIDEO_DIR = "/home/bitech-office/Sanwal/football_app/downloads"
os.makedirs(VIDEO_DIR, exist_ok=True)

# 🔴 PUT YOUR REAL COOKIES HERE
SESSIONID = "YOUR_SESSION_ID"
CSRF = "YOUR_CSRF_TOKEN"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "X-IG-App-ID": "936619743392459",
    "X-CSRFToken": CSRF,
    "Referer": "https://www.instagram.com/"
}

COOKIES = {
    "sessionid": SESSIONID,
    "csrftoken": CSRF
}

# ==============================
# EXTRACT MEDIA ID FROM REEL
# ==============================
def extract_media_id(shortcode):
    # simple API call to resolve shortcode → media_id
    url = f"https://www.instagram.com/api/v1/oembed/?url=https://www.instagram.com/reel/{shortcode}/"

    res = requests.get(url, headers=HEADERS, cookies=COOKIES)

    if res.status_code != 200:
        print("❌ Failed to resolve media id")
        return None

    data = res.json()
    return data.get("media_id")


# ==============================
# GET VIDEO INFO
# ==============================
def get_video_info(media_id):
    url = f"https://www.instagram.com/api/v1/media/{media_id}/info/?hl=en"

    res = requests.get(url, headers=HEADERS, cookies=COOKIES)

    if res.status_code != 200:
        print("❌ API failed:", res.status_code)
        return None

    return res.json()


# ==============================
# EXTRACT VIDEO URL
# ==============================
def extract_video_url(data):
    try:
        return data["items"][0]["video_versions"][0]["url"]
    except:
        return None


# ==============================
# DOWNLOAD VIA FFMPEG
# ==============================
def download_video(video_url, shortcode):
    output_path = f"{VIDEO_DIR}/{shortcode}.mp4"

    try:
        print(f"⬇️ Downloading {shortcode}")

        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", video_url,
            "-c", "copy",
            output_path
        ], check=True)

        return output_path

    except Exception as e:
        print("❌ ffmpeg failed:", e)
        return None


# ==============================
# MAIN PROCESS
# ==============================
def process_shortcode(shortcode):
    print("\n========================")
    print("📌 Processing:", shortcode)

    conn, cur = get_db()

    cur.execute("SELECT status FROM instagram_reels WHERE shortcode=?", (shortcode,))
    row = cur.fetchone()

    if row and row[0] == "done":
        print("⏭️ Already done")
        return

    # insert/update
    cur.execute("""
        INSERT OR IGNORE INTO instagram_reels (shortcode, status)
        VALUES (?, 'pending')
    """, (shortcode,))
    conn.commit()

    # STEP 1: get media id
    media_id = extract_media_id(shortcode)
    if not media_id:
        print("❌ No media id")
        return

    # STEP 2: get video info
    data = get_video_info(media_id)
    if not data:
        return

    video_url = extract_video_url(data)
    if not video_url:
        print("❌ No video url found")
        return

    # STEP 3: download
    path = download_video(video_url, shortcode)

    # STEP 4: update DB
    if path:
        cur.execute("""
            UPDATE instagram_reels
            SET status='done', video_path=?
            WHERE shortcode=?
        """, (path, shortcode))
        print("✅ DONE:", shortcode)
    else:
        cur.execute("""
            UPDATE instagram_reels
            SET status='failed'
            WHERE shortcode=?
        """, (shortcode,))
        print("❌ FAILED:", shortcode)

    conn.commit()
    conn.close()


# ==============================
# TEST RUN
# ==============================
if __name__ == "__main__":

    test_url = "https://www.instagram.com/espnfc/reels/?hl=en"

    # manually extracted shortcodes (you can automate later)
    test_shortcodes = [
        "CyRNhFbO1KR",
        "DX7LlWpMl16",
        "DX7M9uYDvLY"
    ]

    for sc in test_shortcodes:
        process_shortcode(sc)
        time.sleep(3)