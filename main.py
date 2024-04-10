from sys import argv, exit

from PySide6.QtWidgets import QApplication
from graphics.home_window import HomeWindow

if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle("Fusion")

    window = HomeWindow(app)

    window.show()
    exit(app.exec())


# from people import Elector, Candidate
# from random import random

# from electoral_systems.voting_rules.constants import EXHAUSTIVE_BALLOT, PLURALITY_2_ROUNDS
# from electoral_systems.voting_rules.plurality import apply_plurality_rounds
# from electoral_systems.voting_rules.exhaustive_ballot import apply_exhaustive_ballot


# if __name__ == "__main__":
#     c0 = Candidate(id=0, position=(random(), random()), first_name="a", last_name="a")
#     c1 = Candidate(id=1, position=(random(), random()), first_name="b", last_name="b")
#     c2 = Candidate(id=2, position=(random(), random()), first_name="c", last_name="c")
#     c3 = Candidate(id=3, position=(random(), random()), first_name="d", last_name="d")

#     cand = [c0, c1, c2, c3]
#     elect = []
#     for i in range(2):
#         elect.append(Elector(id=i, position=(random(), random()), candidates_ranked=[c0, c1, c2, c3]))
#     elect.append(Elector(id=2, position=(random(), random()), candidates_ranked=[c0, c1, c3, c2]))
#     elect.append(Elector(id=3, position=(random(), random()), candidates_ranked=[c1, c0, c3, c2]))
    
#     res = apply_plurality_rounds(elect, cand, None)
#     print(res)
#     for c in cand:
#         print(c, c.scores[PLURALITY_2_ROUNDS])