from PySide6.QtWidgets import QCheckBox, QWidget


class VotingRuleCheckbox(QCheckBox):
    """Un widget qui représente un checkbox pour une règle de vote."""

    def __init__(self, label: str, nb_cand_min: int, parent: QWidget):
        """Initialise un checkbox pour une règle de vote.

        Args:
            label (str): Un nom d'une règle de vote (nom pour UI).
            nb_cand_min (int): Un nombre minimum de candidats pour une règle de vote.
            parent (PySide6.QtWidgets.QWidget): Le parent d'un widget.
        """

        super().__init__(label, parent)
        self.min = nb_cand_min
