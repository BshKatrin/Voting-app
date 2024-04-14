from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QPushButton,
)
from PySide6.QtCore import Qt, Slot, Signal

from electoral_systems import Election, VotingRulesConstants


class SettingsWidget(QWidget):
    """Une classe qui représente le widget avec les réglages d'une élection (page d'accueil)."""

    sig_saved = Signal()

    def __init__(self, parent: QWidget):
        """Initialise une instance d'élection (pour le partage des données).

        Args:
            parent (PySide6.QtWidgets.QWidget): Un parent d'un widget.
        """
        super().__init__(parent)

        self.election = Election()

        self.initUI()

    def initUI(self) -> None:
        """Initialise l'interface complète des réglages."""

        self.layout = QGridLayout()
        self.layout.setSpacing(40)
        self.setLayout(self.layout)

        # Initialisaton des widgets
        self.liquid_democracy_label = QLabel(parent=self)
        self.liquid_democracy_checkbox = QCheckBox(parent=self)

        self.polls_label = QLabel(parent=self)
        self.nb_polls_btn = QSpinBox(parent=self)
        self.polls_dropdown = QComboBox(parent=self)

        self.tie_breaker_label = QLabel(parent=self)
        self.tie_breaker_checkbox = QCheckBox(parent=self)

        self.initUIPolls()
        self.initUILiquidDemocracy()
        self.initUITieBreaker()

        # Save button, go back on main window
        save_button = QPushButton("Save", parent=self)
        save_button.clicked.connect(self.saveSettings)
        save_button.setFixedHeight(30)

        # Polls
        self.layout.addWidget(self.polls_label, 0, 0, 1, 2)
        self.layout.addWidget(self.nb_polls_btn, 0, 2, 1, 1)
        self.layout.addWidget(self.polls_dropdown, 1, 1, 1, 2)
        # Liquid democracy
        self.layout.addWidget(self.liquid_democracy_label, 2, 0, 1, 2)
        self.layout.addWidget(
            self.liquid_democracy_checkbox,
            2,
            2,
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignRight,
        )
        # Save button
        self.layout.addWidget(self.tie_breaker_label, 3, 0, 1, 2)
        self.layout.addWidget(
            self.tie_breaker_checkbox,
            3,
            2,
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignRight,
        )
        self.layout.addWidget(save_button, 4, 0, 1, 3)

    def initUIPolls(self) -> None:
        """Initialise la partie d'interface correspondant aux sondages."""

        # Number of polls
        self.polls_label.setText("Number of polls to conduct")
        self.nb_polls_btn.setMinimum(0)
        self.nb_polls_btn.setMaximum(10)
        self.nb_polls_btn.setValue(self.election.nb_polls)
        
        self.nb_polls_btn.valueChanged.connect(self.setNumberPolls)
        self.setNumberPolls(self.election.nb_polls)

        self.voting_rule_ui_reverse = dict()
        for voting_rule in VotingRulesConstants.ONE_ROUND:
            self.voting_rule_ui_reverse[VotingRulesConstants.UI[voting_rule]] = (
                voting_rule
            )

        # Choose poll voting rule
        self.polls_dropdown.addItems(self.voting_rule_ui_reverse.keys())
        self.polls_dropdown.currentTextChanged.connect(self.setPollVotingRule)
        self.polls_dropdown.setCurrentText(
            VotingRulesConstants.UI[self.election.poll_voting_rule]
        )

    def initUILiquidDemocracy(self) -> None:
        """Initialise la partie d'interface correspondant à la démocratie liquide."""

        # Activate liquid democracy checkbox
        self.liquid_democracy_label.setText("Activate liquid democracy")
        self.liquid_democracy_checkbox.setChecked(
            self.election.liquid_democracy_activated
        )
        self.liquid_democracy_checkbox.stateChanged.connect(
            self.toggleLiquidDemocracy)

    def initUITieBreaker(self) -> None:
        """Initialise la partie d'interface correspondant au tie-break."""

        # Activer un tie-break par duels
        self.tie_breaker_label.setText("Activate tie-breaker by duels")
        self.tie_breaker_checkbox.setChecked(self.election.tie_breaker_activated)
        self.tie_breaker_checkbox.stateChanged.connect(self.toggleTieBreaker)

    @Slot(str)
    def setPollVotingRule(self, voting_rule_ui: str) -> None:
        """MAJ une règle de vote pour laquelle les sondages seront effectuées."""

        const = self.voting_rule_ui_reverse[voting_rule_ui]
        self.election.poll_voting_rule = const

    @Slot(int)
    def setNumberPolls(self, nb_polls: int) -> None:
        """Change le nombre de sondages maximal à faire. Désactive la democratie liquide."""

        self.election.nb_polls = nb_polls
        self.polls_dropdown.setEnabled(bool(nb_polls))
        
        if nb_polls:
            self.liquid_democracy_checkbox.setEnabled(False)
            self.liquid_democracy_checkbox.setCheckState(Qt.CheckState.Unchecked)
            self.toggleLiquidDemocracy(0)
        else:
            self.liquid_democracy_checkbox.setEnabled(True)
        
    @Slot(int)
    def toggleLiquidDemocracy(self, state: int) -> None:
        """Active ou désactive une démocratie liquide (i.e. si les électeurs pourront ou pas faire des délégations)"""

        self.election.liquid_democracy_activated = bool(state)

    @Slot(int)
    def toggleTieBreaker(self, state: int) -> None:
        """Active ou désactive un tie-break selon les duels."""

        self.election.tie_breaker_activated = bool(state)

    @Slot()
    def saveSettings(self) -> None:
        """Emet le signal `sig_saved`. Permettra de supprimer le widget."""

        self.sig_saved.emit()
