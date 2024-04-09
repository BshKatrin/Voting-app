"""Un module définissant une classe `Polls`, une extension pour une application.

Il est possible d'effectuer les sondages pour les règles du vote à 1 tour, i.e.
    - Pluralité à 1 tour
    - Borda
    - Veto
    - Approval

Attributs:
    Les constantes des clés d'un dictionnaire pour stocker les directions (aussi appelées les divisions) de la carte politique:
        - NE (str): Nord-est.
        - NW (str): Nord-ouest.
        - SE (str): Sud-est.
        - SW (str): Sud-ouest.
        - CENTER (str): Centre. Les coordonnées sont bornés entre -0.3 et 0.3.
    Les constantes des clés d'un dictionnaire pour stocker les données pour chaque direction de la carte politique:
        - AVG (str): Une position moyenne des électeurs.
        - STD_DEV (str): Un écart-type des positions des électeurs.
        - ELECTORS (str): Une liste des électeurs.
        - NB_CANDIDATES (str): Un nombre des candidats.
        - NB_ELECTORS (str): Un nombres des électeurs.
"""


from math import sqrt
from numpy import std
from random import random
from typing import Union, List, Dict

from people import Elector, Candidate

DirectionDataType = Dict[str, Union[int,
                                    List[Elector], float, tuple[float, float]]]


