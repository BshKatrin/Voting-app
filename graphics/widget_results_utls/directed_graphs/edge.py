from math import sin, cos, pi, sqrt, atan2


from PySide6.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsSimpleTextItem,
    QGraphicsPolygonItem,
)
from PySide6.QtGui import QPen, QColor, QPolygonF, QPainterPath
from PySide6.QtCore import Qt, QPointF


class Edge(QGraphicsPathItem):
    """A class which represents an edge of the oriented graph."""

    def __init__(self, painter_path: QPainterPath, start_point: QPointF, end_point: QPointF):
        """Initialize the black edge. Is it an arrow pointing from `start_point` to `end_point`.
        
        Args:
            painter_path (PySide6.QtGui.QPainterPath): The painter which will draw the edge.
            start_point (PySide6.QtCore.QPointF): Edge's starting point.
            end_point (PySide6.QtCore.QPointF): Edge's ending point.
        """
        
        super().__init__(painter_path, None)  # Scene will take ownership

        self.setPen(QPen(Qt.black, 2))
        self.start_point = start_point
        self.end_point = end_point
        self.path = painter_path

        self.initArrowHead()

    def initArrowHead(self) -> None:
        """Initialize the arrow head. The head is filled with black."""

        # Calculate arrowHead
        arrowHeadPolygon = self.calculateArrowHead(self.start_point, self.end_point)

        arrowHead = QGraphicsPolygonItem(arrowHeadPolygon, self)
        arrowHead.setBrush(QColor("black"))

        # Put arrows on top
        arrowHead.setZValue(2)

    def setWeight(self, weight: int) -> None:
        """Put the weight in a middle of the edge.

        Args:
            weight (int): Edge's weight.
        """

        middle = (self.start_point + self.end_point) / 2
        textOffset = QPointF(0, 0)

        self.text = QGraphicsSimpleTextItem(parent=self)
        self.text.setText(str(weight))
        self.text.setPos(middle + textOffset)

    def calculateArrowHead(self, start_pos: QPointF, end_pos: QPointF) -> QPolygonF:
        """Calculate the coordinates of the arrow's head.

        Args:
            start_pos (PySide6.QtCore.QPointF): Starting point.
            end_pos (PySide6.QtCore.QPointF): Ending point. 

        Returns:
            PySide6.QtGui.QPolygonF: A figure of the arrow's head.
        """

        arrowSize = 20
        # Calculate angle, -y since y-axe is inversed
        angle = atan2(
            -(start_pos.y() - end_pos.y()),
            start_pos.x() - end_pos.x(),
        )
        # Calculate offset for each arrow point
        # From polar to normal, inversing axes since we need counter-clockwize angle
        offsetOne = QPointF(
            sin(angle + pi / 3) * arrowSize, cos(angle + pi / 3) * arrowSize
        )
        offsetTwo = QPointF(
            sin(angle + pi * 2 / 3) * arrowSize,
            cos(angle + pi * 2 / 3) * arrowSize,
        )

        pointOne = end_pos + offsetOne
        pointTwo = end_pos + offsetTwo
        return QPolygonF([pointOne, pointTwo, end_pos])
