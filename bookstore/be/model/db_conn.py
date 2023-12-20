import sqlite3

from be.model import store
from be.model.store import User as UserModel, Store as StoreModel, UserStore, Book as BookModel


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()

        # self.sqlite_conn = sqlite3.connect('book_data.db')
        #
        # # 假设你有一个名为book_info的表，包含了图片字段LargeBinary
        # self.sqlite_conn.cursor().execute('''
        #     CREATE TABLE IF NOT EXISTS book_info (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         picture BLOB
        #     )
        # ''')

    def user_id_exist(self, user_id):
        return self.conn.query(UserModel).filter(UserModel.user_id == user_id).first() is not None

    def book_id_exist(self, store_id, book_id):
        # 在这个店里已经存在这本书
        return (
                self.conn.query(StoreModel)
                .filter(StoreModel.store_id == store_id, StoreModel.book_id == book_id)
                .first()
                is not None
        )

    def book_id_exist_all(self, book_id):
        return (
                self.conn.query(BookModel)
                .filter(BookModel.id == book_id)
                .first()
                is not None
        )

    def store_id_exist(self, store_id):
        return (
                self.conn.query(UserStore)
                .filter(UserStore.store_id == store_id)
                .first()
                is not None
        )
