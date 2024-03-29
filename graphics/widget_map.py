from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, Slot, QPoint
from electoral_systems import Election
from people import Elector, Candidate

from PySide6.QtGui import QPixmap, QPainter

from .widget_map_utls import QuadrantMap, WidgetCheckbox, WidgetSettings


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
        # Set layouts
        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Top buttons layout
        layout_btns = QHBoxLayout()

        # Bottom buttons layout
        layout_input = QGridLayout()

        # Navigation button
        self.choose_voting_rules_btn = QPushButton("Choose voting rules", parent=self)
        self.choose_voting_rules_btn.clicked.connect(self.showWidgetCheckbox)

        self.start_election_btn = QPushButton("Start election", parent=self)
        self.start_election_btn.setEnabled(False)
        self.start_election_btn.clicked.connect(self.onStartElectionClick)

        # Quadrant map
        self.quadrant_map = QuadrantMap(parent=self)

        # Voting rules checkbox
        self.voting_rules_checkbox = WidgetCheckbox(parent=None)
        self.voting_rules_checkbox.sig_toggle_election_btn.connect(
            self.toggleElectionBtnState
        )

        self.widget_settings = WidgetSettings(
            self.parent().size(), self.quadrant_map.size()
        )

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

        # MAJ 06.03.24
        # Button to configure data generation
        self.random_settings_btn = QPushButton(
            "Random generation settings", parent=self
        )
        self.random_settings_btn.clicked.connect(self.showWidgetRandomSettings)
        self.random_settings_btn.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        )

        # Add to layout
        # Top
        self.layout.addLayout(layout_btns)
        layout_btns.addWidget(self.choose_voting_rules_btn)
        layout_btns.addWidget(self.start_election_btn)

        # Map
        self.layout.addWidget(self.quadrant_map, 0, Qt.AlignHCenter)

        # Bottom
        self.layout.addLayout(layout_input)
        layout_input.addWidget(self.candidates_text_box, 0, 0)
        layout_input.addWidget(self.electors_text_box, 1, 0)
        layout_input.addWidget(self.random_settings_btn, 0, 1)
        layout_input.addWidget(self.btn_gen_random, 1, 1)

    def _get_int_text_box(self, text_box):
        text = text_box.text()
        return int(text) if text.isdigit() else 0

    @Slot()
    def generateData(self):
        nb_candidates = self._get_int_text_box(self.candidates_text_box)
        nb_electors = self._get_int_text_box(self.electors_text_box)

        for _ in range(nb_candidates):
            generatedPosition = self.quadrant_map.generatePosition()
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
            generatedPosition = self.quadrant_map.generatePosition()
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
        # Draw version with delegations
        self.election.create_electors()
        self.election.make_delegations()
        # Draw last time, with delegations
        self.quadrant_map.final_painting = True
        self.quadrant_map.update()

        # Import drawing to an image
        pixmap = QPixmap(self.quadrant_map.size())
        pixmap_painter = QPainter(pixmap)

        self.quadrant_map.render(pixmap_painter, QPoint(0, 0))
        pixmap_painter.end()

        success = pixmap.save("graphics/temp/map.png", "PNG", 50)
        print("Saved") if success else print("Not saved")

        constantsSet = self.voting_rules_checkbox.getConstantsSet()

        self.sig_start_election.emit(list(constantsSet))

    @Slot()
    def toggleElectionBtnState(self, enable):
        self.start_election_btn.setEnabled(enable)

    # MAJ 06.03.24
    @Slot()
    def showWidgetRandomSettings(self):
        self.widget_settings.show()

    @Slot()
    def destroyChildren(self):
        self.voting_rules_checkbox.deleteLater()
        self.widget_settings.deleteLater()
