from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit
from PySide6.QtCore import Qt
from .graph import Graph
from PySide6.QtCore import Qt
from electoral_systems import Election
from people import Elector, Candidate


class GraphRandom(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.election = Election()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.initUI()

    def initUI(self):
        self.graph = Graph(parent=self)
        self.layout.addWidget(self.graph, 0, Qt.AlignHCenter)

        # Fields
        self.candidatesTextBox = QLineEdit(parent=self)
        self.candidatesTextBox.setPlaceholderText("Number of candidates")
        self.layout.addWidget(self.candidatesTextBox)

        self.electorsTextBox = QLineEdit(parent=self)
        self.electorsTextBox.setPlaceholderText("Number of electors")
        self.layout.addWidget(self.electorsTextBox)

        # Button
        self.btn_gen_random = QPushButton("Generate random")
        self.layout.addWidget(self.btn_gen_random)
        self.btn_gen_random.clicked.connect(self.generateData)

    def generateData(self):
        try:
            nb_electors = int(self.electorsTextBox.text())
            nb_candidates = int(self.candidatesTextBox.text())
            # On est oblige de generer les candidates tout d'abord
            for _ in range(nb_candidates):
                generatedPosition = self.graph.generatePosition()
                newCandidate = Candidate(
                    position=self.graph.normalizePosition(generatedPosition)
                )
                self.election.add_candidate(newCandidate)
                self.graph.candidates.append(
                    (
                        newCandidate.first_name + " " + newCandidate.last_name,
                        generatedPosition,
                    )
                )

            for _ in range(nb_electors):
                generatedPosition = self.graph.generatePosition()
                self.graph.electors.append(generatedPosition)
                self.election.add_electors_position(
                    self.graph.normalizePosition(generatedPosition)
                )
            self.graph.update()

        except ValueError:
            print("Please enter a valid number of electors and candidates")
        self.cleanTextBoxes()

    def cleanTextBoxes(self):
        self.candidatesTextBox.clear()
        self.electorsTextBox.clear()
