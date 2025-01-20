from widget.A661CommonParams import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel

class AbstractWidget:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__startPos = None
        self.model = QStandardItemModel()
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
    #     self.model.itemChanged.connect(self.handle_item_changed)

    # def handle_item_changed(self, item):
    #     row = item.row()
    #     column = item.column()
        
    #     if column == 1:
    #         attr_name = self.model.item(row, 0).text()
    #         if attr_name in self.common_attr: # may change into normal (now is only for move)
    #             try:
    #                 new_value = int(item.text())
    #                 self.common_attr[attr_name] = new_value
    #                 self.move(self.common_attr["PosX"], self.common_attr["PosY"])
    #                 print(f"Moved to: {self.common_attr}")
    #             except ValueError:
    #                 # 如果输入的值不是整数，恢复原值
    #                 item.setText(str(self.common_attr[attr_name]))


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__startPos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.__startPos:
            # calculate
            delta = event.pos() - self.__startPos
            new_pos = self.pos() + delta
            # update
            self.move(new_pos)
            self.common_attr['PosX'] = str(self.pos().x() + delta.x())
            self.common_attr['PosY'] = str(-(self.pos().y() + delta.y()) + 585)
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

        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__startPos = None
        super().mousePressEvent(event)
