from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

book_genre = db.Table('book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id', ondelete='CASCADE'))
)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    genres = db.relationship('Genre', secondary=book_genre, backref='books')
    
    cover = db.relationship(
        'Cover',
        backref='book',
        uselist=False,
        cascade='all, delete-orphan',
        foreign_keys='Cover.book_id' 
    )

    reviews = db.relationship('Review', backref='book', cascade='all, delete-orphan')
    author = db.relationship('Author', backref='books')
    publisher = db.relationship('Publisher', backref='books')

    genres = db.relationship('Genre', secondary=book_genre, backref='books')
    cover = db.relationship('Cover', backref='book', uselist=False, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='book', cascade='all, delete-orphan')



class Cover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    users = db.relationship('User', backref='role', cascade='all, delete-orphan')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    reviews = db.relationship('Review', backref='user', cascade='all, delete-orphan')
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
