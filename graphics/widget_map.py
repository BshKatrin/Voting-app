from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, Slot

from .widget_map_utls import QuadrantMap, WidgetCheckbox, WidgetRandomSettings

from electoral_systems import Election


class WidgetMap(QWidget):
    # signal to main window to show results page
    # it will send final list of chosen voting rules
    sig_start_election = Signal(list)
    sig_widget_map_destroying = Signal()

    def __init__(self, parent):
        super().__init__(parent)

        self.election = Election()

        self.setGeometry(0, 0, parent.width(), parent.height())
        self.initUI()

        # Delete children whose parent is NOT set on a widget_map destroying
        self.sig_widget_map_destroying.connect(self.destroyChildren)

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.initNavigation()
        self.quadrant_map = QuadrantMap(0.8, parent=self)
        self.initInputFields()

        # Navigation buttons
        self.layout.addLayout(self.layout_btns)

        # Map
        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignHCenter)

        # Bottom buttons (input fields)
        self.layout.addLayout(self.layout_input)

    def initNavigation(self):
        # Top buttons layout
        self.layout_btns = QHBoxLayout()

        # Voting rules checkbox
        self.voting_rules_checkbox = WidgetCheckbox(parent=None)
        self.voting_rules_checkbox.sig_toggle_election_btn.connect(
            self.toggleElectionBtnState
        )

        self.choose_voting_rules_btn = QPushButton("Choose voting rules", parent=self)
        self.choose_voting_rules_btn.clicked.connect(self.showWidgetCheckbox)

        self.start_election_btn = QPushButton("Start election", parent=self)
        if not self.election.nb_polls:
            self.start_election_btn.setEnabled(False)
        self.start_election_btn.clicked.connect(self.onStartElectionClick)

        self.layout_btns.addWidget(self.choose_voting_rules_btn)
        self.layout_btns.addWidget(self.start_election_btn)

    def initInputFields(self):
        # Bottom buttons layout
        self.layout_input = QGridLayout()

        self.widget_settings = WidgetRandomSettings(self.parent().size())

        # User input for random data
        self.candidates_text_box = QLineEdit(parent=self)
        self.candidates_text_box.setPlaceholderText("Number of candidates")

        self.electors_text_box = QLineEdit(parent=self)
        self.electors_text_box.setPlaceholderText("Number of electors")

        # Button to generate data
        self.btn_gen_random = QPushButton("Generate random", parent=self)
        self.btn_gen_random.clicked.connect(self.generateData)
        self.btn_gen_random.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        )

        # Button to configure data generation
        self.random_settings_btn = QPushButton(
            "Random generation settings", parent=self
        )
        self.random_settings_btn.clicked.connect(self.showWidgetRandomSettings)
        self.random_settings_btn.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        )

        self.layout_input.addWidget(self.candidates_text_box, 0, 0)
        self.layout_input.addWidget(self.electors_text_box, 1, 0)
        self.layout_input.addWidget(self.random_settings_btn, 0, 1)
        self.layout_input.addWidget(self.btn_gen_random, 1, 1)

    def getIntInputField(self, text_box):
        text = text_box.text()
        return int(text) if text.isdigit() else 0

    @Slot()
    def generateData(self):
        nb_candidates = self.getIntInputField(self.candidates_text_box)
        nb_electors = self.getIntInputField(self.electors_text_box)

        for _ in range(nb_candidates):
            # Normalized
            generated_position = self.quadrant_map.generatePosition()
            self.election.add_candidate(generated_position)

        for _ in range(nb_electors):
            # Normalized
            generated_position = self.quadrant_map.generatePosition()
            self.election.add_elector(generated_position)

        self.quadrant_map.update()
        self.cleanTextBoxes()

    @Slot()
    def onStartElectionClick(self):
        constantsSet = self.voting_rules_checkbox.getChosenVotingRules()
        self.sig_start_election.emit(list(constantsSet))

    @Slot()
    def toggleElectionBtnState(self, enable):
        self.start_election_btn.setEnabled(enable)

    @Slot()
    def showWidgetCheckbox(self):
        self.voting_rules_checkbox.showCustom()

    @Slot()
    def showWidgetRandomSettings(self):
        self.widget_settings.show()

    @Slot()
    def cleanTextBoxes(self):
        self.candidates_text_box.clear()
        self.electors_text_box.clear()

    @Slot()
    def destroyChildren(self):
        self.voting_rules_checkbox.deleteLater()
        self.widget_settings.deleteLater()