class Polls:
    """Une classe qui contient la fonctionnalité nécessaire pour les sondages"""

    AVG = "AVG"
    """Valeur associée sera du type `tuple[float, float]`"""
    STD_DEV = "STD"
    """Valeur associée sera du type `float`"""
    ELECTORS = "ELECS"
    """Valeur associée sera du type `List[Elector]`"""
    NB_CANDIDATES = "NBC"
    """Valeur associée sera du type `int`"""
    NB_ELECTORS = "NBE"
    """Valeur associée sera du type `int`"""

    NE = "NE"
    NW = "NW"
    SE = "SE"
    SW = "SW"
    CENTER = "CNT"

    def calc_distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
        """Calculer la distance euclidienne entre 2 points.

        Args:
            point1 (tuple[float, float]): Une position sur la carte politique dont chaque coordonée est borné entre -1 et 1.
            point2 (tuple[float, float]): Une position sur la carte politique dont chaque coordonée est borné entre -1 et 1.

        Return:
            float: une distance euclidienne.
        """
        x1, y1 = point1
        x2, y2 = point2
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def add_elector_data(directions_data: Dict[str, DirectionDataType], new_elector: Elector) -> None:
        """MAJ les données (`AVG`, `NB_ELECTORS`, `ELECTORS`) d'une case d'un dictionnaire selon la position d'un électeur.
        La valeur correspondante à `AVG` est remplie juste avec la somme. Appel à la fonction `set_avg_electors_positions`
        est nécessaire pour la division.

        Args:
            directions_data Dict[str, DirectionDataType]: Un dictionnaire qui stocke les données
                pour chaque division de la carte politique.
            new_elector (people.elector.Elector): Un nouveau électeur dans une élection
        """

        x, y = new_elector.position

        directions = {
            Polls.in_center(new_elector.position),
            Polls.choose_direction(new_elector.position),
        }
        for direction in directions:
            if direction:
                x_avg, y_avg = directions_data[direction][Polls.AVG]
                x_avg, y_avg = x_avg + x, y_avg + y

                directions_data[direction][Polls.AVG] = (x_avg, y_avg)
                directions_data[direction][Polls.ELECTORS].append(new_elector)
                directions_data[direction][Polls.NB_ELECTORS] += 1

    def add_candidate_data(directions_data: Dict[str, DirectionDataType], new_candidate: Candidate) -> None:
        """MAJ les données (`NB_CANDIDATES`) d'une case d'un dictionnaire selon la position d'un électeur.

        Args:
            directions_data (Dict[str, DirectionDataType]): Un dictionnaire qui stocke les données
                pour chaque division de la carte politique.
            new_candidate (people.candidate.Candidate): Un nouveau candidat dans une élection
        """

        directions = {
            Polls.in_center(new_candidate.position),
            Polls.choose_direction(new_candidate.position),
        }
        for direction in directions:
            if direction:
                directions_data[direction][Polls.NB_CANDIDATES] += 1

    def get_default_directions_data() -> Dict[str, DirectionDataType]:
        """Retourner un dictionnaire des dictionnaires dont chaque clé correpond à la division de la carte politique
        et chaque valeur est un dictionnaire avec les données remis par défaut.

        Returns:
            Dict[str, DirectionDataType]
        """
        directions = {Polls.NE, Polls.NW, Polls.SE, Polls.SW, Polls.CENTER}
        directions_data = dict()
        for direction in directions:
            directions_data[direction] = Polls._get_default_direction_data(
                direction)
        return directions_data

    def _get_default_direction_data(direction: str) -> DirectionDataType:
        """Retourner un dictionnaire dont les clés correpond aux constantes
        AVG, STD_DEV, NB_ELECTORS, ELECTORS, NB_CANDIDATES et les valeurs
        sont remis aux valeurs par défaut, i.e.
            - `AVG` -> (0, 0)
            - `STD_DEV` -> 0
            - `NB_ELECTORS` -> 0
            - `ELECTORS` -> []
            - `NB_CANDIDATES` -> 0

        Args:
            direction (str): Une constante correspondante à la direction pour laquelle il faut retourner un dictionnaire.

        Returns:
            DirectionDataType
        """
        return {
            Polls.AVG: (0, 0),
            Polls.STD_DEV: 0,
            Polls.NB_ELECTORS: 0,
            Polls.ELECTORS: [],  # Pour écart-type
            Polls.NB_CANDIDATES: 0,
        }

    def in_center(position: tuple[float, float]) -> Union[str, None]:
        """Retourne une constante correspondante au centre ssi la position donnée est dans le centre de la carte politique.
        Sinon, retourner None

        Args:
            position (tuple[float, float]): Une position dont chaque coordonnée doit être bornée entre -1 et 1.

        Returns:
            Union[str, None]: Une constante (`CENTER`) ou None.
        """
        x, y = position
        if abs(x) < 0.3 and abs(y) < 0.3:
            return Polls.CENTER
        return None

    def choose_direction(position: tuple[float, float]) -> str:
        """Retourner la constante correpondant à l'une des directions de la carte politique.

        Args:
            position (tuple[float, float]):  Une position dont chaque coordonnée doit être bornée entre -1 et 1.

        Returns:
            str: Une constante correspondante à l'une des directions de la carte politque (`NE`, `SE`, `NW`, `SW`).
        """
        x, y = position
        if x > 0 and y > 0:
            return Polls.NE
        if x > 0 and y < 0:
            return Polls.SE
        if x < 0 and y > 0:
            return Polls.NW
        if x < 0 and y < 0:
            return Polls.SW

    def set_avg_electors_positions(directions_data: Dict[str, DirectionDataType]) -> None:
        """Définir la position moyenne des électeurs.
        Appeler uniquement quand tous les électeurs ont été ajoutés.

        Args:
            directions_data (Dict[str, DirectionDataType]): Un dictionnaire qui stocke les données
                pour chaque division de la carte politique.
        """

        for direction, data in directions_data.items():
            (x_avg,
             y_avg), nb_electors = data[Polls.AVG], data[Polls.NB_ELECTORS]
            x_avg = x_avg / nb_electors if nb_electors else 0
            y_avg = y_avg / nb_electors if nb_electors else 0
            directions_data[direction][Polls.AVG] = (x_avg, y_avg)

    def set_std_deviation(directions_data: Dict[str, DirectionDataType], total_nb_electors: int) -> None:
        """Calculer l'écart-type des positions des électeurs pour chaque direction de la carte politique.
        Remettre à l'échelle le nombre des électeurs par rapport aux autres paramètres en divisant
        le nombre des électeurs dans chaque directions par `total_nb_electors`.
        Supprimer les données stocker dans une liste des électeurs pour chaque direction.
        La fonction doit être appelée après la fonction `set_avg_electors_positions`

        Args:
            directions_data (Dict[str, DirectionDataType]): Un dictionnaire qui stocke les données
                pour chaque division de la carte politique.
            total_nb_electors (int): Un nombre de tous les électeurs qui participent dans une élection.
        """

        for direction in directions_data:
            direct_electors = directions_data[direction][Polls.ELECTORS]

            if len(direct_electors) == 0:
                continue

            direct_x = [elector.position[0] for elector in direct_electors]
            direct_y = [elector.position[1] for elector in direct_electors]

            # Prendre la valeur moyenne entre les axes
            directions_data[direction][Polls.STD_DEV] = (
                std(direct_x) + std(direct_y)
            ) / 2
            # To make it equal to other parameters
            directions_data[direction][Polls.NB_ELECTORS] /= total_nb_electors
            directions_data[direction][Polls.ELECTORS].clear()

    def get_avg_directions_positions(directions_data: Dict[str, DirectionDataType], chosen_directions: List[str]) -> List[tuple[float, float]]:
        """Retourner une liste des positions moyennes des directions dans `chosen_directions`

        Args:
            directions_data (Dict[str, DirectionDataType]): Un dictionnaire qui stocke les données
                pour chaque division de la carte politique.
            chosen_directions (List[str)]): Une liste des constantes correspondantes aux directions.

        Returns:
            List[tuple[float, float]]: Une liste des positions moyennes.
        """

        avg_positions = []
        for direction, _ in chosen_directions:
            avg_positions.append(directions_data[direction][Polls.AVG])
        return avg_positions

    def get_directions_scores(directions_data: Dict[str, DirectionDataType], candidate: Candidate) -> Dict[str, float]:
        """Attribuer les scores à chaque direction. Le score est basé sur les données (`AVG`, `STD_DEV`, `NB_ELECTORS`, `NB_CANDIDATES`)
        et la position d'un candidat `candidate`. Le score est calculé comme une somme pondérée.
        Le calcul est effectué de manière suivante pour chaque direction:
            - Calculer la distance entre la position d'un candidate avec `AVG` de la direction
            - On checher à minimiser la distance, l'écart-type, le nombre des candidates et de maximiser le nombre des électeurs
            (i.e. de minimiser sa valeur négative).
            - On attribue les poids : la distance -> 0.5, l'écart-type -> 0.2,
                le nombre des électeurs -> 0.2, le nombre des candidats -> 0.1
            - Calculer la somme pondérée avec ces paramètres.

        Args:
            directions_data (Dict[str, DirectionDataType]): Un dictionnaire qui stocke les données
                pour chaque division de la carte politique.

            candidate (people.candidate.Candidate): Un candidat qui changer sa position pour améliorer son score dans une élection.

        Returns:
            Dict[str, float]: Un dictionnaire qui pour chaque direction stocke son score selon un candidat.
        """

        directions_scores = {direct: 0 for direct in directions_data}
        for direction, data in directions_data.items():
            # To avoid to choose that direction
            if directions_data[direction][Polls.NB_ELECTORS] <= 0.2:
                directions_scores[direction] = float("inf")
                continue
            dist = Polls.calc_distance(candidate.position, data[Polls.AVG])
            # Weighted sum.
            # Goal : Min dist, std_dev, nb_candidates. Max nb_electors (min negative value)
            score = (
                0.5 * dist
                + 0.2 * directions_data[direction][Polls.STD_DEV]
                - 0.2 * directions_data[direction][Polls.NB_ELECTORS]
                + 0.1 * directions_data[direction][Polls.NB_CANDIDATES]
            )

            directions_scores[direction] = score
        return directions_scores

    def choose_directions_by_scores(directions_scores: Dict[str, float]) -> List[(str, float)]:
        """Choisir les directions selon leurs scores de manière suivante:
            - Choisir toujours la direction qui le score minimal
            - Choisir les autres directions ssi l'écart entre le score minimal est suffisament petit.

        Args:
            directions_scores (Dict[str, float]): Un dictionnaire qui fait correpondondre une constante de la direction
                avec son score

        Returns:
            List[(str, float)]: Une liste des directions et leurs scores choisies
        """
        lst = [(direct, score) for direct, score in directions_scores.items()]
        lst = sorted(lst, key=lambda e: e[1])

        # Gap between 1st min and next values
        percentage = 1.6
        min = lst[0][1]
        chosen = []
        for direct, score in lst:
            if score < min * percentage:
                chosen.append((direct, score))
                percentage -= 0.3
        return chosen

    def move_in_direction(directions_data: Dict[str, DirectionDataType], candidate: Candidate, travel_dist: float) -> None:
        """Changer la position d'un candidat `candidate` avec bougant vers la position moyenne des directions choisies
        (cf. `choose_directions_by_scores() <electoral_systems.extensions.polls.choose_directions_by_scores>`).
        Le changement de la distance est donnée par `travel_dist`. 

        Args:
            directions_data (Dict[str, DirectionDataType]): Un dictionnaire qui stocke les données
                pour chaque division de la carte politique.
            candidate (people.candidate.Candidate): Un candidat qui va bouger.
            travel_dist (float): Le taux de changement de la position d'un candidat (borné entre 0 et 1).
        """

        # Attribuer les scores pour chaque direction (somme pondérée)
        directions_scores = Polls.get_directions_scores(
            directions_data, candidate)
        # Choisir une (des) direction(s) avec des scores minimaux
        chosen_directions = Polls.choose_directions_by_scores(
            directions_scores)

        # Choisir les positions moyennes des électeurs des directions choisies
        avg_positions = Polls.get_avg_directions_positions(
            directions_data, chosen_directions
        )
        # Bouger la candidat vers les positions moyennes choisies
        candidate.move_to_avg(avg_positions, travel_dist)

    # Returns True iff candidate gives up
    def give_up(candidate: Candidate) -> bool:
        """Retourne True ssi le candidat `candidate` décide d'abandonner une élection.
        C'est une vérification supplémentaire pour une alliance.

        Args:
            candidate (people.candidate.Candidate): Un candidat que peut décider d'abandonner
        Returns:
            bool: True si le candidat abandonne, False sinon.
        """

        return random() < 1 - candidate.dogmatism

    # Posssible allies is a sublist of candidate whose score is higher than that of a candidate
    # Function return True iff alliance is formed, we dont care with whom
    def alliance_formed(candidate: Candidate, possible_allies: List[Candidate]) -> bool:
        """Décider si le candidat `candidate` va former ou alliance ou pas. Une alliance peut être formée uniquement
        avec des autres candidats qui sont suffisament proche d'un candidat (par une position politique)
        et leurs scores sont plus élevés que celui d'un candidat. 

        Args:
            candidate (people.candidate.Candidate): Un candidat qui considère une alliance.
            possible_allies:List[people.candidate.Candidate]: Une liste des candidats dont le score est plus élevés que celui d'un candidat.

        Returns:
            bool: True si le candidat a fait une alliance. False, sinon.
        """
        for ally in possible_allies:
            dist = Polls.calc_distance(candidate.position, ally.position)
            if dist < 0.15:
                return True
        return False

    def change_position_candidates(candidates: List[Candidate], winner: Candidate,
                                   ranking: List[Candidate], directions_data: Dict[str, DirectionDataType], travel_dist: float) -> None:
        """Changer les positions des candidats selon les résultats d'une élection.
        Algorithme:
            - Si le candidate gagne, il ne bouge pas. Sinon,
            - Si le candidat est assez dogmatique, il peu probable qu'il bouge. Sinon,
            - Si le candidat décide d'abandonner et il trouve avec qui il faut former une alliance, il sort d'une élection.
            Comme ça il transmets ces votes au candidat avec qui il a fait une alliance. Sinon, 
            - Si le candidat n'est pas très opposé aux autres candidats, il bouge vers la position du gagnant. Sinon,
            - Le candidat bouge vers la direction selon les scores
            (cf. move_in_direction() <electoral_systems.extensions.polls.move_in_direction>)

        Args:
            candidates (List[people.candidate.Candidate]): Une liste de tous les candidats encore participant dans une élection.
            winner (people.candidate.Candidate): Le gagnant courant d'une élection.
            ranking (List[people.candidate.Candidate]): Une liste d'un placement courant des candidats.
            directions_data (Dict[str, DirectionDataType]): Un dictionnaire qui stocke les données
                pour chaque division de la carte politique.
            travel_dist: Un taux de changement de la position d'un candidat (borné entre 0 et 1).
        """
        for i, candidate in enumerate(ranking):
            # Le candidat-gagnant ne bouge pas
            if candidate == winner:
                continue
            # Un candidat très dogmatique préfére de ne pas bouger
            if random() < candidate.dogmatism:
                continue

            if Polls.give_up(candidate) and Polls.alliance_formed(candidate, ranking[:i]):
                candidates.remove(candidate)
                continue
            # Bouger vers gagnant? Base sur l'opposition.
            if random() < 1 - candidate.opposition:
                candidate.move_to_point(winner.position, travel_dist)
                continue
            # Sinon, bouger selon la somme pondérée
            Polls.move_in_direction(directions_data, candidate, travel_dist)

    def change_ranking_electors(electors: List[Elector], score_winner: int, voting_rule: str, approval_gap: float) -> None:
        """Changer les positions des électeurs selon les résultats d'une élection.
        - Plus le taux des connaissances est élevé, plus il est probable qu'un électeur va changer son placement.
        - Les candidats sont choisis dans une cercle dont le rayon maximale dépend du rayon utilisée dans une règle du vote 
        *Approval* (cf. apply_approval() <electoral_systems.voting_rules.approval.apply_approval>).
        Ainsi, le rayon du cercle est inversement proportionnelle au taux des connaissances d'un électeur.

        Algorithme:
            - Pour chaque candidat calculer le rapport entre son score et celui du gagnant.
            - Choisir de manière aléatoire le candidat qu'il faut placer plus haut dans un placement selon ce rapport.
        Donc, plus le score du candidat est proche au celui du gagnant, plus il a de chance d'être placé le premier.
        Un électeur arête de considérer les candidats qui se trouvent en dehors de son cercle ou qui sont placés plus bas 
        que le gagnant actuel.

        Args:
            electors (List[people.elector.Electors]): Une liste de tous les électeurs encore participant dans une élection.
            score_winner (int): Le score du gagnant courant d'une élection.
            voting_rule (str): Une constante correpondante à la règle du vote pour laquelle la sondages est effectuée.
            approval_gap (float): Un rayon du cercle utilisée dans une règle du vote `APPROVAL`
        """

        for elector in electors:
            if random() < elector.knowledge:
                continue

            # Réarranger le placement
            for i, candidate in enumerate(elector.candidates_ranked):
                circle_limit = (1 - elector.knowledge) * approval_gap

                if elector.dist_from_one_cand(candidate) > circle_limit:
                    break

                score_ratio = candidate.scores[voting_rule] / score_winner
                if random() < score_ratio:
                    # Nouvelle candidat
                    chosen_candidate = candidate
                    # Décaler les candidats vers la droite
                    for j in range(i, 0, -1):
                        elector.candidates_ranked[j] = elector.candidates_ranked[j - 1]
                    elector.candidates_ranked[0] = chosen_candidate
                    break
