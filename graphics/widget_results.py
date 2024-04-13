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
    """Une classe qui représente la widget avec les résultats d'une élection,
    permet de voir les graphes et les diagrammes et de lancer les sondages."""

    sig_show_chart = Signal(str)
    """Un signal émis lorsqu'il faut de changer un diagramme à bandes avec une visualisation des diagrammes visibles."""

    sig_poll_conducted = Signal()
    """Un signal émis lorsqu'un nouveau sondage a été effectué."""

    def __init__(self, parent: QWidget):
        """Initialise la taille des views nécessaires et UI.

        Args:
            parent (PySide6.QtWidgets.QWidget): Un parent d'un widget.
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
        """Initialise les views pour les diagrammes à bandes si au moins une règle de vote à 1 ou plusieurs tour a été choisie.
        Initialise les views pour les graphes si au moins une règle de vote Condorcet-cohérente a été choisie."""

        if self.condorcet_bool:
            # Un dictionnaire qui associe voting_rule : QGraphicsScene
            self.graphs_scenes = dict()
            self.initDirectedGraph(self.condorcet_set)

        if self.one_round_bool or self.multi_round_bool:
            self.initChartsView()

        if self.one_round_bool:
            self.charts_view.initOneRoundChart(self.one_round_set)

        if self.multi_round_bool:
            self.charts_view.initMultiRoundChart(self.multi_round_set)

    def oneRoundChosen(self) -> tuple[bool, Set[str]]:
        """Trouve les règles de vote à un tour choisies.

        Returns:
            tuple[bool, Set[str]]: un booléan True si au moins 1 règle de vote à 1 tour a été choisie (False sinon)
                et un ensemble des constantes de telles règles de vote.
        """

        intersect = VotingRulesConstants.ONE_ROUND & self.election.results.keys()
        return bool(intersect), intersect

    def condorcetChosen(self) -> tuple[bool, Set[str]]:
        """Trouve les règles de vote Condorcet-cohérentes choisies.

        Returns:
            tuple[bool, Set[str]]: un booléan True si au moins une règle de vote Condorcet-cohérente a été choisie (False sinon)
                et un ensemble des constantes de telles règles de vote.
        """

        intersect = VotingRulesConstants.CONDORCET & self.election.results.keys()
        return bool(intersect), intersect

    def multiRoundChosen(self) -> tuple[bool, Set[str]]:
        """Trouve les règles de vote à plusieurs tours choisies.

        Returns:
            tuple[bool, Set[str]]: un booléan True si au moins une règle de vote à plusieurs tours a été choisie (False sinon)
                et un ensemble des constantes de telles règles de vote
        """

        intersect = VotingRulesConstants.MULTI_ROUND & self.election.results.keys()
        return bool(intersect), intersect

    def initDirectedGraph(self, condorcet_voting_rules: Set[str]) -> None:
        """Initialise les `PySide6.QtWidgets.QGraphicsScene` et `PySide6.QtWidgets.QGraphicsView` pour afficher les résultats
        des règles de vote Condorcet-cohérentes. Construit un dictionnaire du type `Dict[str, PySide6.QtWidgets.QGraphicsScene]`
        qui associe à chaque constante d'une règle de vote Condorcet-cohérente un `QGraphicsScene`.

        Args:
            condorcet_voting_rules (Set[str]): Un ensemble des constantes des règles de vote Condorcet-cohérentes choisies.
                N'est pas vide.
        """

        graph_scene = None

        for voting_rule in condorcet_voting_rules:
            graph_scene = DirectedGraph(self.getViewSize(), voting_rule, parent=self)
            self.graphs_scenes[voting_rule] = graph_scene

        self.graph_view = DirectedGraphView(graph_scene)
        self.resizeView(self.graph_view)

    def initChartsView(self) -> None:
        """Initialise les `from PySide6.QtCharts.QChartView` pour afficher les résultats
        des règles de vote à 1 ou plusieurs tours."""

        self.charts_view = ChartView()
        self.resizeView(self.charts_view)

        self.sig_show_chart.connect(self.charts_view.setChartBySig)

    def getViewSize(self) -> QSize:
        """Calcule la taille du view en fonction de la taille du parent d'un widget.

        Returns:
            PySide6.QtCore.QSize: La taille du view.
        """

        return QSize(self.parent().width() * 0.7, self.parent().height() * 0.7)

    def resizeView(self, view: Union[QGraphicsView, QChartView]) -> None:
        """Change la taille d'un view donné.

        Args:
            view (Union[PySide6.QtCharts.QChartView, PySide6.QtWidgets.QGraphicsView]): Un view dont la taille doit être changer.
        """

        view.resize(self.getViewSize())

    def initUI(self) -> None:
        """Initialise un layout et UI. Initialise la partie d'interface correspondant aux sondages
        uniquement si nécessaire. Initialise un widget pour afficher la carte politique."""

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(10)

        if self.conduct_polls:
            self.initPollsUI()

        self.initTable()

        self.map_image = MapImage(self.getViewSize())
        self.map_image.closed.connect(self.toggleCheckbox)

    def initPollsUI(self) -> None:
        """Initialise la partie d'interface correspondant aux sondages."""

        # Nombre des sondages
        self.nb_polls_conducted = 1

        self.remaining_polls_label = QLabel(self)
        self.remaining_polls_label.setStyleSheet("font-weight: bold")
        self.remaining_polls_label.setText(
            f"Polls {self.nb_polls_conducted}/{self.election.nb_polls}"
        )

        self.start_poll_btn = QPushButton("Apply new poll", self)

        # Ajouter au layout (en haut)
        self.layout.addWidget(
            self.remaining_polls_label, 0, 0, Qt.AlignmentFlag.AlignHCenter
        )
        self.layout.addWidget(self.start_poll_btn, 0, 1, 1, 3)

        # Désactiver le button si aucune règle du vote à 1 tour a été choisie
        if not self.one_round_bool:
            self.start_poll_btn.setEnabled(False)
            return

        # Faire une connection au slot uniquement si nécessaire
        self.start_poll_btn.clicked.connect(partial(self.conductNewPoll))

    def initTable(self) -> None:
        """Initialise une partie d'interface correpondant au tableau des résultats."""

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
        """Change le texte des labels qui affichent le nom du gagnant et le taux de satisfaction.
        Utile pour les sondages quand le gagnant d'une élection peut changer.
        Appelée à chaque fois  qu'un nouveau sondage a été effectuée et un signal `sig_poll_conducted` a été émis.

        Args:
            winner_label (PySide6.QtWidgets.QLabel): Un label qui afficher le nom du gagnant.
            satisf_label (PySide6.QtWidgets.QLabel): Un label qui afficher le taux de satisfaction.
            voting_rule (str): Une constante associée à une règle du vote.
        """

        winner = self.election.choose_winner(voting_rule)
        # None peut arriver dans un Condorcet simple
        if winner is None:
            winner_label.setText("No winner")
            satisf_label.setText("---")
        else:
            winner_label.setText(f"{winner.first_name} {winner.last_name}")
            satisfaction = self.election.calc_satisfaction(winner)
            satisf_label.setText(f"{satisfaction:.2f}")

    @ Slot()
    def conductNewPoll(self) -> None:
        """Effectue un nouveau sondage. Désactive un button qui permet de lancer un sondage
        si la limite des sondages a été atteinte. Redessiner la carte politique. MAJ les textes des labels.
        MAJ les données des charts."""

        # Effectuer une nouvelle sondage
        self.election.conduct_poll()
        # MAJ du nb des sondages
        self.nb_polls_conducted += 1
        # MAJ d'une partie d'interface correspondante au nb des sondages
        self.remaining_polls_label.setText(
            f"Polls {self.nb_polls_conducted}/{self.election.nb_polls}"
        )
        # Désactiver le button si limite
        if self.nb_polls_conducted == self.election.nb_polls:
            self.start_poll_btn.setEnabled(False)

        # Redéssiner la carte politique
        self.map_image.update()
        # MAJ des labels
        self.sig_poll_conducted.emit()

        # Changer les données dans le chart correspondant
        if self.charts_view:
            self.charts_view.sig_poll_conducted.emit(
                self.election.poll_voting_rule)

    @ Slot(int)
    def toggleMapImage(self, state: int) -> None:
        """Affiche ou cache la carte politique lorsqu'un `checkbox_map` est coché ou décoché.

        Args:
            state (int): L'état du checkbox (0 si décoché, en entier positif si coché).
        """

        if state and (not self.map_image.isVisible()):
            self.map_image.show()
        elif (not state) and self.map_image.isVisible():
            self.map_image.close()

    @ Slot()
    def toggleCheckbox(self) -> None:
        """Désactive un `checkbox_map` si la carte politique a été fermée."""

        self.checkbox_map.setChecked(False)

    @ Slot(str)
    def showChart(self, voting_rule: str) -> None:
        """Affiche le de diagramme à bandes correspondant à une règle de vote donnée.

        Args:
            voting_rule (str): Une constante associée à une règle du vote à un ou plusieurs tours
            dont un diagramme à bandes il faut afficher.
        """

        self.sig_show_chart.emit(voting_rule)

    @ Slot(bool)
    def showDirectedGraph(self, voting_rule: str, weighted: Optional[bool] = False) -> None:
        """Affiche le graphe correspondant à une règle de vote donnée (Condorcet-cohérente).

        Args:
            voting_rule (str): Une constante associée à une règle du vote Condorcet-cohérente dont le graphe 
                il faut afficher.
            weighted (Optional[bool]): si True, affiche le graphe orientés avec les poids (pour Simpson uniquement).
                Si False, affiche le graphe orientés sans les poids. Default = False.
        """

        if voting_rule not in self.graphs_scenes:
            return

        scene = self.graphs_scenes[voting_rule]
        scene.drawGraphics(weighted)
        self.graph_view.setScene(scene)
        self.graph_view.show()

    @ Slot()
    def destroyChildren(self) -> None:
        """Supprime les widget-enfants d'un widget dont le parent à été remis à `None`."""

        self.map_image.deleteLater()
        # Tous Condorcet
        if self.graph_view:
            self.graph_view.deleteLater()

        # Tous 1 tour, plusieurs tours
        if self.charts_view:
            self.charts_view.deleteLater()
