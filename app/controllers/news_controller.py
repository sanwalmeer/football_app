import sqlite3

DB_PATH = "/home/bitech-office/Sanwal/football_app/football.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_news():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title, author, published_at, cover_url, news_type
    FROM news
    ORDER BY id DESC
    LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_news_by_id(news_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM news
    WHERE id = ?
    """, (news_id,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None




def get_all_videos():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        v.id,
        t1.name AS home_team,
        t2.name AS away_team,
        m.home_score,
        m.away_score,
        v.video_url,
        v.source_page_url
    FROM match_videos v
    JOIN matches m ON v.match_id = m.id
    JOIN teams t1 ON m.home_team_id = t1.id
    JOIN teams t2 ON m.away_team_id = t2.id
    ORDER BY v.id DESC
    LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_video_by_id(video_id: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM match_videos WHERE id = ?
    """, (video_id,))

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def get_all_teams():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM teams ORDER BY name ASC")

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_team_by_id(team_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None

def get_all_matches():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        m.id,
        t1.name AS home_team,
        t2.name AS away_team,
        m.home_score,
        m.away_score
    FROM matches m
    JOIN teams t1 ON m.home_team_id = t1.id
    JOIN teams t2 ON m.away_team_id = t2.id
    ORDER BY m.id DESC
    LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_match_by_id(match_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
    row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None


def get_all_leagues():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leagues")

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_league_by_id(league_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leagues WHERE id = ?", (league_id,))
    row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None

def get_news_count():
    conn=get_db() 
    cursor=conn.cursor()
    cursor.execute("Select count(*) as total from news")
    row=cursor.fetchone()
    conn.close()
    return row["total"]
