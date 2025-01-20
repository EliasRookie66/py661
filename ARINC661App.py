import os
import sys
from parse import XMLA661Parser as XMLA661Parser

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from widget.BasicContainer import  ARINC661BasicContainer
from widget.ComboBox import A661ComboBox
from widget.A661CommonParams import *
from PyQt5.QtWidgets import QCheckBox


class AlignmentDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, alignment=Qt.AlignmentFlag.AlignLeft):
        super().__init__(parent)
        self.displayAlignment = alignment

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = self.displayAlignment


class ARINC661App(QMainWindow):

    add_widget_signal = pyqtSignal(str, dict)

    def __init__(self):
        super().__init__(parent=None)

        self.add_widget_signal.connect(self.add_tab)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("ARINC 661 Editor")
        self.setGeometry(420, 60, 1080, 960)

        # menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New DF")
        open_df_action = file_menu.addAction("Open DF")
        open_df_action.triggered.connect(self.on_triggered_open_df)
        file_menu.addMenu("Open recent DFs")
        file_menu.addSeparator()
        file_menu.addAction("Save")
        file_menu.addMenu("Save as")
        file_menu.addAction("Convert")
        file_menu.addSeparator()
        file_menu.addMenu("Import")
        file_menu.addMenu("Export")
        file_menu.addAction("Save Snapshot")
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        # tool

        # main widget
        central_widget = QWidget(self)

        v_splitter = QSplitter(Qt.Vertical)
        self.tab_widget = QTabWidget(self)
        bottom_widget = QWidget(self)
        bottom_text_edit = QTextEdit()
        bottom_text_edit.setReadOnly(True)
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(bottom_text_edit)
        bottom_widget.setLayout(bottom_layout)

        v_splitter.addWidget(self.tab_widget)
        v_splitter.addWidget(bottom_widget)
        v_splitter.setStretchFactor(0, 1)

        central_layout = QHBoxLayout()
        central_layout.addWidget(v_splitter)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)
    
    def on_tree_widget_item_clicked(self, item, column):
        # table
        index = item.data(0, Qt.UserRole)
        self.stacked_widget.setCurrentIndex(index)
        # TODO : focus widget

    
    def on_check_box_clicked(self, state):
        """ check box clicked """
        sender = self.sender()
        clicked_name = sender.text()

        ancestor = sender.parent().parent()
        view = ancestor.findChild(QTableView)
        model = view.model()

        if sender.isChecked():
            for keys, values in A661_WIDGET_EXTENSION.items():
                if keys == clicked_name:
                    if isinstance(values, dict):
                        for key, value in values.items():
                            if isinstance(value, str):
                                model.appendRow([QStandardItem(key), QStandardItem(value)])
                            elif isinstance(value, list):
                                combined_string = ' '.join(str(value))
                                model.appendRow([QStandardItem(key), QStandardItem(combined_string)])
                    else:
                        model.appendRow([QStandardItem(clicked_name), QStandardItem(values)])
        else:
            row = 0
            while row < model.rowCount():
                item = model.item(row, 0)
                
                if isinstance(A661_WIDGET_EXTENSION[clicked_name], dict):
                    for keys in A661_WIDGET_EXTENSION[clicked_name].keys():
                        if item.text() == keys:
                            model.removeRow(row)
                            break
                    else:
                        row += 1
                else:
                    if item.text() == clicked_name:
                        model.removeRow(row)
                    else:
                        row += 1

    def default_check_box(self, layout, widget, type):
        """ default to create a series check boxes for every widget """
        for key in A661_WIDGET_EXTENSION.keys():
            check_box = QCheckBox(key)
            check_box.setChecked(False)
            layout.addWidget(check_box)
            check_box.stateChanged.connect(self.on_check_box_clicked)
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
    
    def init_tree_widget(self):
        try:
            self.tree_widget.setHeaderHidden(True)
            self.tree_widget.itemClicked.connect(self.on_tree_widget_item_clicked)

            # get DF name
            df_name = self.parsed_xml['a661_df']['df_prop']['name']
            df_item = QTreeWidgetItem([str(df_name)])
            df_item.setData(0, Qt.UserRole, 0)
            self.tree_widget.addTopLevelItem(df_item)

            # get all Layer info and add into tree
            layers = self.parsed_xml['a661_layer']
            for index, layer in enumerate(layers):
                layer_name = layer['layer_prop']['name']
                layer_item = QTreeWidgetItem([str(layer_name)])
                layer_item.setData(0, Qt.UserRole, index + 1)
                df_item.addChild(layer_item)

                # get Layer all Widgets info belong to layer and add into tree
                widgets = self.parsed_xml['a661_widget']
                for index, widget in enumerate(widgets):
                    widget_name = widget['widget_prop']['name']
                    widget_item = QTreeWidgetItem([str(widget_name)])
                    widget_item.setData(0, Qt.UserRole, len(self.parsed_xml['a661_layer']) + index + 1)
                    layer_item.addChild(widget_item)
        except Exception as e:
            print(f"Error rendering tree widget: {e}")
    
    def init_df_table(self):
        """ df table view """
        try:
            df_model = QStandardItemModel()

            df_model.setColumnCount(2)
            df_model.setHorizontalHeaderLabels(['Property', 'Value'])

            df_name = self.parsed_xml['a661_df']['df_prop']['name']
            df_id = self.parsed_xml['a661_df']['model_prop']['ApplicationId']

            df_model.appendRow([QStandardItem('Name'), QStandardItem(df_name)])
            df_model.appendRow([QStandardItem('Appli ID'), QStandardItem(df_id)])

            df_view = QTableView(self)
            df_view.setModel(df_model)

            df_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            df_view.verticalHeader().setVisible(False)

            df_widget = QWidget(self)
            df_layout = QVBoxLayout()
            df_layout.addWidget(df_view)
            df_widget.setLayout(df_layout)
            self.stacked_widget.addWidget(df_widget)

        except Exception as e:
            print(f"Error rendering df table: {e}")

    def init_layer_table(self):
        """ layer table view """
        try:
            for layer in self.parsed_xml['a661_layer']:
                layer_model = QStandardItemModel()
                layer_model.setColumnCount(2)
                layer_model.setHorizontalHeaderLabels(['Property', 'Value'])

                layer_name = layer['layer_prop']['name']
                layer_id = layer['model_prop']['LayerId']
                layer_width = layer['model_prop']['Width']
                layer_height = layer['model_prop']['Height']

                layer_model.appendRow([QStandardItem('Name'), QStandardItem(layer_name)])
                layer_model.appendRow([QStandardItem('ID'), QStandardItem(layer_id)])
                layer_model.appendRow([QStandardItem('Width'), QStandardItem(layer_width)])
                layer_model.appendRow([QStandardItem('Height'), QStandardItem(layer_height)])

                layer_view = QTableView(self)
                layer_view.setModel(layer_model)
                layer_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                layer_view.verticalHeader().setVisible(False)

                layer_widget = QWidget(self)
                layer_layout = QVBoxLayout()
                layer_layout.addWidget(layer_view)
                layer_widget.setLayout(layer_layout)
                self.stacked_widget.addWidget(layer_widget)
        
        except Exception as e:
            print(f"Error rendering layer table: {e}")

    def init_widget_table(self):
        try:
            count = 0
            for widget, type in self.widget_dict.items():
                # initialize table view
                widget_view = QTableView(self)
                widget_view.setModel(widget.model)
                widget_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                widget_view.verticalHeader().setVisible(False)

                display_widget = QWidget(self)
                display_widget.setObjectName(f"{type}_{count}")
                widget_layout = QVBoxLayout()

                # create a splitter for table view widget and check box widget
                splitter = QSplitter(display_widget)
                splitter.addWidget(widget_view)

                # create a series of check boxes for every combo box
                additional_widget = QWidget(self)
                additional_layout = QVBoxLayout()

                additional_widget.setLayout(additional_layout)
                self.default_check_box(additional_layout, widget, type)

                splitter.addWidget(additional_widget)
                
                widget_layout.addWidget(splitter)
                display_widget.setLayout(widget_layout)
                self.stacked_widget.addWidget(display_widget)
        except Exception as e:
            print(f"Error rendering widget table: {e}")


    def init_stacked_widget(self):
        try:
            # initialize all tables            
            self.init_df_table()
            self.init_layer_table()
            self.init_widget_table()

            # display widget
            self.stacked_widget.setCurrentIndex(0)

        except Exception as e:
            print(f"Error rendering stacked widget: {e}")

    
    def init_display_widget(self):
        try:
            # initialize display widget 
            self.display_widget.setGeometry(0, 0, 500, 500)
            self.widget_dict = dict()

            # traverse widget and add into display widget 
            for widget in self.parsed_xml['a661_widget']:

                # Step1 : get the element's type
                widget_type = widget['widget_prop']['type']

                # Step2 : create the element
                if widget_type == 'A661_COMBO_BOX':
                    widget_combo_box = A661ComboBox(self.display_widget)  # QComboBox A661ComboBox
                    self.widget_dict[widget_combo_box] = widget_type
                    # step3 : initialize element's attributes and create table model
                    self.init_common_attr(widget, widget_combo_box)
                    self.init_unique_attr(widget, widget_combo_box)

                elif widget_type == 'A661_PUSH_BUTTON':
                    widget_push_button = QPushButton(self.display_widget)
                    self.widget_dict[widget_push_button] = widget_type
                    widget_push_button.setText(widget['model_prop']['prop'].get('LabelString', ''))

        except Exception as e:
            print(f"Error rendering display widget: {e}")
    


    def init_widget_alignment(self, target):
        target.setEditable(True)
        line_edit = target.lineEdit()
        line_edit.setReadOnly(True)
        alignment_name = target.common_attr['Alignment']

        alignment = A661_ALIGNMENT.get(alignment_name)
        if alignment is None:
            raise ValueError("Invalid alignment name: {}".format(alignment_name))
        
        if alignment is not None:
            line_edit.setAlignment(alignment)

        current_delegate = target.itemDelegate()

        # none then create
        if current_delegate is None:
            alignment_delegate = AlignmentDelegate(target, alignment)
            target.setItemDelegate(alignment_delegate)
        elif isinstance(current_delegate, AlignmentDelegate):
            # already have then delete old and create new
            if current_delegate.alignment != alignment:
                target.setItemDelegate(None)
                alignment_delegate = AlignmentDelegate(target, alignment)
                target.setItemDelegate(alignment_delegate)
            # different type then delete old and create new
            else:
                target.setItemDelegate(None)
                alignment_delegate = AlignmentDelegate(target, alignment)
                target.setItemDelegate(alignment_delegate)



    def init_common_attr(self, source, target):
        # create model (only includes common parameters)
        target.model.setColumnCount(2)
        target.model.setHorizontalHeaderLabels(['Property', 'Value'])

        # Name
        target.common_attr['Name'] = source['widget_prop']['name']
        target.model.appendRow([QStandardItem('Name'), QStandardItem(target.common_attr['Name'])])

        # traverse
        for key, value in source['model_prop']['prop'].items():
            if key in target.common_attr:
                target.common_attr[key] = value

        for key, value in target.common_attr.items():
            if key in XMLA661Parser.widget_properties.keys():
                target.model.appendRow([QStandardItem(key), QStandardItem(str(value))])

        # alignment delegate
        self.init_widget_alignment(target)

        # modify the position
        widget_height = self.display_widget.height()
        widget_width = self.display_widget.width()
        widget_pos_x = round(int(source['model_prop']['prop'].get('PosX', 0)) / 10)
        widget_pos_y = round(int(source['model_prop']['prop'].get('PosY', 0)) / 20)
        target.common_attr['SizeX'] = round(int(source['model_prop']['prop'].get('SizeX', 0)) / 20)
        target.common_attr['SizeY'] = round(int(source['model_prop']['prop'].get('SizeY', 0)) / 20)
        target.common_attr['PosX'] = widget_width - widget_pos_x - target.common_attr['SizeX']
        target.common_attr['PosY'] = widget_height - widget_pos_y - target.common_attr['SizeY']
        target.setGeometry(target.common_attr['PosX'], target.common_attr['PosY'], target.common_attr['SizeX'],
                        target.common_attr['SizeY'])


    def init_unique_attr(self, source, target):
        if self.widget_dict[target] == 'A661_COMBO_BOX':
            for key, value in source['model_prop']['prop'].items():
                if key in target.combo_attr.keys():
                    target.combo_attr[key] = value
                    # append model row
                    if key in XMLA661Parser.widget_properties.keys():
                        target.model.appendRow([QStandardItem(XMLA661Parser.widget_properties[key]), QStandardItem(str(value))])

            entry_list = source['model_prop']['arrayprop']
            widget_string_combined = ' '.join(entry_list)
            target.model.appendRow([QStandardItem('A661_STRING_ARRAY'), QStandardItem(widget_string_combined)])
            target.addItems(entry_list)
        # print(f'key:{target}, value:{self.widget_dict[target]}')



    def add_tab(self, file_name):
        # container
        container_widget = QWidget(self)
        layout = QHBoxLayout()

        self.display_widget = ARINC661BasicContainer(self)            # display widget
        self.init_display_widget()

        h_splitter = QSplitter(Qt.Horizontal)
        v_splitter = QSplitter(Qt.Vertical)

        # treeWidget
        self.tree_widget = QTreeWidget(self)
        v_splitter.addWidget(self.tree_widget)
        self.init_tree_widget()


        # stackedWidget(tableWidget)
        self.stacked_widget = QStackedWidget(self)
        v_splitter.addWidget(self.stacked_widget)
        self.init_stacked_widget()        # modify

        h_splitter.addWidget(v_splitter)
        h_splitter.addWidget(self.display_widget)
        h_splitter.setStretchFactor(1, 1)

        self.tree_widget.expandAll()

        layout.addWidget(h_splitter)

        container_widget.setLayout(layout)

        self.tab_widget.addTab(container_widget, file_name)


    def open_df(self, selected_files):
        for file_path in selected_files:
            file_name = os.path.basename(file_path).split(".")[0]
            with open(f'{file_path}', 'r') as file:
                self.parsed_xml = XMLA661Parser.parse(file)
                # XMLA661Parser.print_parts_info(self.parsed_xml)
                self.add_widget_signal.emit(file_name, self.parsed_xml)


    def on_triggered_open_df(self):
        file_filter = "XML Files (*.xml);;Binary Files (*.bin);;All Files (*)"

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter(file_filter)
        default_dir = r"C:\workplace\j661fx\j661fx-src-1.8.1b2\sampleFiles"
        file_dialog.setDirectory(default_dir)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file in selected_files:
                print("Selected file:", file)

            if selected_files:
                self.open_df(selected_files)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ARINC661App()
    window.show()
    sys.exit(app.exec_())
