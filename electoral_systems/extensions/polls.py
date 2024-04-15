"""Un module qui fournit les fonctionnalités nécessaires pour les sondages.  
Il est possible d'effectuer les sondages pour les règles de vote à un tour:  
- Pluralité à un tour  
- Borda  
- Veto  
- Approval  
"""

from math import sqrt
from numpy import std
from random import random
from typing import Union, List, Dict

from people import Elector, Candidate

# Pour une génération des docs uniquement
__pdoc__ = {
    '_get_default_direction_data' : True,
}

direction_data_type = Dict[str, Union[int, List[Elector], float, tuple[float, float]]]
"Un type des données pour chaque direction (division) de la carte politique."

AVG:str = "AVG"
"""Une position moyenne des électeurs. Valeur associée sera du type `tuple[float, float]`."""

STD_DEV:str = "STD"
"""Un écart-type des positions des électeurs. Valeur associée sera du type `float`."""

ELECTORS:str = "ELECS"
"""Une liste des électeurs. Valeur associée sera du type `List[people.elector.Elector]`."""

NB_CANDIDATES:str = "NBC"
"""Un nombre des candidats. Valeur associée sera du type `int`."""

NB_ELECTORS:str = "NBE"
"""Un nombres des électeurs. Valeur associée sera du type `int`."""

NE:str = "NE"
"""La direction (division) de la carte politique nord-est."""

NW = "NW"
"""La direction (division) de la carte politique nord-ouest."""

SE = "SE"
"""La direction (division) de la carte politique sud-est."""

SW = "SW"
"""La direction (division) de la carte politique sud-ouest."""

CENTER = "CNT"
"""La direction (division) de la carte politique centre. Le centre est le carré borné entre -0.3 et 0.3."""


def calc_distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
    """Calcule la distance euclidienne entre 2 points.

    Args:
        point1 (tuple[float, float]): Une position sur la carte politique dont chaque coordonée est bornée entre -1 et 1.
        point2 (tuple[float, float]): Une position sur la carte politique dont chaque coordonée est bornée entre -1 et 1.

    Returns:
        float: Une distance euclidienne.
    """
    x1, y1 = point1
    x2, y2 = point2
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def add_elector_data(directions_data: Dict[str, direction_data_type], new_elector: Elector) -> None:
    """MAJ des données (`AVG`, `NB_ELECTORS`, `ELECTORS`) d'une case d'un dictionnaire `directions_data` selon la position d'un électeur. 
    La valeur correspondante à `AVG` est remplie juste avec la somme. Un appel à la fonction `set_avg_electors_positions`
    est nécessaire pour la division.

    Args:
        directions_data (Dict[str, electoral_systems.extensions.polls.direction_data_type]): Un dictionnaire qui stocke
            les données pour chaque division de la carte politique.
        new_elector (people.elector.Elector): Un nouvel électeur dans une élection.
    """

    x, y = new_elector.position

    directions = {
        in_center(new_elector.position),
        choose_direction(new_elector.position),
    }
    for direction in directions:
        if direction:
            x_avg, y_avg = directions_data[direction][AVG]
            x_avg, y_avg = x_avg + x, y_avg + y

            directions_data[direction][AVG] = (x_avg, y_avg)
            directions_data[direction][ELECTORS].append(new_elector)
            directions_data[direction][NB_ELECTORS] += 1


def add_candidate_data(directions_data: Dict[str, direction_data_type], new_candidate: Candidate) -> None:
    """MAJ des données (`NB_CANDIDATES`) d'une case d'un dictionnaire `directions_data` selon la position d'un électeur.

    Args:
        directions_data (Dict[str, electoral_systems.extensions.polls.direction_data_type]): Un dictionnaire qui stocke
            les données pour chaque division de la carte politique.
        new_candidate (people.candidate.Candidate): Un nouveau candidat dans une élection.
    """

    directions = {
        in_center(new_candidate.position),
        choose_direction(new_candidate.position),
    }
    for direction in directions:
        if direction:
            directions_data[direction][NB_CANDIDATES] += 1


def get_default_directions_data() -> Dict[str, direction_data_type]:
    """Retourne un dictionnaire dont chaque clé correpond à la division de la carte politique et 
    chaque valeur est un dictionnaire avec les données remises par défaut.

    Returns:
        Dict[str, electoral_systems.extensions.polls.direction_data_type]
    """

    directions = {NE, NW, SE, SW, CENTER}
    directions_data = dict()
    for direction in directions:
        directions_data[direction] = _get_default_direction_data()
    return directions_data


