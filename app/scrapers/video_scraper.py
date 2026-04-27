# # from app.db.connection import get_db
# # from requests_html import HTMLSession
# # import re
# # import json
# # import time

# # session = HTMLSession()


# # # -------------------------
# # # GET ALL URLS (like read_urls)
# # # -------------------------
# # def get_urls(cursor):
# #     cursor.execute("SELECT url FROM urls WHERE type='video'")
# #     return [row[0] for row in cursor.fetchall()]


# # # -------------------------
# # # GET ALREADY DONE (like read_done_urls)
# # # -------------------------
# # def get_done_urls(cursor):
# #     try:
# #         cursor.execute("SELECT page_url FROM videos")
# #         return {row[0] for row in cursor.fetchall()}
# #     except:
# #         return set()


# # # -------------------------
# # # Extract video URL
# # # -------------------------
# # def extract_video(html_obj):
# #     html = html_obj.html

# #     # ✅ Streamable CDN (MAIN)
# #     match = re.search(
# #         r'https?://cdn-[^"\']+\.streamable\.com/video/mp4/[^"\']+\.mp4\?[^"\']+',
# #         html
# #     )
# #     if match:
# #         return match.group(0)

# #     # ✅ Flowplayer JSON
# #     flow = html_obj.find("div.flowplayer", first=True)
# #     if flow and flow.attrs.get("data-item"):
# #         try:
# #             data = json.loads(flow.attrs["data-item"])
# #             sources = data.get("sources", [])
# #             if sources:
# #                 return sources[0].get("src", "")
# #         except:
# #             pass

# #     # ✅ fallback
# #     match = re.search(r'https?://[^"\']+\.mp4[^"\']*', html)
# #     if match:
# #         return match.group(0)

# #     return ""


# # # -------------------------
# # # Scrape single page
# # # -------------------------
# # def scrape_page(url):
# #     try:
# #         res = session.get(url, headers={"User-Agent": "Mozilla/5.0"})

# #         # ✅ IMPORTANT (JS render)
# #         res.html.render(timeout=30, sleep=2)

# #         # title
# #         title_tag = res.html.find("h1.page-title", first=True)
# #         title = title_tag.text.strip() if title_tag else ""

# #         # video
# #         video_url = extract_video(res.html)

# #         return title, video_url

# #     except Exception as e:
# #         print("❌ Error scraping:", url)
# #         print("   Reason:", e)
# #         return "", ""


# # # -------------------------
# # # MAIN (same as CSV logic)
# # # -------------------------
# # def main():
# #     conn = get_db()
# #     cursor = conn.cursor()

# #     urls = get_urls(cursor)
# #     done_urls = get_done_urls(cursor)

# #     print(f"Total URLs: {len(urls)}")
# #     print(f"Already done: {len(done_urls)}")

# #     for i, url in enumerate(urls):

# #         if url in done_urls:
# #             print(f"[{i+1}] Skipping: {url}")
# #             continue

# #         print(f"[{i+1}/{len(urls)}] Scraping: {url}")

# #         title, video_url = scrape_page(url)

# #         print("   Title:", title)
# #         print("   Video:", video_url)

# #         # ❌ skip empty
# #         if not video_url:
# #             print("⚠️ No video")
# #             continue

# #         try:
# #             cursor.execute("""
# #             INSERT INTO videos (page_url, title, video_url)
# #             VALUES (?, ?, ?)
# #             """, (url, title, video_url))

# #             conn.commit()
# #             print("✅ Saved")

# #         except Exception as e:
# #             print("⚠️ DB Error:", e)

# #         time.sleep(1)

# #     conn.close()
# #     print("✅ DONE")

# # if __name__ == "__main__":
# #     main()
# from app.db.connection import get_db
# from requests_html import HTMLSession
# import re
# import json
# import time

# session = HTMLSession()


# # -------------------------
# # GET ALL URLS
# # -------------------------
# def get_urls(cursor):
#     cursor.execute("SELECT url FROM urls WHERE type='video'")
#     rows = cursor.fetchall()
#     return [row[0] for row in rows] if rows else []


# # -------------------------
# # GET ALREADY SCRAPED URLS
# # -------------------------
# def get_done_urls(cursor):
#     try:
#         cursor.execute("SELECT page_url FROM videos")
#         return {row[0] for row in cursor.fetchall()}
#     except:
#         return set()


# # -------------------------
# # EXTRACT VIDEO URL
# # -------------------------
# def extract_video(html_obj):
#     html = html_obj.html

