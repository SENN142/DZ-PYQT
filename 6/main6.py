import sys
import sqlite3
import hashlib
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog,
                             QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import uic

# Константы базы данных и картинок
DB_NAME = 'library.db'
PLACEHOLDER_IMAGE = 'no_image.png'  # Картинка, если обложки нет


def init_db():
    """Создает таблицы пользователей и книг, если их еще нет"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Таблица пользователей (логин уникален)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    # Таблица книг
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            image_path TEXT
        )
    ''')
    conn.commit()
    conn.close()


def hash_password(password):
    """Возвращает SHA-256 хеш пароля для безопасного хранения"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class AuthDialog(QDialog):
    """Окно авторизации и регистрации"""

    def __init__(self):
        super().__init__()
        uic.loadUi('auth.ui', self)
        self.setWindowTitle("Авторизация")
        self.is_authorized = False

        self.btn_login.clicked.connect(self.login)
        self.btn_register.clicked.connect(self.register)

    def login(self):
        """Проверка логина и хеша пароля в БД"""
        login = self.line_login.text().strip()
        password = self.line_password.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        pass_hash = hash_password(password)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE login=? AND password_hash=?", (login, pass_hash))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.is_authorized = True
            self.accept()  # Успешный вход, закрываем окно
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль!")

    def register(self):
        """Регистрация нового пользователя с проверкой уникальности логина"""
        login = self.line_login.text().strip()
        password = self.line_password.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля для регистрации!")
            return

        pass_hash = hash_password(password)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (login, password_hash) VALUES (?, ?)", (login, pass_hash))
            conn.commit()
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно! Теперь войдите.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Такой логин уже существует!")
        finally:
            conn.close()


class EditBookDialog(QDialog):
    """Окно для добавления или изменения данных о книге"""

    def __init__(self, parent=None, book_id=None):
        super().__init__(parent)
        uic.loadUi('library_edit.ui', self)
        self.book_id = book_id
        self.image_path = ""

        self.btn_image.clicked.connect(self.choose_image)
        self.btn_save.clicked.connect(self.save_book)

        if self.book_id:
            self.setWindowTitle("Редактирование книги")
            self.load_book_data()
        else:
            self.setWindowTitle("Добавление книги")

    def choose_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите обложку", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            # Требование: сохранять относительный путь, а не саму картинку в БД
            self.image_path = os.path.relpath(file_name)
            self.label_image_path.setText(self.image_path)

    def load_book_data(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, year, genre, image_path FROM books WHERE id=?", (self.book_id,))
        book = cursor.fetchone()
        conn.close()

        if book:
            self.line_title.setText(book[0])
            self.line_author.setText(book[1])
            self.spin_year.setValue(book[2])
            self.line_genre.setText(book[3])
            self.image_path = book[4] if book[4] else ""
            self.label_image_path.setText(self.image_path)

    def save_book(self):
        title = self.line_title.text().strip()
        author = self.line_author.text().strip()
        year = self.spin_year.value()
        genre = self.line_genre.text().strip()

        if not title or not author:
            QMessageBox.warning(self, "Ошибка", "Название и автор обязательны!")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if self.book_id:
            cursor.execute("UPDATE books SET title=?, author=?, year=?, genre=?, image_path=? WHERE id=?",
                           (title, author, year, genre, self.image_path, self.book_id))
        else:
            cursor.execute("INSERT INTO books (title, author, year, genre, image_path) VALUES (?, ?, ?, ?, ?)",
                           (title, author, year, genre, self.image_path))
        conn.commit()
        conn.close()
        self.accept()


class ViewBookDialog(QDialog):
    """Окно просмотра подробной информации о книге и её обложки"""

    def __init__(self, parent=None, book_id=None):
        super().__init__(parent)
        uic.loadUi('library_view.ui', self)
        self.setWindowTitle("Информация о книге")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, year, genre, image_path FROM books WHERE id=?", (book_id,))
        book = cursor.fetchone()
        conn.close()

        if book:
            # Формируем текст
            info = f"<b>Название:</b> {book[0]}<br>" \
                   f"<b>Автор:</b> {book[1]}<br>" \
                   f"<b>Год издания:</b> {book[2]}<br>" \
                   f"<b>Жанр:</b> {book[3]}"
            self.label_info.setText(info)

            # Логика загрузки обложки или стандартной картинки
            img_path = book[4]
            if not img_path or not os.path.exists(img_path):
                img_path = PLACEHOLDER_IMAGE

            pixmap = QPixmap(img_path)
            self.label_image.setPixmap(pixmap)


class LibraryApp(QMainWindow):
    """Главное окно приложения библиотеки"""

    def __init__(self):
        super().__init__()
        uic.loadUi('library_main.ui', self)
        self.setWindowTitle("Каталог библиотеки")

        self.table_books.setColumnCount(5)
        self.table_books.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Год", "Жанр"])
        self.table_books.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.btn_add.clicked.connect(self.add_book)
        self.btn_edit.clicked.connect(self.edit_book)
        self.btn_delete.clicked.connect(self.delete_book)
        self.btn_view.clicked.connect(self.view_book)

        self.btn_search_author.clicked.connect(self.search_by_author)
        self.btn_search_title.clicked.connect(self.search_by_title)

        self.load_data()

    def load_data(self, query="SELECT id, title, author, year, genre FROM books", params=()):
        """Загрузка данных в таблицу с возможностью фильтрации"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        books = cursor.fetchall()
        conn.close()

        self.table_books.setRowCount(len(books))
        for row_idx, row_data in enumerate(books):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table_books.setItem(row_idx, col_idx, item)

    def search_by_author(self):
        author = self.line_search_author.text().strip()
        self.load_data("SELECT id, title, author, year, genre FROM books WHERE author LIKE ?", ('%' + author + '%',))

    def search_by_title(self):
        title = self.line_search_title.text().strip()
        self.load_data("SELECT id, title, author, year, genre FROM books WHERE title LIKE ?", ('%' + title + '%',))

    def add_book(self):
        dialog = EditBookDialog(self)
        if dialog.exec_():
            self.load_data()

    def edit_book(self):
        row = self.table_books.currentRow()
        if row >= 0:
            book_id = int(self.table_books.item(row, 0).text())
            dialog = EditBookDialog(self, book_id)
            if dialog.exec_():
                self.load_data()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для редактирования!")

    def delete_book(self):
        row = self.table_books.currentRow()
        if row >= 0:
            book_id = int(self.table_books.item(row, 0).text())
            title = self.table_books.item(row, 1).text()
            if QMessageBox.question(self, "Удаление", f"Удалить '{title}'?") == QMessageBox.Yes:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
                conn.commit()
                conn.close()
                self.load_data()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для удаления!")

    def view_book(self):
        """Открывает форму просмотра карточки книги"""
        row = self.table_books.currentRow()
        if row >= 0:
            book_id = int(self.table_books.item(row, 0).text())
            dialog = ViewBookDialog(self, book_id)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите книгу для просмотра!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    init_db()  # Инициализируем БД при старте

    # Сначала показываем окно авторизации
    auth = AuthDialog()
    if auth.exec_() and auth.is_authorized:
        # Если авторизация пройдена, открываем главное окно
        window = LibraryApp()
        window.show()
        sys.exit(app.exec_())