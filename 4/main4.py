import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QEvent
from PyQt5 import uic


class RunawayApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загружаем интерфейс
        uic.loadUi('task4.ui', self)

        self.setWindowTitle("Убегающая кнопка")
        self.resize(600, 400)  # Задаем начальный размер окна

        # Устанавливаем "фильтр событий" на нашу кнопку.
        # Это заставит программу пропускать все действия над кнопкой через метод eventFilter.
        self.btn_runaway.installEventFilter(self)

    def eventFilter(self, obj, event):
        """
        Этот метод перехватывает события.
        Мы ищем момент, когда курсор наводится на кнопку.
        """
        # Проверяем, что событие произошло именно с кнопкой btn_runaway
        # И что тип события - Enter (курсор мыши вошел в зону виджета)
        if obj == self.btn_runaway and event.type() == QEvent.Enter:
            self.move_button_away()
            return True  # Сообщаем системе, что мы обработали это событие

        # Остальные события (клики, отрисовка и т.д.) пропускаем как обычно
        return super().eventFilter(obj, event)

    def move_button_away(self):
        """
        Вычисляет новые случайные координаты и перемещает кнопку,
        учитывая текущие размеры окна, чтобы она не улетела за край.
        """
        # Получаем текущие размеры окна
        window_width = self.width()
        window_height = self.height()

        # Получаем размеры самой кнопки
        btn_width = self.btn_runaway.width()
        btn_height = self.btn_runaway.height()

        # Вычисляем максимально возможные координаты X и Y для левого верхнего угла кнопки,
        # чтобы ее правый и нижний края не вышли за границы окна.
        max_x = window_width - btn_width
        max_y = window_height - btn_height

        # Генерируем новые случайные координаты в безопасном диапазоне
        new_x = random.randint(0, max_x)
        new_y = random.randint(0, max_y)

        # Перемещаем кнопку на новые координаты
        self.btn_runaway.move(new_x, new_y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RunawayApp()
    window.show()
    sys.exit(app.exec_())