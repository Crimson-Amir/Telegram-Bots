import sqlite3

def create_database():
    conn = sqlite3.connect('./scraping.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS last_date(id integer primary key, name text, last_time text)')

    conn.commit()
    conn.close()
