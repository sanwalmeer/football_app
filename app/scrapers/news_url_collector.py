# from requests_html import HTMLSession
# from urllib.parse import urljoin
# import sqlite3
# sess = HTMLSession()

# BASE = "https://www.goal.com"

# NEWS_URL = BASE + "/en/news"
# TRANSFER_URL = BASE + "/en/category/transfers/1/k94w8e1yy9ch14mllpf4srnks"
# import os

# # db_path = "/home/bitech-office/Sanwal/PitchScore/backend/football_app/football.db"

# # if not os.path.exists(db_path):
# #     print("❌ Database file not found!")
# #     exit()
# # conn=sqlite3.connect("/home/bitech-office/Sanwal/football_app/football.db", timeout=10)
# # cursor=conn.cursor()

# # cursor.execute("SELECT COUNT(*) FROM news")
# # existing_count = cursor.fetchone()[0]
# import sqlite3
# import os

# db_path = "/home/bitech-office/Sanwal/football_app/football.db"

# if not os.path.exists(db_path):
#     print("❌ Database file not found at:", db_path)
#     exit()

# try:
#     conn = sqlite3.connect(f"file:{db_path}?mode=rw", uri=True, timeout=10)
#     cursor = conn.cursor()
# except sqlite3.OperationalError:
#     print("❌ Unable to open database (wrong path or permissions)")
#     exit()

# cursor.execute("SELECT COUNT(*) FROM news")
# existing_count = cursor.fetchone()[0]

# print("===================================")
# print("Total Existing URLs in DB before Run:", existing_count)
# print("===================================\n")

# inserted_count = 0
# skipped_count = 0

# def save_url(url,news_type):
#     global inserted_count,skipped_count
#     try:
#         cursor.execute("""insert into news (post_url,news_type)
#                        values(?,?)""",(url,news_type))
#         # conn.commit()
#         inserted_count+=1
#         print("New: ",url)
#     except sqlite3.IntegrityError:
#         skipped_count+=1
#         pass

# def scrape_transfers():
#     response = sess.get(TRANSFER_URL)

#     data = []
#     links = response.html.find('.content-body > a')

#     for i in links:
#         link = i.attrs.get('href')

#         if not link:
#             continue

#         link = link.strip().replace(" ", "")
#         full_link = urljoin(BASE, link)

#         if full_link not in data:
#             data.append(full_link)
#             save_url(full_link, "Transfer")
#     return data
  

# def scrape_news_no_skip():
#     response = sess.get(NEWS_URL)
#     response.html.render(sleep=3, scrolldown=10)  # 👈 important

#     data = []
#     links = response.html.find('a')  # 👈 broader selector

#     for i in links:
#         link = i.attrs.get('href')

#         if not link:
#             continue

#         link = link.strip().replace(" ", "")
#         full_link = urljoin(BASE, link)

#         # 👇 filter only valid article URLs
#         if "/en/lists/" not in full_link:
#             continue

#         if full_link not in data:
#             data.append(full_link)
#             save_url(full_link, "general")

#     return data


# transfer_data = scrape_transfers()
# raw_news = scrape_news_no_skip()
# conn.commit()
# # Total
# cursor.execute("SELECT COUNT(*) FROM news")
# final_count = cursor.fetchone()[0]
# # General
# cursor.execute("SELECT COUNT(*) FROM news WHERE news_type='general'")
# general_count = cursor.fetchone()[0]
# # Transfer
# cursor.execute("SELECT COUNT(*) FROM news WHERE news_type='Transfer'")
# transfer_count = cursor.fetchone()[0]

# if inserted_count == 0:
#     print("\nNo new URLs found (already up-to-date) ✅")

# print("\n===== FINAL SUMMARY =====")
# print("Total URLs:", final_count)
# print("General News:", general_count)
# print("Transfer News:", transfer_count)
# print("New Inserted:", inserted_count)
# print("Skipped:", skipped_count)



from requests_html import HTMLSession
from urllib.parse import urljoin
import sqlite3
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

inserted_count = 0
skipped_count = 0
inserted_urls = []

# -----------------------------
# SAVE URL (OPTIMIZED)
# -----------------------------
def save_url(url, news_type):
    global inserted_count, skipped_count, inserted_urls
    try:
        cursor.execute(
            "INSERT INTO news (post_url, news_type) VALUES (?, ?)",
            (url, news_type)
        )
        inserted_count += 1
        inserted_urls.append(url)
        print("🆕 New:", url)
        return True
    except sqlite3.IntegrityError:
        skipped_count += 1
        print("⏭️ Already exists:", url)
        return False


# -----------------------------
# SCRAPE LISTING
# -----------------------------
def scrape_listing(url, selector, news_type):
    print(f"\n🔎 Scraping listing: {url}")

    response = session.get(url)

    # Only render for NEWS page (heavy operation)
    if "news" in url:
        response.html.render(sleep=3, scrolldown=8)

    links = response.html.find(selector)
    results = []

    for l in links:
        link = l.attrs.get("href")
        if not link:
            continue

        full_link = urljoin(BASE, link.strip())

        # Filter valid articles
        if not ("/en/news/" in full_link or "/en/lists/" in full_link):
            continue

        print("👉 VALID:", full_link)

        if full_link in results:
            continue

        results.append(full_link)

        is_new = save_url(full_link, news_type)

        if is_new:
            scrape_and_update(full_link)

    return results


# -----------------------------
# SCRAPE DETAILS
# -----------------------------
def scrape_and_update(url):
    print("📰 Scraping:", url)

    try:
        res = session.get(url)
        soup = res.html

        title = soup.find("h1", first=True)
        title = title.text if title else None

        paragraphs = soup.find("p")
        content = " ".join(p.text for p in paragraphs) if paragraphs else None

        if not title or not content:
            print("⚠️ Skipped (no data)")
            return

        cursor.execute("""
        UPDATE news
        SET title=?, content_body=?
        WHERE post_url=?
        """, (title, content, url))

        print("✅ Updated")

    except Exception as e:
        print("❌ Error:", e)


# -----------------------------
# BEFORE COUNT
# -----------------------------
cursor.execute("SELECT COUNT(*) FROM news")
before = cursor.fetchone()[0]

cursor.execute("SELECT MAX(id) FROM news")
before_max = cursor.fetchone()[0]

print(f"\n📊 BEFORE → Rows: {before} | Max ID: {before_max}")

# -----------------------------
# RUN
# -----------------------------
scrape_listing(TRANSFER_URL, ".content-body > a", "Transfer")
scrape_listing(NEWS_URL, 'a[data-testid="card-title-url"]', "general")

# -----------------------------
# AFTER COUNT
# -----------------------------
conn.commit()  # ✅ single commit

cursor.execute("SELECT COUNT(*) FROM news")
after = cursor.fetchone()[0]

print(f"\n📊 AFTER → Rows: {after}")
print("🆕 INSERTED:", inserted_count)
print("⏭️ SKIPPED:", skipped_count)

# -----------------------------
# PRINT INSERTED URLS
# -----------------------------
if inserted_urls:
    print("\n🆕 Inserted URLs:")
    for u in inserted_urls:
        print("-", u)
else:
    print("\n✅ No new URLs (already up-to-date)")

# -----------------------------
# CLOSE
# -----------------------------
conn.close()
session.close()