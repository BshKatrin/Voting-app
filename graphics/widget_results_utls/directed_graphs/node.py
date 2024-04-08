from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsSimpleTextItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor


class Node(QGraphicsEllipseItem):
    RADIUS = 20.0

    def __init__(self, x, y, title):
        super().__init__(
            -self.RADIUS, -self.RADIUS, 2 * self.RADIUS, 2 * self.RADIUS, None
        )

        self.setZValue(1)
        self.setBrush(QColor(217, 185, 155))
        self.setPos(QPointF(x, y))

        self.title = QGraphicsSimpleTextItem(self)
        self.title.setText(title)

        width = self.boundingRect().size().width()
        height = self.boundingRect().size().height()
        titleOffset = QPointF(-width / 3, -height / 3)
        self.title.setPos(titleOffset)
