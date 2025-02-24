
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QComboBox

class ComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        self.lineEdit().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.lineEdit() and event.type() == event.MouseButtonPress:
            self.showPopup()
            return True
        return super().eventFilter(obj, event)