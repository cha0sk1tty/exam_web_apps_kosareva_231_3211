import os
import hashlib
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
)
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
import markdown
import bleach
from werkzeug.datastructures import FileStorage, MultiDict

from app.models import Book, Review, Genre, Cover, Publisher, Author, User
from app.forms import BookForm, ReviewForm, LoginForm, SearchForm
from app.forms import BookForm
from app import db

from sqlalchemy import func


views = Blueprint("views", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_markdown(text):
    html = markdown.markdown(text)
    allowed_tags = bleach.sanitizer.ALLOWED_TAGS.union(
        {
            "p",
            "pre",
            "code",
            "ul",
            "ol",
            "li",
            "strong",
            "em",
        }
    )
    cleaned = bleach.clean(html, tags=allowed_tags, strip=True)
    return cleaned


def role_required(*roles):
    def decorator(f):
        from functools import wraps

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(
                    "Для выполнения данного действия необходимо пройти процедуру аутентификации",
                    "error",
                )
                return redirect(url_for("views.login"))
            if current_user.role.name not in roles:
                flash(
                    "У вас недостаточно прав для выполнения данного действия", "error"
                )
                return redirect(url_for("views.index"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def make_multi_value_args(args):
    args = args.to_dict(flat=False)
    # Если ключ отсутствует — ставим пустой список
    for key in ["genres", "years"]:
        if key not in args:
            args[key] = []
    return MultiDict(args)


@views.route("/")
@views.route("/index")
def index():
    args = make_multi_value_args(request.args)
    form = SearchForm(args)

    # Заполняем choices
    years = [
        y[0] for y in db.session.query(Book.year).distinct().order_by(Book.year).all()
    ]
    genres = Genre.query.order_by(Genre.name).all()

    form.years.choices = [(y, str(y)) for y in years]
    form.genres.choices = [(g.id, g.name) for g in genres]

    # Базовый запрос с агрегатами отзывов
    query = (
        db.session.query(
            Book,
            func.coalesce(func.avg(Review.rating), 0).label("avg_rating"),
            func.count(Review.id).label("reviews_count"),
        )
        .outerjoin(Review, Review.book_id == Book.id)
        .group_by(Book.id)
    )

    if form.validate():
        if form.title.data:
            query = query.filter(Book.title.ilike(f"%{form.title.data.strip()}%"))
        if form.author.data:
            query = query.outerjoin(Book.author).filter(
                Author.name.ilike(f"%{form.author.data.strip()}%")
            )
        if form.years.data:
            years_int = [int(y) for y in form.years.data]
            query = query.filter(Book.year.in_(years_int))
        if form.genres.data:
            genres_int = [int(g) for g in form.genres.data]
            query = query.filter(Book.genres.any(Genre.id.in_(genres_int)))
        if form.pages_min.data:
            query = query.filter(Book.pages >= form.pages_min.data)
        if form.pages_max.data:
            query = query.filter(Book.pages <= form.pages_max.data)

    query = query.distinct()
    query = query.order_by(Book.year.desc())

    page = request.args.get("page", 1, type=int)
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    results = pagination.items

    return render_template(
        "index.html", results=results, pagination=pagination, form=form
    )



@views.route("/book/<int:book_id>")
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)

    description_html = sanitize_markdown(book.description or "")

    reviews = book.reviews or []

    reviews_html = []
    for r in reviews:
        review_text = r.text or ""
        reviews_html.append(
            {
                "user": r.user,
                "rating": r.rating,
                "text_html": sanitize_markdown(review_text),
                "created_at": r.created_at,
            }
        )

    user_review = None
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(
            book_id=book.id, user_id=current_user.id
        ).first()

    return render_template(
        "book_detail.html",
        book=book,
        description_html=description_html,
        reviews=reviews_html,
        user_review=user_review,
    )


@views.route("/book/<int:book_id>/review", methods=["GET", "POST"])
@login_required
def submit_review(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == "POST":
        # Получаем данные из формы
        rating = request.form.get("rating")
        text = request.form.get("text")

        # Применяем санитайзер для текста рецензии
        text = bleach.clean(text)

        # Проверка, написал ли пользователь рецензию ранее
        existing_review = Review.query.filter_by(
            book_id=book_id, user_id=current_user.id
        ).first()
        if existing_review:
            flash("Вы уже написали рецензию на эту книгу.", "error")
            return redirect(url_for("views.book_detail", book_id=book.id))

        # Сохраняем рецензию
        review = Review(
            book_id=book_id, user_id=current_user.id, rating=rating, text=text
        )
        db.session.add(review)
        db.session.commit()

        flash("Рецензия успешно добавлена!", "success")
        return redirect(url_for("views.book_detail", book_id=book.id))

    return render_template("add_review.html", book=book)


@views.route("/book/add", methods=["GET", "POST"])
@login_required
@role_required("администратор")
def add_book():
    form = BookForm()
    # Заполняем выбор жанров
    form.genres.choices = [
        (g.id, g.name) for g in Genre.query.order_by(Genre.name).all()
    ]

    if form.validate_on_submit():
        try:
            # Автор
            author_name = form.author.data.strip()
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                author = Author(name=author_name)
                db.session.add(author)
                db.session.flush()

            # Издатель
            publisher_name = form.publisher.data.strip()
            publisher = Publisher.query.filter_by(name=publisher_name).first()
            if not publisher:
                publisher = Publisher(name=publisher_name)
                db.session.add(publisher)
                db.session.flush()

            # Создаём книгу
            book = Book(
                title=form.title.data.strip(),
                description=bleach.clean(form.description.data.strip()),
                year=form.year.data,
                pages=form.pages.data,
                author=author,
                publisher=publisher,
            )
            # Жанры
            selected_genre_ids = form.genres.data or []
            book.genres = Genre.query.filter(Genre.id.in_(selected_genre_ids)).all()

            db.session.add(book)
            db.session.commit()  # Сохраняем книгу, чтобы получить book.id

            # Обработка обложки
            if form.cover.data:
                uploaded_file = form.cover.data
                if (
                    isinstance(uploaded_file, FileStorage)
                    and uploaded_file.filename != ""
                ):
                    file_data = uploaded_file.read()
                    md5_hash = hashlib.md5(file_data).hexdigest()

                    cover = Cover.query.filter_by(md5_hash=md5_hash).first()
                    if not cover:
                        cover = Cover(
                            filename="",
                            mime_type=uploaded_file.mimetype,
                            md5_hash=md5_hash,
                            book_id=book.id,
                        )
                        db.session.add(cover)
                        db.session.flush()

                        ext = (
                            secure_filename(uploaded_file.filename)
                            .rsplit(".", 1)[1]
                            .lower()
                        )
                        cover.filename = f"{cover.id}.{ext}"

                        save_path = os.path.join(
                            current_app.config["UPLOAD_FOLDER"], cover.filename
                        )
                        with open(save_path, "wb") as f:
                            f.write(file_data)

                    else:
                        cover.book_id = book.id

                    book.cover = cover
                    db.session.commit()

            flash("Книга успешно добавлена!", "success")
            return redirect(url_for("views.book_detail", book_id=book.id))

        except Exception as e:
            db.session.rollback()
            flash(
                "При сохранении данных возникла ошибка. Проверьте корректность введённых данных.",
                "error",
            )

    return render_template("book_form.html", form=form, editing=False)


@views.route("/book/edit/<int:book_id>", methods=["GET", "POST"])
@login_required
@role_required("администратор", "модератор")
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    form.genres.choices = [
        (g.id, g.name) for g in Genre.query.order_by(Genre.name).all()
    ]

    if request.method == "GET":
        # Заполнить мультиселект жанров
        form.genres.data = [g.id for g in book.genres]
        # Заполнить поля автора и издателя вручную
        form.author.data = book.author.name if book.author else ""
        form.publisher.data = book.publisher.name if book.publisher else ""

    if form.validate_on_submit():
        try:
            # Обновляем простые поля
            book.title = form.title.data.strip()
            book.description = bleach.clean(form.description.data.strip())
            book.year = form.year.data
            book.pages = form.pages.data

            # Обновляем автора
            author_name = form.author.data.strip()
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                author = Author(name=author_name)
                db.session.add(author)
                db.session.flush()  # чтобы получить id

            book.author = author

            # Обновляем издателя
            publisher_name = form.publisher.data.strip()
            publisher = Publisher.query.filter_by(name=publisher_name).first()
            if not publisher:
                publisher = Publisher(name=publisher_name)
                db.session.add(publisher)
                db.session.flush()

            book.publisher = publisher

            # Обновляем жанры
            selected_genre_ids = form.genres.data or []
            book.genres = Genre.query.filter(Genre.id.in_(selected_genre_ids)).all()

            db.session.commit()
            db.session.commit()
            flash("Книга успешно обновлена!", "success")
            return redirect(url_for("views.book_detail", book_id=book.id))
        except Exception as e:
            db.session.rollback()
            flash(
                "При сохранении данных возникла ошибка. Проверьте корректность введённых данных.",
                "error",
            )
            # Возврат формы с введёнными данными
            return render_template("book_form.html", form=form, editing=True, book=book)


@views.route("/book/delete/<int:book_id>", methods=["POST"])
@login_required
@role_required("администратор")
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    try:
        # Удалить файл обложки из файловой системы
        if book.cover:
            cover_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], book.cover.filename
            )
            if os.path.exists(cover_path):
                os.remove(cover_path)

        db.session.delete(book)
        db.session.commit()
        flash("Книга успешно удалена", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при удалении книги: {str(e)}", "error")
    return redirect(url_for("views.index"))


@views.route("/review/add/<int:book_id>", methods=["GET", "POST"])
@login_required
def add_review(book_id):
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()

    form.rating.choices = [
        (5, "Отлично"),
        (4, "Хорошо"),
        (3, "Удовлетворительно"),
        (2, "Неудовлетворительно"),
        (1, "Плохо"),
        (0, "Ужасно"),
    ]

    # Проверка, писал ли пользователь отзыв
    existing_review = Review.query.filter_by(
        book_id=book.id, user_id=current_user.id
    ).first()
    if existing_review:
        flash("Вы уже оставили отзыв на эту книгу.", "info")
        return redirect(url_for("views.book_detail", book_id=book.id))

    if form.validate_on_submit():
        try:
            review = Review(
                book_id=book.id,
                user_id=current_user.id,
                rating=form.rating.data,
                text=form.text.data.strip(),
            )
            db.session.add(review)
            db.session.commit()
            flash("Отзыв добавлен!", "success")
            return redirect(url_for("views.book_detail", book_id=book.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при добавлении отзыва: {str(e)}", "error")

    return render_template("review_form.html", form=form, book=book)


@views.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and user.check_password(
            form.password.data
        ):  # предполагается метод check_password
            login_user(user, remember=form.remember.data)
            flash("Успешный вход!", "success")
            return redirect(url_for("views.index"))

        flash("Невозможно аутентифицироваться с указанными логином и паролем", "error")

    return render_template("login.html", form=form)


@views.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    next_page = request.form.get("next")
    flash("Вы вышли из системы", "info")
    return redirect(next_page or url_for("views.index"))
