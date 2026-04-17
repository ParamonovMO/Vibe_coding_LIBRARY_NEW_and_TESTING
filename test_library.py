"""
Pytest тесты с Allure для системы управления библиотекой.
"""

import pytest
import allure
from datetime import datetime
from library import Book, User, Library  # импорты для классов, если нужны явно


# ---------- Тесты для книги ----------
@allure.feature("Управление книгами")
@allure.story("Создание и просмотр книг")
@allure.title("Создание книги")
def test_book_creation(sample_book):
    with allure.step("Проверка атрибутов книги"):
        assert sample_book.title == "Чистый код"
        assert sample_book.author == "Роберт Мартин"
        assert sample_book.isbn == "978-0132350884"
        assert sample_book.year == 2008
        assert not sample_book.is_borrowed
        assert sample_book.get_borrow_info() == {}


@allure.feature("Управление книгами")
@allure.story("Выдача книги")
@allure.title("Взять книгу успешно")
def test_book_borrow(sample_book):
    with allure.step("Выдача книги пользователю"):
        sample_book.borrow("U001")
    with allure.step("Проверка состояния"):
        assert sample_book.is_borrowed
        info = sample_book.get_borrow_info()
        assert info["borrowed_by"] == "U001"
        assert isinstance(info["borrowed_date"], datetime)


@allure.feature("Управление книгами")
@allure.story("Выдача книги")
@allure.title("Нельзя взять уже взятую книгу")
def test_book_borrow_twice_raises_error(sample_book):
    sample_book.borrow("U001")
    with allure.step("Попытка взять снова"):
        with pytest.raises(RuntimeError, match="уже взята"):
            sample_book.borrow("U002")


@allure.feature("Управление книгами")
@allure.story("Возврат книги")
@allure.title("Вернуть взятую книгу")
def test_book_return(sample_book):
    sample_book.borrow("U001")
    sample_book.return_book()
    assert not sample_book.is_borrowed
    assert sample_book.get_borrow_info() == {}


@allure.feature("Управление книгами")
@allure.story("Возврат книги")
@allure.title("Возврат доступной книги ничего не делает")
def test_book_return_when_available_does_nothing(sample_book):
    sample_book.return_book()
    assert not sample_book.is_borrowed


# ---------- Тесты для пользователя ----------
@allure.feature("Управление пользователями")
@allure.story("Регистрация и выдача")
@allure.title("Создание пользователя")
def test_user_creation(sample_user):
    assert sample_user.name == "Алиса Иванова"
    assert sample_user.user_id == "U001"
    assert sample_user.borrowed_isbns == []


@allure.feature("Управление пользователями")
@allure.story("Выдача пользователю")
@allure.title("Пользователь берёт книгу")
def test_user_borrow_book(sample_user):
    sample_user.borrow_book("ISBN123")
    assert "ISBN123" in sample_user.borrowed_isbns


@allure.feature("Управление пользователями")
@allure.story("Выдача пользователю")
@allure.title("Пользователь не может взять ту же книгу дважды")
def test_user_borrow_same_book_twice_raises(sample_user):
    sample_user.borrow_book("ISBN123")
    with pytest.raises(RuntimeError, match="уже взял"):
        sample_user.borrow_book("ISBN123")


@allure.feature("Управление пользователями")
@allure.story("Возврат пользователем")
@allure.title("Пользователь возвращает книгу")
def test_user_return_book(sample_user):
    sample_user.borrow_book("ISBN123")
    sample_user.return_book("ISBN123")
    assert sample_user.borrowed_isbns == []


@allure.feature("Управление пользователями")
@allure.story("Возврат пользователем")
@allure.title("Нельзя вернуть книгу, которую не брал")
def test_user_return_not_borrowed_raises(sample_user):
    with pytest.raises(ValueError, match="не брал"):
        sample_user.return_book("ISBN999")


# ---------- Тесты библиотеки ----------
@allure.feature("Система библиотеки")
@allure.story("Добавление/удаление книг")
@allure.title("Добавить книгу в библиотеку")
def test_add_book(library_with_books, sample_book):
    with allure.step("Попытка добавить дубликат"):
        with pytest.raises(ValueError, match="уже существует"):
            library_with_books.add_book(sample_book)

    with allure.step("Добавление новой книги"):
        new_book = Book("Новая книга", "Новый автор", "999-999", 2022)
        library_with_books.add_book(new_book)
        assert len(library_with_books.get_all_books()) == 3


