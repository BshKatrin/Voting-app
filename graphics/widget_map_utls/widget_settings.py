from PySide6.QtWidgets import *
from PySide6.QtCore import *
from sys import argv, exit

from electoral_systems import Election
from .quadrant_map import QuadrantMap


class WidgetSettings(QWidget):
    # map_size est de type QSize
    def __init__(self, map_size, parent=None):
        super().__init__(parent)
        self.election = Election()
        # En sachant que map_size.width = map_size.height()
        self.map_side_size = map_size.width() / 100
        self.setWindowTitle("Random generation settings")
        self.initUI()

    def initUI(self):
        self.economical_label = QLabel("Economical", self)
        self.social_label = QLabel("Social", self)

        self.mu_eco_label = QLabel("mu", self)
        self.sigma_eco_label = QLabel("sigma", self)
        self.mu_social_label = QLabel("mu", self)
        self.sigma_social_label = QLabel("sigma", self)

        self.mu_eco_result = QLabel("", self)
        self.sigma_eco_result = QLabel("", self)
        self.mu_social_result = QLabel("", self)
        self.sigma_social_result = QLabel("", self)

        # Labels ajoutés pour calculer les niveau de compétences des électeurs de manière aléatoire suivant une loi normale
        self.knowledge_label = QLabel("Knowledge", self)

        self.mu_knowledge_label = QLabel("mu", self)
        self.sigma_knowledge_label = QLabel("sigma", self)

        self.mu_knowledge_result = QLabel("", self)
        self.sigma_knowledge_result = QLabel("", self)

        self.slider_mu_eco = QSlider(Qt.Horizontal, self)
        self.slider_mu_eco.valueChanged.connect(self.majMuEcoValue)
        self.slider_mu_eco.setValue(
            int(self.election.economical_constants[0] / self.map_side_size)
        )
        self.slider_mu_eco.setRange(0, 100)

        self.slider_mu_socio = QSlider(Qt.Horizontal, self)
        self.slider_mu_socio.valueChanged.connect(self.majMuSocioValue)
        self.slider_mu_socio.setValue(
            int(self.election.social_constants[0] / self.map_side_size)
        )
        self.slider_mu_socio.setRange(0, 100)

        self.slider_sigma_eco = QSlider(Qt.Horizontal, self)
        self.slider_sigma_eco.valueChanged.connect(self.majSigmaEcoValue)
        self.slider_sigma_eco.setValue(
            int(
                self.election.economical_constants[1] / self.map_side_size
                + self.election.economical_constants[0] / self.map_side_size
            )
        )
        self.slider_sigma_eco.setRange(0, 100)

        self.slider_sigma_socio = QSlider(Qt.Horizontal, self)
        self.slider_sigma_socio.valueChanged.connect(self.majSigmaSocioValue)
        self.slider_sigma_socio.setValue(
            int(
                self.election.social_constants[1] / self.map_side_size
                + self.election.social_constants[0] / self.map_side_size
            )
        )
        self.slider_sigma_socio.setRange(0, 100)

        self.slider_mu_knowledge = QSlider(Qt.Horizontal, self)
        self.slider_mu_knowledge.valueChanged.connect(self.majMuKnowledgeValue)
        self.slider_mu_knowledge.setValue(self.election.knowledge_constants[0] * 100)
        self.slider_mu_knowledge.setRange(0, 100)

        self.slider_sigma_knowledge = QSlider(Qt.Horizontal, self)
        self.slider_sigma_knowledge.valueChanged.connect(self.majSigmaKnowledgeValue)
        self.slider_sigma_knowledge.setValue(self.election.knowledge_constants[1] * 100)
        self.slider_sigma_knowledge.setRange(0, 100)

        # mise en place du layout
        self.layout_widget = QGridLayout()
        self.setLayout(self.layout_widget)
        # implementation des titres
        self.layout_widget.addWidget(self.economical_label, 1, 2)
        self.layout_widget.addWidget(self.social_label, 1, 5)
        self.layout_widget.addWidget(self.knowledge_label, 5, 2)
        # implementation des slider dans le layout
        self.layout_widget.addWidget(self.slider_mu_eco, 3, 2)
        self.layout_widget.addWidget(self.slider_sigma_eco, 4, 2)
        self.layout_widget.addWidget(self.slider_mu_socio, 3, 5)
        self.layout_widget.addWidget(self.slider_sigma_socio, 4, 5)
        self.layout_widget.addWidget(self.slider_mu_knowledge, 6, 2)
        self.layout_widget.addWidget(self.slider_sigma_knowledge, 7, 2)
        # implementation des labes des slider
        self.layout_widget.addWidget(self.mu_eco_label, 3, 1)
        self.layout_widget.addWidget(self.sigma_eco_label, 4, 1)
        self.layout_widget.addWidget(self.mu_social_label, 3, 4)
        self.layout_widget.addWidget(self.sigma_social_label, 4, 4)
        self.layout_widget.addWidget(self.mu_knowledge_label, 6, 1)
        self.layout_widget.addWidget(self.sigma_knowledge_label, 7, 1)
        # implementation des valeurs des slider
        self.layout_widget.addWidget(self.mu_eco_result, 3, 3)
        self.layout_widget.addWidget(self.sigma_eco_result, 4, 3)
        self.layout_widget.addWidget(self.mu_social_result, 3, 6)
        self.layout_widget.addWidget(self.sigma_social_result, 4, 6)
        self.layout_widget.addWidget(self.mu_knowledge_result, 6, 3)
        self.layout_widget.addWidget(self.sigma_knowledge_result, 7, 3)

    def majMuEcoValue(self, value):
        self.election.economical_constants = (
            int(value * (self.map_side_size)),
            self.election.economical_constants[1],
        )
        self.mu_eco_result.setText(f"Current Value: {value}")

    def majMuSocioValue(self, value):
        self.election.social_constants = (
            int(value * (self.map_side_size)),
            self.election.social_constants[1],
        )
        self.mu_social_result.setText(f"Current Value: {value}")

    def majSigmaEcoValue(self, value):
        self.election.economical_constants = (
            self.election.economical_constants[0],
            abs(
                int(
                    value * (self.map_side_size) - self.election.economical_constants[0]
                )
            ),
        )
        self.sigma_eco_result.setText(f"Current Value: {value}")

    def majSigmaSocioValue(self, value):
        self.election.social_constants = (
            self.election.social_constants[0],
            abs(int(value * (self.map_side_size) - self.election.social_constants[0])),
        )
        self.sigma_social_result.setText(f"Current Value: {value}")

    def majMuKnowledgeValue(self, value):
        self.election.knowledge_constants = (
            value / 100,
            self.election.knowledge_constants[1],
        )
        self.mu_knowledge_result.setText(f"Current Value: {value/100}")

    def majSigmaKnowledgeValue(self, value):
        self.election.knowledge_constants = (
            self.election.knowledge_constants[0],
            value / 100,
        )
        self.sigma_knowledge_result.setText(f"Current Value: {value/100}")


if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle("Fusion")

    window = WidgetSettings(app)

    window.show()
    exit(app.exec())
