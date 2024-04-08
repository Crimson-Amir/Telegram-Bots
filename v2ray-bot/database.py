import sqlite3


def create_database():
    conn = sqlite3.connect('./v2ray.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS User(id integer primary key, name text, c '
              'date text, traffic integer, period i1nteger, free_service integer, notification_gb integer,'
              'notification_day integer, wallet integer, notification_wallet INTEGER DEFAULT 5000,'
              'notif_wallet INTEGER DEFAULT 0, notif_low_wallet INTEGER DEFAULT 0, invited_by integer)')


    c.execute('CREATE TABLE IF NOT EXISTS Credit_History(id integer primary key, name text, user_name text, chat_id text,'
              ' operation integer, value integer, value_now integer, date text, active integer)')


    c.execute('CREATE TABLE IF NOT EXISTS Rank(id integer primary key, name text, user_name text, chat_id text,'
              ' level integer, rank_name text)')

    c.execute('CREATE TABLE IF NOT EXISTS Hourly_service(id integer primary key, purchased_id integer, chat_id text, last_traffic_usage integer)')


    c.execute('CREATE TABLE IF NOT EXISTS Partner(id integer primary key, name text, user_name text, chat_id integer,'
              'traffic_price integer, period_price integer)')


    c.execute('CREATE TABLE IF NOT EXISTS Product(id integer primary key, inbound_id integer, active integer, name text'
              ',country text, period integer, traffic integer, price integer, date text, is_personalization text,'
              'domain text, server_domain text, status integer)')


    c.execute('CREATE TABLE IF NOT EXISTS Purchased(id integer primary key, active integer, name text, user_name text,'
              'chat_id integer, factor_id text, product_id integer, inbound_id integer, details text, client_email text,'
              ' client_id text, status integer, date text, notif_day integer, notif_gb integer,'
              ' auto_renewal integer DEFAULT 0)')

    c.execute('CREATE TABLE IF NOT EXISTS Statistics(id integer primary key, traffic_usage text, date text)')

    c.execute('CREATE TABLE IF NOT EXISTS Last_usage(id integer primary key, last_usage text, date text)')

    c.execute('CREATE TABLE IF NOT EXISTS Gift_service(id integer primary key, name text, user_name text,'
              'chat_id integer, traffic integer, date text)')

    # c.execute('ALTER TABLE Purchased ADD COLUMN auto_renewal integer DEFAULT 0')
    # c.execute('CREATE TABLE IF NOT EXISTS Ticket(id integer primary key, answered integer, chat_id text, last_traffic_usage integer)')
    # c.execute('CREATE TABLE IF NOT EXISTS Initialization(id integer primary key, answered integer, chat_id text, last_traffic_usage integer)')

    conn.commit()
    conn.close()
