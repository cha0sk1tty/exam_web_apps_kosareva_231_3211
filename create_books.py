from app import create_app, db
from app.models import Book, Author, Publisher, Genre

app = create_app()

with app.app_context():
    # Создадим несколько жанров
    genres_names = ["Фантастика", "Детектив", "Роман", "История", "Фэнтези"]
    genres = []
    for name in genres_names:
        genre = Genre.query.filter_by(name=name).first()
        if not genre:
            genre = Genre(name=name)
            db.session.add(genre)
        genres.append(genre)
    db.session.commit()

    # Создадим авторов
    authors_data = ["Александр Пушкин", "Лев Толстой", "Фёдор Достоевский"]
    new_authors = [
        "Михаил Булгаков",
        "Антон Чехов",
        "Николай Гоголь",
        "Иван Тургенев",
        "Агата Кристи",
        "Джордж Мартин",
        "Дж. Р. Р. Толкин",
        "Стивен Кинг",
        "Артур Конан Дойл",
        "Эдгар Аллан По",
    ]
    authors = []
    for name in authors_data:
        author = Author.query.filter_by(name=name).first()
        if not author:
            author = Author(name=name)
            db.session.add(author)
        authors.append(author)
    db.session.commit()

    # Создадим издателей
    publishers_data = ["Издательство А", "Издательство Б"]
    new_publishers = ["Издательство В", "Издательство Г"]

    publishers = []
    for name in publishers_data:
        publisher = Publisher.query.filter_by(name=name).first()
        if not publisher:
            publisher = Publisher(name=name)
            db.session.add(publisher)
        publishers.append(publisher)
    db.session.commit()
        
    for name in new_authors:
        author = Author.query.filter_by(name=name).first()
        if not author:
            author = Author(name=name)
            db.session.add(author)
    db.session.commit()

    for name in new_publishers:
        publisher = Publisher.query.filter_by(name=name).first()
        if not publisher:
            publisher = Publisher(name=name)
            db.session.add(publisher)
    db.session.commit()

    all_authors_names = new_authors + authors_data
    all_publishers_names = new_publishers + publishers_data

    authors_map = {a.name: a for a in Author.query.filter(Author.name.in_(all_authors_names)).all()}
    publishers_map = {p.name: p for p in Publisher.query.filter(Publisher.name.in_(all_publishers_names)).all()}

    # Добавим книги
    books_data = [
        {
            "title": "Война и мир",
            "description": "Эпический роман Льва Толстого...",
            "year": 1869,
            "pages": 1200,
            "author": authors[1],  # Лев Толстой
            "publisher": publishers[0],
            "genres": [genres[2], genres[3]],  # Роман, История
        },
        {
            "title": "Преступление и наказание",
            "description": "Роман Фёдора Достоевского...",
            "year": 1866,
            "pages": 700,
            "author": authors[2],  # Фёдор Достоевский
            "publisher": publishers[1],
            "genres": [genres[1], genres[2]],  # Детектив, Роман
        },
        {
            "title": "Евгений Онегин",
            "description": "Роман в стихах Александра Пушкина...",
            "year": 1833,
            "pages": 350,
            "author": authors[0],  # Александр Пушкин
            "publisher": publishers[0],
            "genres": [genres[2]],  # Роман
        },
    ]
    
    new_books_data = [
    {
        "title": "Мастер и Маргарита",
        "description": "Роман Михаила Булгакова...",
        "year": 1967,
        "pages": 450,
        "author": authors_map["Михаил Булгаков"],
        "publisher": publishers_map["Издательство В"],
        "genres": [genres[0], genres[4]],  # Фантастика, Фэнтези
    },
    {
        "title": "Вишнёвый сад",
        "description": "Пьеса Антона Чехова...",
        "year": 1904,
        "pages": 200,
        "author": authors_map["Антон Чехов"],
        "publisher": publishers_map["Издательство Г"],
        "genres": [genres[2]],  # Роман
    },
    {
        "title": "Мёртвые души",
        "description": "Поэма Николая Гоголя...",
        "year": 1842,
        "pages": 300,
        "author": authors_map["Николай Гоголь"],
        "publisher": publishers_map["Издательство В"],
        "genres": [genres[2], genres[3]],  # Роман, История
    },
    {
        "title": "Отцы и дети",
        "description": "Роман Ивана Тургенева...",
        "year": 1862,
        "pages": 400,
        "author": authors_map["Иван Тургенев"],
        "publisher": publishers_map["Издательство Г"],
        "genres": [genres[2]],  # Роман
    },
    {
        "title": "Убийство в Восточном экспрессе",
        "description": "Детектив Агаты Кристи...",
        "year": 1934,
        "pages": 280,
        "author": authors_map["Агата Кристи"],
        "publisher": publishers_map["Издательство В"],
        "genres": [genres[1]],  # Детектив
    },
    {
        "title": "Песнь льда и пламени",
        "description": "Фэнтези Джорджа Мартина...",
        "year": 1996,
        "pages": 900,
        "author": authors_map["Джордж Мартин"],
        "publisher": publishers_map["Издательство Г"],
        "genres": [genres[4]],  # Фэнтези
    },
    {
        "title": "Властелин колец",
        "description": "Эпическая фэнтези Дж. Р. Р. Толкина...",
        "year": 1954,
        "pages": 1200,
        "author": authors_map["Дж. Р. Р. Толкин"],
        "publisher": publishers_map["Издательство В"],
        "genres": [genres[4]],  # Фэнтези
    },
    {
        "title": "Оно",
        "description": "Роман ужасов Стивена Кинга...",
        "year": 1986,
        "pages": 1100,
        "author": authors_map["Стивен Кинг"],
        "publisher": publishers_map["Издательство Г"],
        "genres": [genres[0]],  # Фантастика
    },
    {
        "title": "Шерлок Холмс: Собрание рассказов",
        "description": "Детективы Артура Конан Дойла...",
        "year": 1892,
        "pages": 600,
        "author": authors_map["Артур Конан Дойл"],
        "publisher": publishers_map["Издательство В"],
        "genres": [genres[1]],  # Детектив
    },
    {
        "title": "Рассказы Эдгара Аллана По",
        "description": "Сборник рассказов Эдгара Аллана По...",
        "year": 1845,
        "pages": 350,
        "author": authors_map["Эдгар Аллан По"],
        "publisher": publishers_map["Издательство Г"],
        "genres": [genres[1], genres[0]],  # Детектив, Фантастика
    }
]

    for bdata in new_books_data:
        book = Book.query.filter_by(title=bdata["title"]).first()
        if not book:
            book = Book(
                title=bdata["title"],
                description=bdata["description"],
                year=bdata["year"],
                pages=bdata["pages"],
                author_id=bdata["author"].id,
                publisher_id=bdata["publisher"].id,
            )
            book.genres = bdata["genres"]
            db.session.add(book)
    db.session.commit()

    print("Дополнительные 10 книг успешно добавлены.")

    for bdata in books_data:
        book = Book.query.filter_by(title=bdata["title"]).first()
        if not book:
            book = Book(
                title=bdata["title"],
                description=bdata["description"],
                year=bdata["year"],
                pages=bdata["pages"],
                author_id=bdata["author"].id,
                publisher_id=bdata["publisher"].id,
            )

            book.genres = bdata["genres"]
            db.session.add(book)
            

    db.session.commit()
    print("Книги успешно добавлены в базу данных.")
