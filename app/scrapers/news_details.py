# from requests_html import HTMLSession
# from bs4 import BeautifulSoup
# import sqlite3
# import time

# # -----------------------------
# # DB CONNECT
# # -----------------------------
# conn = sqlite3.connect("/home/bitech-office/Sanwal/football_app/football.db")
# cursor = conn.cursor()

# session = HTMLSession()

# # -----------------------------
# # FETCH ONLY VALID ARTICLES
# # -----------------------------
# cursor.execute("""
# SELECT post_url, news_type FROM news
# WHERE (content_body IS NULL OR content_body = '')
# AND post_url NOT LIKE '%/news/%'
# """)

# urls = cursor.fetchall()

# print(f"🔎 Found {len(urls)} URLs")


# # -----------------------------
# # SCRAPER FUNCTION
# # -----------------------------
# # def scrape_article(url):
# #     headers = {"User-Agent": "Mozilla/5.0"}

# #     try:
# #         res = session.get(url, headers=headers)

# #         soup = BeautifulSoup(res.text, "html.parser")

# #         body = soup.find("div", {"data-testid": "article-body"})

# #         # render only if needed
# #         if not body:
# #             print("⚠️ No content, trying render...")
# #             try:
# #                 res.html.render(timeout=20, sleep=2)
# #                 soup = BeautifulSoup(res.html.html, "html.parser")
# #                 body = soup.find("div", {"data-testid": "article-body"})
# #             except:
# #                 print("⚠️ Render failed")

# #         # -------------------------
# #         # EXTRACT
# #         # -------------------------
# #         title_tag = soup.find("h1", {"data-testid": "article-title"})
# #         title = title_tag.get_text(strip=True) if title_tag else None

# #         if not content:
# #             print("⚠️ Skipped (no content)")
# #             continue

# #         date_tag = soup.find("span", {"class": "publish-date_time__CE4oF"})
# #         published_date = date_tag.get_text(strip=True) if date_tag else None

# #         author_tag = soup.find("span", {"data-testid": "author-link"})
# #         author = author_tag.get_text(strip=True) if author_tag else None

# #         img_tag = soup.find("img", {"class": "component-image"})
# #         image_url = img_tag.get("src") if img_tag else None

# #         content = ""
# #         if body:
# #             paragraphs = body.find_all("p")
# #             content = " ".join(p.get_text(strip=True) for p in paragraphs)

# #         return title, published_date, author, image_url, content

# #     except Exception as e:
# #         print("❌ Error:", url, e)
# #         return None, None, None, None, None


# # # -----------------------------
# # # LOOP
# # # -----------------------------
# # for (url, category) in urls:
# #     print(f"\n📰 Scraping: {url}")

# #     title, date, author, image, content = scrape_article(url)

# #     if not title:
# #         print("⚠️ Skipped (invalid article)")
# #         continue

# #     try:
# #         cursor.execute("""
# #         UPDATE news
# #         SET
# #             title = COALESCE(title, ?),
# #             author = COALESCE(author, ?),
# #             published_at = COALESCE(published_at, ?),
# #             cover_url = COALESCE(cover_url, ?),
# #             content_body = ?,
# #             meta_desc = ?
# #         WHERE post_url = ?
# #         """, (
# #             title,
# #             author,
# #             date,
# #             image,
# #             content,
# #             content[:160] if content else None,
# #             url
# #         ))

# #         conn.commit()
# #         print("✅ Updated")

# #     except Exception as e:
# #         print("⚠️ DB Error:", e)

# #     time.sleep(1)


# # # -----------------------------
# # # CLOSE
# # # -----------------------------
# # session.close()
# # conn.close()

# # print("\n✅ DONE")
# def scrape_article(url):
#     headers = {"User-Agent": "Mozilla/5.0"}

#     try:
#         res = session.get(url, headers=headers)
#         soup = BeautifulSoup(res.text, "html.parser")

#         body = soup.find("div", {"data-testid": "article-body"})

