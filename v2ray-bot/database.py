import sqlite3


def create_database(db_name='test'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS Ticket (id INTEGER PRIMARY KEY, master_ticket_id TEXT, status TEXT, user_id TEXT,'
              'department TEXT, priority INTEGER, title TEXT, body_text INTEGER, image BLOB, date TEXT, update_date TEXT)')

    c.execute('CREATE TABLE IF NOT EXISTS Statistics(id integer primary key, traffic_usage text, date text)')
    c.execute('CREATE TABLE IF NOT EXISTS Last_usage(id integer primary key, last_usage text, date text)')

    conn.commit()
    conn.close()
