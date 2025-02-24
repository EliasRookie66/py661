from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QFile, Qt, QVariant
from demo.ComboBox import ComboBox
from demo.TabWidget import TabWidget


class Display(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ARINC 661 Editor")
        self.setGeometry(620, 60, 1080, 960)

        container_layout = QVBoxLayout()
        container_item_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # top  layout
        top_layout = QHBoxLayout()
        top_combobox = QComboBox()
        top_combobox.addItems(['FMS 1'])
        top_combobox.setStyleSheet("""
                background-color: transparent;
                color: rgb(0, 227, 227);
                border: 1px solid white;
        """)
        top_layout.addWidget(top_combobox)
        top_item_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        top_layout.addItem(top_item_spacer)
        top_label = QLabel('- - - - - - - - - -  ')
        top_label.setStyleSheet('color: white;')
        top_layout.addWidget(top_label)
        container_layout.addLayout(top_layout)

        # menu combobox layout
        active_box = ComboBox()

        active_box.addItems(['ACTIVE', 'F-PLN', 'PERF', 'FUEL&LOAD', 'WIND', 'INIT'])
        active_box.setItemData(4, QVariant(0), Qt.ItemDataRole.UserRole - 1)
        menu_box_layout = QHBoxLayout()
        menu_box_layout.setSpacing(0)
        menu_box_layout.addWidget(active_box)
        container_layout.addLayout(menu_box_layout)

        position_box = ComboBox()
        position_box.addItems(['POSITION'])
        menu_box_layout.addWidget(position_box)

        sec_box = ComboBox()
        sec_box.addItems(['SEC INDEX'])
        menu_box_layout.addWidget(sec_box)

        data_box = ComboBox()
        data_box.addItems(['DATA'])
        menu_box_layout.addWidget(data_box)

        # label
        title_label = QLabel('FLIGHTMANAGERSYSTEM                |       |           ')
        title_label.setStyleSheet('color: black;'
                                  'background-color: rgb(134, 138, 157);'
                                  )
        title_label.setMinimumHeight(30)
        title_label.resize(self.width(), 30)
        container_layout.addWidget(title_label)

        tabwidget = TabWidget()
        container_layout.addWidget(tabwidget)

        container_layout.addItem(container_item_spacer)
        self.setLayout(container_layout)

        file = QFile(r'C:\py661\demo\dis.qss')
        file.open(QFile.ReadOnly)
        style_sheet = file.readAll()
        self.setStyleSheet(str(style_sheet, encoding='utf-8'))


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = Display()
    w.show()
    sys.exit(app.exec_())