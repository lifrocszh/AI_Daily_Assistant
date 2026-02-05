import sqlite3
from datetime import datetime
import shutil
import os

def init_db():
    conn = sqlite3.connect('./data/nutrition.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (user_id INTEGER, date TEXT, food_name TEXT,
                  calories INTEGER, protein INTEGER, carbs INTEGER, fat INTEGER)''')
    conn.commit()
    conn.close()

def log_meal(user_id, data):
    conn = sqlite3.connect('./data/nutrition.db')
    c = conn.cursor()
    # Ensure keys match your dictionary (calories vs estimated_calories)
    c.execute("INSERT INTO logs VALUES (?, ?, ?, ?, ?, ?, ?)",
              (user_id,
               datetime.now().strftime("%Y-%m-%d"),
               data['food_name'],
               data['calories'],
               data['protein'],
               data['carbs'],
               data['fats']))
    conn.commit()
    conn.close()

def get_daily_stats(user_id):
    conn = sqlite3.connect('./data/nutrition.db')
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("""SELECT SUM(calories), SUM(protein), SUM(carbs), SUM(fat)
                 FROM logs WHERE user_id=? AND date=?""", (user_id, today))
    stats = c.fetchone()
    conn.close()
    print(f'stats: {stats}')
    return stats # Returns (total_cal, total_prot, total_carb, total_fat)

DB_PATH = './data/nutrition.db'

def delete_last_sql_entry(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Find the ID/Row of the latest entry for this user
    c.execute("""
        DELETE FROM logs WHERE rowid = (
            SELECT MAX(rowid) FROM logs WHERE user_id = ?
        )
    """, (user_id,))
    conn.commit()
    conn.close()

def reset_sql_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