#     # ✅ Streamable CDN
#     match = re.search(
#         r'https?://cdn-[^"\']+\.streamable\.com/video/mp4/[^"\']+\.mp4\?[^"\']+',
#         html
#     )
#     if match:
#         return match.group(0)

#     # ✅ Flowplayer JSON
#     flow = html_obj.find("div.flowplayer", first=True)
#     if flow and flow.attrs.get("data-item"):
#         try:
#             data = json.loads(flow.attrs["data-item"])
#             sources = data.get("sources", [])
#             if sources:
#                 return sources[0].get("src", "")
#         except:
#             pass

#     # ✅ fallback (any mp4)
#     match = re.search(r'https?://[^"\']+\.mp4[^"\']*', html)
#     if match:
#         return match.group(0)

#     return ""


# # -------------------------
# # SCRAPE SINGLE PAGE
# # -------------------------
# def scrape_page(url):
#     try:
#         res = session.get(url, headers={"User-Agent": "Mozilla/5.0"})

#         # ✅ render JS
#         res.html.render(timeout=30, sleep=2)

#         # title
#         title_tag = res.html.find("h1.page-title", first=True)
#         title = title_tag.text.strip() if title_tag else ""

#         # video
#         video_url = extract_video(res.html)

#         return title, video_url

#     except Exception as e:
#         print("❌ Error scraping:", url)
#         print("   Reason:", e)
#         return "", ""


# # -------------------------
# # MAIN
# # -------------------------
# def main():
#     conn = get_db()
#     cursor = conn.cursor()

#     urls = get_urls(cursor)

#     # ✅ handle empty DB
#     if not urls:
#         print("⚠️ No video URLs found. Run video URL scraper first.")
#         conn.close()
#         return

#     done_urls = get_done_urls(cursor)

#     print(f"Total URLs: {len(urls)}")
#     print(f"Already done: {len(done_urls)}")

#     for i, url in enumerate(urls):

#         if url in done_urls:
#             print(f"[{i+1}] Skipping: {url}")
#             continue

#         print(f"[{i+1}/{len(urls)}] Scraping: {url}")

#         title, video_url = scrape_page(url)

#         print("   Title:", title)
#         print("   Video:", video_url[:100] if video_url else "None")

#         # ❌ skip if no video
#         if not video_url:
#             print("⚠️ No video found")
#             continue

#         try:
#             cursor.execute("""
#             INSERT OR IGNORE INTO videos (page_url, title, video_url)
#             VALUES (?, ?, ?)
#             """, (url, title, video_url))

#             conn.commit()
#             print("✅ Saved")

#         except Exception as e:
#             print("⚠️ DB Error:", e)

#         time.sleep(1)

#     session.close()
#     conn.close()
#     print("✅ DONE")


# # -------------------------
# # RUN
# # -------------------------
# if __name__ == "__main__":
#     main()

 



# from requests_html import HTMLSession
# import re
# import json

# session = HTMLSession()


# # -------------------------
# # EXTRACT VIDEO
# # -------------------------
# def extract_video(html_obj):
#     html = html_obj.html

#     # 1. Streamable CDN
#     match = re.search(
#         r'https?://cdn-[^"\']+\.streamable\.com/video/mp4/[^"\']+\.mp4[^"\']*',
#         html
#     )
#     if match:
#         return match.group(0)

#     # 2. Flowplayer JSON
#     flow = html_obj.find("div.flowplayer", first=True)
#     if flow and flow.attrs.get("data-item"):
#         try:
#             data = json.loads(flow.attrs["data-item"])
#             sources = data.get("sources", [])
#             for src in sources:
#                 if src.get("src"):
#                     return src.get("src")
#         except:
#             pass

#     # 3. iframe
#     iframe = html_obj.find("iframe", first=True)
#     if iframe:
#         src = iframe.attrs.get("src", "")
#         if "streamable" in src:
#             return src

#     # 4. fallback
#     match = re.search(r'https?://[^"\']+\.mp4[^"\']*', html)
#     if match:
#         return match.group(0)

#     return ""


# # -------------------------
# # HELPER (lazy image fix)
# # -------------------------
# def get_img_src(img):
#     return img.attrs.get("src") or img.attrs.get("data-src") or ""


# # -------------------------
# # MAIN EXTRACTOR
# # -------------------------
# def extract_data(url):
#     try:
#         res = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         res.html.render(timeout=60, sleep=5, scrolldown=2)

#         # -------------------------
#         # TITLE
#         # -------------------------
#         title_tag = res.html.find("h1.page-title", first=True)
#         title = title_tag.text.strip() if title_tag else ""

#         # -------------------------
#         # SCORE (REAL SELECTOR)
#         # -------------------------
#         score = ""
#         score_tag = res.html.find("span.kp-score-value", first=True)
#         if score_tag:
#             score = score_tag.text.strip()

#         # -------------------------
#         # TEAMS + LOGOS (REAL DATA)
#         # -------------------------
#         team1 = ""
#         team2 = ""
#         team1_logo = ""
#         team2_logo = ""

#         team_imgs = res.html.find("img.kp-team-logo")

#         if len(team_imgs) >= 2:
#             team1 = team_imgs[0].attrs.get("alt", "").strip()
#             team2 = team_imgs[1].attrs.get("alt", "").strip()

#             team1_logo = get_img_src(team_imgs[0])
#             team2_logo = get_img_src(team_imgs[1])

#         # -------------------------
#         # DATE (from URL)
#         # -------------------------
#         date_match = re.search(r'\d{4}-\d{2}-\d{2}', url)
#         match_date = date_match.group(0) if date_match else ""

#         # -------------------------
#         # LEAGUE (basic detection)
#         # -------------------------
#         league = ""
#         if any(x in title for x in ["Real Madrid", "Barcelona", "Atletico"]):
#             league = "La Liga"
#         elif any(x in title for x in ["Chelsea", "Arsenal", "Liverpool", "Man"]):
#             league = "Premier League"
#         elif any(x in title for x in ["Juventus", "Inter", "Milan"]):
#             league = "Serie A"

#         # -------------------------
#         # VIDEO
#         # -------------------------
#         video_url = extract_video(res.html)

#         return {
#             "url": url,
#             "title": title,
#             "team1": team1,
#             "team2": team2,
#             "team1_logo": team1_logo,
#             "team2_logo": team2_logo,
#             "score": score,
#             "match_date": match_date,
#             "league": league,
#             "video_url": video_url
#         }

#     except Exception as e:
#         print("❌ Error:", url)
#         print("   Reason:", e)
#         return None


# # -------------------------
# # TEST RUN
# # -------------------------
# if __name__ == "__main__":
#     test_url = "https://dasfootball.com/real-madrid-vs-alaves-match-highlights-2026-04-21/"

#     data = extract_data(test_url)

#     if data:
#         print("\n✅ EXTRACTED DATA:\n")
#         for key, value in data.items():
#             print(f"{key}: {value}")\
\



# from app.db.connection import get_db
# from requests_html import HTMLSession
# import re
# import json
# import time

# session = HTMLSession()

# # -------------------------
# # GET URLS FROM DB
# # -------------------------
# def get_pending_urls(cursor):
#     cursor.execute("""
#     SELECT url FROM match_scrape_queue
#     WHERE is_scraped = 0
#     """)
#     return [row[0] for row in cursor.fetchall()]


# # -------------------------
# # VIDEO EXTRACT
# # -------------------------
# def extract_video(html_obj):
#     html = html_obj.html

#     match = re.search(
#         r'https?://cdn-[^"\']+\.streamable\.com/video/mp4/[^"\']+\.mp4[^"\']*',
#         html
#     )
#     if match:
#         return match.group(0)

#     flow = html_obj.find("div.flowplayer", first=True)
#     if flow and flow.attrs.get("data-item"):
#         try:
#             data = json.loads(flow.attrs["data-item"])
#             for s in data.get("sources", []):
#                 if s.get("src"):
#                     return s["src"]
#         except:
#             pass

#     iframe = html_obj.find("iframe", first=True)
#     if iframe:
#         return iframe.attrs.get("src", "")

#     return ""


# # -------------------------
# # SCRAPE PAGE
# # -------------------------
# def scrape_page(url):
#     res = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
#     res.html.render(timeout=30, sleep=2)

#     title_tag = res.html.find("h1.page-title", first=True)
#     title = title_tag.text.strip() if title_tag else ""

#     # teams
#     team1, team2 = "", ""
#     if " vs " in title:
#         parts = title.split(" vs ")
#         team1 = parts[0].strip()
#         team2 = parts[1].split(" Highlights")[0].strip()

#     # score
#     score_tag = res.html.find("span.kp-score-value", first=True)
#     score = score_tag.text.strip() if score_tag else ""

#     # logos
#     logos = res.html.find("img.kp-team-logo")
#     team1_logo = logos[0].attrs.get("src", "") if len(logos) > 0 else ""
#     team2_logo = logos[1].attrs.get("src", "") if len(logos) > 1 else ""

#     # date
#     date_match = re.search(r'\d{4}-\d{2}-\d{2}', url)
#     match_date = date_match.group(0) if date_match else ""

