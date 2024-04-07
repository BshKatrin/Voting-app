from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsSimpleTextItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor

RADIUS = 20.0


class Node(QGraphicsEllipseItem):
    def __init__(self, x, y, title):
        super().__init__(-RADIUS, -RADIUS, 2 * RADIUS, 2 * RADIUS, None)
        self.radius = RADIUS

        self.setZValue(1)
        self.setBrush(QColor(217, 185, 155))
        self.setPos(QPointF(x, y))

        self.title = QGraphicsSimpleTextItem(self)
        self.title.setText(title)

        width = self.boundingRect().size().width()
        height = self.boundingRect().size().height()
        # print(x, y, self.pos())
        titleOffset = QPointF(-width / 3, -height / 3)
        self.title.setPos(titleOffset)
        # print(self.title.pos())
