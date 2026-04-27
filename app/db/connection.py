import sqlite3

DB_PATH = "/home/bitech-office/Sanwal/football_app/football.db"

def get_db():
    return sqlite3.connect(DB_PATH)