#     # league (basic)
#     league = "Unknown"
#     if "Madrid" in title or "Barcelona" in title:
#         league = "La Liga"
#     elif "Chelsea" in title or "Liverpool" in title:
#         league = "Premier League"
#     elif "Juventus" in title or "Inter" in title:
#         league = "Serie A"

#     video_url = extract_video(res.html)

#     return {
#         "title": title,
#         "team1": team1,
#         "team2": team2,
#         "team1_logo": team1_logo,
#         "team2_logo": team2_logo,
#         "score": score,
#         "match_date": match_date,
#         "league": league,
#         "video_url": video_url
#     }


# # -------------------------
# # DB HELPERS
# # -------------------------
# def get_or_create_team(cursor, name, logo):
#     cursor.execute("SELECT id FROM teams WHERE name=?", (name,))
#     row = cursor.fetchone()

#     if row:
#         return row[0]

#     cursor.execute(
#         "INSERT INTO teams (name, logo_url) VALUES (?, ?)",
#         (name, logo)
#     )
#     return cursor.lastrowid


# def get_or_create_league(cursor, name):
#     cursor.execute("SELECT id FROM leagues WHERE name=?", (name,))
#     row = cursor.fetchone()

#     if row:
#         return row[0]

#     cursor.execute(
#         "INSERT INTO leagues (name) VALUES (?)",
#         (name,)
#     )
#     return cursor.lastrowid


# def insert_match(cursor, t1, t2, league_id, date, score):
#     cursor.execute("""
#     INSERT INTO matches (team1_id, team2_id, league_id, match_date, score)
#     VALUES (?, ?, ?, ?, ?)
#     """, (t1, t2, league_id, date, score))

#     return cursor.lastrowid


# def insert_video(cursor, match_id, title, video_url, page_url):
#     cursor.execute("""
#     INSERT INTO match_videos (match_id, title, video_url, source_page_url)
#     VALUES (?, ?, ?, ?)
#     """, (match_id, title, video_url, page_url))


# # -------------------------
# # MAIN
# # -------------------------
# def main():
#     conn = get_db()
#     cursor = conn.cursor()

#     urls = get_pending_urls(cursor)

#     print(f"Pending URLs: {len(urls)}")

#     for url in urls:
#         print("Scraping:", url)

#         data = scrape_page(url)

#         if not data["video_url"]:
#             print("⚠️ No video found")
#             continue

#         # DB FLOW
#         team1_id = get_or_create_team(cursor, data["team1"], data["team1_logo"])
#         team2_id = get_or_create_team(cursor, data["team2"], data["team2_logo"])
#         league_id = get_or_create_league(cursor, data["league"])

#         match_id = insert_match(
#             cursor,
#             team1_id,
#             team2_id,
#             league_id,
#             data["match_date"],
#             data["score"]
#         )

#         insert_video(
#             cursor,
#             match_id,
#             data["title"],
#             data["video_url"],
#             url
#         )

#         # mark done
#         cursor.execute("""
#         UPDATE match_scrape_queue
#         SET is_scraped = 1
#         WHERE url = ?
#         """, (url,))

#         conn.commit()
#         print("✅ Saved everything")

#         time.sleep(1)

#     conn.close()
#     session.close()
#     print("✅ DONE")


# if __name__ == "__main__":
#     main()

from app.db.connection import get_db
from requests_html import HTMLSession
import re
import json
import time

session = HTMLSession()

# -------------------------
# GET URLS FROM DB
# -------------------------
def get_pending_urls(cursor):
    cursor.execute("""
    SELECT url FROM match_scrape_queue
    WHERE is_scraped = 0
    """)
    return [row[0] for row in cursor.fetchall()]


# -------------------------
# SPLIT SCORE
# -------------------------
def split_score(score):
    try:
        parts = score.split("-")
        return int(parts[0].strip()), int(parts[1].strip())
    except:
        return None, None


# -------------------------
# VIDEO EXTRACT
# -------------------------
def extract_video(html_obj):
    html = html_obj.html

    match = re.search(
        r'https?://cdn-[^"\']+\.streamable\.com/video/mp4/[^"\']+\.mp4[^"\']*',
        html
    )
    if match:
        return match.group(0)

    flow = html_obj.find("div.flowplayer", first=True)
    if flow and flow.attrs.get("data-item"):
        try:
            data = json.loads(flow.attrs["data-item"])
            for s in data.get("sources", []):
                if s.get("src"):
                    return s["src"]
        except:
            pass

    iframe = html_obj.find("iframe", first=True)
    if iframe:
        return iframe.attrs.get("src", "")

    return ""


