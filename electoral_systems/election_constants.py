from .voting_rules import *


class VotingRulesConstants:
    PLURALITY_SIMPLE = "PS"
    PLURALITY_2_ROUNDS = "PR"
    VETO = "VT"
    BORDA = "BRD"
    CONDORCET_SIMPLE = "CS"
    CONDORCET_COPELAND = "CC"
    CONDORCET_SIMPSON = "CSN"
    EXHAUSTIVE_BALLOT = "EB"
    APPROVAL = "AL"

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

    LINEAR = 0
    GAUSS = 1

    # UI constants (QT)
    UI = {
        ECONOMICAL: "Economical (left-right)",
        SOCIAL: "Social (liberal-autoritarian)",
        ORIENTATION: "Orientation",
        KNOWLEDGE: "Knowledge",
    }

    # Graph type for each category
    GRAPH_TYPE = {
        ECONOMICAL: GAUSS,
        SOCIAL: GAUSS,
        ORIENTATION: LINEAR,
        KNOWLEDGE: GAUSS,
    }
