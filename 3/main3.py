import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QColor, QPolygon
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import uic


class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('task3.ui', self)

        # Устанавливаем произвольный размер формы
        self.resize(800, 600)
        self.setWindowTitle("Рисовалка фигур")

        # Список для хранения координат, цветов и размеров всех нарисованных фигур
        self.shapes = []

    def get_random_color(self):
        """Генерирует случайный цвет (R, G, B)"""
        return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def get_random_size(self):
        """Генерирует случайный размер от 20 до 150 пикселей"""
        return random.randint(20, 150)

    def mousePressEvent(self, event):
        """Обработка кликов мыши для рисования круга и квадрата"""
        x = event.x()
        y = event.y()

        if event.button() == Qt.LeftButton:
            # Требование: левая кнопка - круг[cite: 11]
            self.shapes.append({
                'type': 'circle',
                'x': x, 'y': y,
                'color': self.get_random_color(),
                'size': self.get_random_size()
            })
        elif event.button() == Qt.RightButton:
            # Требование: правая кнопка - квадрат[cite: 11]
            self.shapes.append({
                'type': 'square',
                'x': x, 'y': y,
                'color': self.get_random_color(),
                'size': self.get_random_size()
            })

        # Даем команду окну перерисовать интерфейс (вызывает paintEvent)
        self.update()

    def keyPressEvent(self, event):
        """Обработка нажатий клавиатуры для рисования треугольника"""
        if event.key() == Qt.Key_Space:
            # Требование: Пробел рисует треугольник там, где сейчас курсор[cite: 11]

            # Получаем координаты мыши относительно текущего окна
            mouse_pos = self.mapFromGlobal(self.cursor().pos())

            self.shapes.append({
                'type': 'triangle',
                'x': mouse_pos.x(),
                'y': mouse_pos.y(),
                'color': self.get_random_color(),
                'size': self.get_random_size()
            })
            self.update()

    def paintEvent(self, event):
        """Встроенный метод, который отрисовывает фигуры на экране"""
        painter = QPainter(self)

        # Перебираем все сохраненные фигуры и рисуем их
        for shape in self.shapes:
            painter.setBrush(shape['color'])  # Устанавливаем цвет заливки
            painter.setPen(Qt.NoPen)  # Убираем черную обводку

            x = shape['x']
            y = shape['y']
            size = shape['size']
            half = size // 2

            if shape['type'] == 'circle':
                # Смещаем на half, чтобы центр круга был ровно под курсором
                painter.drawEllipse(x - half, y - half, size, size)

            elif shape['type'] == 'square':
                painter.drawRect(x - half, y - half, size, size)

            elif shape['type'] == 'triangle':
                # Треугольник рисуется по трем точкам с помощью QPolygon
                points = [
                    QPoint(x, y - half),  # Верхний угол
                    QPoint(x - half, y + half),  # Левый нижний угол
                    QPoint(x + half, y + half)  # Правый нижний угол
                ]
                painter.drawPolygon(QPolygon(points))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec_())