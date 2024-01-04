import sqlite3


def create_database():
    conn = sqlite3.connect('v2ray.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS User(name text, user_name text, id integer,date text)')
    c.execute('CREATE TABLE IF NOT EXISTS Admin(name text, user_name text, id text, level integer)')
    c.execute('CREATE TABLE IF NOT EXISTS Product(active integer, name text, product_id integer,'
              'country text, period integer, traffic real, date text)')
    c.execute('CREATE TABLE IF NOT EXISTS Purchased(active integer, name text, user_name text, id integer,'
              'chat_id integer, factor_id text, product_id integer, date text)')

    conn.commit()
    conn.close()
