from math import sin, cos, pi, sqrt, atan2


from PySide6.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsSimpleTextItem,
    QGraphicsPolygonItem,
)
from PySide6.QtGui import QPen, QColor, QPolygonF, QPainterPath
from PySide6.QtCore import Qt, QPointF


class Edge(QGraphicsPathItem):
    """Une classe qui représente une arête d'un graphe orienté."""

    def __init__(self, painter_path: QPainterPath, start_point: QPointF, end_point: QPointF):
        """Initialise une arête noire et une tête d'une flèche qui sort de `start_point` et arrive dans `end_point`.
        
        Args:
            painter_path (PySide6.QtGui.QPainterPath): Un painter qui dessinera une arête.
            start_point (PySide6.QtCore.QPointF): Un point de départ.
            end_point (PySide6.QtCore.QPointF): Un point d'arrivée.
        """
        
        super().__init__(painter_path, None)  # Scene will take ownership

        self.setPen(QPen(Qt.black, 2))
        self.start_point = start_point
        self.end_point = end_point
        self.path = painter_path

        self.initArrowHead()

    def initArrowHead(self) -> None:
        """Initialise une tête d'une flèche noire."""

        # Calculate arrowHead
        arrowHeadPolygon = self.calculateArrowHead(self.start_point, self.end_point)

        arrowHead = QGraphicsPolygonItem(arrowHeadPolygon, self)
        arrowHead.setBrush(QColor("black"))

        # Put arrows on top
        arrowHead.setZValue(2)

    def setWeight(self, weight: int) -> None:
        """Met le poids `weight` au milleu d'une arête.

        Args:
            weight (int): Le poids d'une arête.
        """

        middle = (self.start_point + self.end_point) / 2
        textOffset = QPointF(0, 0)

        self.text = QGraphicsSimpleTextItem(parent=self)
        self.text.setText(str(weight))
        self.text.setPos(middle + textOffset)

    def calculateArrowHead(self, start_pos: QPointF, end_pos: QPointF) -> QPolygonF:
        """Calcule les coordonnées d'une tête d'une flèche.

        Args:
            start_pos (PySide6.QtCore.QPointF): Un point de début.
            end_pos (PySide6.QtCore.QPointF): Un point de l'arrivé.

        Returns:
            PySide6.QtGui.QPolygonF: Une figure d'une flèche.
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
