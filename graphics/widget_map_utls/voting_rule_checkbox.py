from PySide6.QtWidgets import QCheckBox, QWidget


class VotingRuleCheckbox(QCheckBox):
    """A class representing a single checkbox corresponding to the voting rule."""

    def __init__(self, label: str, nb_cand_min: int, parent: QWidget):
        """Initialize the checkbox corresponding to the voting rule.

        Args:
            label (str): A name of the voting rule (UI version).
            nb_cand_min (int): A minimum number of candidates for the voting rule. 
            parent (PySide6.QtWidgets.QWidget): Widget's parent. Default = `None`.
        """

        super().__init__(label, parent)
        self.min = nb_cand_min
