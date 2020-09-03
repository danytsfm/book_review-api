import os
import requests

from flask import Flask, session, redirect, request, url_for, flash, render_template, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt
from user import User
from book import Book
from exception import IncorrectCredentials



app = Flask(__name__)
app.secret_key = '1144'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
conn = scoped_session(sessionmaker(bind=engine))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form.get('username')
        email = request.form.get('email')
        password = sha256_crypt.encrypt(str(request.form.get('password')))
        user = User(user_name, email, password, None)
        try:
            user.save_user()
            flash('You are now registered, log in and have some fun!', 'success')
        except Exception as e:
            flash('Email already registered :(', 'danger')
    return render_template('signup.html')


@app.route('/auth', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = User.user_login(email, password)
            session['user_name'] = user.user_name
            session['id'] = user.user_id
        except Exception:
            if IncorrectCredentials:
                flash('Incorrect username or password.', 'danger')
            else:
                flash('Email not registered yet', 'danger')
            return render_template('index.html')

    return redirect(url_for('book_search'))


@app.route('/home', methods=['GET', 'POST'])
def book_search():
    session['books'] = []
    if request.method == 'POST':
        if session.get('user_name') is None:
            return render_template('index.html')
        isbn = request.form.get('search')
        title = request.form.get('search')
        author = request.form.get('search')
        try:
            books = Book.search_books(isbn, title.title(), author.title())
            if not books:
                flash('No books found :(', 'danger')
            else:
                for data in books:
                    # session['books'].append({'isbn': data[0]})
                    session['books'].append({'title': data[1]})
        except:
            flash('No books found :(', 'danger')
    return render_template('home.html', user_name=session['user_name'], books=session['books'])


@app.route('/book_list', methods=['GET', 'POST'])
def select_book():
    if request.method == 'GET':
        return redirect(url_for('book_info', user_name=session['user_name']))


@app.route('/book_page', methods=['GET'])
def book_info():
    session['info'] = []
    session['isbn'] = ''
    lst_reviews = []
    if request.method == 'GET':
        if session.get('title') is None:
            session['title'] = request.args.get('title')
        try:
            book = Book.get_book_info(session['title'])
            if book:
                for data in book:
                    session['info'].append({'isbn':data[0], 'title': data[1], 'author': data[2],
                                            'year': data[3], 'count': data[4], 'average': data[5]})
            session['isbn'] = data[0]

            review = Book.get_review_info(session['isbn'])
            if review:
                for data in review:
                    lst_reviews.append({'user_name': data[1], 'reviews': data[2], 'post_date': data[3], 'ratings': data[4]})

        except: EnvironmentError('No info for selected book')

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "rBJbmzwD7tvVz4mqq2ObXw", "isbns": session['isbn']})
    if res.status_code != 200:
        ratings_good_read = 'No ratings from goodreads'
    else:
        data = res.json()
        ratings_good_read = data['average_rating']

    return render_template('book_page.html', user_name=session['user_name'], user_id=session['id'],
                           info=session['info'], reviews=lst_reviews)


@app.route('/write_review', methods=['GET', 'POST'])
def write_review():
    if session.get('title') is None:
        session['title'] = request.args.get('title')
    if request.method == 'POST':
        book = Book.get_book_info(session['title'])
        if book:
            for data in book:
                session['isbn'] = data[0]
        review = request.form.get('textreview')
        if request.form.get('1') == '1':
            rating = 1
        elif request.form.get('2') == '2':
            rating = 2
        elif request.form.get('3') == '3':
            rating = 3
        elif request.form.get('4') == '4':
            rating = 4
        elif request.form.get('5') == '5':
            rating = 5
        else:
            rating = 0
        try:
            book = Book.save_review(session['id'], session['isbn'], review, rating)
            flash('Your review was saved with success!', 'success')
            return redirect(url_for('book_info', user_name=session['user_name'], user_id=session['id'], title=session['title']))

        except:
            flash('You have submitted a review for this book already', 'danger')
    return render_template('reviews.html', user_name=session['user_name'],user_id=session['id'], title=session['title'])



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     return response


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/api/readanview/<string:isbn>')
def book_api(isbn):
    '''Return info about books'''
    books = Book.get_book_api(isbn)
    if books is None:
        return jsonify({'Error 404': 'Not Found'}), 404
    for data in books:
        return jsonify({
            "isbn": data[0],
            "title": data[1],
            "author": data[2],
            "year": int(data[3]),
            "average": str(data[4]),
            "reviews_count": data[5]
        })


if __name__ == '__main__':
    app.run()