from typing import Set, Optional, List, Union, Dict
from math import sqrt
from random import random

from .utls import Singleton, NameIterator, IdIterator
from .election_constants import RandomConstants, VotingRulesConstants
from .extensions.polls import (
    add_elector_data,
    add_candidate_data,
    get_default_directions_data,
    set_avg_electors_positions,
    set_std_deviation,
    change_position_candidates,
    change_ranking_electors,
    direction_data_type
)
from .extensions.liquid_democracy import choose_delegee, choose_possible_delegees
from .voting_rules.utls import set_duels_scores, sort_cand_by_value, sort_cand_by_round, duels_type

from people import Candidate, Elector

from codecarbon import track_emissions

# Pour une génération des docs uniquement 
__pdoc__ = {
    'random':False,
    'Election._init_results_keys':True,
    'Election._calc_distance':True,
    'Election._define_ranking':True,
    'Election._calc_proportion_satisfaction':True,
    'Election._make_delegations':True
}

class Election(metaclass=Singleton):
    """Une classe Singleton qui contient toutes les données nécessaires à une élection."""

    def __init__(self):
        super().__init__()
        self.electors:List[Elector] = []
        """Une liste qui stocke tous les électeurs qui participent dans une élection."""

        self.candidates = []
        """Une liste qui stocke tous les candidats qui participent dans une élection."""

        self.first_name_iter = NameIterator()
        """Un itérateur qui génére des prénoms des candidats (uniquement pour les données générées aléatoirement)"""

        self.last_name_iter = NameIterator()
        """Un itérateur qui génére des noms des candidats (uniquement pour les données générées aléatoirement)"""

        self.id_iter = IdIterator(0)
        """Un itérateur qui génére des IDs des candidats et des électeurs."""

        # Stocke les resultats
        self.results:Dict[str, List[Candidate]] = dict()
        """Un dictionnaire qui stocke un classement des candidats (dans l'ordre décroissant) pour chaque règle de vote choisie."""

        # Stocke les duels
        self.duels_scores:duels_type = dict()
        """Un dictionnaire qui stocke les résultats des duels entre les candidats."""

        # Pour la satisfaction
        self.average_position_electors:tuple[float, float] = (0, 0)
        self.proportion_satisfaction:float = 0
        """La distance maximale entre la position moyenne des électeurs et la position de chaque candidat."""

        self.directions_data:Dict[str, direction_data_type] = get_default_directions_data()
        """Un dictionnaire dont chaque clé correpond à la division de la carte politique et 
        chaque valeur est un dictionnaire avec les données remises par défaut. Pour les sondages uniquement."""

        # Init les constantes
        self.set_default_settings()

    def set_default_settings(self) -> None:
        """Initialise les réglages par défaut."""

        # Nb de sondages à faire
        self.nb_polls:int = 0

        # Active/désactive la démocratie liquide
        self.liquid_democracy_activated = False

        # Une règle de vote pour les sondages
        self.poll_voting_rule = VotingRulesConstants.PLURALITY_SIMPLE

        # Active/désactive un tie-break selon les duels
        self.tie_breaker_activated = True

        # Les constantes de la génération des données
        self.generation_constants = dict()
        for type, default_value in RandomConstants.DEFAULT_VALUES.items():
            self.generation_constants[type] = default_value

    def _init_results_keys(self, set_keys: Set[str]) -> None:
        """Initialiser des clés du dictionnaire `results` avec des constantes associées aux règles du vote choisies.
        Les valeurs sont remises à `None`.
        """

        for key in set_keys:
            self.results[key] = None

    def _calc_distance(self, point1: tuple[float, float], point2: tuple[float, float]) -> float:
        """Calcule la distance euclidienne entre 2 points.

        Args:
            point1 (tuple[float, float]): position sur la carte politique
            point2 (tuple[float, float]): position sur la carte politique
        Returns:
            float: La distance euclidienne entre 2 points.
        """
        x1, y1 = point1
        x2, y2 = point2
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def has_electors_candidates(self) -> bool:
        """Vérifie qu'il existe au moins un électeur et un candidat dans une élection.

        Returns:
            bool: `True` s'il existe au moins un électeur et un candidat dans une élection, sinon `False`.
        """

        if not self.electors and not self.candidates:
            return False
        return True

    def add_elector_import(self, new_elector: Elector) -> None:
        """Ajoute un électeur dont les données sont déjà initialisées. 
        Si les sondages sont activés, MAJ des données sur les directions de la carte politique. 
        MAJ des données sur la position moyenne de tous les électeurs participants à l'élection. 
        Utilisée lors d'une importation de données.

        Args:
            new_elector (people.elector.Elector): Un nouvel électeur.
        """

        if self.nb_polls:
            add_elector_data(self.directions_data, new_elector)

        x, y = new_elector.position
        x_avg, y_avg = self.average_position_electors
        x_avg, y_avg = x_avg + x, y_avg + y
        self.average_position_electors = (x_avg, y_avg)

        self.electors.append(new_elector)

    def add_elector(self, position: tuple[float, float]) -> None:
        """Ajoute un nouvel électeur dans une élection avec sa position position. 
        Si les sondages sont activés, MAJ des données sur les directions de la carte politique. 
        MAJ des données sur la position moyenne de tous les électeurs participants à l'élection.

        Args:
            position (tuple[float, float]): La position d'un électeur sur la carte politique. 
                Chaque coordonnée doit être bornée entre -1 et 1.
        """

        knowledge_const = self.generation_constants[RandomConstants.KNOWLEDGE]
        new_elector = Elector(
            id=next(self.id_iter), position=position, knowledge_const=knowledge_const
        )
        x, y = new_elector.position

        if self.nb_polls:
            add_elector_data(self.directions_data, new_elector)

        # All electors average
        x_avg, y_avg = self.average_position_electors
        x_avg, y_avg = x_avg + x, y_avg + y
        self.average_position_electors = (x_avg, y_avg)
        self.electors.append(new_elector)

    def add_candidate_import(self, new_candidate: Candidate) -> None:
        """Ajoute un candidat dont les données sont déjà initialisées. 
        Si les sondages sont activés, MAJ des données sur les directions de la carte politique. 
        Utilisée lors d'une importation de données.

        Args:
            new_elector (people.elector.Elector): Un nouvel électeur.
        """

        self.candidates.append(new_candidate)
        if self.nb_polls:
            add_candidate_data(self.directions_data, new_candidate)

    def add_candidate(self, position: tuple[float, float], first_name: Optional[str] = "", last_name: Optional[str] = "") -> None:
        """Ajoute un nouveau candidat dans une élection avec sa position position, 
        et éventuellement son nom (`last_name`) et son prénom (`first_name`). Si les sondages sont activés, 
        MAJ des données sur les directions de la carte politique.

        Args:
            position (tuple[float, float]): La position d'un candidat sur la carte politique. 
                Chaque coordonnée doit être bornée entre -1 et 1.
            first_name (Optional[str]): Le prénom d'un candidat.
            last_name (Optional[str]): Le nom d'un candidat.
        """

        dogmat_const = self.generation_constants[RandomConstants.DOGMATISM]
        oppos_const = self.generation_constants[RandomConstants.OPPOSITION]

        first_name = next(self.first_name_iter) if not first_name else first_name
        last_name = next(self.last_name_iter) if not last_name else last_name

        new_candidate = Candidate(
            id=next(self.id_iter),
            position=position,
            first_name=first_name,
            last_name=last_name,
            dogmatism_const=dogmat_const,
            opposition_const=oppos_const,
        )
        if self.nb_polls:
            add_candidate_data(self.directions_data, new_candidate)

        self.candidates.append(new_candidate)

    # @track_emissions(project_name="voting_rule", output_dir = 'codecarbon', output_file = '10-3000.csv', measure_power_secs=5)
    def apply_voting_rule(self, voting_rule: str) -> None:
        """Applique une règle de vote voting_rule. 
        Remplit la case correspondante à voting_rule du dictionnaire results avec une liste (un classement) des candidats. 
        La fonction est appliquée uniquement s'il existe au moins un électeur et un candidat, sinon elle ne fait rien.

        Args:
            voting_rule (str): Une constante correspondant à une règle de vote.
        """
        print("Applying voting rule", VotingRulesConstants.UI[voting_rule])
        if not self.has_electors_candidates():
            return

        result = []
        func = VotingRulesConstants.VOTING_RULES_FUNC[voting_rule]

        if voting_rule in VotingRulesConstants.CONDORCET:
            result = func(self.electors, self.candidates, self.duels_scores)

        if voting_rule in VotingRulesConstants.ONE_ROUND:
            if voting_rule == VotingRulesConstants.APPROVAL:
                result = func(
                    self.electors,
                    self.candidates,
                    VotingRulesConstants.APPROVAL_GAP_COEF,
                    self.duels_scores if self.tie_breaker_activated else None,
                )
            else:
                result = func(
                    self.electors,
                    self.candidates,
                    self.duels_scores if self.tie_breaker_activated else None,
                )

        if voting_rule in VotingRulesConstants.MULTI_ROUND:
            result = func(self.electors, self.candidates)

        self.results[voting_rule] = result

    def choose_winner(self, voting_rule: str) -> Union[Candidate, None]:
        """Retourne le gagnant d'après la règle de vote voting_rule.

        Args:
            voting_rule (str): Une constante correspondant à une règle de vote.

        Returns:
            Union[Candidate, None]: Un candidat-gagnant. Peut retourner `None` dans le cas de la règle de vote *Condorcet simple*
                ou si le classement associé à voting_rule est vide.
        """
        if voting_rule not in self.results:
            self.apply_voting_rule(voting_rule)

        if not len(self.results[voting_rule]):
            return None

        if voting_rule in VotingRulesConstants.MULTI_ROUND:
            return self.results[voting_rule][-1][0]

        if voting_rule == VotingRulesConstants.CONDORCET_SIMPLE:
            return self.choose_condorcet_winner()

        return self.results[voting_rule][0]

    def choose_condorcet_winner(self) -> Union[Candidate, None]:
        """Retourne le gagnant d'après le système de vote "Condorcet simple". 
        Le gagnant est un candidat qui bat tous les autres en duel.

        Returns:
            Union[Candidate, None]: Un candidat du Condorcet s'il existe, sinon`None`.
        """

        fst_candidate = self.results[VotingRulesConstants.CONDORCET_SIMPLE][0]
        score = fst_candidate.scores[VotingRulesConstants.CONDORCET_SIMPLE]
        return fst_candidate if score == len(self.candidates) - 1 else None

    def _define_ranking(self) -> None:
        """Classe les candidats pour chaque électeur. Doit être appelée uniquement quand tous les candidats ont été ajoutés."""

        for elector in self.electors:
            elector.rank_candidates(self.candidates)

    def calc_results(self, imported: Optional[bool] = False) -> None:
        """Calcule les résultats d'une élection : calcule les duels entre les candidats, 
        attribue des scores aux candidats, et calcule le classement des candidats pour chaque règle de vote choisie.

        Args:
            imported (bool): True si les données ont été importés. Si oui, 
                ne calcule pas les duels et les scores des candidats pour chaque règle de vote choisie. 
                Ils sont importés. Cependant, un calcul des classements est effectué.
        """

        if imported:
            # Les duels sont importés dans sqlite.ImportData
            self.set_results()
            return

        self.duels_scores = set_duels_scores(self.electors, self.candidates)
        for voting_rule in self.results:
            self.apply_voting_rule(voting_rule)

    def set_avg_electors_position(self) -> None:
        """Calcule la position moyenne des électeurs. Uniquement la division est faite. 
        La somme de toutes les positions est déjà stockée."""

        x_avg, y_avg = self.average_position_electors
        x_avg /= len(self.electors)
        y_avg /= len(self.electors)
        self.average_position_electors = (x_avg, y_avg)

    def _calc_proportion_satisfaction(self) -> None:
        """Calcule la distance maximale entre la position moyenne des électeurs et la position
            de chaque candidat et la stock dans `Election.proportion_satisfaction`.
        """

        proportion = 0
        for candidate in self.candidates:
            dist_cand_electors = self._calc_distance(
                candidate.position, self.average_position_electors
            )
            proportion = max(proportion, dist_cand_electors)
        self.proportion_satisfaction = proportion

    def calc_satisfaction(self, candidate: Candidate) -> float:
        """Calcule le pourcentage de la population qui est satisfait par une victoire du candidat candidate dans une élection.  
        **Algorithme**:  
            - Calcule la distance du candidat par rapport a la position moyenne des électeurs  
            - Calcule la valeur absolue de la différence de cette distance moins la distance maximale (`proportion_satisfaction`)  
            - Calcule le pourcentage de satisfaction selon cette valeur absolue divisée par la valeur maximale (`proportion_satisfaction`)  
            - Renvoie ce pourcentage (plus la distance au point moyen est faible, plus le pourcentage sera élevé et inversement)  

        Args:
            candidate (people.candidate.Candidate): Un candidat-gagnant.

        Returns:
            float: Le pourcentage de satisfaction de la population.
        """

        diff = abs(
            self._calc_distance(candidate.position, self.average_position_electors)
            - self.proportion_satisfaction
        )
        percentage = (
            diff / self.proportion_satisfaction * 100
            if self.proportion_satisfaction != 0
            else 0
        )
        return percentage

    def set_results(self) -> None:
        """Calcule un classement des candidats selon leurs scores (les scores sont déjà attribués à chaque candidat). 
        Utilisée lors de l'importation des données. MAJ d'un dictionnaire results. 
        La fonction ne fait rien s'il n'existe pas au moins un électeur et un candidat.
        """

        if not self.has_electors_candidates():
            return
        # Assuming every candidate has the same voting_rules
        candidate = self.candidates[0]
        keys = candidate.scores.keys()

        duels = self.duels_scores if self.tie_breaker_activated else None
        for voting_rule in keys:
            if voting_rule in VotingRulesConstants.ONE_ROUND:
                result = sort_cand_by_value(self.candidates, voting_rule, nb_electors=len(self.electors), duels=duels)
                self.results[voting_rule] = result

            if voting_rule in VotingRulesConstants.MULTI_ROUND:
                self.results[voting_rule] = [None] * len(candidate.scores[voting_rule])

                for round in range(len(candidate.scores[voting_rule])):
                    result = sort_cand_by_round(self.candidates, voting_rule, round)
                    self.results[voting_rule][round] = result

            if voting_rule in VotingRulesConstants.CONDORCET:
                sort_asc = (
                    True
                    if voting_rule == VotingRulesConstants.CONDORCET_SIMPSON
                    else False
                )
                result = sort_cand_by_value(self.candidates, voting_rule, nb_electors=len(
                    self.electors), duels=None, scores_asc=sort_asc)
                self.results[voting_rule] = result

    def start_election(self, imported: Optional[bool] = False, chosen_voting_rules: List[str] = None) -> None:
        """Commence une élection. Fait tous les calculs nécessaires:  
            - Chaque électeur définit son classement de candidats  
            - MAJ de la position moyenne des électeurs  
            - Calcule le taux de satisfaction  
            - Si les sondages sont activés, MAJ des données pour chaque direction de la carte politique  
            - Si la démocratie liquide est activée, fait les délégations  
            - Initialise un dictionnaire results avec des règles de vote choisies  
            - Calcule les résultats  

        Args:
            imported (Optional[bool]): `True` si les données ont été importées, sinon `False`. 
                Cf. `Election.calc_results()` <electoral_systems.election.Election>
            chosen_voting_rules (Set[str]): Une liste des constantes des règles de vote choisies.
        """

        self._define_ranking()
        self.set_avg_electors_position()
        self._calc_proportion_satisfaction()

        # Set data for polls
        if self.nb_polls:
            set_avg_electors_positions(self.directions_data)
            set_std_deviation(self.directions_data, len(self.electors))
        if self.liquid_democracy_activated:
            self._make_delegations()
        if chosen_voting_rules:
            self._init_results_keys(chosen_voting_rules)
            
        self.calc_results(imported)

    def _make_delegations(self) -> None:
        """Pour une démocratie liquide. Pour chaque électeur décide s'il fera une délégation de son vote.
        Si oui, MAJ des données de son délégataire et de lui-même."""

        for elector in self.electors:
            proba = 1 - elector.knowledge
            # Pas de délégation
            if random() > proba:
                continue
            # Faire une délégation
            possible_delegees = choose_possible_delegees(
                self.electors, elector
            )
            delegee = choose_delegee(possible_delegees)
            if delegee is None:
                continue
            delegee.weight += elector.weight
            elector.weight = 0

    def conduct_poll(self) -> None:
        """Fait un nouveau sondage. Tout d'abord les candidats changent leurs positions. 
        Les électeurs redéfinissent leur classement de candidats. Puis les électeurs changent leur classement. 
        Cf. `electoral_systems.extensions.polls` pour les détails."""

        voting_rule = self.poll_voting_rule
        winner = self.choose_winner(voting_rule)
        ranking = self.results[voting_rule]

        # Des candidats changent leurs positions politiques
        change_position_candidates(
            self.candidates,
            winner,
            ranking,
            self.directions_data,
            self.generation_constants[RandomConstants.TRAVEL_DIST],
        )

        # Des électeurs changent leur classement
        self._define_ranking()

        # Des électeurs s'adaptent en changeant leur classement intelligemment
        score_winner = winner.scores[voting_rule]
        change_ranking_electors(
            self.electors,
            score_winner,
            voting_rule,
            VotingRulesConstants.APPROVAL_GAP_COEF,
        )
        # Recalcule des résultats
        self.calc_results()

    def delete_all_data(self) -> None:
        """Supprime toutes les données d'une élection. Relance les itérateurs-générateurs des noms, prénoms, IDs.
        Réinitialise le dictionnaire des données des divisions de la carte politique."""

        self.electors.clear()
        self.candidates.clear()
        self.results.clear()

        self.first_name_iter.restart()
        self.last_name_iter.restart()
        self.id_iter.restart()

        self.directions_data = get_default_directions_data()
