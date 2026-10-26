import sys
import sqlite3
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog,
                             QTableWidgetItem, QMessageBox, QHeaderView)
from PyQt5 import uic
from PyQt5.QtCore import Qt


class EditFilmDialog(QDialog):
    """
    Класс второго окна (диалога) для добавления и редактирования фильма.
    """

    def __init__(self, parent=None, film_id=None):
        super().__init__(parent)
        # Загружаем интерфейс окна редактирования
        uic.loadUi('task2_edit.ui', self)

        # Сохраняем ID фильма. Если он None - значит мы добавляем новый фильм.
        # Если ID передан - значит мы редактируем существующий.
        self.film_id = film_id

        # Словарь для связи названия жанра и его ID в базе данных
        self.genre_dict = {}

        self.load_genres()  # Загружаем жанры в выпадающий список
        self.btn_save.clicked.connect(self.save_data)

        # Если передан ID фильма, загружаем его текущие данные в поля ввода
        if self.film_id is not None:
            self.setWindowTitle("Редактирование фильма")
            self.load_film_data()
        else:
            self.setWindowTitle("Добавление фильма")

    def load_genres(self):
        """Загружает названия жанров из БД в ComboBox"""
        conn = sqlite3.connect('films_db.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM genres")

        for genre_id, title in cursor.fetchall():
            self.combo_genre.addItem(title)
            self.genre_dict[title] = genre_id  # Запоминаем ID каждого жанра

        conn.close()

    def load_film_data(self):
        """Загружает данные выбранного фильма для редактирования"""
        conn = sqlite3.connect('films_db.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT title, year, genre, duration FROM films WHERE id=?", (self.film_id,))
        film = cursor.fetchone()
        conn.close()

        if film:
            # Распределяем полученные данные по виджетам
            self.line_title.setText(film[0])
            self.spin_year.setValue(film[1])
            self.spin_duration.setValue(film[3])

            # Находим нужное текстовое название жанра по его ID и ставим в ComboBox
            for title, g_id in self.genre_dict.items():
                if g_id == film[2]:
                    self.combo_genre.setCurrentText(title)
                    break

    def save_data(self):
        """Проверяет введенные данные (валидация) и сохраняет их в БД"""
        title = self.line_title.text().strip()
        year = self.spin_year.value()
        duration = self.spin_duration.value()
        genre_id = self.genre_dict[self.combo_genre.currentText()]

        # --- ВАЛИДАЦИЯ И ОШИБКИ (По заданию) ---
        if not title:
            QMessageBox.warning(self, "Ошибка", "Название фильма не может быть пустым!")
            return

        current_year = datetime.datetime.now().year
        if year > current_year:
            QMessageBox.warning(self, "Ошибка", f"Год выпуска не может быть больше текущего ({current_year})!")
            return

        if duration <= 0:
            QMessageBox.warning(self, "Ошибка", "Продолжительность фильма должна быть больше 0!")
            return
        # ---------------------------------------

        conn = sqlite3.connect('films_db.sqlite')
        cursor = conn.cursor()

        # Если есть ID - обновляем запись (UPDATE), иначе добавляем новую (INSERT)
        if self.film_id:
            cursor.execute("""
                UPDATE films 
                SET title=?, year=?, genre=?, duration=? 
                WHERE id=?
            """, (title, year, genre_id, duration, self.film_id))
        else:
            cursor.execute("""
                INSERT INTO films (title, year, genre, duration) 
                VALUES (?, ?, ?, ?)
            """, (title, year, genre_id, duration))

        conn.commit()
        conn.close()

        # Закрываем окно с успешным статусом
        self.accept()


class FilmsApp(QMainWindow):
    """
    Главное окно приложения с таблицей фильмов.
    """

    def __init__(self):
        super().__init__()
        # Загружаем интерфейс главного окна
        uic.loadUi('task2_main.ui', self)
        self.setWindowTitle("База данных фильмов")

        # Растягиваем столбцы таблицы по ширине окна
        self.table_films.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Подключаем кнопки к методам
        self.btn_add.clicked.connect(self.add_film)
        self.btn_edit.clicked.connect(self.edit_film)
        self.btn_delete.clicked.connect(self.delete_film)

        # Загружаем данные в таблицу при старте
        self.update_table()

    def update_table(self):
        """Читает данные из БД и заполняет QTableWidget"""
        conn = sqlite3.connect('films_db.sqlite')
        cursor = conn.cursor()

        # SQL-запрос объединяет таблицу фильмов и жанров (чтобы вывести текст жанра, а не цифру)
        query = """
            SELECT films.id, films.title, films.year, genres.title AS genre_name, films.duration 
            FROM films 
            LEFT JOIN genres ON films.genre = genres.id
        """
        cursor.execute(query)
        data = cursor.fetchall()

        # --- ТРЕБОВАНИЕ ЗАДАНИЯ ---
        # "Названия полей должны получаться непосредственно из базы данных (параметры курсора)"
        # cursor.description содержит информацию о колонках после выполнения запроса
        column_names = [description[0] for description in cursor.description]

        self.table_films.setRowCount(len(data))
        self.table_films.setColumnCount(len(column_names))
        self.table_films.setHorizontalHeaderLabels(column_names)

        # Заполняем ячейки таблицы
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                # Делаем ячейки доступными только для чтения
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table_films.setItem(row_idx, col_idx, item)

        conn.close()

    def add_film(self):
        """Открывает диалог для добавления фильма"""
        dialog = EditFilmDialog(self)
        if dialog.exec_():  # Если данные успешно сохранены
            self.update_table()  # Обновляем таблицу

    def edit_film(self):
        """Открывает диалог для изменения выбранного фильма"""
        row = self.table_films.currentRow()
        # Проверка на то, что строка выделена (Требование задания)
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите фильм в таблице для редактирования!")
            return

        # Получаем ID фильма из первого столбца (индекс 0) выделенной строки
        film_id = int(self.table_films.item(row, 0).text())
        dialog = EditFilmDialog(self, film_id)
        if dialog.exec_():
            self.update_table()

    def delete_film(self):
        """Удаляет выбранный фильм из БД"""
        row = self.table_films.currentRow()
        # Проверка на то, что строка выделена (Требование задания)
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите фильм в таблице для удаления!")
            return

        film_title = self.table_films.item(row, 1).text()
        film_id = int(self.table_films.item(row, 0).text())

        # Окно подтверждения удаления
        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Вы действительно хотите удалить фильм '{film_title}'?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            conn = sqlite3.connect('films_db.sqlite')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM films WHERE id=?", (film_id,))
            conn.commit()
            conn.close()
            self.update_table()  # Обновляем таблицу после удаления


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FilmsApp()
    window.show()
    sys.exit(app.exec_())