@allure.feature("Система библиотеки")
@allure.story("Добавление/удаление книг")
@allure.title("Удалить книгу из библиотеки")
def test_remove_book(library_with_books, sample_book):
    library_with_books.remove_book(sample_book.isbn)
    assert sample_book.isbn not in [b.isbn for b in library_with_books.get_all_books()]


@allure.feature("Система библиотеки")
@allure.story("Добавление/удаление книг")
@allure.title("Удаление несуществующей книги вызывает ошибку")
def test_remove_nonexistent_book_raises(library_with_books):
    with pytest.raises(ValueError, match="не найдена"):
        library_with_books.remove_book("INVALID-ISBN")


@allure.feature("Система библиотеки")
@allure.story("Добавление/удаление книг")
@allure.title("Нельзя удалить взятую книгу")
def test_remove_borrowed_book_raises(library_with_books, sample_book, sample_user):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    with pytest.raises(RuntimeError, match="Нельзя удалить взятую книгу"):
        library_with_books.remove_book(sample_book.isbn)


@allure.feature("Система библиотеки")
@allure.story("Регистрация пользователей")
@allure.title("Зарегистрировать нового пользователя")
def test_register_user(library_with_books, another_user):
    library_with_books.register_user(another_user)
    assert another_user.user_id in library_with_books._users


@allure.feature("Система библиотеки")
@allure.story("Регистрация пользователей")
@allure.title("Регистрация дубликата вызывает ошибку")
def test_register_duplicate_user_raises(library_with_books, sample_user):
    with pytest.raises(ValueError, match="уже существует"):
        library_with_books.register_user(sample_user)


@allure.feature("Система библиотеки")
@allure.story("Удаление пользователей")
@allure.title("Удалить пользователя без книг")
def test_unregister_user(library_with_books, sample_user):
    library_with_books.unregister_user(sample_user.user_id)
    with pytest.raises(ValueError, match="не найден"):
        library_with_books._get_user_by_id(sample_user.user_id)


@allure.feature("Система библиотеки")
@allure.story("Удаление пользователей")
@allure.title("Нельзя удалить пользователя с взятыми книгами")
def test_unregister_user_with_borrowed_books_raises(library_with_books, sample_user, sample_book):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    with pytest.raises(RuntimeError, match="Нельзя удалить.*всё ещё"):
        library_with_books.unregister_user(sample_user.user_id)


@allure.feature("Система библиотеки")
@allure.story("Выдача/возврат")
@allure.title("Выдать книгу успешно")
def test_borrow_book_success(library_with_books, sample_user, sample_book):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    assert sample_book.is_borrowed
    assert sample_book.isbn in sample_user.borrowed_isbns
    assert sample_book in library_with_books.get_borrowed_books()
    assert sample_book not in library_with_books.get_available_books()


@allure.feature("Система библиотеки")
@allure.story("Выдача/возврат")
@allure.title("Нельзя выдать уже выданную книгу")
def test_borrow_unavailable_book_raises(library_with_books, sample_user, another_user, sample_book):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    with pytest.raises(RuntimeError, match="уже взята другим"):
        library_with_books.borrow_book(another_user.user_id, sample_book.isbn)


@allure.feature("Система библиотеки")
@allure.story("Выдача/возврат")
@allure.title("Нельзя выдать несуществующую книгу")
def test_borrow_nonexistent_book_raises(library_with_books, sample_user):
    with pytest.raises(ValueError, match="не найдена"):
        library_with_books.borrow_book(sample_user.user_id, "INVALID-ISBN")


@allure.feature("Система библиотеки")
@allure.story("Выдача/возврат")
@allure.title("Нельзя выдать одну книгу дважды одному пользователю")
def test_borrow_twice_by_same_user_raises(library_with_books, sample_user, sample_book):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    with pytest.raises(RuntimeError, match="уже взял"):
        library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)