def _get_default_direction_data() -> direction_data_type:
    """Retourne un dictionnaire dont les clés correpondent aux constantes
    `AVG`, `STD_DEV`, `NB_ELECTORS`, `ELECTORS`, `NB_CANDIDATES` et les valeurs
    sont remises aux valeurs par défaut:  
        - `AVG` -> (0, 0)  
        - `STD_DEV` -> 0  
        - `NB_ELECTORS` -> 0  
        - `ELECTORS` -> []  
        - `NB_CANDIDATES` -> 0  

    Returns:
        electoral_systems.extensions.polls.direction_data_type: Un dictionnaire rempli avec les valeurs par défaut.
    """

    return {
        AVG: (0, 0),
        STD_DEV: 0,
        NB_ELECTORS: 0,
        ELECTORS: [],  # Pour écart-type
        NB_CANDIDATES: 0,
    }


def in_center(position: tuple[float, float]) -> Union[str, None]:
    """Retourne une constante correspondante au centre ssi la position donnée est dans le centre de la carte politique.
        Sinon, retourne `None`

    Args:
        position (tuple[float, float]): Une position dont chaque coordonnée doit être bornée entre -1 et 1.

    Returns:
        Union[str, None]: Une constante `CENTER` ou `None`.
    """

    x, y = position
    if abs(x) < 0.3 and abs(y) < 0.3:
        return CENTER
    return None


def choose_direction(position: tuple[float, float]) -> str:
    """Retourne la constante correpondant à l'une des directions de la carte politique.

    Args:
        position (tuple[float, float]):  Une position dont chaque coordonnée doit être bornée entre -1 et 1.

    Returns:
        str: Une constante correspondant à l'une des directions de la carte politque (`NE`, `SE`, `NW`, `SW`).
    """

    x, y = position
    if x > 0 and y > 0:
        return NE
    if x > 0 and y < 0:
        return SE
    if x < 0 and y > 0:
        return NW
    if x < 0 and y < 0:
        return SW


def set_avg_electors_positions(directions_data: Dict[str, direction_data_type]) -> None:
    """Définit la position moyenne des électeurs. Appele uniquement quand tous les électeurs ont été ajoutés.

    Args:
        directions_data (Dict[str, electoral_systems.extensions.polls.direction_data_type]): Un dictionnaire
            qui stocke les données pour chaque division de la carte politique.
    """

    for direction, data in directions_data.items():
        (x_avg,
            y_avg), nb_electors = data[AVG], data[NB_ELECTORS]
        x_avg = x_avg / nb_electors if nb_electors else 0
        y_avg = y_avg / nb_electors if nb_electors else 0
        directions_data[direction][AVG] = (x_avg, y_avg)


def set_std_deviation(directions_data: Dict[str, direction_data_type], total_nb_electors: int) -> None:
    """Calcule l'écart-type des positions des électeurs pour chaque direction de la carte politique. 
    Remet à l'échelle le nombre des électeurs par rapport aux autres paramètres en divisant le nombre des 
    électeurs dans chaque directions par `total_nb_electors`. Supprime les données stockées dans une liste 
    des électeurs pour chaque direction. La fonction doit être appelée après la fonction `set_avg_electors_positions`.

    Args:
        directions_data (Dict[str, electoral_systems.extensions.polls.direction_data_type]): Un dictionnaire qui stocke les données
            pour chaque division de la carte politique.
        total_nb_electors (int): Le nombre d'électeurs qui participent dans une élection.
    """

    for direction in directions_data:
        direct_electors = directions_data[direction][ELECTORS]

        if len(direct_electors) == 0:
            continue

        direct_x = [elector.position[0] for elector in direct_electors]
        direct_y = [elector.position[1] for elector in direct_electors]

        # Prendre la valeur moyenne entre les axes
        directions_data[direction][STD_DEV] = (
            std(direct_x) + std(direct_y)
        ) / 2
        # To make it equal to other parameters
        directions_data[direction][NB_ELECTORS] /= total_nb_electors
        directions_data[direction][ELECTORS].clear()


def get_avg_directions_positions(directions_data: Dict[str, direction_data_type], chosen_directions: List[str]) -> List[tuple[float, float]]:
    """Retourne une liste des positions moyennes des directions dans `chosen_directions`

    Args:
        directions_data (Dict[str, electoral_systems.extensions.polls.direction_data_type]): Un dictionnaire
            qui stocke les données pour chaque division de la carte politique.
        chosen_directions (List[str]): Une liste des constantes correspondantes aux directions

    Returns:
        List[tuple[float, float]]: Une liste des positions moyennes.
    """

    avg_positions = []
    for direction, _ in chosen_directions:
        avg_positions.append(directions_data[direction][AVG])
    return avg_positions


