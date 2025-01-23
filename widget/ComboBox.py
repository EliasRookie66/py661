from widget.AbstractWidget import *
from PyQt5.QtWidgets import QComboBox

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

    def init_widget_alignment(self):
        self.setEditable(True)
        self.line_edit = self.lineEdit()
        self.line_edit.setParent(self)
        self.line_edit.setReadOnly(True)
        alignment_name = self.common_attr['Alignment']

        alignment = A661_ALIGNMENT.get(alignment_name)
        if alignment is None:
            raise ValueError("Invalid alignment name: {}".format(alignment_name))
        
        if alignment is not None:
            self.line_edit.setAlignment(alignment)

        current_delegate = self.itemDelegate()

        # none then create
        if current_delegate is None:
            alignment_delegate = AlignmentDelegate(self, alignment)
            self.setItemDelegate(alignment_delegate)
        elif isinstance(current_delegate, AlignmentDelegate):
            # already have then delete old and create new
            if current_delegate.alignment != alignment:
                self.setItemDelegate(None)
                alignment_delegate = AlignmentDelegate(self, alignment)
                self.setItemDelegate(alignment_delegate)
            # different type then delete old and create new
            else:
                self.setItemDelegate(None)
                alignment_delegate = AlignmentDelegate(self, alignment)
                self.setItemDelegate(alignment_delegate)
    def setAlignment(self, alignment):
        self.line_edit.setAlignment(alignment)