from math import sin, cos, pi, sqrt, atan2

from PySide6.QtWidgets import QGraphicsScene, QWidget
from PySide6.QtGui import QPainterPath, QColor
from PySide6.QtCore import QPointF, QSize

from .node import Node
from .edge import Edge

from electoral_systems import Election


class DirectedGraph(QGraphicsScene):
    """Une scène sur laquelle un graphe orienté sera dessiné."""

    def __init__(self, view_size: QSize, voting_rule: str, parent: QWidget):
        """Initialise une instance d'élection (pour le partage des données). 
        Initialise un `PySide6.QtGui.QPainterPath` pour les arêtes. 

        Args:
            view_size (PySide6.QtCore.QSize): La taille d'un view associé.
            voting_rule (str): Une constante d'une règle du vote dont les résultats une scène dessinera.
            parent (PySide6.QtWidgets.QWidget): Le parent d'une scène.
        """

        super().__init__(parent)
        self.election = Election()

        # Un dict sera rempli dans initNodes
        self.id_position = dict()

        self.view_size = view_size
        self.voting_rule = voting_rule
        self.path = QPainterPath()

        # Couleur gris-claire
        self.setBackgroundBrush(QColor(238, 238, 238))
        self.calculateCircle()

    def drawGraphics(self, weighted: bool) -> None:
        """Initialise et place les noeuds et les arêtes d'un graphe orienté.

        Args:
            weighted (bool): True s'il faut représenter des poids. Sinon, False.
        """

        self.initNodes()
        self.initEdges(weighted)

    def initNodes(self) -> None:
        """Initialise et place les noeuds. Remplit un dictionnaire `id_position` qui associe l'ID d'un candidat
        et le noeud d'un candidat."""

        # Dict key : ID d'un candidat, value : son noeud associé
        winner = self.election.choose_winner(self.voting_rule)

        for i in range(len(self.election.candidates)):
            x = self.center.x() + self.radius * cos(self.angle * i)
            y = self.center.y() + self.radius * sin(self.angle * i)

            candidate = self.election.candidates[i]
            node = Node(x, y, f"{candidate.first_name} {candidate.last_name}")

            if candidate == winner:
                node.highlight()

            self.id_position[candidate.id] = node
            self.addItem(node)

    # draw edges between nodes
    def initEdges(self, weighted: bool) -> None:
        """Initialise et place les arêtes d'un graphe.

        Args:
            weighted (bool): `True` s'il faut représenter des poids. Sinon, `False`.
        """

        # Les duels des candidats déjà remplis
        for (winner, loser), weight in self.election.duels_scores.items():

            winner_node = self.id_position[winner.id]
            loser_node = self.id_position[loser.id]

            # Calculate edge of a node (end point of an arrow)
            lw_vector = loser_node.pos() - winner_node.pos()
            lw_vector_norm = self.calculateNorm(winner_node, loser_node)

            edge_point = (
                loser_node.pos() - lw_vector / lw_vector_norm * loser_node.RADIUS
            )

            # Connect nodes
            self.path.moveTo(winner_node.pos())
            self.path.lineTo(edge_point)

            edge = Edge(self.path, winner_node.pos(), edge_point)
            if weighted:
                edge.setWeight(weight)

            self.addItem(edge)

    def calculateCircle(self) -> None:
        """Calcule un cercle sur la bordure sur laquelle les noeuds vont être placés."""

        self.center = QPointF(self.view_size.width() / 2, self.view_size.height() / 2)
        # Radius = 70% of window size
        self.radius = min(self.center.x() * 0.7, self.center.y() * 0.7)
        # Angle between candidates in radians
        nb_candidates = len(self.election.candidates)
        self.angle = 0 if nb_candidates == 0 else 2 * pi / nb_candidates

    def calculateNorm(self, point1: QPointF, point2: QPointF) -> float:
        """Calcule la norme d'un vecteur point1 -> point2.

        Args:
            point1 (PySide6.QtCore.QPointF): Point de départ d'un vecteur.
            point2 (PySide6.QtCore.QPointF): Point d'arrivée d'un vecteur.

        Returns:
            float: La norme d'un vecteur.
        """

        x1, y1 = point1.x(), point1.y()
        x2, y2 = point2.x(), point2.y()
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
