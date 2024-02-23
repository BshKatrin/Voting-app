from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtCharts import QChartView
import sys

from graphics.main_window import HomeWindow

from electoral_systems.voting_rules import constants
from electoral_systems.voting_rules import plurality

from electoral_systems import Election

from people import Candidate, Elector

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     app.setStyle("Fusion")
#     e = Election()
#     c1 = Candidate()
#     c2 = Candidate()
#     c3 = Candidate()
#     e.add_candidate(c1)
#     e.add_candidate(c2)
#     e.add_candidate(c3)

#     for _ in range(50):
#         e.add_elector(Elector(candidates=[c1, c2, c3]))

#     e.apply_voting_rule(constants.BORDA)
#     e.apply_voting_rule(constants.PLURALITY_SIMPLE)
#     e.apply_voting_rule(constants.APPROVAL)
#     e.apply_voting_rule(constants.VETO)

#     for c in e.candidates:
#         print(c.scores)

#     voting_rules = {
#         constants.BORDA,
#         constants.PLURALITY_SIMPLE,
#         constants.APPROVAL,
#         constants.VETO,
#     }
#     chart = WidgetChart(voting_rules)
#     view = ChartView(chart)

#     view.show()

#     sys.exit(app.exec())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = HomeWindow(app)

    window.show()
    sys.exit(app.exec())
