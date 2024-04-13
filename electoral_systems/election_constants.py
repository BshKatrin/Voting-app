from typing import Dict, Union, Set, Callable

from .voting_rules import *
from .voting_rules.constants import *


class VotingRulesConstants:
    """Une classe qui regroupent les constantes utilisées par rapport aux règles de vote."""

    # Des règles du vote. Cf. le module electoral_systems.voting_rules.constants
    PLURALITY_SIMPLE: str = PLURALITY_SIMPLE
    PLURALITY_2_ROUNDS: str = PLURALITY_2_ROUNDS
    VETO: str = VETO
    BORDA: str = BORDA
    CONDORCET_SIMPLE: str = CONDORCET_SIMPLE
    CONDORCET_COPELAND: str = CONDORCET_COPELAND
    CONDORCET_SIMPSON: str = CONDORCET_SIMPSON
    EXHAUSTIVE_BALLOT: str = EXHAUSTIVE_BALLOT
    APPROVAL: str = APPROVAL

    APPROVAL_GAP_COEF: float = 0.3  # Constante pour approbaton

    # Associer des fonctions avec des constantes
    VOTING_RULES_FUNC: Dict[str, Callable] = {
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

    # UI constantes (QT)
    UI: Dict[str, str] = {
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

    # Séparation pour vérification après
    ONE_ROUND: Set[str] = {PLURALITY_SIMPLE, VETO, BORDA, APPROVAL}
    MULTI_ROUND: Set[str] = {PLURALITY_2_ROUNDS, EXHAUSTIVE_BALLOT}
    CONDORCET: Set[str] = {CONDORCET_SIMPLE, CONDORCET_COPELAND, CONDORCET_SIMPSON}


class RandomConstants:
    """Une classe qui regroupe les constantes utilisées lors de la génération des données."""

    # Random generating constants
    ECONOMICAL: str = "ECON"
    SOCIAL: str = "SOC"
    ORIENTATION: str = "ORIENT"
    KNOWLEDGE: str = "KNW"
    DOGMATISM: str = "DGC"
    OPPOSITION: str = "OPP"
    TRAVEL_DIST: str = "TD"  # Proportion. Entre 0 et 1

    # Types des graphes
    LINEAR: int = 0
    GAUSS: int = 1
    SLIDER: int = 2

    # UI constantes (QT)
    UI: Dict[str, str] = {
        ECONOMICAL: "Economical (left-right)",
        SOCIAL: "Social (liberal-autoritarian)",
        ORIENTATION: "Orientation",
        KNOWLEDGE: "Knowledge",
        DOGMATISM: "Dogmatism",
        OPPOSITION: "Opposition",
        TRAVEL_DIST: "Candidate's travel distance",
    }

    # Associer les types des graphes aux constantes
    GRAPH_TYPE: Dict[str, int] = {
        ECONOMICAL: GAUSS,
        SOCIAL: GAUSS,
        ORIENTATION: LINEAR,
        KNOWLEDGE: GAUSS,
        DOGMATISM: GAUSS,
        OPPOSITION: GAUSS,
        TRAVEL_DIST: SLIDER,
    }

    # Les valeurs min et max pour des sliders (QT). Div par 100 car les sliders de QT acceptent uniquement des entiers.
    VALUES_MIN_MAX: Dict[str, tuple[int, int]] = {
        ECONOMICAL: (-85, 85),  # Div par 100
        SOCIAL: (-85, 85),  # Div par 100
        ORIENTATION: (-1, 1),  # PAS div par 100
        KNOWLEDGE: (10, 90),  # Div par 100
        DOGMATISM: (10, 90),  # Div par 100
        OPPOSITION: (10, 90),  # Div par 100
        TRAVEL_DIST: (1, 100),  # Div par 100
    }

    # Les valeurs par défaut
    DEFAULT_VALUES: Dict[str, Union[tuple[float, float], float, int]] = {
        ECONOMICAL: (0.0, 0.5),
        SOCIAL: (0.0, 0.5),
        ORIENTATION: 1,
        KNOWLEDGE: (0.5, 0.3),
        DOGMATISM: (0.3, 0.3),
        OPPOSITION: (0.3, 0.3),
        TRAVEL_DIST: 0.1,
    }
