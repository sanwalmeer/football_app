import sqlite3

conn = sqlite3.connect("football.db")
cursor = conn.cursor()

# URLs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    type TEXT,
    category TEXT,
    is_scraped INTEGER DEFAULT 0
)
""")

# Articles table
cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT,
    content TEXT,
    image_url TEXT,
    published_date TEXT,
    category TEXT
)
""")

# Videos table
cursor.execute("""
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_url TEXT UNIQUE,
    title TEXT,
    video_url TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database created!")