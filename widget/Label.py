from widget.AbstractWidget import *
from PyQt5.QtWidgets import QLabel

class A661Label(AbstractWidget, QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.combo_attr = {
            ...
        }

    def mousePressEvent(self, event):
        event.accept()

    def mouseMoveEvent(self, event):
        event.accept()

    def mouseReleaseEvent(self, event):
        event.accept()