#         # render if needed
#         if not body:
#             print("⚠️ No content, trying render...")
#             try:
#                 res.html.render(timeout=20, sleep=2)
#                 soup = BeautifulSoup(res.html.html, "html.parser")
#                 body = soup.find("div", {"data-testid": "article-body"})
#             except:
#                 print("⚠️ Render failed")

#         # EXTRACT
#         title_tag = soup.find("h1")
#         title = title_tag.get_text(strip=True) if title_tag else None

#         date_tag = soup.find("span", {"class": "publish-date_time__CE4oF"})
#         published_date = date_tag.get_text(strip=True) if date_tag else None

#         author_tag = soup.find("span", {"data-testid": "author-link"})
#         author = author_tag.get_text(strip=True) if author_tag else None

#         img_tag = soup.find("img", {"class": "component-image"})
#         image_url = img_tag.get("src") if img_tag else None

#         content = ""
#         if body:
#             paragraphs = body.find_all("p")
#             content = " ".join(p.get_text(strip=True) for p in paragraphs)

#         return title, published_date, author, image_url, content

#     except Exception as e:
#         print("❌ Error:", url, e)
#         return None, None, None, None, None




from requests_html import HTMLSession
from bs4 import BeautifulSoup
import sqlite3
import time

# -----------------------------
# DB CONNECT
# -----------------------------
conn = sqlite3.connect("/home/bitech-office/Sanwal/football_app/football.db")
cursor = conn.cursor()

session = HTMLSession()

# -----------------------------
# FETCH ONLY VALID ARTICLES
# -----------------------------
cursor.execute("""
SELECT post_url, news_type FROM news
WHERE (content_body IS NULL OR content_body = '')
AND post_url NOT LIKE '%/news/%'
AND post_url NOT LIKE '%/lists/%'
""")

urls = cursor.fetchall()

print(f"🔎 Found {len(urls)} URLs")


# -----------------------------
# SCRAPER FUNCTION (FIXED)
# -----------------------------
def scrape_article(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = session.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        body = soup.find("div", {"data-testid": "article-body"})

        # render if needed
        if not body:
            print("⚠️ No content, trying render...")
            try:
                res.html.render(timeout=20, sleep=2)
                soup = BeautifulSoup(res.html.html, "html.parser")
                body = soup.find("div", {"data-testid": "article-body"})
            except:
                print("⚠️ Render failed")

        # -------------------------
        # EXTRACT
        # -------------------------
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        date_tag = soup.find("span", {"class": "publish-date_time__CE4oF"})
        published_date = date_tag.get_text(strip=True) if date_tag else None

        author_tag = soup.find("span", {"data-testid": "author-link"})
        author = author_tag.get_text(strip=True) if author_tag else None

        img_tag = soup.find("img", {"class": "component-image"})
        image_url = img_tag.get("src") if img_tag else None

        content = ""
        if body:
            paragraphs = body.find_all("p")
            content = " ".join(p.get_text(strip=True) for p in paragraphs)

        return title, published_date, author, image_url, content

    except Exception as e:
        print("❌ Error:", url, e)
        return None, None, None, None, None


# -----------------------------
# LOOP (FIXED LOGIC HERE)
# -----------------------------
for (url, category) in urls:
    print(f"\n📰 Scraping: {url}")

    title, date, author, image, content = scrape_article(url)

    # ✅ Proper skip logic here
    if not title or not content:
        print("⚠️ Skipped (no title/content)")
        continue

    try:
        cursor.execute("""
        UPDATE news
        SET
            title = COALESCE(title, ?),
            author = COALESCE(author, ?),
            published_at = COALESCE(published_at, ?),
            cover_url = COALESCE(cover_url, ?),
            content_body = ?,
            meta_desc = ?
        WHERE post_url = ?
        """, (
            title,
            author,
            date,
            image,
            content,
            content[:160] if content else None,
            url
        ))

        conn.commit()
        print("✅ Updated")

    except Exception as e:
        print("⚠️ DB Error:", e)

    time.sleep(1)


# -----------------------------
# CLOSE
# -----------------------------
session.close()
conn.close()

print("\n✅ DONE")