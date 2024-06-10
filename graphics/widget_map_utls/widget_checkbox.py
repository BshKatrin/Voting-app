from functools import partial
from typing import Set, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Slot
from electoral_systems import Election

from electoral_systems.voting_rules.constants import *
from electoral_systems import VotingRulesConstants
from .voting_rule_checkbox import VotingRuleCheckbox


class WidgetCheckbox(QWidget):
    """A class which represents the widget with a set of checkboxes.
    These checkboxes allow to choose voting rules to use in the election."""

    sig_toggle_election_btn = Signal()
    """A signal emitted if the confirmation button has been clicked. 
    Allows to toggle the button allowing to start the election."""

    def __init__(self, parent: Optional[QWidget] = None):
        """"Initialize an instance of the election (for data sharing).
        If polls have been activated, check the checkbox corresponding to the chosen for polls voting rule 
        and desactivate every other checkbox. 

        Args:
            parent (Optional[PySide6.QtWidgets.QWidget]): Widget's parent. The idea is to to show this widget
                in a separate window so the default is `None`.
        """

        super().__init__(parent)
        self.election = Election()

        self.setWindowTitle("Voting rules")
        self.setGeometry(100, 100, 300, 200)

        self.chosen_voting_rules = set()
        self.initUI()

        if self.election.nb_polls:
            self.choosePollVotingRule(self.election.poll_voting_rule)
            self.disableAllVotingRules()

    def initUI(self) -> None:
        """Initialize the layout, a set of checkboxes for currently available each voting rule and the `Choose all`, `Confirm` buttons.
        *Voting rules availability depends on the number of candidates and electors."""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.rule_checkbox = dict()

        for voting_rule, voting_rule_name in VotingRulesConstants.UI.items():
            # Minimum number of candidate for each voting rule
            min = 3 if voting_rule in VotingRulesConstants.MULTI_ROUND else 2

            checkbox = VotingRuleCheckbox(voting_rule_name, min, parent=self)

            checkbox.stateChanged.connect(partial(self.onStateChanged, voting_rule))
            checkbox.setEnabled(False)

            self.layout.addWidget(checkbox)
            self.rule_checkbox[voting_rule] = checkbox

        self.confirm_btn = QPushButton("Confirm", self)
        self.confirm_btn.clicked.connect(self.confirmVotingRules)

        self.choose_all_btn = QPushButton("Choose all", self)
        self.choose_all_btn.clicked.connect(self.chooseAllVotingRules)
        if self.election.nb_polls:
            self.choose_all_btn.setDisabled(True)

        self.layout.addWidget(self.confirm_btn)
        self.layout.addWidget(self.choose_all_btn)

    @Slot(str, int)
    def onStateChanged(self, voting_rule: str, state: int) -> None:
        """Update a set of chosen voting rules if the corresponding checkbox has been checked/unchecked."""

        (
            self.chosen_voting_rules.add(voting_rule)
            if state
            else self.chosen_voting_rules.discard(voting_rule)
        )

    def enableCheckboxes(self) -> None:
        """Activate the checkboxes whose the minumum number of candidates has been reached."""

        nb_candidates = len(self.election.candidates)
        for checkbox in self.rule_checkbox.values():
            if nb_candidates >= checkbox.min:
                checkbox.setEnabled(True)

    def showCustom(self) -> None:
        """Show the widget."""

        if not self.election.nb_polls:
            self.enableCheckboxes()
        self.show()

    @Slot()
    def confirmVotingRules(self) -> None:
        """Emit the signal `sig_toggle_election_btn` and close the widget. *The widget is not deleted, just hidden*."""

        self.sig_toggle_election_btn.emit()
        self.close()

    @Slot()
    def chooseAllVotingRules(self) -> None:
        """Choose all available (i.e. activated checkboxes)."""

        for checkbox in self.rule_checkbox.values():
            if checkbox.isEnabled():
                checkbox.setChecked(True)

    def getChosenVotingRules(self) -> Set[str]:
        """Get a set of constants related to the voting rules chosen with checkboxes.

        Returns:
            Set[str]: A set of constants related to the voting rules.
        """

        return self.chosen_voting_rules

    def votingRuleChosen(self) -> bool:
        """Verify that at least 1 voting rule has been chosen.

        Returns:
            bool: `True` if at least 1 voting rule has been chosen, `False` otherwise.
        """

        return bool(self.chosen_voting_rules)

    def choosePollVotingRule(self, voting_rule: str) -> None:
        """Check the checkbox corresponding to the given voting rule.

        Args:
            voting_rule (str): A constant related to the voting rule whose checkbox should be checked. 
        """

        self.rule_checkbox[voting_rule].setChecked(True)

    def disableAllVotingRules(self) -> None:
        """Desactivate all checkboxes."""

        for checkbox in self.rule_checkbox.values():
            checkbox.setEnabled(False)
