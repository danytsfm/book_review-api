import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt
from exception import IncorrectCredentials


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
conn = scoped_session(sessionmaker(bind=engine))


class User:

    def __init__(self, user_name, email, password, user_id):
        self.user_name = user_name
        self.email = email
        self.password = password
        self.user_id = user_id

    def save_user(self):

        x = conn.execute('SELECT * FROM users WHERE email = :email', {'email': self.email}).fetchone()
        if x:
            raise ValueError('Email already registered')
        else:
            conn.execute('INSERT INTO users (user_name, email, password) VALUES(:user_name, :email, :password)',
                         {'user_name': self.user_name, 'email': self.email, 'password': self.password})
            conn.commit()
            conn.close()

    @classmethod
    def user_login(cls, email, password):
        user_data = conn.execute('SELECT id, user_name, email, password FROM users WHERE email = :email',
                            {'email': email}).fetchone()
        if user_data:
            if sha256_crypt.verify(password, user_data[3]):
                return cls(user_name=user_data[1], email=user_data[2], password=user_data[3], user_id=user_data[0])
            else:
                raise IncorrectCredentials
        else:
            raise LookupError



