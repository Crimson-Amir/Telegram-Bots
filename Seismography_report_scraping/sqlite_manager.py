import sqlite3


class ManageDb:
    def __init__(self, db_name: str = "test"):
        self.db_name = db_name + ".db"

    @staticmethod
    def connecting_manage(org):
        def wrapper(self, *args, **kwargs):
            with sqlite3.connect(self.db_name) as self.db:
                self.cursor = self.db.cursor()
                return org(self, *args, **kwargs)

        return wrapper

    @connecting_manage
    def create_table(self, table: dict):
        """
        :arg table: {"table_name": {"name": "TEXT", "family": "TEXT"}}
        """
        for key, val in table.items():
            coul = [f"{name} {v}" for name, v in val.items()]
            self.cursor.execute("CREATE TABLE IF NOT EXISTS {0} ({1})".format(key, ", ".join(coul)))
        self.db.commit()

    @connecting_manage
    def select(self, column: str = "*", table: str = "sqlite_master",
               where: str = None, distinct: bool = False, order_by: str = None,
               limit: int = None, ret_raw_res=False):
        """
        :param column: select <column> from db
        :param table: table name
        :param where: 'name = "amir" AND id between 10 and 20
               OR name IN ('amir', 'ziba') OR name LIKE "%amir%"'
        :param distinct: True or False
        :param order_by: 'id ACS | DECS'
        :param limit: 10 OFFSET 5
        """
        distinct_ = "DISTINCT " if distinct else ''
        order_by_ = f'ORDER BY {order_by}' if order_by else ''
        limit_ = f'LIMIT {limit}' if limit else ''
        where_ = f'WHERE {where}' if where else ''

        sql = f"SELECT {distinct_}{column} FROM {table} {where_} {order_by_} {limit_}"
        self.cursor.execute(sql)
        self.db_values = self.cursor.fetchall()
        return self.db_values

    @connecting_manage
    def insert(self, table: str, rows: list, custom_order=""):
        """
        :param table: name of table
        :param rows: [{'name': 'amir', 'family':'any'}, {...}, {...}]
        :param custom_order
        """
        column = ', '.join(rows[0].keys())
        touples = []

        for row in rows:
            values = [f"'{val}'" for val in row.values()]
            touples.append(f"({', '.join(values)})")
        ex = self.cursor.execute(f'INSERT INTO {table} ({column}) VALUES {", ".join(touples)}')
        self.db.commit()
        return self.cursor.lastrowid

    @connecting_manage
    def delete(self, table: dict):
        """
        :param table: {"table_name": ["name", "something"]}
        :return: delete column where name is somthing, from table_name
        """
        for key, value in table.items():
            self.cursor.execute(f"DELETE FROM {key} WHERE {value[0]}='{value[1]}'")
        self.db.commit()

    @connecting_manage
    def advanced_delete(self, table):
        """
        :param table: {"table_name": [["name", "something"],['id', 2]]}
        :return: delete column where name is somthing, from table_name
        """
        for key, value in table.items():
            where = ''
            for arg in value:
                key_ = arg[0]
                val_ = arg[1] if type(arg[1]) is int else f'"{arg[1]}"'
                where += f'{key_} = {val_} AND '
            self.cursor.execute(f"DELETE FROM {key} WHERE {where[:-4]}")
        self.db.commit()

    @connecting_manage
    def drop_table(self, table: str):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
        self.db.commit()

    @connecting_manage
    def update(self, table, where):

        where = f'where {where}' or None
        for key, value in table.items():
            for k, v in value.items():
                text = f"UPDATE {key} SET {k} = '{v}' {where}"
                self.cursor.execute(text)
            self.db.commit()
        return self.cursor.lastrowid

    @connecting_manage
    def custom(self, order: str):
        self.cursor.execute(order)
        self.db.commit()
        return self.cursor.fetchall()

# t = {
#     "student": {
#         "id": "integer primary key",
#         "name": "TEXT",
#         "family": "TEXT",
#         "age": "INTEGER"
#     },
#     "teacher": {
#         "name": "TEXT",
#         "family": "TEXT",
#         "age": "INTEGER"
#     }
# }
# a = ManageDb()
# a.create_table(t)
# print(a.custom("SELECT name from sqlite_master where type='table'"))
# a.insert(table='student', rows=[{'name': 'amir', 'family': 'najafi', 'age': 21}, {'name': 'fsd', 'family': 'sfd', 'age': 34}])
# a.delete({'student': ['name', 'amir']})
# a.drop_table('teacher')
# print(a.order_by(table='student'))
# print(a.select(table='student'))
