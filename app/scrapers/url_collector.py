# from app.db.connection import get_db
# import asyncio
# import aiohttp
# from bs4 import BeautifulSoup

# BASE_URL = "https://dasfootball.com/"
# HEADERS = {"User-Agent": "Mozilla/5.0"}


# # -------------------------
# # FETCH
# # -------------------------
# async def fetch(session, url):
#     try:
#         async with session.get(url) as res:
#             if res.status != 200:
#                 return None
#             return await res.text()
#     except:
#         return None


# # -------------------------
# # PARSE LINKS
# # -------------------------
# def parse(html):
#     soup = BeautifulSoup(html, "html.parser")
#     articles = soup.select(".agh-title a")
#     return [a.get("href") for a in articles if a.get("href")]


# # -------------------------
# # SAVE TO DB
# # -------------------------
# def save_urls(urls):
#     conn = get_db()
#     cursor = conn.cursor()

#     for url in urls:
#         try:
#             cursor.execute("""
#             INSERT INTO urls (url, type)
#             VALUES (?, 'video')
#             """, (url,))
#             print("✅ Saved:", url)
#         except:
#             print("⚠️ Exists:", url)

#     conn.commit()
#     conn.close()


# # -------------------------
# # MAIN
# # -------------------------
# async def main():
#     async with aiohttp.ClientSession(headers=HEADERS) as session:
#         tasks = []

#         MAX_PAGES = 10

#         for i in range(1, MAX_PAGES + 1):
#             url = f"{BASE_URL}page/{i}/" if i > 1 else BASE_URL
#             tasks.append(fetch(session, url))

#         pages = await asyncio.gather(*tasks)

#         all_urls = []

#         for html in pages:
#             if not html:
#                 continue
#             links = parse(html)
#             all_urls.extend(links)

#         save_urls(set(all_urls))


# if __name__ == "__main__":
#     asyncio.run(main())


from app.db.connection import get_db
import asyncio
import aiohttp
from bs4 import BeautifulSoup

BASE_URL = "https://dasfootball.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}


# -------------------------
# FETCH
# -------------------------
async def fetch(session, url):
    try:
        async with session.get(url) as res:
            if res.status != 200:
                return None
            return await res.text()
    except:
        return None


# -------------------------
# PARSE LINKS
# -------------------------
def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.select(".agh-title a")
    return [a.get("href") for a in articles if a.get("href")]


# -------------------------
# SAVE TO DB (UPDATED)
# -------------------------
def save_urls(urls):
    conn = get_db()
    cursor = conn.cursor()

    for url in urls:
        try:
            cursor.execute("""
            INSERT INTO match_scrape_queue (url)
            VALUES (?)
            """, (url,))
            print("✅ Saved:", url)

        except:
            # UNIQUE constraint will trigger here
            print("⚠️ Exists:", url)

    conn.commit()
    conn.close()


# -------------------------
# MAIN
# -------------------------
async def main():
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = []

        MAX_PAGES = 10

        for i in range(1, MAX_PAGES + 1):
            url = f"{BASE_URL}page/{i}/" if i > 1 else BASE_URL
            tasks.append(fetch(session, url))

        pages = await asyncio.gather(*tasks)

        all_urls = []

        for html in pages:
            if not html:
                continue
            links = parse(html)
            all_urls.extend(links)

        # remove duplicates before DB insert
        save_urls(set(all_urls))


if __name__ == "__main__":
    asyncio.run(main())