from math import sin, cos, pi, sqrt, atan2

from PySide6.QtWidgets import QGraphicsScene, QWidget
from PySide6.QtGui import QPainterPath, QColor
from PySide6.QtCore import QPointF, QSize

from .node import Node
from .edge import Edge

from electoral_systems import Election


class DirectedGraph(QGraphicsScene):
    """A scene (kinda like canvas) on which an oriented graph will be drawn."""

    def __init__(self, view_size: QSize, voting_rule: str, parent: QWidget):
        """Initialize an instance of the election (for data sharing).
            Initialize the `PySide6.QtGui.QPainterPath` to draw edges.

        Args:
            view_size (PySide6.QtCore.QSize): A size of the associated view.
            voting_rule (str): A constant related to the Condorcet-based voting rule whose results will be drawn. 
            parent (PySide6.QtWidgets.QWidget): Scene's parent.
        """

        super().__init__(parent)
        self.election = Election()

        # Dict will be filled in initNodes
        self.id_position = dict()

        self.view_size = view_size
        self.voting_rule = voting_rule
        self.path = QPainterPath()

        # White color
        self.setBackgroundBrush(QColor(255, 255, 255))
        self.calculateCircle()

    def drawGraphics(self, weighted: bool) -> None:
        """Initialize and place nodes and edges of the oriented graph.

        Args:
            weighted (bool): `True` if graph is also weighted. Otherwise, `False`.
        """

        self.initNodes()
        self.initEdges(weighted)

    def initNodes(self) -> None:
        """Initialize and place nodes. Fill the dictionnary `id_position` which associates a candidate's ID and his node."""

        # Dict key : ID d'un candidat, value : his node
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
        """Initialize and draw the graph edges.

        Args:
            weighted (bool): `True` if the graph is also weighted. Otherwise, `False`.
        """

        # Duels between candidates are already set
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
        """Calculate a circle of the border on which nodes will be places. Nodes are places equidistantly."""

        self.center = QPointF(self.view_size.width() / 2, self.view_size.height() / 2)
        # Radius = 70% of window size
        self.radius = min(self.center.x() * 0.7, self.center.y() * 0.7)
        # Angle between candidates in radians
        nb_candidates = len(self.election.candidates)
        self.angle = 0 if nb_candidates == 0 else 2 * pi / nb_candidates

    def calculateNorm(self, point1: QPointF, point2: QPointF) -> float:
        """Calculate a vector norm. Vector is *point1 -> point2*.

        Args:
            point1 (PySide6.QtCore.QPointF): Vector's starting point.
            point2 (PySide6.QtCore.QPointF): Vector's ending point.

        Returns:
            float: Vector norm.
        """

        x1, y1 = point1.x(), point1.y()
        x2, y2 = point2.x(), point2.y()
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