def get_directions_scores(directions_data: Dict[str, direction_data_type], candidate: Candidate) -> Dict[str, float]:
    """Attribue les scores à chaque direction. Le score est basé sur les données (`AVG`, `STD_DEV`, `NB_ELECTORS`, `NB_CANDIDATES`) 
    et la position d'un candidat candidate. Le score est calculé comme une somme pondérée. 
    Le calcul est effectué de manière suivante pour chaque direction:  
    - Calcule la distance entre la position d'un candidat avec AVG de la direction  
    - On cherche à minimiser la distance, l'écart-type, le nombre des candidates et de maximiser le nombre des électeurs 
    (i.e. de minimiser sa valeur négative)  
    - On attribue les poids : la distance -> 0.5, l'écart-type -> 0.2, le nombre des électeurs -> 0.2, le nombre des candidats -> 0.1  
    - Calcule la somme pondérée avec ces paramètres.  

    Args:
        directions_data (Dict[str, electoral_systems.extensions.polls.direction_data_type]): Un dictionnaire
            qui stocke les données pour chaque division de la carte politique.
        candidate (people.candidate.Candidate): Un candidat qui change sa position pour améliorer son score dans une élection.

    Returns:
        Dict[str, float]: Un dictionnaire qui pour chaque direction, stocke son score selon un candidat.
    """

    directions_scores = {direct: 0 for direct in directions_data}
    for direction, data in directions_data.items():
        # To avoid to choose that direction
        if directions_data[direction][NB_ELECTORS] <= 0.2:
            directions_scores[direction] = float("inf")
            continue
        dist = calc_distance(candidate.position, data[AVG])
        # Weighted sum.
        # Goal : Min dist, std_dev, nb_candidates. Max nb_electors (min negative value)
        score = (
            0.5 * dist
            + 0.2 * directions_data[direction][STD_DEV]
            - 0.2 * directions_data[direction][NB_ELECTORS]
            + 0.1 * directions_data[direction][NB_CANDIDATES]
        )

        directions_scores[direction] = score
    return directions_scores


