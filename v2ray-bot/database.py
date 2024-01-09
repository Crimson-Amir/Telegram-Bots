import sqlite3


def create_database():
    conn = sqlite3.connect('./v2ray.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS User(id integer primary key, name text, user_name text, chat_id integer, '
              'date text, traffic integer, period integer)')

    c.execute('CREATE TABLE IF NOT EXISTS Admin(id integer primary key, name text, user_name text, chat_id text,'
              ' level integer)')

    c.execute('CREATE TABLE IF NOT EXISTS Product(id integer primary key, inbound_id integer, active integer, name text'
              ',country text, period integer, traffic integer, price integer, date text)')

    c.execute('CREATE TABLE IF NOT EXISTS Purchased(id integer primary key, active integer, name text, user_name text,'
              'chat_id integer, factor_id text, product_id integer, inbound_id integer, details text, client_email text,'
              ' client_id text, status integer, date text)')

    conn.commit()
    conn.close()
