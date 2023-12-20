import traceback

import jwt
import time
import logging

from sqlalchemy.exc import IntegrityError

from be.model import error
from be.model import db_conn
from be.model.store import User as UserModel

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    # return encoded.decode("utf-8")
    return encoded


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - float(ts) >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            if self.user_id_exist(user_id):
                return error.error_exist_user_id(user_id)
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            new_user = UserModel(
                user_id=user_id,
                password=password,
                balance=0,
                token=token,
                terminal=terminal,
            )

            self.conn.add(new_user)
            self.conn.commit()
        except IntegrityError as e:
            return 528, "{}".format(str(e))

        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        user = self.conn.query(UserModel).filter_by(user_id=user_id).first()
        if user is None:
            return error.error_authorization_fail()
        db_token = user.token
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        user = self.conn.query(UserModel).filter_by(user_id=user_id).first()
        if user is None:
            return error.error_authorization_fail()

        if password != user.password:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            user = self.conn.query(UserModel).filter_by(user_id=user_id).first()
            user.token = token
            user.terminal = terminal

            self.conn.commit()
        except IntegrityError as e:
            self.conn.rollback()
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str):
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            user = self.conn.query(UserModel).filter_by(user_id=user_id).first()
            user.token = dummy_token
            user.terminal = terminal

            self.conn.commit()
        except IntegrityError as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            user = self.conn.query(UserModel).filter_by(user_id=user_id).first()
            self.conn.delete(user)
            self.conn.commit()
        except IntegrityError as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ):
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            user = self.conn.query(UserModel).filter_by(user_id=user_id).first()
            user.password = new_password
            user.token = token
            user.terminal = terminal

            self.conn.commit()
        except IntegrityError as e:
            self.conn.rollback()
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
