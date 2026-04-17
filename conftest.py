"""
Конфигурация pytest и настройка Allure.
Содержит все фикстуры для тестов.
"""

import pytest
from library import Book, User, Library


def pytest_configure(config):
    """Настройка окружения Allure."""
    config.option.allure_report_dir = "./allure-results"


# ----- Простая фикстура -----
@pytest.fixture
def empty_library():
    """Создаёт пустую библиотеку (без книг и пользователей)."""
    return Library("Пустая библиотека")


# ----- Фикстуры для книг -----
@pytest.fixture
def sample_book():
    """Фикстура: образец книги на русском."""
    return Book("Чистый код", "Роберт Мартин", "978-0132350884", 2008)


@pytest.fixture
def another_book():
    """Фикстура: другая книга на русском."""
    return Book("Программист-прагматик", "Дэвид Томас", "978-0201616224", 1999)


# ----- Фикстуры для пользователей -----
@pytest.fixture
def sample_user():
    """Фикстура: образец пользователя."""
    return User("Алиса Иванова", "U001")


@pytest.fixture
def another_user():
    """Фикстура: другой пользователь."""
    return User("Борис Петров", "U002")


# ----- Составная фикстура: библиотека с книгами и пользователем -----
@pytest.fixture
def library_with_books(sample_book, another_book, sample_user):
    """Фикстура: библиотека с двумя книгами и одним пользователем."""
    lib = Library("Тестовая библиотека")
    lib.add_book(sample_book)
    lib.add_book(another_book)
    lib.register_user(sample_user)
    return lib