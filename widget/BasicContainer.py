
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class AbstractContainer:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = True
        self.visible = True
        self.interactivity = True
        self.current_pos = None

    def mouseMoveEvent(self, event):
        # print(f"Mouse Moved to: ({event.x()}, {event.y()})")
        self.current_pos = event.pos()
        event.accept()


class ARINC661BasicContainer(AbstractContainer, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.layout = QVBoxLayout()  # default vertical
        self.setLayout(self.layout)
        # self.resize(500, 500)      # should be

    def setActivity(self):
        self.active = True
        self.setVisible(False)
        self.setEnabled(False)

    def setVisibility(self, visible):
        self.visible = visible
        self.setVisible(visible)

    def setInteractivity(self, interactivity):
        self.interactivity = interactivity
        self.setEnabled(interactivity)