from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsSimpleTextItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor


class Node(QGraphicsEllipseItem):
    """Une classe qui représente un noeud d'un graphe orienté."""

    RADIUS:float = 40.0
    """Un rayon d'un noeud."""

    def __init__(self, x:float, y:float, title: str):
        """Initialise un noeud d'un graphe orienté.

        Args:
            x (float): La coordonnée horizontale dans le système des coordonnées de l'ordinateur.
            y (float): La coordonnée horizontale dans le système des coordonnées de l'ordinateur.
            title (str): Un titre d'un noeud.
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
        """Change le d'un noeud couleur en vert pâle."""

        self.setBrush(QColor(152,251,152))
