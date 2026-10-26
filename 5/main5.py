import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import uic
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class UFOApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('task5.ui', self)

        self.setWindowTitle("Управление НЛО")
        self.resize(600, 600)  # Размер космоса (окна)

        # Фиксированное расстояние (шаг) перемещения в пикселях
        self.step = 20

    def keyPressEvent(self, event):
        """
        Обработка нажатий клавиатуры для управления НЛО.
        """
        # Получаем текущие координаты НЛО
        x = self.label_ufo.x()
        y = self.label_ufo.y()

        # Получаем размеры самой картинки НЛО
        ufo_width = self.label_ufo.width()
        ufo_height = self.label_ufo.height()

        # Получаем текущие размеры окна
        win_width = self.width()
        win_height = self.height()

        # Меняем координаты в зависимости от нажатой стрелки
        if event.key() == Qt.Key_Left:
            x -= self.step
        elif event.key() == Qt.Key_Right:
            x += self.step
        elif event.key() == Qt.Key_Up:
            y -= self.step
        elif event.key() == Qt.Key_Down:
            y += self.step

        # --- ЛОГИКА ТЕЛЕПОРТАЦИИ ПРИ ВЫХОДЕ ЗА ЭКРАН ---
        # Если улетели вправо за экран -> появляемся слева
        if x > win_width:
            x = -ufo_width
        # Если улетели влево -> появляемся справа
        elif x < -ufo_width:
            x = win_width

        # Если улетели вниз -> появляемся сверху
        if y > win_height:
            y = -ufo_height
        # Если улетели вверх -> появляемся снизу
        elif y < -ufo_height:
            y = win_height

        # Применяем новые координаты к виджету
        self.label_ufo.move(x, y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UFOApp()
    window.show()
    sys.exit(app.exec_())