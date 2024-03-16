import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import sqlite3


class Scraping():
    def __init__(self, database_name):
        self.database_name = database_name
        self.ensure_last_date_entry()

    def ensure_last_date_entry(self):
        with sqlite3.connect(self.database_name) as db:
            cursor = db.cursor()
            cursor.execute("SELECT id FROM last_date")
            get_last_time = cursor.fetchall()

            if not get_last_time:
                current_utc_time = datetime.now(tz=pytz.utc).strftime('%Y-%m-%d %H:%M:%S%z')
                cursor.execute(f"INSERT INTO last_date (last_time,name) VALUES ('{current_utc_time}','eeta')")
                db.commit()

    def eeta_scraping(self, url):
        try:
            get_data = requests.get(url, timeout=5)
            get_data.raise_for_status()

            soup = BeautifulSoup(get_data.text, 'html.parser')
            get_message = soup.find_all(class_='etme_widget_message_wrap')

            last_message_time = self.get_last_message_time_from_db('eeta')

            list_of_text = []
            for message in get_message:
                get_time = message.time.get('datetime')
                get_datetime = datetime.strptime(get_time, '%Y-%m-%dT%H:%M:%S%z')

                if get_datetime > last_message_time:
                    last_message_time = get_datetime
                    list_of_text.append(message.find(class_='etme_widget_message_text').text)

            self.update_last_message_time_in_db('eeta', last_message_time)

            return list_of_text

        except requests.RequestException as e:
            print(f"Error occurred while fetching data: {e}")

    def get_last_message_time_from_db(self, name):
        with sqlite3.connect(self.database_name) as db:
            cursor = db.cursor()
            cursor.execute(f"SELECT last_time FROM last_date where name = '{name}'")
            get_last_time_from_db = cursor.fetchall()

        return datetime.strptime(get_last_time_from_db[0][0], '%Y-%m-%d %H:%M:%S%z')

    def update_last_message_time_in_db(self, name, last_message_time):
        with sqlite3.connect(self.database_name) as db:
            cursor = db.cursor()
            cursor.execute(f"UPDATE last_date SET last_time = '{last_message_time}' where name = '{name}'")
            db.commit()

