from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsSimpleTextItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor


class Node(QGraphicsEllipseItem):
    """A class which represents a node of the oriented graph."""

    RADIUS:float = 40.0
    """A node's radius."""

    def __init__(self, x:float, y:float, title: str):
        """Initialize the node of the oriented graph.

        Args:
            x (float): A horizontal coordinate in the computer coordinate system.
            y (float): A vertical coordinate in the computer coordinate system.
            title (str): A text to put inside the node.
        """

        # Scene will take ownership
        super().__init__(-self.RADIUS, -self.RADIUS, 2 * self.RADIUS, 2 * self.RADIUS, None) 
        

        self.setZValue(1)
        self.setBrush(QColor(217, 185, 155))
        self.setPos(QPointF(x, y))

        self.title = QGraphicsSimpleTextItem(self)

        self.title.setText(title.replace(' ', '\n', 1))

        width = self.boundingRect().size().width()
        height = self.boundingRect().size().height()

        titleOffset = QPointF(-width / 3, -height / 3)
        self.title.setPos(titleOffset)

    def highlight(self) -> None:
        """Change the node's color to the pale green."""

        self.setBrush(QColor(152,251,152))
