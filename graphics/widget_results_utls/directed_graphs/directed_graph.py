from math import sin, cos, pi, sqrt, atan2

from PySide6.QtWidgets import QGraphicsScene, QGraphicsPolygonItem
from PySide6.QtGui import QPainterPath, QColor, QPolygonF
from PySide6.QtCore import QPointF

from .node import Node
from .edge import Edge

from electoral_systems import Election


class DirectedGraph(QGraphicsScene):
    # view_size est de type QSize
    def __init__(self, view_size, parent=None):

        super().__init__(parent)
        self.election = Election()
        self.id_position = dict()  # dict will be filled on initNodes

        self.view_size = view_size

        self.initUI()
        self.calculateCircle()

    def initUI(self):
        self.path = QPainterPath()
        self.setBackgroundBrush(QColor(238, 238, 238))

    def drawGraphics(self, weighted):
        self.initNodes()
        self.initEdges(weighted)

    # math to place candidates in a circle
    def calculateCircle(self):
        self.center = QPointF(self.view_size.width() / 2, self.view_size.height() / 2)
        # Radius = 70% of window size
        self.radius = min(self.center.x() * 0.7, self.center.y() * 0.7)
        # Angle between candidates in radians
        nb_candidates = len(self.election.candidates)
        self.angle = 0 if nb_candidates == 0 else 2 * pi / nb_candidates

    # draw nodes, fill dict
    def initNodes(self):
        # Dict such as key : id of a candidate, value : it's associated node
        for i in range(len(self.election.candidates)):
            x = self.center.x() + self.radius * cos(self.angle * i)
            y = self.center.y() + self.radius * sin(self.angle * i)

            candidate = self.election.candidates[i]
            node = Node(x, y, f"{candidate.first_name} {candidate.last_name}")

            self.id_position[candidate.id] = node
            self.addItem(node)

    # draw edges between nodes
    def initEdges(self, weighted):
        # Dict of id of candidates who were already placed with corresponding node position
        for (winner, loser), weight in self.election.duels_scores.items():

            winner_node = self.id_position[winner.id]
            loser_node = self.id_position[loser.id]

            # Calculate edge of a node (end point of an arrow)
            lw_vector = loser_node.pos() - winner_node.pos()
            lw_vector_norm = self.calculateNorm(winner_node, loser_node)

            edge_point = (
                loser_node.pos() - lw_vector / lw_vector_norm * loser_node.radius
            )

            # Connect nodes
            self.path.moveTo(winner_node.pos())
            self.path.lineTo(edge_point)

            edge = Edge(self.path, winner_node.pos(), edge_point)
            if weighted:
                edge.setWeight(weight)

            self.addItem(edge)

    # Calculate norm of a vector
    def calculateNorm(self, point1, point2):
        x1, y1 = point1.x(), point1.y()
        x2, y2 = point2.x(), point2.y()
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