# -------------------------
# SCRAPE PAGE
# -------------------------
def scrape_page(url):
    try:
        res = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
        res.html.render(timeout=30, sleep=2)
    except Exception as e:
        print("❌ Render failed:", e)
        return None

    title_tag = res.html.find("h1.page-title", first=True)
    title = title_tag.text.strip() if title_tag else ""

    team1, team2 = "", ""
    if " vs " in title:
        parts = title.split(" vs ")
        team1 = parts[0].strip()
        team2 = parts[1].split(" Highlights")[0].strip()

    score_tag = res.html.find("span.kp-score-value", first=True)
    score = score_tag.text.strip() if score_tag else ""

    logos = res.html.find("img.kp-team-logo")
    team1_logo = logos[0].attrs.get("src", "") if len(logos) > 0 else ""
    team2_logo = logos[1].attrs.get("src", "") if len(logos) > 1 else ""

    date_match = re.search(r'\d{4}-\d{2}-\d{2}', url)
    match_date = date_match.group(0) if date_match else ""

    league = "Unknown"
    if any(x in title for x in ["Madrid", "Barcelona", "Atletico"]):
        league = "La Liga"
    elif any(x in title for x in ["Chelsea", "Arsenal", "Liverpool", "Man"]):
        league = "Premier League"
    elif any(x in title for x in ["Juventus", "Inter", "Milan"]):
        league = "Serie A"

    video_url = extract_video(res.html)

    return {
        "title": title,
        "team1": team1,
        "team2": team2,
        "team1_logo": team1_logo,
        "team2_logo": team2_logo,
        "score": score,
        "match_date": match_date,
        "league": league,
        "video_url": video_url
    }


# -------------------------
# DB HELPERS
# -------------------------
def get_or_create_team(cursor, name, logo):
    cursor.execute("SELECT id FROM teams WHERE name=?", (name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO teams (name, icon_url) VALUES (?, ?)",
        (name, logo)
    )
    return cursor.lastrowid


def get_or_create_league(cursor, name):
    cursor.execute("SELECT id FROM leagues WHERE name=?", (name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO leagues (name) VALUES (?)",
        (name,)
    )
    return cursor.lastrowid


# ✅ FIX: prevent duplicate matches
def get_or_create_match(cursor, t1, t2, league_id, date, score):
    cursor.execute("""
    SELECT id FROM matches
    WHERE home_team_id=? AND away_team_id=? AND match_datetime=?
    """, (t1, t2, date))

    row = cursor.fetchone()
    if row:
        return row[0]

    home_score, away_score = split_score(score)

    cursor.execute("""
    INSERT INTO matches (
        league_id,
        home_team_id,
        away_team_id,
        home_score,
        away_score,
        match_datetime
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        league_id,
        t1,
        t2,
        home_score,
        away_score,
        date
    ))

    return cursor.lastrowid


# ✅ FIX: avoid UNIQUE crash
def insert_video(cursor, match_id, title, video_url, page_url):
    cursor.execute("""
    INSERT OR IGNORE INTO match_videos (
        match_id, title, video_url, source_page_url
    )
    VALUES (?, ?, ?, ?)
    """, (match_id, title, video_url, page_url))

    if cursor.rowcount == 0:
        print("⚠️ Duplicate video skipped:", page_url)


# -------------------------
# MAIN
# -------------------------
def main():
    conn = get_db()
    cursor = conn.cursor()

    urls = get_pending_urls(cursor)

    print(f"Pending URLs: {len(urls)}")

    for url in urls:
        print("Scraping:", url)

        data = scrape_page(url)
        if not data:
            continue

        if not data["video_url"]:
            print("⚠️ No video found")
            continue

        team1_id = get_or_create_team(cursor, data["team1"], data["team1_logo"])
        team2_id = get_or_create_team(cursor, data["team2"], data["team2_logo"])
        league_id = get_or_create_league(cursor, data["league"])

        match_id = get_or_create_match(
            cursor,
            team1_id,
            team2_id,
            league_id,
            data["match_date"],
            data["score"]
        )

        insert_video(
            cursor,
            match_id,
            data["title"],
            data["video_url"],
            url
        )

        cursor.execute("""
        UPDATE match_scrape_queue
        SET is_scraped = 1
        WHERE url = ?
        """, (url,))

        conn.commit()
        print("✅ Saved everything")

        time.sleep(1)

    conn.close()
    session.close()
    print("✅ DONE")


if __name__ == "__main__":
    main()