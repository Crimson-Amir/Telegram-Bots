import sqlite3

with sqlite3.connect('scraping.db') as db:
    cursor = db.cursor()
    cursor.execute(f"UPDATE last_date SET last_time = '2022-01-01 14:20:36+0000' where name = 'eeta'")
    db.commit()