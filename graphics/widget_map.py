from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit
from PySide6.QtCore import Qt, Signal, Slot
from electoral_systems import Election
from people import Elector, Candidate

from .widget_map_utls import QuadrantMap, WidgetCheckbox


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
        self.choose_voting_rules_btn.clicked.connect(self.showWidgetCheckbox)

        self.start_election_btn = QPushButton("Start election", parent=self)
        self.start_election_btn.setEnabled(False)
        self.start_election_btn.clicked.connect(self.onStartElectionClick)
        """
        #MAJ 06.03.24
        self.random_settings_btn = QPushButton("Random generation settings", parent=self)
        self.random_settings_btn.clicked.connect(self.showWidgetRandomSettings)
"""
        # Quadrant map
        self.quadrant_map = QuadrantMap(parent=self)

        self.voting_rules_checkbox = WidgetCheckbox(parent=None)
        self.voting_rules_checkbox.sig_toggle_election_btn.connect(
            self.toggleElectionBtnState
        )

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
        #self.layout.addWidget(self.random_settings_btn)
        self.layout.addWidget(self.btn_gen_random)

    def _get_int_text_box(self, text_box):
        text = text_box.text()
        return int(text) if text.isdigit() else 0

    @Slot()
    def generateData(self):
        nb_candidates = self._get_int_text_box(self.candidates_text_box)
        nb_electors = self._get_int_text_box(self.electors_text_box)

        for _ in range(nb_candidates):
            generatedPosition = self.quadrant_map.generatePosition(self.election.economical_constants,self.election.social_constants,self.election.coef_dir)
            newCandidate = Candidate(
                position=self.quadrant_map.normalizePosition(generatedPosition)
            )
            self.election.add_candidate(newCandidate)
            self.quadrant_map.candidates.append(
                (
                    newCandidate.first_name,
                    newCandidate.last_name,
                    generatedPosition,
                )
            )

        for _ in range(nb_electors):
            generatedPosition = self.quadrant_map.generatePosition(self.election.economical_constants,self.election.social_constants,self.election.coef_dir)
            self.quadrant_map.electors.append(generatedPosition)
            self.election.add_electors_position(
                self.quadrant_map.normalizePosition(generatedPosition)
            )
        self.quadrant_map.update()

        self.cleanTextBoxes()

    @Slot()
    def showWidgetCheckbox(self):
        self.voting_rules_checkbox.showCustom()

    @Slot()
    def cleanTextBoxes(self):
        self.candidates_text_box.clear()
        self.electors_text_box.clear()

    @Slot()
    def onStartElectionClick(self):
        constantsSet = self.voting_rules_checkbox.getConstantsSet()
        self.sig_start_election.emit(list(constantsSet))

    @Slot()
    def toggleElectionBtnState(self, enable):
        self.start_election_btn.setEnabled(enable)
"""
    #MAJ 06.03.24
    @Slot()
    def showWidgetRandomSettings(self):
        self.widget_settings= WidgetSettings()
        self.widget_settings.show()
"""