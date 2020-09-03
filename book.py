import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
conn = scoped_session(sessionmaker(bind=engine))


class Book:

    @staticmethod
    def search_books(isbn, title, author):
        books = conn.execute("SELECT * FROM books WHERE isbn like :isbn or title like :title or "
                                 "author like :author ",
                                 {'isbn': '%' + isbn + '%', 'title': '%' + title + '%', 'author': '%' + author + '%'}).fetchall()
        if books:
            return books

    @staticmethod
    def get_book_info(title):
        info = conn.execute('SELECT * FROM book_info  WHERE title = :title', {'title': title}).fetchall()

        if info:
            return info

    @staticmethod
    def get_review_info(isbn):
        r = conn.execute('SELECT * FROM get_info WHERE isbn = :isbn', {'isbn': isbn}).fetchall()
        if r:
            return r

    @staticmethod
    def save_review(user_id, isbn, reviews, ratings):
        x = conn.execute('SELECT * FROM reviews WHERE isbn = :isbn and user_id = :user_id', {'isbn': isbn,
                                                                                             'user_id': user_id}).fetchone()
        if x:
            raise ValueError('You already wrote a review for this book')
        else:
            conn.execute('INSERT INTO reviews (user_id, isbn, reviews, ratings) VALUES(:user_id, :isbn, :reviews, '
                              ':ratings)', {'user_id': user_id, 'isbn': isbn, 'reviews': reviews, 'ratings': ratings})
            conn.commit()
            conn.close()

    @staticmethod
    def get_book_api(isbn):
        book = conn.execute('SELECT * FROM get_api_info where isbn = :isbn', {'isbn': isbn}).fetchall()
        if book:
            return book

