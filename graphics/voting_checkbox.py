from PySide6.QtWidgets import QApplication, QWidget, QCheckBox, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from electoral_systems import Election

from electoral_systems.voting_rules import constants


class VotingCheckbox(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.election = Election()

        self.mainWindow = main_window
        self.setConstants = set()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Voting systems")
        self.setGeometry(100, 100, 300, 200)

        ##   Création des checkbox
        self.checkboxps = QCheckBox("Plurality simple", self)
        self.checkboxps.stateChanged.connect(self.checkbox_stateps)

        self.checkboxp2r = QCheckBox("Plurality 2 rounds", self)
        self.checkboxp2r.stateChanged.connect(self.checkbox_statep2r)

        self.checkboxv = QCheckBox("Veto", self)
        self.checkboxv.stateChanged.connect(self.checkbox_statev)

        self.checkboxb = QCheckBox("Borda", self)
        self.checkboxb.stateChanged.connect(self.checkbox_stateb)

        self.checkboxcs = QCheckBox("Condorcet simple", self)
        self.checkboxcs.stateChanged.connect(self.checkbox_statecs)

        self.checkboxcc = QCheckBox("Condorcet Copeland", self)
        self.checkboxcc.stateChanged.connect(self.checkbox_statecc)

        self.checkboxcsimp = QCheckBox("Condorcet Simpson", self)
        self.checkboxcsimp.stateChanged.connect(self.checkbox_statecsimp)

        self.checkboxeb = QCheckBox("Exhaustive ballot", self)
        self.checkboxeb.stateChanged.connect(self.checkbox_stateeb)

        self.checkboxap = QCheckBox("Approval", self)
        self.checkboxap.stateChanged.connect(self.checkbox_stateap)

        ## QVBoxLayout pour placer les widgets verticalement
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.checkboxps)
        self.layout.addWidget(self.checkboxp2r)
        self.layout.addWidget(self.checkboxv)
        self.layout.addWidget(self.checkboxb)
        self.layout.addWidget(self.checkboxcs)
        self.layout.addWidget(self.checkboxcc)
        self.layout.addWidget(self.checkboxcsimp)
        self.layout.addWidget(self.checkboxeb)
        self.layout.addWidget(self.checkboxap)

        #   ajoute un bouton d'affichage
        self.btnConfirm = QPushButton("Confirm", self)
        self.layout.addWidget(self.btnConfirm)

        #   Connecte le signal clicked du bouton
        self.btnConfirm.clicked.connect(self.confirmVotingRules)

    ##   fonctions liés à chaque checkbox qui ajoutent à la liste de fontion le nom du système de vote utilisé quand la checkbox est cochée
    ##   décocher la checkbos retire l'élément de la liste

    def desactivateCheckboxes(self):
        nb_candidates = len(self.election.candidates)
        # Desactiver tous les checkbox
        if nb_candidates < 2:
            for i in range(self.layout.count()):
                widget = self.layout.itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    widget.setEnabled(False)
        elif nb_candidates < 3:
            # Desactiver les checkbox des systemes de vote a plusieurs tours
            self.checkboxp2r.setEnabled(False)
            self.checkboxeb.setEnabled(False)

    def checkbox_stateps(self):

        if self.checkboxps.isChecked():
            self.setConstants.add(constants.PLURALITY_SIMPLE)
        else:
            self.setConstants.discard(constants.PLURALITY_SIMPLE)

    def checkbox_statep2r(self):
        if self.checkboxp2r.isChecked():
            self.setConstants.add(constants.PLURALITY_2_ROUNDS)
        else:
            self.setConstants.discard(constants.PLURALITY_2_ROUNDS)

    def checkbox_statev(self):
        if self.checkboxv.isChecked():
            self.setConstants.add(constants.VETO)
        else:
            self.setConstants.discard(constants.VETO)

    def checkbox_stateb(self):
        if self.checkboxb.isChecked():
            self.setConstants.add(constants.BORDA)
        else:
            self.setConstants.discard(constants.BORDA)

    def checkbox_statecs(self):
        if self.checkboxcs.isChecked():
            self.setConstants.add(constants.CONDORCET_SIMPLE)
        else:
            self.setConstants.discard(constants.CONDORCET_SIMPLE)

    def checkbox_statecc(self):
        if self.checkboxcc.isChecked():
            self.setConstants.add(constants.CONDORCET_COPELAND)
        else:
            self.setConstants.discard(constants.CONDORCET_COPELAND)

    def checkbox_statecsimp(self):
        if self.checkboxcsimp.isChecked():
            self.setConstants.add(constants.CONDORCET_SIMPSON)
        else:
            self.setConstants.discard(constants.CONDORCET_SIMPSON)

    def checkbox_stateeb(self):
        if self.checkboxeb.isChecked():
            self.setConstants.add(constants.EXHAUSTIVE_BALLOT)
        else:
            self.setConstants.discard(constants.EXHAUSTIVE_BALLOT)

    def checkbox_stateap(self):
        if self.checkboxap.isChecked():
            self.setConstants.add(constants.APPROVAL)
        else:
            self.setConstants.discard(constants.APPROVAL)

    # Trigger for button 'Confirm'
    def confirmVotingRules(self):
        # Activate button on main_window only if at least 1 voting rule was chosen
        print(self.setConstants)
        if len(self.getConstantsSet()):
            self.mainWindow.button_vote.setEnabled(True)
        # Close checkbox widget
        self.close()

    def getConstantsSet(self):
        return self.setConstants


if __name__ == "__main__":
    app = QApplication([])
    window = VotingCheckbox()
    window.show()
    app.exec()
