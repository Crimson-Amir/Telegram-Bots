import sqlite3


def create_database(db_name='test'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS User(id integer primary key, name text, chat_id integer'
              'date text, traffic integer, period integer, free_service integer, notification_gb integer,'
              'notification_day integer, wallet integer, notification_wallet INTEGER DEFAULT 5000,'
              'notif_wallet INTEGER DEFAULT 0, notif_low_wallet INTEGER DEFAULT 0, invited_by integer)')


    c.execute('CREATE TABLE IF NOT EXISTS Product(id integer primary key, inbound_id integer, active integer, name text'
              ',country text, period integer, traffic integer, price integer, date text, is_personalization text,'
              'domain text, server_domain text, status integer,inbound_host, inbound_header_type)')


    c.execute('CREATE TABLE IF NOT EXISTS Purchased(id integer primary key, active integer, name text, user_name text,'
              'chat_id integer, factor_id text, product_id integer, inbound_id integer, details text, client_email text,'
              ' client_id text, status integer, date text, notif_day integer, notif_gb integer,'
              ' auto_renewal integer DEFAULT 0)')

    c.execute('CREATE TABLE IF NOT EXISTS Ticket (id INTEGER PRIMARY KEY, master_ticket_id TEXT, status TEXT, user_id TEXT,'
              'department TEXT, priority INTEGER, title TEXT, body_text INTEGER, image BLOB, date TEXT, update_date TEXT)')


    c.execute('CREATE TABLE IF NOT EXISTS Credit_History(id integer primary key, name text, user_name text, chat_id text,'
              ' operation integer, value integer, value_now integer, date text, active integer)')


    c.execute('CREATE TABLE IF NOT EXISTS Rank(id integer primary key, name text, user_name text, chat_id text, '
              'level integer, rank_name text)')

    c.execute('CREATE TABLE IF NOT EXISTS Hourly_service(id integer primary key, purchased_id integer, chat_id text, '
              'last_traffic_usage integer)')


    c.execute('CREATE TABLE IF NOT EXISTS Partner(id integer primary key, name text, user_name text, chat_id integer,'
              'traffic_price integer, period_price integer)')


    c.execute('CREATE TABLE IF NOT EXISTS Statistics(id integer primary key, traffic_usage text, date text)')
    c.execute('CREATE TABLE IF NOT EXISTS Last_usage(id integer primary key, last_usage text, date text)')


    c.execute('CREATE TABLE IF NOT EXISTS Gift_service(id integer primary key, name text, user_name text,'
              'chat_id integer, traffic integer, date text)')

    c.execute("""CREATE TABLE IF NOT EXISTS Cryptomus(id integer primary key, status integer default 0,order_id TEXT NOT NULL,
                 amount VARCHAR(255) NOT NULL, currency VARCHAR(255) NOT NULL, network VARCHAR(255), url_callback VARCHAR(255),
                 is_payment_multiple BOOLEAN DEFAULT TRUE, lifetime INT DEFAULT 3600,
                 to_currency VARCHAR(255), subtract INT DEFAULT 0, accuracy_payment_percent FLOAT DEFAULT 0, additional_data TEXT,
                 currencies TEXT, except_currencies TEXT, course_source VARCHAR(255), from_referral_code VARCHAR(255), discount_percent INT,
                 is_refresh BOOLEAN DEFAULT FALSE, pay_status TEXT, is_final TEXT, chat_id integer,
                 FOREIGN KEY (chat_id) REFERENCES User(chat_id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS iraIranPaymentGeway(id integer primary key, action VARCHAR(100),
                 id_holder integer default null, code integer default 0,
                 authority VARCHAR(255), amount integer NOT NULL, currency VARCHAR(255) NOT NULL, url_callback VARCHAR(255),
                 description TEXT, metadata TEXT, pay_status TEXT, is_final TEXT, chat_id integer, fee_type VARCHAR(15), fee INTEGER,
                 FOREIGN KEY (chat_id) REFERENCES User(chat_id))""")

    # c.execute("drop table Cryptomus")
    # c.execute('ALTER TABLE Cryptomus ADD COLUMN status integer DEFAULT 0')

    # c.execute('CREATE TABLE IF NOT EXISTS Ticket(id integer primary key, answered integer, chat_id text, last_traffic_usage integer)')
    # c.execute('CREATE TABLE IF NOT EXISTS Initialization(id integer primary key, answered integer, chat_id text, last_traffic_usage integer)')

    conn.commit()
    conn.close()
