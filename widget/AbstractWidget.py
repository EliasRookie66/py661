from widget.A661CommonParams import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class AbstractWidget:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__startPos = None
        self.is_user_input = True
        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.on_item_changed)
        self.common_attr = {
            'Name' : None,
            'WidgetIdent' : None,
            'Alignment' : A661_ALIGNMENT.get('A661_CENTER'),
            'MaxStringLength' : 20,
            'PosX' : None,
            'PosY' : None,
            'SizeX' : None,
            'SizeY' : None,
            'AutomaticFocusMotion' : A661_AUTO_FOCUS_MOTION.get('A661_FALSE'),
            'Enable' : A661_ENABLE.get('A661_TRUE'),
            'NextFocusedWidget' : None,
            'StyleSet' : 0,
            'Visible' : A661_VISIBLE.get('A661_TRUE')
        }

    def on_item_changed(self, item):
        if self.is_user_input:
            print(f"Item changed: {item.text()}")
            # get the index to confirm the item changed
            index = item.index()
            row = index.row()
            column = index.column()
            previous_index = self.model.index(row, column - 1)
            previous_item = self.model.itemFromIndex(previous_index)

            if previous_item.text() == 'PosX':
                self.common_attr['PosX'] = item.text()
                x = int(item.text())
                y = int(self.common_attr['PosY'])
                # print(f'x:{x} \t y:{y}')
                self.move(x, 400 - y) # 500 - widget_height
            elif previous_item.text() == 'PosY':
                self.common_attr['PosY'] = item.text()
                x = int(self.common_attr['PosX'])
                y = int(item.text())
                # print(f'x:{x} \t y:{y}')
                self.move(x, 400 - y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__startPos = event.pos()

    def mouseMoveEvent(self, event):
        self.is_user_input = False
        if event.buttons() == Qt.LeftButton and self.__startPos:
            # calculate
            delta = event.pos() - self.__startPos
            new_pos = self.pos() + delta
            # update
            self.move(new_pos)
            self.common_attr['PosX'] = str(self.pos().x() + delta.x())
            self.common_attr['PosY'] = str(-(self.pos().y() + delta.y()) + 425)
            # print(f"x:{self.common_attr['PosX']}, y:{self.common_attr['PosY']}")

            for row in range(self.model.rowCount()):
                for column in range(self.model.columnCount()):
                    item = self.model.item(row, column)
                    if item.text() == 'PosX':
                        self.model.item(row, column + 1).setText(self.common_attr['PosX'])
                        continue
                    elif item.text() == 'PosY':
                        self.model.item(row, column + 1).setText(self.common_attr['PosY'])
                        continue

        self.is_user_input = True
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__startPos = None
        super().mousePressEvent(event)
