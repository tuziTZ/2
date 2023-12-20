import json
import traceback
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from be.model import error
from be.model import db_conn
from be.model.store import Store as StoreModel, Book as BookModel, UserStore, NewOrder


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
            self,
            user_id: str,
            store_id: str,
            book_json_str: str,
            stock_level: int,
    ):
        book_info=json.loads(book_json_str)
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_info['id']):
                return error.error_exist_book_id(book_info['id'])
            if self.book_id_exist_all(book_info['id']):
                new_store = StoreModel(
                    store_id=store_id,
                    book_id=book_info['id'],
                    price=book_info["price"],
                    stock_level=stock_level
                )

                self.conn.add(new_store)
                self.conn.commit()
            else:
                # 使用SQLAlchemy插入数据
                new_book = BookModel(
                    id=book_info['id'],
                    title=book_info["title"],
                    author=book_info["author"],
                    publisher=book_info["publisher"],
                    original_title=book_info["original_title"],
                    translator=book_info["translator"],
                    pub_year=book_info["pub_year"],
                    pages=book_info["pages"],
                    price=book_info["price"],
                    currency_unit=book_info["currency_unit"],
                    binding=book_info["binding"],
                    isbn=book_info["isbn"],
                    author_intro=book_info["author_intro"],
                    book_intro=book_info["book_intro"],
                    content=book_info["content"],
                    tags=book_info["tags"],
                    # picture=book_info["picture"]  # 假设这里的图片存储在数据库中的字段为 LargeBinary
                )
                # self.sqlite_conn.execute('INSERT INTO book_info (picture) VALUES (?)', (book_info["picture"],))
                # self.sqlite_conn.commit()

                new_store = StoreModel(
                    store_id=store_id,
                    book_id=book_info['id'],
                    price=book_info["price"],
                    stock_level=stock_level
                )

                self.conn.add_all([new_book, new_store])
                self.conn.commit()

        except IntegrityError as e:
            return 528, "{}".format(str(e))
        except Exception as e:

            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
            self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            # 使用SQLAlchemy更新数据
            store = self.conn.query(StoreModel).filter_by(store_id=store_id, book_id=book_id).first()
            store.stock_level += add_stock_level
            self.conn.commit()

        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            # 使用SQLAlchemy插入数据
            new_user_store = UserStore(
                store_id=store_id,
                user_id=user_id
            )

            self.conn.add(new_user_store)
            self.conn.commit()

        except IntegrityError as e:
            return 528, "{}".format(str(e))
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def ship_order(self, store_id: str, order_id: str) -> (int, str):
        try:
            if not self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            # 使用SQLAlchemy更新数据
            order = self.conn.query(NewOrder).filter_by(order_id=order_id, store_id=store_id).first()

            if order is None:
                return error.error_invalid_order_id(order_id)

            if order.status == "shipped":
                return 200, "Order is already shipped."

            if order.status != "paid":
                return error.error_status_fail(order_id)

            order.status = "shipped"
            order.shipped_at = datetime.now()
            self.conn.commit()
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def get_seller_orders(self, user_id: str) -> (int, str, list):
        try:
            # 使用SQLAlchemy查询数据
            seller_stores = self.conn.query(UserStore).filter_by(user_id=user_id).all()

            # print(seller_stores)

            seller_orders = []

            for store in seller_stores:
                orders = self.conn.query(NewOrder).filter_by(store_id=store.store_id).all()
                order_dict=[]
                for order in orders:
                    order_dict.append({
                        'store_id': order.store_id,
                        'order_id': order.order_id,
                        'status': order.status,
                    })
                seller_orders.extend(order_dict)

            return 200, "ok", seller_orders
        except Exception as e:
            return 530, "{}".format(str(e)), []
