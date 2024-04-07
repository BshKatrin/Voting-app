from random import choices
from math import sqrt

"""choose_delegee(Elector[]) -> Elector"""


class LiquidDemocracy:
    DELEGATION_GAP_COEF = 0.1  # Liquid democracy constant

    def init_directions_data():
        return {
            "AVG": (0, 0),
            "STD_DEV": 0,
            "NB_ELECTORS": 0,
            "ELECTORS": [],  # For std deviation
            "NB_CANDIDATES": 0,
        }

    def choose_delegee(electors):
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

    def choose_possible_delegees(electors, delegator, radius):
        electors_in_radius = []
        x1, y1 = delegator.get_position()

        for elector in electors:
            if elector == delegator:
                continue
            x2, y2 = elector.get_position()
            dist = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            if dist <= radius and elector.weight != 0:
                electors_in_radius.append(elector)

        return electors_in_radius
