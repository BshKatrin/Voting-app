"""Un module définissant une classe `WidgetResults`.

Ce module fournit une classe `WidgetResults` qui représente un widget avec des résultats d'une élection,
permet de voir les graphs et de lancer des sondages.

Attributs:
    Widgets:
        - graph_view (graphics.widget_results_utls.directed_graphs.directed_graph_view): Un view permettant d'afficher des graphes 
            orientés des résultats des règles du vote Condorcet-cohérentes.
        - charts_view (graphics.widget_results_utls.charts.chart_view): Un view permettant d'afficher des diagrammes à bandes
            des résultats des règles du vote à 1 et plusieurs tours.
        - conduct_polls (bool): Une indication si les sondages seront effectuées ou pas.

    Données d'une élection:
        - election (electoral_systems.election.Election) : une instance de la classe `Election` pour partager les données entre les widgets.

Methodes:
    - initViews: Initialiser des views nécessaires.
    - oneRoundChosen: Vérifier si des règles du vote à 1 tour ont été choisies.
    - condorcetChosen: Vérifier si des règles du vote Condorcet-cohérentes ont été choisies.
    - multiRoundChosen: Vérifier si des règles du vote à plusieurs tours ont été choisies.
    - initDirectedGraph: Initialiser des graphes orientés pour afficher des résultats des règles du vote Condorcet-cohérentes.
    - initChartsView: Initialiser des diagrammes à bandes pour afficher des résultats des règles du vote à 1 et plusieurs tours.
    - getViewSize: Calculer la taille des views.
    - resizeView: Changer la taille des views.
    - initUI: Initialiser une interface complète.
    - initPollsUI: Initialiser une partie d'interface correspondante aux sondages.
    - initTable: Initialiser une partie d'interface correpondante au tableau des résultats.

Slots:
    - setResultsLabel: Un slot permettant de changer le contenu des labels d'un tableau des résultats.
    - conductNewPoll: Un slot permettant d'effectuer une nouvelle sondage.
    - toggleMapImage: Un slot permettant d'afficher ou de cacher la carte politique.
    - toggleCheckbox: Un slot permettant de décocher le checkbox si la carte politique a été cachée.
    - showChart: Un slot permettant d'afficher un diagramme à bandes.
    - showDirectedGraph: Un slot permettant d'affciher un graphe.
    - destroyChildren: Un slot permettant de détruire des *widget-enfants* dont le parent a été remis à `None`.


Signals:
    - sig_show_chart (PySide6.QtCore.QSignal): Un signal émis lorsqu'il faut de changer un diagramme à bandes
        avec un view des diagrammes visible.
    - sig_poll_conducted (PySide6.QtCore.QSignal): Un signal émis lorsqu'une nouvelle sondange a été effectuée.
"""


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
    sig_show_chart = Signal(str)
    sig_poll_conducted = Signal()

    def __init__(self, parent: QWidget):
        """Initialiser la taille, des views nécessaires et une interface complète.

        Args:
            parent (PySide6.QtWidgets.QWidget): Un parent d'un widget.
        """

        super().__init__(parent)

        self.election = Election()

        self.setGeometry(0, 0, parent.width(), parent.height())

        self.graph_view = None
        self.charts_view = None

        self.conduct_polls = True if self.election.nb_polls else False

        self.initViews()
        self.initUI()

    def initViews(self) -> None:
        """Initialiser les views pour  des diagrammes à bandes si au moins une règle du vote à 1 ou plusieurs tour a été choisie.
        Initialiser les views pour des graphes si au moins une règle du vote Condorcet-cohérente a été choisie."""
        if self.condorcetChosen():
            self.initDirectedGraph()

        self.oneRoundBool, self.oneRoundSet = self.oneRoundChosen()
        self.multiRoundBool, multiRoundSet = self.multiRoundChosen()

        if self.oneRoundBool or self.multiRoundBool:
            self.initChartsView()

        if self.oneRoundBool:
            self.charts_view.initOneRoundChart(self.oneRoundSet)

        if self.multiRoundBool:
            self.charts_view.initMultiRoundChart(multiRoundSet)

    # Returns True iff veto, plurality(1 round), veto, borda or approval was chosen
    def oneRoundChosen(self) -> tuple[bool, Set[str]]:
        """Trouver des règles du vote à 1 tour choisies.

        Returns:
            tuple[bool, Set[str]]: un booléan True si au moins 1 règle du vote à 1 tour a été choisie (False sinon)
                et un ensemble des constantes de telles règles du vote
        """
        intersect = VotingRulesConstants.ONE_ROUND & self.election.results.keys()
        return bool(intersect), intersect

    # Returns True iff one the condorcet method was chosen
    def condorcetChosen(self) -> bool:
        """Trouver des règles du vote à 1 tour choisies.

        Returns:
            bool: True si au moins 1 règle du vote Condorcet-cohérente a été choisie.
        """
        setCondorcet = VotingRulesConstants.CONDORCET
        return bool(setCondorcet & self.election.results.keys())

    def multiRoundChosen(self) -> tuple[bool, Set[str]]:
        """Trouver des règles du vote à 1 tour choisies.

        Returns:
            tuple[bool, Set[str]]: un booléan True si au moins 1 règle du vote à plusieurs tour a été choisie (False sinon)
                et un ensemble des constantes de telles règles du vote
        """
        intersect = VotingRulesConstants.MULTI_ROUND & self.election.results.keys()
        return bool(intersect), intersect

    def initDirectedGraph(self) -> None:
        """Initialiser les `PySide6.QtWidgets.QGraphicsScene` et `PySide6.QtWidgets.QGraphicsView` pour afficher des résultats
        des règles du vote Condorcet-cohérentes."""

        self.graph_scene = DirectedGraph(self.getViewSize(), parent=self)
        self.graph_view = DirectedGraphView(self.graph_scene)
        self.resizeView(self.graph_view)

    def initChartsView(self) -> None:
        """Initialiser les `from PySide6.QtCharts.QChartView` pour afficher des résultats 
        des règles du vote à 1 ou plusieurs tours."""

        self.charts_view = ChartView()
        self.resizeView(self.charts_view)

        self.sig_show_chart.connect(self.charts_view.setChartBySig)

    def getViewSize(self) -> QSize:
        """Retourner la taille des views en fonction de la taille du parent d'un widget."""

        return QSize(self.parent().width() * 0.7, self.parent().height() * 0.7)

    def resizeView(self, view: Union[QGraphicsView, QChartView]) -> None:
        """Changer la taille d'un view donné."""

        view.resize(self.getViewSize())

    def initUI(self) -> None:
        """Initialiser un layout et une interface complète. Initialiser une partie d'interface correspondant aux sondages
        uniquement si nécessaire. Initialiser un widget pour afficher la carte politique."""

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(10)
        # Add polls row only if nb_polls != 0
        # and at least one of 1 round voting rules were chosen
        if self.conduct_polls:
            self.initPollsUI()

        self.initTable()

        self.map_image = MapImage()
        self.map_image.closed.connect(self.toggleCheckbox)

    def initPollsUI(self) -> None:
        """Initialiser la partie d'interface correspondante aux sondages."""

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
        if not self.oneRoundBool:
            self.start_poll_btn.setEnabled(False)
            return

        # Faire une connection au slot uniquement si nécessaire
        self.start_poll_btn.clicked.connect(partial(self.conductNewPoll))

    def initTable(self) -> None:
        """Initialiser une partie d'interface correpondante au tableau des résultats."""

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

        self.checkbox = QCheckBox("Show quadrant map", parent=self)
        self.checkbox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.checkbox.stateChanged.connect(self.toggleMapImage)
        self.layout.addWidget(
            self.checkbox, start_row, 3, Qt.AlignRight | Qt.AlignVCenter
        )

        for row, voting_rule in enumerate(self.election.results, start=start_row + 1):
            # Create label with name to find it later with findChild if necessary
            label_voting_rule = QLabel(parent=self)
            label_winner = QLabel(parent=self)
            label_satisfaction = QLabel(parent=self)

            show_btn = QPushButton(parent=self)

            # Connect buttons to emitting signals
            if voting_rule in {
                VotingRulesConstants.CONDORCET_SIMPLE,
                VotingRulesConstants.CONDORCET_COPELAND,
            }:
                show_btn.clicked.connect(self.showDirectedGraph)
                show_btn.setText("Show graph")
            elif voting_rule == VotingRulesConstants.CONDORCET_SIMPSON:
                show_btn.clicked.connect(lambda: self.showDirectedGraph(True))
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

    @Slot(QLabel, QLabel, str)
    def setResultsLabel(self, winner_label: QLabel, satisf_label: QLabel, voting_rule: str) -> None:
        """Changer le text des labels qui affichent le nom du gagnant et du taux de satisfaction.
        Utile pour les sondages quand le gagnant d'une élection peut changer.
        Appelé chaque foir lorsque une nouvelle sondage a été effectuée et un signal `sig_poll_conducted` a été émis."""

        winner = self.election.choose_winner(voting_rule)
        # None peut arriver dans un Condorcet simple
        if winner is None:
            winner_label.setText("No winner")
            satisf_label.setText("---")
        else:
            winner_label.setText(f"{winner.first_name} {winner.last_name}")
            satisfaction = self.election.calc_satisfaction(winner)
            satisf_label.setText(f"{satisfaction:.2f}")

    @Slot()
    def conductNewPoll(self) -> None:
        """Effectuer une nouvelle sondage. Désactiver un button qui permet de lancer une sondage
        si la limite des sondages a été atteinte."""

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

    @Slot(int)
    def toggleMapImage(self, state: int) -> None:
        """Afficher ou cacher la carte politique lorsque un checkbox est coché ou décoché."""

        if state and (not self.map_image.isVisible()):
            self.map_image.show()
        elif (not state) and self.map_image.isVisible():
            self.map_image.close()

    @Slot()
    def toggleCheckbox(self) -> None:
        """Désactiver un checkbox si la carte politique a été fermée."""
        self.checkbox.setChecked(False)

    @Slot(str)
    def showChart(self, voting_rule: str) -> None:
        """Afficher un de diagramme à bandes correspondant à une règle du vote donnée.

        Args:
            voting_rule (str): une règle du vote à 1 ou plusieurs tours dont un diagramme à bandes il faut afficher.
        """

        self.sig_show_chart.emit(voting_rule)

    @Slot(bool)
    def showDirectedGraph(self, weighted: Optional[bool] = False) -> None:
        """Afficher le graphe correspondant à une règle du vote donnée (Condorcet-cohérente).

        Args:
            weighted (Optional[bool]): si True, afficher le graphe orientés avec les poids (pour Simpson uniquement).
                Si False, afficher le graphe orientés sans les poids.
        """

        self.graph_scene.drawGraphics(weighted)
        self.graph_view.show()

    @Slot()
    def destroyChildren(self) -> None:
        """Supprimer les widget-enfants d'un widget dont le parent à été remis à `None`."""
        self.map_image.deleteLater()
        # Tous Condorcet
        if self.graph_view:
            self.graph_view.deleteLater()
        # Tous 1 tour, plusieurs tours
        if self.charts_view:
            self.charts_view.deleteLater()
