from abc import ABC, abstractmethod
from sqlite_manager import ManageDb
from datetime import datetime
import pytz


class Singleton(type):
    _isinstance = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._isinstance:
            cls._isinstance[cls] = super().__call__(*args, **kwargs)
        return cls._isinstance[cls]


class InstanceIsNotAllowed(ABC, type):
    def __call__(cls, *args, **kwargs):
        class_name = cls.__name__
        if class_name == 'TicketKernel':
            error_msg = f"Instances of '{class_name}' are not allowed. Use 'TicketManager' class instead."
            raise TypeError(error_msg)
        return super().__call__(*args, **kwargs)


class TicketClosedError(Exception):
    def __init__(self, message="The ticket is closed"):
        self.message = message
        super().__init__(self.message)

class PreparationAdapter:
    list_of_character = ['"', "'", "/", ";", "%"]
    departments = ['technical', 'sales', 'communications']
    priority = {1: 'necessary', 2: 'medium', 3: 'low'}
    ticket_status = ['open', 'close']

    def text_preparation(self, text : str):
        clean_text = str(text).maketrans({char: None for char in self.list_of_character})
        return clean_text

    @staticmethod
    def date_now(timezone='utc', time_format=False):
        time_now = datetime.now(tz=pytz.timezone(timezone))
        if time_format: time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
        return time_now


    def return_priority_name(self, priority_number):
        priority = self.priority.get(priority_number, self.priority.get(max(self.priority)))
        return priority


class TicketKernel(ManageDb, PreparationAdapter, metaclass=InstanceIsNotAllowed):
    table_name = 'ticket'
    def __init__(self, db_name):
        super().__init__(db_name=db_name)

    def create_ticket(self, user_id, title, text, priority, department, photo=None):
        preparation_text = self.text_preparation(text)
        date_now = self.date_now('Asia/Tehran', True)
        master_ticket_id = self.insert(table=self.table_name, rows={'user_id': user_id, 'department': department,
                                                                    'priority': priority, 'title': title, 'body_text': preparation_text,
                                                                    'date': date_now, 'status': 'open', 'image': photo})
        return master_ticket_id


    @abstractmethod
    def reply_to_ticket(self, master_ticket_id, user_id, text, photo=None):
        preparation_text = self.text_preparation(text)
        date_now = self.date_now('Asia/Tehran', True)
        ticket_id = self.insert(table=self.table_name, rows={'master_ticket_id': master_ticket_id, 'user_id': user_id,
                                                             'body_text': preparation_text, 'image': photo, 'date': date_now})
        return ticket_id

    def change_ticket_status(self, ticket_id, change_to='close'):
        date_now = self.date_now('Asia/Tehran', True)
        self.update_ticket(ticket_id, {'status': change_to, 'update_date': date_now})


    def check_ticket_status(self, master_ticket_id):
        get_ticket_from_db = self.select(column='status,user_id', table=self.table_name, where=f'id={master_ticket_id}')
        if get_ticket_from_db[0][0] == 'open':
            return True, get_ticket_from_db[0][1]
        return False, get_ticket_from_db[0][1]

    def update_ticket(self, ticket_id, edit_dict: dict):
        date_now = self.date_now('Asia/Tehran', True)
        sql_rows = {'date': date_now}
        sql_rows.update(edit_dict)
        ticket_id = self.update({self.table_name: sql_rows}, where=f'id = {ticket_id}')
        return ticket_id


    def remove_ticket(self, key, value):
        ticket_id = self.delete({self.table_name: {key: value}})
        return ticket_id



class TicketManager(TicketKernel):  # Decorator
    def reply_to_ticket(self, master_ticket_id, user_id, text, photo=None):
        if self.check_ticket_status(master_ticket_id):
            return super().reply_to_ticket(master_ticket_id, user_id, text)
        raise TicketClosedError()

