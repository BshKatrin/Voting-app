from PySide6.QtWidgets import QApplication, QWidget, QCheckBox, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from electoral_systems import Election


class VotingCheckbox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.election = Election()

        self.listfonct = set()
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
        self.btnShowPositions = QPushButton("Afficher les positions", self)
        self.layout.addWidget(self.btnShowPositions)

        #   Connecte le signal clicked du bouton
        self.btnShowPositions.clicked.connect(self.showPositions)
        self.setLayout(self.layout)

    ##   fonctions liés à chaque checkbox qui ajoutent à la liste de fontion le nom du système de vote utilisé quand la checkbox est cochée
    ##   décocher la checkbos retire l'élément de la liste

    def desactivate_checkboxes(self):
        nb_candidates = len(self.election.candidates)
        # Desactiver tous les checkbox
        if nb_candidates < 2:
            for i in range(self.layout.count()):
                checkbox = self.layout.itemAt(i).widget()
                checkbox.setEnabled(False)
        elif nb_candidates < 3:
            # Desactiver les checkbox des systemes de vote a plusieurs tours
            self.checkboxp2r.setEnabled(False)
            self.checkboxeb.setEnabled(False)

    def checkbox_stateps(self):
        if self.checkboxps.isChecked():
            self.listfonct.add("PLURALITY_SIMPLE")
        else:
            self.listfonct.discard("PLURALITY_SIMPLE")

    def checkbox_statep2r(self):

        if self.checkboxp2r.isChecked():
            self.listfonct.add("PLURALITY_2_ROUNDS")
        else:
            self.listfonct.discard("PLURALITY_2_ROUNDS")

    def checkbox_statev(self):
        if self.checkboxv.isChecked():
            self.listfonct.add("VETO")
        else:
            self.listfonct.discard("VETO")

    def checkbox_stateb(self):
        if self.checkboxeb.isChecked():
            self.listfonct.add("BORDA")
        else:
            self.listfonct.discard("BORDA")

    def checkbox_statecs(self):
        if self.checkboxcs.isChecked():
            self.listfonct.add("CONDORCET_SIMPLE")
        else:
            self.listfonct.discard("CONDORCET_SIMPLE")

    def checkbox_statecc(self):
        if self.checkboxcc.isChecked():
            self.listfonct.add("CONDORCET_COPELAND")
        else:
            self.listfonct.discard("CONDORCET_COPELAND")

    def checkbox_statecsimp(self):
        if self.checkboxcsimp.isChecked():
            self.listfonct.add("CONDORCET_SIMPSON")
        else:
            self.listfonct.discard("CONDORCET_SIMPSON")

    def checkbox_stateeb(self):
        if self.checkboxeb.isChecked():
            self.listfonct.add("EXHAUSTIVE_BALLOT")
        else:
            self.listfonct.discard("EXHAUSTIVE_BALLOT")

    def checkbox_stateap(self):
        if self.checkboxap.isChecked():
            self.listfonct.add("APPROVAL")
        else:
            self.listfonct.discard("APPROVAL")

    #####   fonctions de test (à enlever)

    def showPositions(self):
        #   affiches les positions politiques des electeurs et les noms et positions des candidats dans la console
        positions_text = "\n".join([f"Position: {fonct}" for fonct in self.listfonct])
        print(positions_text)


if __name__ == "__main__":
    app = QApplication([])
    window = VotingCheckbox()
    window.show()
    app.exec()
