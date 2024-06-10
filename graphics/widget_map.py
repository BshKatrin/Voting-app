from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
)

from .widget_map_utls import QuadrantMap, WidgetCheckbox, WidgetRandomSettings

from electoral_systems import Election


class WidgetMap(QWidget):
    """A class which represents a widget with a political map (aka quadrant map), data generation settings and the choice of voting rules."""

    sig_start_election = Signal(list)
    """A signal emitted with a list of constants related to voting rules chosen with checkboxes."""

    def __init__(self, parent: QWidget):
        """Initialise une instance  d'élection (pour le partage des données).

        Args:
            parent (PySide6.QtWidgets.QWidget): Le parent d'un widget.
        """

        super().__init__(parent)

        self.election = Election()

        self.setGeometry(0, 0, parent.width(), parent.height())
        self.initUI()

    def initUI(self) -> None:
        """Initialize the layout and the UI (buttons, input fields, political map)s de saisie et la carte politique)."""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.initNavigation()

        # Political map
        self.quadrant_map = QuadrantMap(0.8, parent=self)
        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignHCenter)

        self.initInputFields()

    def initNavigation(self) -> None:
        """Initialize buttons to start the election and open the widget with checkboxes to choose the voting rules"""

        # Layout for top buttons
        layout_btns = QHBoxLayout()

        # Widget-checkbox to choose the voting rules 
        self.voting_rules_checkbox = WidgetCheckbox(parent=None)
        self.voting_rules_checkbox.sig_toggle_election_btn.connect(
            self.toggleElectionBtnState
        )

        self.choose_voting_rules_btn = QPushButton(
            "Choose voting rules", parent=self)
        self.choose_voting_rules_btn.clicked.connect(self.showWidgetCheckbox)

        self.start_election_btn = QPushButton("Start election", parent=self)

        # Button is activated only if there is at least 1 elector & 1 candidate & 1 voting rule has been chosen
        if (not self.election.has_electors_candidates()) or (not self.voting_rules_checkbox.votingRuleChosen()):
            self.start_election_btn.setEnabled(False)

        self.start_election_btn.clicked.connect(self.onStartElectionClick)

        layout_btns.addWidget(self.choose_voting_rules_btn)
        layout_btns.addWidget(self.start_election_btn)

        self.layout.addLayout(layout_btns)

    def initInputFields(self) -> None:
        """Initialize input fields for number of candidates and of electors to generate randomly.
        Initialize a button to confirm entered numbers, a button to open the widget with data generation settings."""

        # Layout for bottom widgets
        layout_input = QGridLayout()

        self.widget_settings = WidgetRandomSettings(self.parent().size())

        # User input to generate randomly
        self.candidates_text_box = QLineEdit(parent=self)
        self.candidates_text_box.setPlaceholderText("Number of candidates")

        self.electors_text_box = QLineEdit(parent=self)
        self.electors_text_box.setPlaceholderText("Number of electors")

        # Button to generate data 
        self.btn_gen_random = QPushButton("Generate random", parent=self)
        self.btn_gen_random.clicked.connect(self.generateData)

        if not self.election.has_electors_candidates():
            self.btn_gen_random.clicked.connect(self.toggleElectionBtnState)

        self.btn_gen_random.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred,
                        QSizePolicy.Policy.Preferred)
        )

        # Buttong to configure data generation parameters 
        self.random_settings_btn = QPushButton(
            "Random generation settings", parent=self
        )
        self.random_settings_btn.clicked.connect(self.showWidgetRandomSettings)
        self.random_settings_btn.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred,
                        QSizePolicy.Policy.Preferred)
        )

        layout_input.addWidget(self.candidates_text_box, 0, 0)
        layout_input.addWidget(self.electors_text_box, 1, 0)
        layout_input.addWidget(self.random_settings_btn, 0, 1)
        layout_input.addWidget(self.btn_gen_random, 1, 1)

        self.layout.addLayout(layout_input)

    def getIntInputField(self, text_box: QLineEdit) -> int:
        """Convert entered string to an integer.

        Args:
            text_box (PySide6.QtWidgets.QLineEdit): An input field whose text should be converted.

        Returns:
            int: An entered integer or 0 if string contained characters other then numbers.
        """

        text = text_box.text()
        return int(text) if text.isdigit() else 0

    @Slot()
    def generateData(self) -> None:
        """Generate candidates and electors. Number of generated candidates and electors corresponds to entered numbers
        in the input fields. Redraw a political map and delete enterred text in the input fields."""

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
    def onStartElectionClick(self) -> None:
        """Emit the signal `sig_start_election` with a list of constants related to voting rules 
        chosen with checkboxes. Called when a button `start_election_btn` has been clicked.
        """

        chosen_voting_rule = self.voting_rules_checkbox.getChosenVotingRules()
        self.sig_start_election.emit(list(chosen_voting_rule))

    @Slot()
    def toggleElectionBtnState(self) -> None:
        """Toggle  the button `start_election_btn` which allows to start the election. 
        The button is activated iff there is at least 1 elector & 1 candidate & 1 voting rule has been chosen.
        """

        enable = self.election.has_electors_candidates() and self.voting_rules_checkbox.votingRuleChosen()
        self.start_election_btn.setEnabled(enable)

    @Slot()
    def showWidgetCheckbox(self) -> None:
        """Show the widget with checbkoxes for voting rules."""

        self.voting_rules_checkbox.showCustom()
        self.voting_rules_checkbox.raise_()

    @Slot()
    def showWidgetRandomSettings(self) -> None:
        """Show the widget with data generation settings."""

        self.widget_settings.show()
        self.widget_settings.raise_()

    @Slot()
    def cleanTextBoxes(self) -> None:
        """Delete contente from input fields for the number of candidates and electors."""

        self.candidates_text_box.clear()
        self.electors_text_box.clear()

    @Slot()
    def destroyChildren(self) -> None:
        """Delete children-widgets whose parent is `None`"""

        self.voting_rules_checkbox.deleteLater()
        self.widget_settings.deleteLater()
