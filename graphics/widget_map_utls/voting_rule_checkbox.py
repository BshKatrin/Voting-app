from PySide6.QtWidgets import QCheckBox


class VotingRuleCheckbox(QCheckBox):
    def __init__(self, label, nb_cand_min, parent):
        super().__init__(label, parent)
        self.min = nb_cand_min
