import traceback
import uuid
import json
import logging

from sqlalchemy import func

from be.model import error
from be.model import db_conn

from sqlalchemy.exc import IntegrityError

from be.model import error
from be.model import db_conn
from sqlalchemy.orm import aliased
from be.model.store import Store as StoreModel, Book as BookModel


class Book(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    # def search_all(self,title,author,publisher,isbn,content,tags,book_intro):
    def search_in_store(self, store_id, title, author, publisher, isbn, content, tags, book_intro, page, per_page):
        try:
            store_alias = aliased(StoreModel)
            book_alias = aliased(BookModel)

            query = (
                self.conn.query(book_alias)
                .join(store_alias, store_alias.book_id == book_alias.id)
                .filter(store_alias.store_id == store_id)
                # .filter(
                #     book_alias.title.ilike(f'%{title}%'),
                #     book_alias.author.ilike(f'%{author}%'),
                #     book_alias.publisher.ilike(f'%{publisher}%'),
                #     book_alias.isbn.ilike(f'%{isbn}%'),
                #     book_alias.content.ilike(f'%{content}%'),
                #     book_alias.tags.ilike(f'%{tags}%'),
                #     book_alias.book_intro.ilike(f'%{book_intro}%'),
                # )
            )
            if title:
                query = query.filter(book_alias.title.ilike(f'%{title}%'))
            if author:
                query = query.filter(book_alias.author.ilike(f'%{author}%'))
            if publisher:
                query = query.filter(book_alias.publisher.ilike(f'%{publisher}%'))
            if isbn:
                query = query.filter(book_alias.isbn.ilike(f'%{isbn}%'))
            if content:
                query = query.filter(book_alias.content.ilike(f'%{content}%'))
            if book_intro:
                query = query.filter(book_alias.book_intro.ilike(f'%{book_intro}%'))

            if tags:
                for tag in tags:
                    query = query.filter(book_alias.tags.ilike(f'%{tag}%'))

            result = []
            skip = (page - 1) * per_page
            limit = per_page
            paged_result=query.all()[skip: skip + limit]
            for book in paged_result:
                result.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'publisher': book.publisher,
                    'original_title': book.original_title,
                    'translator': book.translator,
                    'pub_year': book.pub_year,
                    'pages': book.pages,
                    'price': book.price,
                    'currency_unit': book.currency_unit,
                    'binding': book.binding,
                    'isbn': book.isbn,
                    'author_intro': book.author_intro,
                    'book_intro': book.book_intro,
                    'content': book.content,
                    'tags': book.tags,
                    # 'picture': book.picture
                })
        except Exception as e:
            traceback.print_exc()
            return 530, str(e)

        return 200, result

    def search_all(self, title, author, publisher, isbn, content, tags, book_intro,page,per_page):
        try:

            query = (
                self.conn.query(BookModel)
            )
            if title:
                query = query.filter(BookModel.title.ilike(f'%{title}%'))
            if author:
                query = query.filter(BookModel.author.ilike(f'%{author}%'))
            if publisher:
                query = query.filter(BookModel.publisher.ilike(f'%{publisher}%'))
            if isbn:
                query = query.filter(BookModel.isbn.ilike(f'%{isbn}%'))
            if content:
                query = query.filter(BookModel.content.ilike(f'%{content}%'))
            if book_intro:
                query = query.filter(BookModel.book_intro.ilike(f'%{book_intro}%'))

            if tags:
                for tag in tags:
                    query = query.filter(BookModel.tags.ilike(f'%{tag}%'))
            result = []
            skip = (page - 1) * per_page
            limit = per_page
            if skip + limit< len(query.all()):
                paged_result = query.all()[skip: skip + limit]
            else:
                paged_result= query.all()
            print(len(query.all()))
            for book in paged_result:
                result.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'publisher': book.publisher,
                    'original_title': book.original_title,
                    'translator': book.translator,
                    'pub_year': book.pub_year,
                    'pages': book.pages,
                    'price': book.price,
                    'currency_unit': book.currency_unit,
                    'binding': book.binding,
                    'isbn': book.isbn,
                    'author_intro': book.author_intro,
                    'book_intro': book.book_intro,
                    'content': book.content,
                    'tags': book.tags,
                    # 'picture': book.picture
                })
        except Exception as e:
            traceback.print_exc()
            return 530, str(e)

        return 200, result
