from PySide6.QtWidgets import QApplication, QStyleFactory, QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
import sys

from graphics.main_window import HomeWindow
from graphics.settings import GRAPHICS_VIEW_WIDTH, GRAPHICS_VIEW_HEIGHT

from graphics import DirectedGraph
from electoral_systems import Election
from electoral_systems.voting_rules.constants import CONDORCET_SIMPLE
from people import Candidate, Elector


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    c0 = Candidate()
    c1 = Candidate()
    c2 = Candidate()
    c3 = Candidate()
    lst_c = [c0, c1, c2, c3]
    lst_e = [
        Elector(candidates=lst_c, candidates_ranked=[c0, c1, c3, c2]),
        Elector(candidates=lst_c, candidates_ranked=[c3, c1, c0, c2]),
        Elector(candidates=lst_c, candidates_ranked=[c2, c0, c1, c3]),
    ]

    e = Election()
    for c in lst_c:
        e.add_candidate(c)
    for el in lst_e:
        e.add_elector(el)
    e.apply_voting_rule(CONDORCET_SIMPLE)
    # print(e.results)
    # print(e.condorcet_graph_info)

    scene = DirectedGraph()
    view = QGraphicsView(scene)

    view.resize(GRAPHICS_VIEW_WIDTH, GRAPHICS_VIEW_HEIGHT)
    scene.drawGraphics(True)
    view.show()

    # for c in lst_c:
    # print(c, c.scores)

    # window = HomeWindow(app)

    # window.show()
    sys.exit(app.exec())