@allure.feature("Система библиотеки")
@allure.story("Выдача/возврат")
@allure.title("Вернуть книгу успешно")
def test_return_book_success(library_with_books, sample_user, sample_book):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    library_with_books.return_book(sample_user.user_id, sample_book.isbn)
    assert not sample_book.is_borrowed
    assert sample_book.isbn not in sample_user.borrowed_isbns
    assert sample_book in library_with_books.get_available_books()


@allure.feature("Система библиотеки")
@allure.story("Выдача/возврат")
@allure.title("Нельзя вернуть книгу, которая не была взята")
def test_return_book_not_borrowed_raises(library_with_books, sample_user, sample_book):
    with pytest.raises(RuntimeError, match="не была взята"):
        library_with_books.return_book(sample_user.user_id, sample_book.isbn)


@allure.feature("Система библиотеки")
@allure.story("Выдача/возврат")
@allure.title("Нельзя вернуть книгу, взятую другим пользователем")
def test_return_book_wrong_user_raises(library_with_books, sample_user, another_user, sample_book):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    with pytest.raises(RuntimeError, match="взята другим пользователем"):
        library_with_books.return_book(another_user.user_id, sample_book.isbn)


@allure.feature("Система библиотеки")
@allure.story("Поиск")
@allure.title("Поиск книг по названию")
def test_search_books_by_title(library_with_books, sample_book, another_book):
    results = library_with_books.search_books("чистый", by="title")
    assert sample_book in results
    assert another_book not in results

    results = library_with_books.search_books("прагматик", by="title")
    assert another_book in results
    assert sample_book not in results


@allure.feature("Система библиотеки")
@allure.story("Поиск")
@allure.title("Поиск книг по автору")
def test_search_books_by_author(library_with_books, sample_book, another_book):
    results = library_with_books.search_books("мартин", by="author")
    assert sample_book in results
    assert another_book not in results

    results = library_with_books.search_books("томас", by="author")
    assert another_book in results
    assert sample_book not in results


@allure.feature("Система библиотеки")
@allure.story("Поиск")
@allure.title("Поиск книг по ISBN")
def test_search_books_by_isbn(library_with_books, sample_book):
    results = library_with_books.search_books(sample_book.isbn, by="isbn")
    assert len(results) == 1
    assert results[0] == sample_book


@allure.feature("Система библиотеки")
@allure.story("Запросы")
@allure.title("Получить доступные книги")
def test_get_available_books(library_with_books, sample_book, another_book, sample_user):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    available = library_with_books.get_available_books()
    assert another_book in available
    assert sample_book not in available


@allure.feature("Система библиотеки")
@allure.story("Запросы")
@allure.title("Получить взятые книги")
def test_get_borrowed_books(library_with_books, sample_book, another_book, sample_user):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    borrowed = library_with_books.get_borrowed_books()
    assert sample_book in borrowed
    assert another_book not in borrowed


@allure.feature("Система библиотеки")
@allure.story("Запросы")
@allure.title("Получить книги, взятые конкретным пользователем")
def test_get_user_borrowed_books(library_with_books, sample_user, sample_book, another_book):
    library_with_books.borrow_book(sample_user.user_id, sample_book.isbn)
    user_books = library_with_books.get_user_borrowed_books(sample_user.user_id)
    assert sample_book in user_books
    assert another_book not in user_books


@allure.feature("Система библиотеки")
@allure.story("Запросы")
@allure.title("Пользователь без взятых книг возвращает пустой список")
def test_get_user_borrowed_books_none(library_with_books, sample_user):
    user_books = library_with_books.get_user_borrowed_books(sample_user.user_id)
    assert user_books == []


@allure.feature("Система библиотеки")
@allure.story("Вспомогательное")
@allure.title("Строковое представление библиотеки")
def test_library_string_representation(library_with_books):
    assert "Тестовая библиотека" in str(library_with_books)
    assert "2 книг" in str(library_with_books)
    assert "1 пользователей" in str(library_with_books)


# ---------- Тест с использованием пустой библиотеки (фикстура из conftest) ----------
@allure.feature("Система библиотеки")
@allure.story("Пустая библиотека")
@allure.title("Пустая библиотека имеет 0 книг и 0 пользователей")
def test_empty_library(empty_library):
    assert len(empty_library.get_all_books()) == 0
    assert len(empty_library._users) == 0