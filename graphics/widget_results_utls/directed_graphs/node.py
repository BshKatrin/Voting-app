from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsSimpleTextItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor


class Node(QGraphicsEllipseItem):
    """Une classe qui représente un noeud d'un graphe orienté."""

    RADIUS = 40.0

    def __init__(self, x, y, title: str):
        super().__init__(
            -self.RADIUS, -self.RADIUS, 2 * self.RADIUS, 2 * self.RADIUS, None
        )
        # Scene will take ownership

        self.setZValue(1)
        self.setBrush(QColor(217, 185, 155))
        self.setPos(QPointF(x, y))

        self.title = QGraphicsSimpleTextItem(self)

        self.title.setText(title.replace(' ', '\n', 1))

        width = self.boundingRect().size().width()
        height = self.boundingRect().size().height()
        titleOffset = QPointF(-width / 3, -height / 3)
        self.title.setPos(titleOffset)

    def highlight(self):
        self.setBrush(QColor(250, 128, 114))
