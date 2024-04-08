from functools import partial

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Slot
from electoral_systems import Election

from electoral_systems.voting_rules.constants import *
from electoral_systems import VotingRulesConstants
from .voting_rule_checkbox import VotingRuleCheckbox


class WidgetCheckbox(QWidget):
    sig_toggle_election_btn = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.election = Election()
        self.chosen_voting_rules = set()
        self.initUI()

        if self.election.nb_polls:
            self.choosePollVotingRule(self.election.poll_voting_rule)
            self.disableAllVotingRules()

    def initUI(self):
        self.setWindowTitle("Voting rules")
        self.setGeometry(100, 100, 300, 200)

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
    def onStateChanged(self, voting_rule, state):
        (
            self.chosen_voting_rules.add(voting_rule)
            if state
            else self.chosen_voting_rules.discard(voting_rule)
        )

    # Enable checkboxes whose candidates min was reached
    def enableCheckboxes(self):
        nb_candidates = len(self.election.candidates)
        for checkbox in self.rule_checkbox.values():
            if nb_candidates >= checkbox.min:
                checkbox.setEnabled(True)

    def showCustom(self):
        if not self.election.nb_polls:
            self.enableCheckboxes()
        self.show()

    @Slot()
    def confirmVotingRules(self):
        # Activate button 'Start election' only if at least 1 voting rule was chosen
        emit_value = bool(self.chosen_voting_rules)
        self.sig_toggle_election_btn.emit(emit_value)

        # Close checkbox widget
        self.close()

    # Check all checkboxes at once
    @Slot()
    def chooseAllVotingRules(self):
        for checkbox in self.rule_checkbox.values():
            if checkbox.isEnabled():
                checkbox.setChecked(True)

    def getChosenVotingRules(self):
        return self.chosen_voting_rules

    # For polls
    def choosePollVotingRule(self, voting_rule):
        self.rule_checkbox[voting_rule].setChecked(True)

    def disableAllVotingRules(self):
        for checkbox in self.rule_checkbox.values():
            checkbox.setEnabled(False)
