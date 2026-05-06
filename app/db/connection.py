import sqlite3

DB_PATH = "/home/bitech-office/Sanwal/football_app/football.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn