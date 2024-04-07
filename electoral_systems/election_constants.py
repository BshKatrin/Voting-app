from .voting_rules import *
from .voting_rules.constants import *


class VotingRulesConstants:
    PLURALITY_SIMPLE = PLURALITY_SIMPLE
    PLURALITY_2_ROUNDS = PLURALITY_2_ROUNDS
    VETO = VETO
    BORDA = BORDA
    CONDORCET_SIMPLE = CONDORCET_SIMPLE
    CONDORCET_COPELAND = CONDORCET_COPELAND
    CONDORCET_SIMPSON = CONDORCET_SIMPSON
    EXHAUSTIVE_BALLOT = EXHAUSTIVE_BALLOT
    APPROVAL = APPROVAL

    APPROVAL_GAP_COEF = 0.3  # Approval constant

    # functions association
    VOTING_RULES_FUNC = {
        PLURALITY_SIMPLE: plurality.apply_plurality_simple,
        PLURALITY_2_ROUNDS: plurality.apply_plurality_rounds,
        VETO: veto.apply_veto,
        BORDA: borda.apply_borda,
        CONDORCET_SIMPLE: condorcet.apply_condorcet_simple,
        CONDORCET_COPELAND: condorcet.apply_condorcet_copeland,
        CONDORCET_SIMPSON: condorcet.apply_condorcet_simpson,
        EXHAUSTIVE_BALLOT: exhaustive_ballot.apply_exhaustive_ballot,
        APPROVAL: approval.apply_approval,
    }

    # UI constants (QT)
    UI = {
        PLURALITY_SIMPLE: "Plurality (1 round)",
        PLURALITY_2_ROUNDS: "Plurality (2 rounds)",
        VETO: "Veto",
        BORDA: "Borda",
        CONDORCET_SIMPLE: "Condorcet Simple",
        CONDORCET_COPELAND: "Condorcet Copeland",
        CONDORCET_SIMPSON: "Condorcet Simpson",
        EXHAUSTIVE_BALLOT: "Exhaustive Ballot",
        APPROVAL: "Approval",
    }

    # Separation for various checks
    ONE_ROUND = {PLURALITY_SIMPLE, VETO, BORDA, APPROVAL}
    MULTI_ROUND = {PLURALITY_2_ROUNDS, EXHAUSTIVE_BALLOT}
    CONDORCET = {CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON}


class RandomConstants:
    # Random generating constants
    ECONOMICAL = "ECON"
    SOCIAL = "SOC"
    ORIENTATION = "ORIENT"
    KNOWLEDGE = "KNW"
    DOGMATISM = "DGC"
    OPPOSITION = "OPP"
    TRAVEL_DIST = "TD"  # In percentage, between 1 and

    LINEAR = 0
    GAUSS = 1
    SLIDER = 2

    # UI constants (QT)
    UI = {
        ECONOMICAL: "Economical (left-right)",
        SOCIAL: "Social (liberal-autoritarian)",
        ORIENTATION: "Orientation",
        KNOWLEDGE: "Knowledge",
        DOGMATISM: "Dogmatism",
        OPPOSITION: "Opposition",
        TRAVEL_DIST: "Candidate's travel distance",
    }

    # Graph type for each category
    GRAPH_TYPE = {
        ECONOMICAL: GAUSS,
        SOCIAL: GAUSS,
        ORIENTATION: LINEAR,
        KNOWLEDGE: GAUSS,
        DOGMATISM: GAUSS,
        OPPOSITION: GAUSS,
        TRAVEL_DIST: SLIDER,
    }

    # Change later
    VALUES_MIN_MAX = {
        ECONOMICAL: (-85, 85),  # Div by 100
        SOCIAL: (-85, 85),  # Div by 100
        ORIENTATION: (-1, 1),  # NO div by 100
        KNOWLEDGE: (10, 90),  # Div by 100
        DOGMATISM: (10, 90),  # Div by 100
        OPPOSITION: (10, 90),  # Div by 100
        TRAVEL_DIST: (1, 100),  # Div by 100
    }

    DEFAULT_VALUES = {
        ECONOMICAL: (0.0, 0.5),
        SOCIAL: (0.0, 0.5),
        ORIENTATION: 1,
        KNOWLEDGE: (0.5, 0.3),
        DOGMATISM: (0.3, 0.3),
        OPPOSITION: (0.3, 0.3),
        TRAVEL_DIST: 0.1,
    }
