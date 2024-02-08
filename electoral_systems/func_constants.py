from .voting_rules import *
from .voting_rules.constants import *

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
