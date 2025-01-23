from widget.A661CommonParams import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QStyledItemDelegate

class AlignmentDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, alignment=Qt.AlignmentFlag.AlignLeft):
        super().__init__(parent)
        self.displayAlignment = alignment

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = self.displayAlignment

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

    def init_widget_alignment(self):
        alignment_name = self.common_attr['Alignment']
        alignment = A661_ALIGNMENT.get(alignment_name)
        if alignment is None:
            raise ValueError("Invalid alignment name: {}".format(alignment_name))
        
        if alignment is not None:
            self.setAlignment(alignment)

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

    def on_item_changed(self, item):
        if self.is_user_input:
            # print(f"Item changed: {item.text()}")
            # get the index to confirm the item changed
            index = item.index()
            row = index.row()
            column = index.column()
            previous_index = self.model.index(row, column - 1)
            previous_item = self.model.itemFromIndex(previous_index)

            if previous_item == None:
                return
            elif previous_item.text() == 'PosX':
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
            elif previous_item.text() == 'Alignment':
                self.common_attr['Alignment'] = item.text()
                self.setAlignment(A661_ALIGNMENT.get(item.text()))
            elif previous_item.text() == 'A661_ENABLE':
                self.common_attr['Enable'] = A661_ENABLE.get(item.text())
                self.setEnabled(A661_ENABLE.get(item.text()))
            elif previous_item.text() == 'A661_VISIBLE':
                self.common_attr['Visible'] = A661_VISIBLE.get(item.text())
                self.setVisible(A661_VISIBLE.get(item.text()))
        

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
