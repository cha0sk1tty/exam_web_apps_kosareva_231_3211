import hashlib
from app import create_app, db
from app.models import Book, Cover

def generate_md5(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def create_covers_for_all_books():
    app = create_app()
    with app.app_context():
        books = Book.query.all()
        for book in books:
            # Формируем имя файла, например, "book_id.jpg"
            filename = f"{book.id}.jpg"
            mime_type = "image/jpeg"
            md5_hash = generate_md5(filename)  # Для примера хэш от имени файла

            # Проверяем, есть ли уже обложка у книги
            existing_cover = Cover.query.filter_by(book_id=book.id).first()
            if existing_cover:
                print(f"Обложка для книги id={book.id} уже существует, пропускаем.")
                continue

            # Создаем новую запись
            cover = Cover(
                filename=filename,
                mime_type=mime_type,
                md5_hash=md5_hash,
                book_id=book.id
            )
            db.session.add(cover)
            print(f"Добавляю обложку для книги id={book.id} filename={filename}")

        db.session.commit()
        print("Все обложки созданы и сохранены.")

if __name__ == "__main__":
    create_covers_for_all_books()
