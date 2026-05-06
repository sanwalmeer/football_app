from app.db.connection import get_db
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re
import json
import time

BASE_URL = "https://dasfootball.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

session = HTMLSession()


# -------------------------
# FETCH LIST PAGES
# -------------------------
async def fetch(session_http, url):
    try:
        async with session_http.get(url) as res:
            if res.status != 200:
                return None
            return await res.text()
    except:
        return None


# -------------------------
# PARSE LINKS
# -------------------------
def parse_links(html):
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.select(".agh-title a")
    return [a.get("href") for a in articles if a.get("href")]


# -------------------------
# CHECK DUPLICATE (IMPORTANT)
# -------------------------
def url_already_scraped(cursor, url):
    cursor.execute(
        "SELECT 1 FROM match_videos WHERE source_page_url=?",
        (url,)
    )
    return cursor.fetchone() is not None


# -------------------------
# SPLIT SCORE
# -------------------------
def split_score(score):
    try:
        a, b = score.split("-")
        return int(a.strip()), int(b.strip())
    except:
        return None, None


# -------------------------
# VIDEO EXTRACT
# -------------------------
def extract_video(html_obj):
    html = html_obj.html

    # 1. streamable mp4
    match = re.search(r'https?://cdn-[^"\']+\.streamable\.com/video/mp4/[^"\']+\.mp4[^"\']*', html)
    if match:
        return match.group(0)

    # 2. ANY mp4 (fallback)
    match = re.search(r'https?://[^"\']+\.mp4[^"\']*', html)
    if match:
        return match.group(0)

    # 3. flowplayer JSON
    flow = html_obj.find("div.flowplayer", first=True)
    if flow and flow.attrs.get("data-item"):
        try:
            data = json.loads(flow.attrs["data-item"])
            for s in data.get("sources", []):
                if s.get("src"):
                    return s["src"]
        except:
            pass

    # 4. iframe (VERY IMPORTANT)
    iframe = html_obj.find("iframe", first=True)
    if iframe:
        src = iframe.attrs.get("src", "")
        if src:
            return src

    return ""

# -------------------------
# SCRAPE PAGE
# -------------------------
def scrape_page(url):
    try:
        res = session.get(url, headers=HEADERS)
        res.html.render(timeout=20, sleep=2)
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

    video_url = extract_video(res.html)

    return {
        "title": title,
        "team1": team1,
        "team2": team2,
        "team1_logo": team1_logo,
        "team2_logo": team2_logo,
        "score": score,
        "match_date": match_date,
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


def get_or_create_match(cursor, t1, t2, date, score):
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
        home_team_id,
        away_team_id,
        home_score,
        away_score,
        match_datetime
    )
    VALUES (?, ?, ?, ?, ?)
    """, (t1, t2, home_score, away_score, date))

    return cursor.lastrowid


def insert_video(cursor, match_id, title, video_url, page_url):
    cursor.execute("""
    INSERT OR IGNORE INTO match_videos (
        match_id, title, video_url, source_page_url
    )
    VALUES (?, ?, ?, ?)
    """, (match_id, title, video_url, page_url))


# -------------------------
# MAIN
# -------------------------
async def main():
    conn = get_db()
    cursor = conn.cursor()

    async with aiohttp.ClientSession(headers=HEADERS) as session_http:

        tasks = []
        for i in range(1, 6):
            url = f"{BASE_URL}page/{i}/" if i > 1 else BASE_URL
            tasks.append(fetch(session_http, url))

        pages = await asyncio.gather(*tasks)

        all_links = []
        for html in pages:
            if not html:
                continue
            all_links.extend(parse_links(html))

        print(f"Total found: {len(all_links)}")

        for url in set(all_links):

            if url_already_scraped(cursor, url):
                print("⚠️ Already scraped:", url)
                continue

            print("Scraping:", url)

            data = scrape_page(url)
            if not data or not data["video_url"]:
                print("⚠️ No video")
                continue

            t1 = get_or_create_team(cursor, data["team1"], data["team1_logo"])
            t2 = get_or_create_team(cursor, data["team2"], data["team2_logo"])

            match_id = get_or_create_match(
                cursor,
                t1,
                t2,
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

            conn.commit()
            print("✅ Saved")

            time.sleep(1)

    conn.close()
    session.close()
    print("✅ DONE")


if __name__ == "__main__":
    asyncio.run(main())