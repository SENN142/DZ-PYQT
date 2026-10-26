import sys
import csv
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor
from PyQt5 import uic


class OlympiadApp(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('task1.ui', self)
        self.resize(800, 600)

        # Растягиваем столбцы по ширине таблицы
        self.table_results.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data = []
        self.load_data()

        # Настраиваем комбобоксы
        schools = sorted(list(set(item['school'] for item in self.data)))
        classes = sorted(list(set(item['class'] for item in self.data)))

        self.combo_school.addItem("Все")
        self.combo_school.addItems(schools)

        self.combo_class.addItem("Все")
        self.combo_class.addItems(classes)

        self.combo_school.currentTextChanged.connect(self.update_table)
        self.combo_class.currentTextChanged.connect(self.update_table)

        # Первичная отрисовка таблицы
        self.update_table()

    def load_data(self):
        # Читаем CSV файл
        with open('rez.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Пропускаем заголовки
            for row in reader:
                if len(row) < 8:
                    continue
                login = row[2]
                parts = login.split('-')
                if len(parts) >= 4:
                    school = parts[2]
                    cls = parts[3]
                    try:
                        score = int(row[7])
                    except ValueError:
                        score = 0

                    self.data.append({
                        'login': login,
                        'name': row[1],
                        'score': score,
                        'school': school,
                        'class': cls
                    })

    def update_table(self):
        filter_school = self.combo_school.currentText()
        filter_class = self.combo_class.currentText()

        # Фильтруем данные
        filtered = []
        for item in self.data:
            if filter_school != "Все" and item['school'] != filter_school:
                continue
            if filter_class != "Все" and item['class'] != filter_class:
                continue
            filtered.append(item)

        # Сортируем по убыванию баллов
        filtered.sort(key=lambda x: x['score'], reverse=True)

        # Ищем уникальные баллы для определения 1, 2, 3 мест
        unique_scores = sorted(list(set(x['score'] for x in filtered)), reverse=True)

        # Настраиваем таблицу
        self.table_results.setRowCount(len(filtered))
        self.table_results.setColumnCount(3)
        self.table_results.setHorizontalHeaderLabels(["Логин", "ФИО", "Суммарный балл"])

        # Цвета для призовых мест (Золото, Серебро, Бронза)
        colors = {
            0: QColor(255, 215, 0),
            1: QColor(192, 192, 192),
            2: QColor(205, 127, 50)
        }

        for row, item in enumerate(filtered):
            # Определяем место (индекс балла в отсортированном уникальном списке)
            place_index = unique_scores.index(item['score'])

            login_widget = QTableWidgetItem(item['login'])
            name_widget = QTableWidgetItem(item['name'])
            score_widget = QTableWidgetItem(str(item['score']))

            # Красим строку, если это 1, 2 или 3 место
            if place_index in colors:
                login_widget.setBackground(colors[place_index])
                name_widget.setBackground(colors[place_index])
                score_widget.setBackground(colors[place_index])

            self.table_results.setItem(row, 0, login_widget)
            self.table_results.setItem(row, 1, name_widget)
            self.table_results.setItem(row, 2, score_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OlympiadApp()
    window.show()
    sys.exit(app.exec_())