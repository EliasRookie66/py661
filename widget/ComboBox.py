from widget.AbstractWidget import *
from PyQt5.QtWidgets import QComboBox
from enum import Enum

OpeningMode = {
    'A661_OPEN_DOWN' : ...,
    'A661_OPEN_UP' : ...,
    'A661_OPEN_CENTERED' : ...
}

class A661ComboBox(AbstractWidget, QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.combo_attr = {
            'MaxNumberOfEntries' : 20,
            'OpeningMode' : OpeningMode['A661_OPEN_DOWN'],
            'SelectingAreaWidth' : None,
            'SelectingAreaHeight' : None,
            'NumberOfEntries' : None,
            'OpeningEntry' : None,
            'SelectedEntry' : None,
            'StringArray' : list()
        }