from math import sin, cos, pi, sqrt, atan2

from PySide6.QtWidgets import QGraphicsScene, QGraphicsPolygonItem
from PySide6.QtGui import QPainterPath, QColor, QPolygonF
from PySide6.QtCore import QPointF

from .directed_graph_utls import Node
from .directed_graph_utls import Edge

from electoral_systems import Election
from .settings import GRAPHICS_VIEW_WIDTH, GRAPHICS_VIEW_HEIGHT


class DirectedGraph(QGraphicsScene):
    # Set canvas
    def __init__(self, parent=None):
        super().__init__(parent)
        self.election = Election()
        self.id_position = dict()  # dict will be filled on initNodes

        self.initUI()
        self.calculateCircle()

    def initUI(self):
        self.path = QPainterPath()
        self.setBackgroundBrush(QColor(238, 238, 238))

    def drawGraphics(self, weighted):
        self.initNodes()
        self.initEdges(weighted)

    # make math to place candidates in a circle
    def calculateCircle(self):
        self.center = QPointF(GRAPHICS_VIEW_WIDTH / 2, GRAPHICS_VIEW_HEIGHT / 2)
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
        for (winner, loser), weight in self.election.condorcet_graph_info.items():

            winner_node = self.id_position[winner.id]
            loser_node = self.id_position[loser.id]

            # Calculate edge of a node (end point of an arrow)
            lw_vector = loser_node.pos() - winner_node.pos()
            lw_vector_norm = self.calculateDistance(winner_node, loser_node)

            edge_point = (
                loser_node.pos() - lw_vector / lw_vector_norm * loser_node.radius
            )

            # Connect nodes
            self.path.moveTo(winner_node.pos())
            self.path.lineTo(edge_point)

            # Calculate arrowHead
            arrowHeadPolygon = self.calculateArrowHead(winner_node, edge_point)

            arrowHead = QGraphicsPolygonItem(arrowHeadPolygon)
            arrowHead.setBrush(QColor("black"))

            # Put arrows on top
            arrowHead.setZValue(2)

            edge = Edge(self.path, winner_node.pos(), edge_point)
            if weighted:
                text = edge.setWeight(weight)
            self.addItem(edge)
            self.addItem(arrowHead)

    # Calculate distance between 2 points
    def calculateDistance(self, point1, point2):
        x1, y1 = point1.x(), point1.y()
        x2, y2 = point2.x(), point2.y()
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def calculateArrowHead(self, start_pos, end_pos):
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
