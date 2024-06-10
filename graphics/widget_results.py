from functools import partial
from typing import Set, Union, Optional

from PySide6.QtCharts import QChartView
from PySide6.QtCore import Qt, Slot, Signal, QSize
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QGraphicsView
)

from .widget_results_utls import DirectedGraph, DirectedGraphView, ChartView, MapImage

from electoral_systems import Election, VotingRulesConstants


class WidgetResults(QWidget):
    """A class which represents the widget with the results of the election (numerical + visualization).
    Polls can be conducted from this widget as well."""

    sig_show_chart = Signal(str)
    """A signal emitted if the current displayed chart should be switched."""

    sig_poll_conducted = Signal()
    """A signal emitted if a new poll has been conducted.s"""

    def __init__(self, parent: QWidget):
        """Initialize an instance of the election (for data sharing).

        Args:
            parent (PySide6.QtWidgets.QWidget): Widget's parent.
        """

        super().__init__(parent)

        self.election = Election()

        self.setGeometry(0, 0, parent.width(), parent.height())

        self.graph_view = None
        self.charts_view = None

        self.condorcet_bool, self.condorcet_set = self.condorcetChosen()
        self.one_round_bool, self.one_round_set = self.oneRoundChosen()
        self.multi_round_bool, self.multi_round_set = self.multiRoundChosen()

        self.conduct_polls = False
        if (self.election.nb_polls and (not self.condorcet_bool) and (not self.multi_round_bool)
                and self.one_round_bool):
            self.conduct_polls = True

        self.initViews()
        self.initUI()

    def initViews(self) -> None:
        """Initialize views for charts if at least 1 one round OR multu-round voting rule has been chosen.
        Initialize views for graphs if at least 1 Condorcet-based voting rule has been chosen."""

        if self.condorcet_bool:
            # A dict associating voting_rule : QGraphicsScene
            self.graphs_scenes = dict()
            self.initDirectedGraph(self.condorcet_set)

        if self.one_round_bool or self.multi_round_bool:
            self.initChartsView()

        if self.one_round_bool:
            self.charts_view.initOneRoundChart(self.one_round_set)

        if self.multi_round_bool:
            self.charts_view.initMultiRoundChart(self.multi_round_set)

    def oneRoundChosen(self) -> tuple[bool, Set[str]]:
        """Find chosen one round voting rules.

        Returns:
            tuple[bool, Set[str]]: A bool `True` if at least 1 one round voting rule has been chosen, `False` otherwise.
                A set of constants related to such voting rules.
        """

        intersect = VotingRulesConstants.ONE_ROUND & self.election.results.keys()
        return bool(intersect), intersect

    def condorcetChosen(self) -> tuple[bool, Set[str]]:  
        """Find chosen Condorcet-based voting rules.

        Returns:
            tuple[bool, Set[str]]: A bool `True` if at least 1 Condorcet-based voting rule has been chosen, `False` otherwise.
                A set of constants related to such voting rules.
        """

        intersect = VotingRulesConstants.CONDORCET & self.election.results.keys()
        return bool(intersect), intersect

    def multiRoundChosen(self) -> tuple[bool, Set[str]]:
        """Find chosen multi-round voting rules.

        Returns:
            tuple[bool, Set[str]]: A bool `True` if at least 1 multi-round voting rule has been chosen, `False` otherwise.
                A set of constants related to such voting rules.
        """

        intersect = VotingRulesConstants.MULTI_ROUND & self.election.results.keys()
        return bool(intersect), intersect

    def initDirectedGraph(self, condorcet_voting_rules: Set[str]) -> None:
        """Initialize one or more `PySide6.QtWidgets.QGraphicsScene` and `PySide6.QtWidgets.QGraphicsView` to show the results 
        of Condorcet-based voting rules. Construct a dictionary of type `Dict[str, PySide6.QtWidgets.QGraphicsScene]` which 
        associates to each constant related to Condorcet-based voting rule a `QGraphicsScene`


        Args:
            condorcet_voting_rules (Set[str]): A set of constants related to chosen Condorcet-based voting rules. **Is not empty**. 
        """

        graph_scene = None

        for voting_rule in condorcet_voting_rules:
            graph_scene = DirectedGraph(self.getViewSize(), voting_rule, parent=self)
            self.graphs_scenes[voting_rule] = graph_scene

        self.graph_view = DirectedGraphView(graph_scene)
        self.resizeView(self.graph_view)

    def initChartsView(self) -> None:
        """Initialize one or more `PySide6.QtCharts.QChartView` to show the results of one round or multi-round voting rules."""


        self.charts_view = ChartView()
        self.resizeView(self.charts_view)

        self.sig_show_chart.connect(self.charts_view.setChartBySig)

    def getViewSize(self) -> QSize:
        """Calculate a size of view which depends on the size of `WidgetResults`'s parent.

        Returns:
            PySide6.QtCore.QSize: A size of view.
        """

        return QSize(self.parent().width() * 0.7, self.parent().height() * 0.7)

    def resizeView(self, view: Union[QGraphicsView, QChartView]) -> None:
        """Change the size of the given view.

        Args:
            view (Union[PySide6.QtCharts.QChartView, PySide6.QtWidgets.QGraphicsView]): A view whose size should be changed.
        """

        view.resize(self.getViewSize())

    def initUI(self) -> None:
        """Initialize the layout et the UI. Initialize a part of the interface corresponding to polls only if necessary.
        Initialize the widget to show the non-interactif political map."""

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(10)

        if self.conduct_polls:
            self.initPollsUI()

        self.initTable()

        self.map_image = MapImage(self.getViewSize())
        self.map_image.closed.connect(self.toggleCheckbox)

    def initPollsUI(self) -> None:
        """Initialize a part of the interface corresponding to polls."""

        # Number of polls

        self.remaining_polls_label = QLabel(self)
        self.remaining_polls_label.setStyleSheet("font-weight: bold")
        self.remaining_polls_label.setText(
            f"Polls {self.nb_polls_conducted}/{self.election.nb_polls}"
        )

        self.start_poll_btn = QPushButton("Apply new poll", self)

        # Add a layout (top)
        self.layout.addWidget(
            self.remaining_polls_label, 0, 0, Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addWidget(self.start_poll_btn, 0, 1, 1, 3)

        # Desactivate the button if no one round voting rule has been chosen. 
        if not self.one_round_bool:
            self.start_poll_btn.setEnabled(False)
            return

        # Make a slot connection only if necessary 
        self.start_poll_btn.clicked.connect(partial(self.conductNewPoll))

    def initTable(self) -> None:
        """Initialize a part of the interface corresponding to the results table."""

        start_row = 1 if self.conduct_polls else 0

        column_one_header = QLabel()
        column_one_header.setText("Voting rule")
        self.layout.addWidget(
            column_one_header, start_row, 0, alignment=Qt.AlignHCenter
        )
        column_one_header.setStyleSheet("font-weight: bold")

        column_two_header = QLabel()
        column_two_header.setText("Winner")
        self.layout.addWidget(
            column_two_header, start_row, 1, alignment=Qt.AlignHCenter
        )
        column_two_header.setStyleSheet("font-weight: bold")

        column_three_header = QLabel()
        column_three_header.setText("Satisfaction")
        self.layout.addWidget(
            column_three_header, start_row, 2, alignment=Qt.AlignHCenter
        )
        column_three_header.setStyleSheet("font-weight: bold")

        self.checkbox_map = QCheckBox("Show quadrant map", parent=self)
        self.checkbox_map.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.checkbox_map.stateChanged.connect(self.toggleMapImage)
        self.layout.addWidget(
            self.checkbox_map, start_row, 3, Qt.AlignRight | Qt.AlignVCenter
        )

        for row, voting_rule in enumerate(self.election.results, start=start_row + 1):
            # Create label with name to find it later with findChild if necessary
            label_voting_rule = QLabel(parent=self)
            label_winner = QLabel(parent=self)
            label_satisfaction = QLabel(parent=self)

            show_btn = QPushButton(parent=self)

            # Connect buttons to emitting signals
            if voting_rule in {VotingRulesConstants.CONDORCET_SIMPLE, VotingRulesConstants.CONDORCET_COPELAND}:
                show_btn.clicked.connect(partial(self.showDirectedGraph, voting_rule, False))
                show_btn.setText("Show graph")

            elif voting_rule == VotingRulesConstants.CONDORCET_SIMPSON:
                show_btn.clicked.connect(partial(self.showDirectedGraph, voting_rule, True))
                show_btn.setText("Show graph")

            else:
                show_btn.clicked.connect(partial(self.showChart, voting_rule))
                show_btn.setText("Show chart")

            label_voting_rule.setText(VotingRulesConstants.UI[voting_rule])

            self.sig_poll_conducted.connect(
                partial(
                    self.setResultsLabel, label_winner, label_satisfaction, voting_rule
                )
            )
            self.setResultsLabel(label_winner, label_satisfaction, voting_rule)

            self.layout.addWidget(label_voting_rule, row,
                                  0, alignment=Qt.AlignHCenter)
            self.layout.addWidget(label_winner, row, 1,
                                  alignment=Qt.AlignHCenter)
            self.layout.addWidget(label_satisfaction, row,
                                  2, alignment=Qt.AlignHCenter)

            self.layout.addWidget(show_btn, row, 3, alignment=Qt.AlignHCenter)

    @ Slot(QLabel, QLabel, str)
    def setResultsLabel(self, winner_label: QLabel, satisf_label: QLabel, voting_rule: str) -> None:
        """Change the text of labels which displays the full name of the candidate-winner and his rate of satisfaction.

        Useful for polls when the winner of the election can be changed. 
        Called every time when the new poll has been conducted and the signal `sig_poll_conducted` has been emitted. 

        Args:
            winner_label (PySide6.QtWidgets.QLabel): A label which displays the full name of the candidate-winner.
            satisf_label (PySide6.QtWidgets.QLabel): A label which displays the rate of satisfaction. 
            voting_rule (str): A constante associated to the voting rule. 
        """

        winner = self.election.choose_winner(voting_rule)
        # None can be in Condorcet simple
        if winner is None:
            winner_label.setText("No winner")
            satisf_label.setText("---")
        else:
            winner_label.setText(f"{winner.first_name} {winner.last_name}")
            satisfaction = self.election.calc_satisfaction(winner)
            satisf_label.setText(f"{satisfaction:.2f}")

    @ Slot()
    def conductNewPoll(self) -> None:
        """Conduct a new poll. Desactivate a button which allows to conduct a new poll if the polls limit has been reached. 
        Redraw the political map, update texts of labels. Update charts data. """

        # Conduct new poll
        self.election.conduct_poll()
        # Update the number of polls 
        self.nb_polls_conducted += 1
        # Update a part of the interface corresponding to poll 
        self.remaining_polls_label.setText(
            f"Polls {self.nb_polls_conducted}/{self.election.nb_polls}"
        )
        # Desactivate the button if the limit has been reached
        if self.nb_polls_conducted == self.election.nb_polls:
            self.start_poll_btn.setEnabled(False)

        # Redraw the political map 
        self.map_image.update()
        # Update labels
        self.sig_poll_conducted.emit()

        # Change data of correponding charts
        if self.charts_view:
            self.charts_view.sig_poll_conducted.emit(
                self.election.poll_voting_rule)

    @ Slot(int)
    def toggleMapImage(self, state: int) -> None:
        """Show or hide the widget with the political map when the checkbox `checkbox_map` is checked/unchecked.

        Args:
            state (int): The state of the checkbox (0 for unchecked, positive integer for checked).
        """

        if state and (not self.map_image.isVisible()):
            self.map_image.show()
        elif (not state) and self.map_image.isVisible():
            self.map_image.close()

    @ Slot()
    def toggleCheckbox(self) -> None:
        """Desactivate the checkbox `checkbox_map` if the widget with the politcal map has been closed."""

        self.checkbox_map.setChecked(False)

    @ Slot(str)
    def showChart(self, voting_rule: str) -> None:
        """Show a chart with the results of the voting rule `voting_rule`

        Args:
            voting_rule (str): A constante related to the one round or multi-round voting rule.
                The voting rule should have been chosen in the election.
        """

        self.sig_show_chart.emit(voting_rule)
        self.charts_view.raise_()

    @ Slot(bool)
    def showDirectedGraph(self, voting_rule: str, weighted: Optional[bool] = False) -> None:
        """Show the graph corresponding to the given voting rule.

        Args:
            voting_rule (str): A constant related to the Condorcet-based voting rule. 
            weighted (Optional[bool]): If `True`, show oriented graph weights (Simpson method only).
                If `False`, show oriented graph without weights. Default = `False`
        """

        if voting_rule not in self.graphs_scenes:
            return

        scene = self.graphs_scenes[voting_rule]
        scene.drawGraphics(weighted)
        self.graph_view.setScene(scene)
        self.graph_view.show()
        self.graph_view.raise_()

    @ Slot()
    def destroyChildren(self) -> None:
        """Delete children-widgets whose parent is `None`"""

        self.map_image.deleteLater()
        # All Condorcet-based
        if self.graph_view:
            self.graph_view.deleteLater()

        # All one round, multi-round 
        if self.charts_view:
            self.charts_view.deleteLater()
