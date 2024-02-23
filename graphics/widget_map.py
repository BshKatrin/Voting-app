from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit
from PySide6.QtCore import Qt, Signal, Slot
from electoral_systems import Election
from people import Elector, Candidate

from .widget_map_utls import QuadrantMap, VotingCheckbox


class WidgetMap(QWidget):
    # signal to main window to show results page
    # it will send final list of chosen voting rules
    sig_start_election = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.election = Election()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.initUI()

    def initUI(self):
        # Navigation button
        self.choose_voting_rules_btn = QPushButton("Choose voting rules", parent=self)
        self.choose_voting_rules_btn.clicked.connect(
            lambda: self.voting_rules_checkbox.show()
        )

        self.start_election_btn = QPushButton("Start election", parent=self)
        self.start_election_btn.setEnabled(False)
        self.start_election_btn.clicked.connect(self.onStartElectionClick)

        # Quadrant map
        self.quadrant_map = QuadrantMap(parent=self)

        # Checkboxes for voting rules
        self.voting_rules_checkbox = VotingCheckbox(parent=None)
        self.voting_rules_checkbox.sig_toggle_btn.connect(self.toggleBtnState)

        # User input for random data
        self.candidates_text_box = QLineEdit(parent=self)
        self.candidates_text_box.setPlaceholderText("Number of candidates")

        self.electors_text_box = QLineEdit(parent=self)
        self.electors_text_box.setPlaceholderText("Number of electors")

        self.btn_gen_random = QPushButton("Generate random", parent=self)
        self.btn_gen_random.clicked.connect(self.generateData)

        # Add to layout
        self.layout.addWidget(self.choose_voting_rules_btn)
        self.layout.addWidget(self.start_election_btn)
        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignHCenter)
        self.layout.addWidget(self.candidates_text_box)
        self.layout.addWidget(self.electors_text_box)
        self.layout.addWidget(self.btn_gen_random)

    @Slot()
    def generateData(self):
        try:
            nb_electors = int(self.electors_text_box.text())
            nb_candidates = int(self.candidates_text_box.text())
            # On est oblige de generer les candidates tout d'abord
            for _ in range(nb_candidates):
                generatedPosition = self.quadrant_map.generatePosition()
                newCandidate = Candidate(
                    position=self.quadrant_map.normalizePosition(generatedPosition)
                )
                self.election.add_candidate(newCandidate)
                self.quadrant_map.candidates.append(
                    (
                        newCandidate.first_name + " " + newCandidate.last_name,
                        generatedPosition,
                    )
                )

            for _ in range(nb_electors):
                generatedPosition = self.quadrant_map.generatePosition()
                self.quadrant_map.electors.append(generatedPosition)
                self.election.add_electors_position(
                    self.quadrant_map.normalizePosition(generatedPosition)
                )
            self.quadrant_map.update()

        except ValueError:
            print("Please enter a valid number of electors and candidates")
        self.cleanTextBoxes()

    @Slot()
    def cleanTextBoxes(self):
        self.candidates_text_box.clear()
        self.electors_text_box.clear()

    @Slot()
    def onStartElectionClick(self):
        constantsSet = self.voting_rules_checkbox.getConstantsSet()
        self.sig_start_election.emit(list(constantsSet))

    @Slot()
    def toggleBtnState(self, enable):
        self.start_election_btn.setEnabled(enable)
