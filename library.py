"""
Система управления библиотекой
Демонстрирует принципы ООП: классы, инкапсуляция, полиморфизм.
Используются только стандартные исключения (ValueError, RuntimeError).
"""

from datetime import datetime


class Book:
    """Представляет книгу в библиотеке."""

    def __init__(self, title: str, author: str, isbn: str, year: int):
        self._title = title
        self._author = author
        self._isbn = isbn
        self._year = year
        self._is_borrowed = False
        self._borrowed_by: str | None = None
        self._borrowed_date: datetime | None = None

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def year(self) -> int:
        return self._year

    @property
    def is_borrowed(self) -> bool:
        return self._is_borrowed

    def borrow(self, user_id: str) -> None:
        """Отметить книгу как взятую пользователем."""
        if self._is_borrowed:
            raise RuntimeError(
                f"Книга '{self._title}' (ISBN: {self._isbn}) уже взята."
            )
        self._is_borrowed = True
        self._borrowed_by = user_id
        self._borrowed_date = datetime.now()

    def return_book(self) -> None:
        """Отметить книгу как возвращённую."""
        if not self._is_borrowed:
            return
        self._is_borrowed = False
        self._borrowed_by = None
        self._borrowed_date = None

    def get_borrow_info(self) -> dict:
        """Вернуть информацию о взятии книги, если она взята."""
        if self._is_borrowed:
            return {
                "borrowed_by": self._borrowed_by,
                "borrowed_date": self._borrowed_date,
            }
        return {}

    def __str__(self) -> str:
        status = "Взята" if self._is_borrowed else "Доступна"
        return f"'{self.title}' автора {self.author} ({self.year}) - {status}"

    def __repr__(self) -> str:
        return f"Book(title='{self.title}', author='{self.author}', isbn='{self.isbn}', year={self.year})"


class User:
    """Представляет пользователя библиотеки."""

    def __init__(self, name: str, user_id: str):
        self._name = name
        self._user_id = user_id
        self._borrowed_isbns: list[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def borrowed_isbns(self) -> list[str]:
        return self._borrowed_isbns.copy()

    def borrow_book(self, isbn: str) -> None:
        if isbn in self._borrowed_isbns:
            raise RuntimeError(
                f"Пользователь '{self._user_id}' уже взял книгу с ISBN {isbn}"
            )
        self._borrowed_isbns.append(isbn)

    def return_book(self, isbn: str) -> None:
        if isbn not in self._borrowed_isbns:
            raise ValueError(
                f"Пользователь '{self._user_id}' не брал книгу с ISBN {isbn}."
            )
        self._borrowed_isbns.remove(isbn)

    def __str__(self) -> str:
        return f"Пользователь: {self.name} (ID: {self.user_id})"

    def __repr__(self) -> str:
        return f"User(name='{self.name}', user_id='{self.user_id}')"


class Library:
    """Главная система библиотеки, управляющая книгами и пользователями."""

    def __init__(self, name: str = "Городская библиотека"):
        self._name = name
        self._books: dict[str, Book] = {}
        self._users: dict[str, User] = {}

    @property
    def name(self) -> str:
        return self._name

    # ---------- Управление книгами ----------
    def add_book(self, book: Book) -> None:
        if book.isbn in self._books:
            raise ValueError(f"Книга с ISBN {book.isbn} уже существует.")
        self._books[book.isbn] = book

    def remove_book(self, isbn: str) -> None:
        book = self._get_book_by_isbn(isbn)
        if book.is_borrowed:
            raise RuntimeError(
                f"Нельзя удалить взятую книгу '{book.title}' (ISBN: {isbn})"
            )
        del self._books[isbn]

    def _get_book_by_isbn(self, isbn: str) -> Book:
        if isbn not in self._books:
            raise ValueError(f"Книга с ISBN {isbn} не найдена.")
        return self._books[isbn]

    # ---------- Управление пользователями ----------
    def register_user(self, user: User) -> None:
        if user.user_id in self._users:
            raise ValueError(f"Пользователь с ID {user.user_id} уже существует.")
        self._users[user.user_id] = user

    def unregister_user(self, user_id: str) -> None:
        user = self._get_user_by_id(user_id)
        if user.borrowed_isbns:
            raise RuntimeError(
                f"Нельзя удалить пользователя '{user_id}' — у него всё ещё {len(user.borrowed_isbns)} взятых книг."
            )
        del self._users[user_id]

    def _get_user_by_id(self, user_id: str) -> User:
        if user_id not in self._users:
            raise ValueError(f"Пользователь с ID {user_id} не найден.")
        return self._users[user_id]

    # ---------- Выдача и возврат книг ----------
    def borrow_book(self, user_id: str, isbn: str) -> None:
        user = self._get_user_by_id(user_id)
        book = self._get_book_by_isbn(isbn)

        if book.is_borrowed:
            raise RuntimeError(
                f"Книга '{book.title}' (ISBN: {isbn}) уже взята другим пользователем."
            )

        if isbn in user.borrowed_isbns:
            raise RuntimeError(
                f"Пользователь {user_id} уже взял книгу '{book.title}'"
            )

        book.borrow(user_id)
        user.borrow_book(isbn)

    def return_book(self, user_id: str, isbn: str) -> None:
        user = self._get_user_by_id(user_id)
        book = self._get_book_by_isbn(isbn)

        if not book.is_borrowed:
            raise RuntimeError(
                f"Книга '{book.title}' (ISBN: {isbn}) не была взята."
            )

        if book._borrowed_by != user_id:
            raise RuntimeError(
                f"Книга '{book.title}' взята другим пользователем, не {user_id}."
            )

        book.return_book()
        user.return_book(isbn)

    # ---------- Поиск и запросы ----------
    def search_books(self, query: str, by: str = "title") -> list[Book]:
        results = []
        query_lower = query.lower()
        for book in self._books.values():
            if by == "title" and query_lower in book.title.lower():
                results.append(book)
            elif by == "author" and query_lower in book.author.lower():
                results.append(book)
            elif by == "isbn" and query_lower == book.isbn.lower():
                results.append(book)
        return results

    def get_all_books(self) -> list[Book]:
        return list(self._books.values())

    def get_available_books(self) -> list[Book]:
        return [book for book in self._books.values() if not book.is_borrowed]

    def get_borrowed_books(self) -> list[Book]:
        return [book for book in self._books.values() if book.is_borrowed]

    def get_user_borrowed_books(self, user_id: str) -> list[Book]:
        user = self._get_user_by_id(user_id)
        borrowed_books = []
        for isbn in user.borrowed_isbns:
            book = self._get_book_by_isbn(isbn)
            borrowed_books.append(book)
        return borrowed_books

    def __str__(self) -> str:
        return f"Библиотека '{self.name}': {len(self._books)} книг, {len(self._users)} пользователей"