"""Un module qui fournit la fonctionnalité nécessaire pour la démocratie liquide, i.e. faire les délégations."""

from math import sqrt
from random import choices
from typing import List

from people import Elector


DELEGATION_GAP_COEF = 0.1
"""Une constante qui définit un rayon maximale d'une cercle pour choisir les délégataires.
    Les délégataires doivent être assez proches par une position politique.
"""


def choose_delegee(electors: List[Elector]) -> Elector:
    """Choisir un électeur-délégataire parmi les électeurs de façon suivante:
        - Calculer le taux de connaissances total des électeurs
        - Choisir un électeur de manière aléatoire selon leur taux de connaissances.
        Plus le taux de connaisances d'un électeur est élevé, plus il est probable qu'il soit choisi
        comme un délégataire, et inversement, moins son taux de connaissances est élevé, moins il est probable
        qu'il soit choisi comme un délégataire.

    Args:
        electors (List[Elector]) -> Une liste des électeurs qui peuvent être les délégataires.
    Returns:
        people.elector.Elector: un délégateur choisi.
    """
    if len(electors) == 0:
        return None

    if len(electors) == 1:
        return electors[0]

    weights = []
    total_knowledge = 0

    for elector in electors:
        total_knowledge += elector.knowledge

    for elector in electors:
        proba = elector.knowledge / total_knowledge
        weights.append(proba)

    # Retourne un électeur à qui délégé
    return choices(electors, weights=weights, k=1)[0]


def choose_possible_delegees(electors: List[Elector], delegator: Elector) -> List[Elector]:
    """Choisir parmi `electors` des électeurs-délégataires pour un électeur `delegator` de façon suivante:
        - Calculer la distance entre un électeur et `delegator`
        - Si elle est inférieure à `DELEGATION_GAP_COEF`, ajouter cet électeur dans une liste des délégataires. Sinon, continuer.

    Args:
        electors (List[Elector]): tous les électeurs participant dans une élection
        delagator (Elector): un électeur qui veut déléger

    Returns:
        List[Elector]: Une liste des électeurs qui peuvent être considérés comme des délégataires.
    """
    electors_in_radius = []
    x1, y1 = delegator.position
    for elector in electors:
        if elector == delegator:
            continue
        x2, y2 = elector.position
        dist = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if dist <= DELEGATION_GAP_COEF and elector.weight != 0:
            electors_in_radius.append(elector)

    return electors_in_radius
