import os
from fastapi import HTTPException
from fastapi.responses import FileResponse

from app.db.connection import get_db



def get_all_instagram_videos():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT shortcode, reel_url, video_path, status
        FROM instagram_reels
        ORDER BY rowid DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_instagram_video(shortcode: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT shortcode, reel_url, video_path, status
        FROM instagram_reels
        WHERE shortcode = ?
    """, (shortcode,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Video not found")
    return dict(row)
def play_instagram_video(shortcode: str):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT video_path
        FROM instagram_reels
        WHERE shortcode = ?
    """, (shortcode,))

    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Video not found")

    file_path = row["video_path"]

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing on disk")

    return FileResponse(file_path, media_type="video/mp4")