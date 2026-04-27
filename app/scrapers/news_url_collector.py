from app.db.connection import get_db
from requests_html import HTMLSession

session = HTMLSession()

# -----------------------------
# MEMORY DEDUP
# -----------------------------
seen_urls = set()

# -----------------------------
# SAVE FUNCTION (FIXED FOR YOUR DB)
# -----------------------------
def save_url(cursor, conn, url, category):
    cursor.execute("SELECT news_type FROM news WHERE post_url = ?", (url,))
    result = cursor.fetchone()

    if result:
        existing_category = result[0]

        if existing_category == "transfer":
            print("⚠️ Already TRANSFER, skipping:", url)
            return

        if existing_category == "general" and category == "transfer":
            cursor.execute(
                "UPDATE news SET news_type = ? WHERE post_url = ?",
                ("transfer", url)
            )
            conn.commit()
            print("🔄 Updated to TRANSFER:", url)
            return

        print("⚠️ Already exists:", url)
        return

    cursor.execute(
        "INSERT INTO news (post_url, news_type) VALUES (?, ?)",
        (url, category)
    )
    conn.commit()
    print("✅ Saved:", url)


# -----------------------------
# SCRAPER FUNCTION
# -----------------------------
def scrape_first_page(cursor, conn, url, category):
    print(f"\n🔎 Scraping {category.upper()}")

    try:
        res = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
        res.html.render(timeout=20, sleep=2)

        links = res.html.find("a")

        for a in links:
            href = a.attrs.get("href")

            if not href:
                continue

            if not href.startswith("/en") and not href.startswith("http"):
                continue

            if not ("/news/" in href or "/lists/" in href):
                continue

            if href.startswith("http"):
                full_url = href
            else:
                full_url = "https://www.goal.com" + href

            full_url = full_url.split("?")[0]

            if full_url.endswith(("/news", "/lists")):
                continue

            if full_url in seen_urls:
                continue

            seen_urls.add(full_url)

            save_url(cursor, conn, full_url, category)

    except Exception as e:
        print("❌ Error:", e)


# -----------------------------
# MAIN
# -----------------------------
def main():
    conn = get_db()
    cursor = conn.cursor()

    scrape_first_page(
        cursor, conn,
        "https://www.goal.com/en/category/transfers/1/k94w8e1yy9ch14mllpf4srnks",
        "transfer"
    )

    scrape_first_page(
        cursor, conn,
        "https://www.goal.com/en/news",
        "general"
    )

    conn.close()
    session.close()

    print("\n✅ URL scraping complete!")


if __name__ == "__main__":
    main()