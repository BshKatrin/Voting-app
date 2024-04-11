from PySide6.QtWidgets import QCheckBox, QWidget


class VotingRuleCheckbox(QCheckBox):
    """Un widget qui représente un checkbox pour une règle du vote."""

    def __init__(self, label: str, nb_cand_min: int, parent: QWidget):
        """Initialiser un checkbox pour une règle du vote.

        Args:
            label (str): Un nom d'une règle du vote (nom pour UI).
            nb_cand_min (int): Un nombre minimum des candidats pour une règle du vote.
            parent (PySide6.QtWidgets.QWidget): Un parent d'un widget.
        """

        super().__init__(label, parent)
        self.min = nb_cand_min