def choose_directions_by_scores(directions_scores: Dict[str, float]) -> List[tuple[str, float]]:
    """Choisit les directions selon leurs scores de manière suivante:  
    - Choisit toujours la direction qui le score minimal  
    - Choisit les autres directions ssi l'écart entre le score minimal est suffisament petit. 

    Args:
        directions_scores (Dict[str, float]): Un dictionnaire qui fait correpondondre une constante de la direction avec son score

    Returns:
        List[tuple[str, float]]: Une liste des directions et leurs scores choisies
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


def move_in_direction(directions_data: Dict[str, direction_data_type], candidate: Candidate, travel_dist: float) -> None:
    """Change la position d'un candidat candidate en bougeant vers la position moyenne des directions choisies 
    (cf. `choose_directions_by_scores`). 
    Le changement de la distance est donnée par `travel_dist`.

    Args:
        directions_data (Dict[str, electoral_systems.extensions.polls.direction_data_type]): Un dictionnaire
            qui stocke les données pour chaque division de la carte politique.
        candidate (people.candidate.Candidate): Un candidat qui va bouger.
        travel_dist (float): Le taux de changement de la position d'un candidat (borné entre 0 et 1).
    """

    # Attribuer les scores pour chaque direction (somme pondérée)
    directions_scores = get_directions_scores(
        directions_data, candidate)
    # Choisir une (des) direction(s) avec des scores minimaux
    chosen_directions = choose_directions_by_scores(
        directions_scores)

    # Choisir les positions moyennes des électeurs des directions choisies
    avg_positions = get_avg_directions_positions(
        directions_data, chosen_directions
    )
    # Bouger la candidat vers les positions moyennes choisies
    candidate.move_to_avg(avg_positions, travel_dist)


def give_up(candidate: Candidate) -> bool:
    """Retourne `True` ssi le candidat candidate décide d'abandonner une élection.
    C'est une vérification supplémentaire pour une alliance.

    Args:
        candidate (people.candidate.Candidate): Un candidat qui peut décider d'abandonner

    Returns:
        bool: `True` si le candidat abandonne, `False` sinon.
    """

    return random() < 1 - candidate.dogmatism

def alliance_formed(candidate: Candidate, possible_allies: List[Candidate]) -> bool:
    """Décide si le candidat candidate va former ou alliance ou pas. Une alliance peut être formée uniquement 
    avec des autres candidats qui sont suffisament proche d'un candidat (par une position politique) et 
    leurs scores sont plus élevés que celui d'un candidat.

    Args:
        candidate (people.candidate.Candidate): Un candidat qui considère une alliance
        possible_allies (List[people.candidate.Candidate]): Une liste des candidats dont le score est plus élevés que celui d'un candidat

    Returns:
        bool: `True` si le candidat a fait une alliance. Sinon, `False`.
    """

    for ally in possible_allies:
        dist = calc_distance(candidate.position, ally.position)
        if dist < 0.15:
            return True
    return False


def change_position_candidates(candidates: List[Candidate], winner: Candidate,
                               ranking: List[Candidate], directions_data: Dict[str, direction_data_type], travel_dist: float) -> None:
    """Change les positions des candidats selon les résultats d'une élection.  
    **Algorithme**:  
        -Si le candidat gagne, il ne bouge pas.
        -Si le candidat est assez dogmatique, il est très probable qu'il décide ne pas bouger. Sinon,  
        -Si le candidat décide d'abandonner et qu'il trouve avec qui former une alliance, il sort de l'élection.
            Comme ça il transmet ses votes au candidat avec qui il a fait une alliance. 
        -Si le candidat n'est pas très opposé aux autres candidats, il bouge vers la position du gagnant. Sinon,  
        -Le candidat bouge de façon à recupérer plus de votes (cf. `move_in_direction`)

    Args:
        candidates (List[people.candidate.Candidate]): Une liste de tous les candidats participant encore à une élection.
        winner (people.candidate.Candidate): Le gagnant courant d'une élection.
        ranking (List[people.candidate.Candidate]): Une liste d'un placement courant des candidats.
        directions_data (Dict[str, electoral_systems.extensions.polls.direction_data_type]): Un dictionnaire
            qui stocke les données pour chaque division de la carte politique.
        travel_dist: Un taux de changement de la position d'un candidat (borné entre 0 et 1).
    """
    for i, candidate in enumerate(ranking):
        # Le candidat-gagnant ne bouge pas
        if candidate == winner:
            continue
        # Un candidat très dogmatique préfére de ne pas bouger
        if random() < candidate.dogmatism:
            continue
        # Alliance ?
        if give_up(candidate) and alliance_formed(candidate, ranking[:i]):
            candidates.remove(candidate)
            continue
        # Bouger vers gagnant? Base sur l'opposition.
        if random() < 1 - candidate.opposition:
            candidate.move_to_point(winner.position, travel_dist)
            continue
        # Sinon, bouger selon la somme pondérée
        move_in_direction(directions_data, candidate, travel_dist)


def change_ranking_electors(electors: List[Elector], score_winner: int, voting_rule: str, approval_gap: float) -> None:
    """Change les positions des électeurs selon les résultats d'une élection.  
    - Plus le taux de connaissance est élevé, plus il est probable qu'un électeur va changer son placement.  
    - Les candidats sont choisis dans une cercle dont le rayon maximale dépend du rayon utilisé dans la règle  
    de vote par approbation. Ainsi, le rayon du cercle est inversement proportionnel au taux de connaissance d'un électeur.  

    **Algorithme**:  
        - Pour chaque candidat calcule le rapport entre son score et celui du gagnant.  
        - Choisir de manière pseudo-aléatoire le candidat qu'il faut placer plus haut selon ce rapport.  
            Donc, plus le score du candidat est proche de celui du gagnant, plus il a de chance d'être placé en première position. 
            Un électeur arrête de considérer les candidats qui se trouvent en dehors de son cercle ou qui sont 
            placés plus bas que le gagnant actuel.
    Args:
        electors (List[people.elector.Electors]): Une liste de tous les électeurs participant encore à une élection.
        score_winner (int): Le score du gagnant courant d'une élection.
        voting_rule (str): Une constante correpondante à la règle de vote pour laquelle le sondage est effectué.
        approval_gap (float): Un rayon du cercle utilisée dans la règle de vote par approbation.
    """

    for elector in electors:
        if random() < elector.knowledge: #l'electeur ne change pas de vote grâce à son taux de connaissance
            continue

        # Réarranger le placement
        for i, candidate in enumerate(elector.candidates_ranked):
            circle_limit = (1 - elector.knowledge) * approval_gap

            if elector.dist_from_one_cand(candidate) > circle_limit: #le candidat est en dehors de son cercle d'acceptance
                break

            score_ratio = candidate.scores[voting_rule] / score_winner
            if random() < score_ratio: #vote pour ce candidat
                # Nouveau candidat
                chosen_candidate = candidate
                # Décaler les candidats vers la droite
                for j in range(i, 0, -1):
                    elector.candidates_ranked[j] = elector.candidates_ranked[j - 1]
                elector.candidates_ranked[0] = chosen_candidate
                break
