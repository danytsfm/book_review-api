import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
conn = scoped_session(sessionmaker(bind=engine))


def main():
    f = open('books.csv')
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        conn.execute('INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)',
                     {'isbn': isbn, 'title': title, 'author': author, 'year': year})
        conn.commit()
        conn.close()


if __name__ == '__main__':
    main()




