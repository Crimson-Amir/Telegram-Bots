from abc import ABC, abstractmethod
from sqlite_manager import ManageDb


class Sindleton(type):
    _isinstance = None
    def __call__(self, *args, **kwargs):
        if not self._isinstance:
            self._isinstance = super().__call__(*args, **kwargs)
        return self._isinstance


class PreparationAdapter:
    list_of_character = ['"', "'", "/", ";", "%"]
    def text_preparation(self, text : str):
        clean_text = str(text).maketrans({char: None for char in self.list_of_character})
        return clean_text

class Ticket(ABC, ManageDb, metaclass=Sindleton):
    table_name = 'ticket'
    def __int__(self, db_name):
        super().__init__(db_name=db_name)

    def create_ticket(self, user_id, text, priority):
        preparation_text = PreparationAdapter().text_preparation(text)
        self.insert(table=self.table_name, rows={})
