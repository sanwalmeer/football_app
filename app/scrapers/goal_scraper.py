from requests_html import HTMLSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3
import time
import os

# -----------------------------
# CONFIG
# -----------------------------
BASE = "https://www.goal.com"
NEWS_URL = BASE + "/en/news"
TRANSFER_URL = BASE + "/en/category/transfers/1/k94w8e1yy9ch14mllpf4srnks"

db_path = "/home/bitech-office/Sanwal/football_app/football.db"

# -----------------------------
# DB CONNECT
# -----------------------------
if not os.path.exists(db_path):
    print("❌ DB not found")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

session = HTMLSession()

# -----------------------------
# HELPERS
# -----------------------------
def url_exists(url):
    cursor.execute("SELECT 1 FROM news WHERE post_url=?", (url,))
    return cursor.fetchone() is not None


def save_url(url, news_type):
    try:
        cursor.execute(
            "INSERT INTO news (post_url, news_type) VALUES (?, ?)",
            (url, news_type)
        )
        return True
    except sqlite3.IntegrityError:
        return False


def get_latest_url(news_type):
    cursor.execute("""
        SELECT post_url 
        FROM news 
        WHERE news_type = ?
        ORDER BY id DESC 
        LIMIT 1
    """, (news_type,))
    
    row = cursor.fetchone()
    return row[0] if row else None



# -----------------------------
# SCRAPE LISTING
# -----------------------------
def scrape_listing(url, selector, news_type):
    print(f"\n🔎 Scraping listing: {url}")

    latest_db_url = get_latest_url(news_type)
    print(f"🧠 Latest in DB ({news_type}):", latest_db_url)

    response = session.get(url)
    response.html.render(sleep=3, scrolldown=8)

    links = response.html.find(selector)

    results = []

    for l in links:
        link = l.attrs.get("href")
        if not link:
            continue

        full_link = urljoin(BASE, link.strip())

        # ✅ FILTER (only valid articles)
        if not any(x in full_link for x in ["/en/news/", "/en/lists/"]):
            continue

        print("👉 Found:", full_link)

        # 🛑 STOP when reached latest DB record (incremental logic)
        if latest_db_url and full_link == latest_db_url:
            print(f"🛑 Stop reached for {news_type}")
            break

        # ✅ avoid duplicates in memory
        if full_link in results:
            continue

        results.append(full_link)

        # ✅ SAFE INSERT (double safety)
        if not url_exists(full_link):
            is_new = save_url(full_link, news_type)

            if is_new:
                print("🆕 New URL:", full_link)
                scrape_and_update(full_link)
        else:
            print("⏭️ Already exists:", full_link)

    return results
# -----------------------------
# SCRAPE DETAILS
# -----------------------------
def scrape_and_update(url):
    print(f"📰 Scraping article: {url}")

    try:
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        body = soup.find("div", {"data-testid": "article-body"})
        if not body:
            try:
                res.html.render(timeout=20, sleep=2)
                soup = BeautifulSoup(res.html.html, "html.parser")
                body = soup.find("div", {"data-testid": "article-body"})
            except:
                print("⚠️ Render failed")
                return

        title = soup.find("h1")
        title = title.get_text(strip=True) if title else None

        if not body or not title:
            print("⚠️ Skipped (no content/title)")
            return

        date = soup.find("span", {"class": "publish-date_time__CE4oF"})
        date = date.get_text(strip=True) if date else None

        author = soup.find("span", {"data-testid": "author-link"})
        author = author.get_text(strip=True) if author else None

        img = soup.find("img", {"class": "component-image"})
        image = img.get("src") if img else None

        paragraphs = body.find_all("p")
        content = " ".join(p.get_text(strip=True) for p in paragraphs)

        # -----------------------------
        # UPDATE DB
        # -----------------------------
        cursor.execute("""
        UPDATE news
        SET
                       
            title=?,
            author=?,
            published_at=?,
            cover_url=?,
            content_body=?,
            meta_desc=?
        WHERE post_url=?
        """, (
            title,
            author,
            date,
            image,
            content,
            content[:160],
            url
        ))

        # conn.commit()
        print("✅ Updated")

        time.sleep(1)

    except Exception as e:
        print("❌ Error:", e)

cursor.execute("SELECT COUNT(*) FROM news")
before_total = cursor.fetchone()[0]

print("\n==============================")
print("📊 TOTAL NEWS BEFORE RUN:", before_total)
print("==============================\n")
# -----------------------------
# MAIN FLOW
# -----------------------------
def main():
    scrape_listing(TRANSFER_URL, ".content-body > a", "Transfer")
    scrape_listing(NEWS_URL, 'a[data-testid="card-title-url"]', "general")


if __name__ == "__main__":
    main()
    session.close()

    cursor.execute("SELECT COUNT(*) FROM news")
    after_total = cursor.fetchone()[0]

    print("\n==============================")
    print("📊 TOTAL NEWS AFTER RUN:", after_total)
    print("🆕 NEW INSERTED:", after_total - before_total)
    print("==============================\n")
    conn.commit() 
    conn.close()
    print("\n✅ DONE")