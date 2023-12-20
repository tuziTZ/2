# import logging
# import os
# import sqlite3 as sqlite
#
#
# class Store:
#     database: str
#
#     def __init__(self, db_path):
#         self.database = os.path.join(db_path, "be.db")
#         self.init_tables()
#
#     def init_tables(self):
#         try:
#             conn = self.get_db_conn()
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS user ("
#                 "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
#                 "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
#             )
#
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS user_store("
#                 "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
#             )
#
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS store( "
#                 "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
#                 " PRIMARY KEY(store_id, book_id))"
#             )
#
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS new_order( "
#                 "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
#             )
#
#             conn.execute(
#                 "CREATE TABLE IF NOT EXISTS new_order_detail( "
#                 "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
#                 "PRIMARY KEY(order_id, book_id))"
#             )
#
#             conn.commit()
#         except sqlite.Error as e:
#             logging.error(e)
#             conn.rollback()
#
#     def get_db_conn(self) -> sqlite.Connection:
#         return sqlite.connect(self.database)
#
#
# database_instance: Store = None
#
#
# def init_database(db_path):
#     global database_instance
#     database_instance = Store(db_path)
#
#
# def get_db_conn():
#     global database_instance
#     return database_instance.get_db_conn()


from sqlalchemy import Column, String, create_engine, Integer, Text, Date, ForeignKey, LargeBinary
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.sql import func

Base = sqlalchemy.orm.declarative_base()


class User(Base):
    __tablename__ = 'user'
    user_id = Column(String, primary_key=True,unique=True)
    password = Column(String, nullable=False)
    balance = Column(Integer, nullable=False)
    token = Column(String)
    terminal = Column(String)


class Store(Base):
    __tablename__ = 'store'

    store_id = Column(String,ForeignKey('user_store.store_id'), primary_key=True)
    book_id = Column(String, primary_key=True)
    price = Column(Integer)
    stock_level = Column(Integer)


class UserStore(Base):
    __tablename__ = 'user_store'

    user_id = Column(String, ForeignKey('user.user_id'))
    store_id = Column(String, primary_key=True,unique=True)


class Book(Base):
    __tablename__ = 'book'

    id = Column(String, primary_key=True, unique=True)
    title = Column(String)
    author = Column(String)
    publisher = Column(String)
    original_title = Column(String)
    translator = Column(String)
    pub_year = Column(String)
    pages = Column(Integer)
    price = Column(Integer)
    currency_unit = Column(String)
    binding = Column(String)
    isbn = Column(String)
    author_intro = Column(Text)
    book_intro = Column(Text)
    content = Column(Text)
    tags = Column(String)
    picture = Column(LargeBinary)


class NewOrder(Base):
    __tablename__ = 'new_order'

    order_id = Column(String, primary_key=True, unique=True)
    user_id = Column(String)
    store_id = Column(String)
    status = Column(String)
    created_at = Column(Date, server_default=func.now())
    shipped_at = Column(Date)
    received_at = Column(Date)


class NewOrderDetail(Base):
    __tablename__ = 'new_order_detail'

    order_id = Column(String, ForeignKey('new_order.order_id'), primary_key=True)
    book_id = Column(String, primary_key=True)
    count = Column(Integer)
    price = Column(Integer)


class BookStore:

    def __init__(self):
        self.engine = create_engine('postgresql://postgres:123456@localhost:5432/bookstore')
        self.DbSession = sessionmaker(bind=self.engine)
        self.session = self.DbSession()
        self.init_tables()

    def init_tables(self):
        Base.metadata.create_all(self.engine)

    def get_db_conn(self):
        return self.session


database_instance: BookStore = None


def init_database():
    global database_instance
    database_instance = BookStore()


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()

# 调用这两句可以创建所有表并且获取到session
# init_database()
# session = get_db_conn()
