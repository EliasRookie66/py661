from PyQt5.QtWidgets import QPushButton
from widget.AbstractWidget import *

class A661PushButton(AbstractWidget, QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_attr = {
            'LabelString' : '',
        }
    def init_widget_alignment(self):
        self.setAlignment()

    def setAlignment(self):
        if self.text() == '':
            return
        elif self.text() == 'A661_CENTER':
            self.setStyleSheet('text-align: center')
        elif self.text() == 'A661_LEFT':
            self.setStyleSheet('text-align: left')
        elif self.text() == 'A661_RIGHT':
            self.setStyleSheet('text-align: right')
        else:
            raise('Alignment Value Error')
