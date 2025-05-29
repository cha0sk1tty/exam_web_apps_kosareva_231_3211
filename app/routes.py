from flask import Blueprint, render_template
from app.models import Book

main = Blueprint('main', __name__)

@main.route('/')
def home():
    books = Book.query.all()
    return render_template('index.html', books=books)

