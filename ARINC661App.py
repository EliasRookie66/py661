import os
import sys
from parse import XMLA661Parser as XMLA661Parser

from PyQt5.QtCore import Qt, pyqtSignal, QFile
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon

from widget.Container import  AppContainer
from widget.ComboBox import *
from widget.A661CommonParams import *
from widget.Label import A661Label
from widget.TabWidget import *
from widget.PushButton import *
from client.Client import *

class ModelDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        column = index.column()
        # always create combobox when click item
        # wait to handle
        if column == 1:
            left_text = index.siblingAtColumn(0).data()
            if left_text == 'Alignment':
                combo = QComboBox(parent)
                combo.addItems(list(A661_ALIGNMENT.keys()))
                return combo
            elif left_text == 'OpeningMode':
                combo = QComboBox(parent)
                combo.addItems(list(OpeningMode.keys()))
                return combo
            elif left_text == 'A661_AUTO_FOCUS_MOTION':
                combo = QComboBox(parent)
                combo.addItems(list(A661_AUTO_FOCUS_MOTION.keys()))
                return combo
            elif left_text == 'A661_ENABLE':
                combo = QComboBox(parent)
                combo.addItems(list(A661_ENABLE.keys()))
                return combo
            elif left_text == 'A661_VISIBLE':
                combo = QComboBox(parent)
                combo.addItems(list(A661_VISIBLE.keys()))
                return combo
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            value = index.data()
            if value:
                editor.setCurrentText(value)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            model.setData(index, editor.currentText())
        else:
            super().setModelData(editor, model, index)

class ARINC661App(QMainWindow):

    add_widget_signal = pyqtSignal(str, dict)

    def __init__(self):
        super().__init__(parent=None)

        self.add_widget_signal.connect(self.add_tab)
        self.setup_ui()
        file = QFile(r'C:\Users\shconnet\Downloads\Integrid\Integrid.qss')
        file.open(QFile.ReadOnly)
        style_sheet = file.readAll()
        self.setStyleSheet(str(style_sheet, encoding='utf-8'))

    def setup_ui(self):
        self.setWindowTitle(self.tr("ARINC 661 Editor"))
        self.setGeometry(420, 60, 1080, 960)

        # menu
        menubar = self.menuBar()

        # File
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New DF")
        open_df_action = file_menu.addAction("Open DF")
        open_df_action.triggered.connect(self.on_triggered_open_df)
        file_menu.addMenu("Open recent DFs")
        file_menu.addSeparator()
        file_menu.addAction("Save")
        save_as_menu = file_menu.addMenu("Save as")
        save_as_menu.addAction('As XML')
        save_as_menu.addAction('As Binary')
        file_menu.addAction("Convert")
        file_menu.addSeparator()
        import_menu = file_menu.addMenu("Import")
        import_menu.setEnabled(False)
        export_menu = file_menu.addMenu("Export")
        export_menu.setEnabled(False)
        file_menu.addAction("Save Snapshot")
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        # Editor
        editor_menu = menubar.addMenu('Editor')
        editor_menu.addAction('Search')
        editor_menu.addAction('Set Background')
        editor_menu.addAction('Background Parameters')
        editor_menu.addSeparator()
        editor_menu.addAction('Snap To Grid')

        # Runtime
        runtime_menu = menubar.addMenu('Runtime')
        runtime_menu.addAction('Create Server')
        runtime_menu.addSeparator()
        self.open_client_action = runtime_menu.addAction('Open Client')
        self.open_client_action.setEnabled(False)
        self.open_client_action.triggered.connect(self.on_triggered_open_client)
        runtime_menu.addSeparator()
        runtime_menu.addAction('Set Look And Feel')
        runtime_menu.addAction('Reload Look And Feel')

        # Options
        option_menu = menubar.addMenu('Options')
        option_menu.addAction('Settings')
        option_menu.addSeparator()
        option_menu.addAction('Load Configuration')
        option_menu.addAction('Save Configuration')
        option_menu.addAction('Reload Configuration')

        # Tools
        tools_menu = menubar.addMenu('Tools')
        tools_menu.addAction('Extract UI Defaults')
        cockpit_plugin = tools_menu.addMenu('Cockpit Plugin')
        cockpit_plugin.addAction('Convert Cockpit Configuration File')
        debugging = tools_menu.addMenu('Debugging')
        debugging.addAction('Decode Message')
        debugging.addAction('Decode Scenario')
        debugging.addSeparator()
        debugging.addAction('Debug Server')
        editor_scriping = tools_menu.addMenu('Editor Scripting')
        editor_scriping.addAction('Apply Script On Current DF')
        editor_scriping.addAction('Apply Script On All DFs')
        look_n_feel = tools_menu.addMenu('Look Model')
        look_n_feel.addAction('Open Look Capacities')
        look_n_feel.addAction('Open Look Definition')
        look_n_feel.addAction('Convert Look Model')
        synth2_menu = look_n_feel.addMenu('Synth2')
        synth2_menu.addAction('Convert From Synth2 to Look Model')
        synth2_menu.addAction('Convert From Look Model to Synth2')
        style_set_extraction_menu = look_n_feel.addMenu('Style Set Extraction')
        style_set_extraction_menu.addAction('Extract Style Sets from Look and Feel file')

        uacds_plugin = tools_menu.addMenu('UACDS Plugin')
        uacds_plugin.addAction('Create UACDS Interface')
        uacds_plugin.addAction('Save UACDS Interface File')
        wd_plugin = tools_menu.addMenu('WidgetDefinition Plugin')
        wd_plugin.addAction('View Widget Definition')
        wd_plugin.addAction('Extract Supplement')
        wd_plugin.addAction('Produce Full Metadefinition')
        wd_plugin.addAction('Generate Documentation')
        wd_plugin.addSeparator()
        wd_plugin.addAction('Apply Meta-definition Script')

        help_menu = menubar.addMenu('Help')
        help_menu.addAction('Wiki')
        help_menu.addAction('About')
        help_menu.addAction('About Plugins')

        # tool bar
        file_bar = self.addToolBar('File Bar')
        file_bar.setAllowedAreas(Qt.TopToolBarArea)
        file_bar.setMovable(True)
        new_file_action = file_bar.addAction(QIcon(r'C:\icons\new_file'), 'New Definition File')

        open_folder_action = file_bar.addAction(QIcon(r'C:\icons\open_folder'), 'Open Folder')
        open_folder_action.triggered.connect(self.on_triggered_open_df)

        save_file_action = file_bar.addAction(QIcon(r'C:\icons\save_file'), 'Save')

        # main widget
        central_widget = QWidget(self)

        v_splitter = QSplitter(Qt.Vertical)
        self.tab_widget = A661TabWidget(self)
        self.tab_widget.enable_client_state_signal.connect(self.on_update_client_state)
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

    def on_update_client_state(self, state):
        self.open_client_action.setEnabled(state)

    def on_triggered_open_client(self):
        self.client = ClientWindow('client', self.parsed_xml, udp_port=5001, target_port=5000)
        self.client.show()

    
    def on_tree_widget_item_clicked(self, item, column):
        # table
        index = item.data(0, Qt.UserRole)
        self.stacked_widget.setCurrentIndex(index)
        # TODO : focus widget

    def set_properties_ineditable(self, model):
        for row in range(model.rowCount()):
            for column in range(model.columnCount()):
                item = model.item(row, column)
                if column == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
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
                                combined_string = ' '.join(str(v) for v in value)
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
        self.set_properties_ineditable(model)

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

            self.set_properties_ineditable(df_model)


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

                self.set_properties_ineditable(layer_model)

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
            for widget, type in self.widget_dict.items():
                # initialize table view
                widget_view = QTableView(self)
                widget.is_user_input = False
                self.set_properties_ineditable(widget.model)
                delegate = ModelDelegate(widget_view)
                widget_view.setItemDelegate(delegate)
                widget_view.setModel(widget.model)
                widget.is_user_input = True
                widget_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                widget_view.verticalHeader().setVisible(False)
                

                display_widget = QWidget(self)
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
            self.hint_label = A661Label(self.display_widget)
            self.hint_label.setFrameStyle(QFrame.Box)
            self.hint_label.setGeometry(0, 0, 500, 500)
            # self.hint_label.setStyleSheet("")
            
            self.display_widget.setGeometry(0, 0, 500, 500)
            self.widget_dict = dict()

            # traverse widget and add into display widget 
            for widget in self.parsed_xml['a661_widget']:

                # Step1 : get the element's type
                widget_type = widget['widget_prop']['type']

                # Step2 : create the element
                if widget_type == 'A661_COMBO_BOX':
                    widget_combo_box = A661ComboBox(self.hint_label)
                    self.widget_dict[widget_combo_box] = widget_type
                    # step3 : initialize element's attributes and create table model
                    self.init_common_attr(widget, widget_combo_box)
                    self.init_unique_attr(widget, widget_combo_box)

                elif widget_type == 'A661_PUSH_BUTTON':
                    widget_push_button = A661PushButton(self.hint_label) # QPushButton
                    self.widget_dict[widget_push_button] = widget_type
                    self.init_common_attr(widget, widget_push_button)
                    self.init_unique_attr(widget, widget_push_button)
                    

        except Exception as e:
            print(f"Error rendering display widget: {e}")


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
                target.model.appendRow([QStandardItem(XMLA661Parser.widget_properties[key]), QStandardItem(str(value))])

        # alignment delegate
        target.init_widget_alignment()

        # modify the position
        transform_into_py661_position_rate = 0.05 # 380 / 10000 * 25 / 19 = 0.05

        # widget_height = self.hint_label.height()
        # widget_width = self.hint_label.width()

        target.common_attr['SizeX'] = round(int(source['model_prop']['prop'].get('SizeX', 0)) * transform_into_py661_position_rate)
        target.common_attr['SizeY'] = round(int(source['model_prop']['prop'].get('SizeY', 0)) * transform_into_py661_position_rate)
        target.common_attr['PosX'] = round(int(source['model_prop']['prop'].get('PosX', 0)) * transform_into_py661_position_rate)
        target.common_attr['PosY'] = round(int(source['model_prop']['prop'].get('PosY', 0)) * transform_into_py661_position_rate)
        # print(f"widget_pos_x:{target.common_attr['PosX']} \t widget_position_y:{target.common_attr['PosY']}")

        target.setGeometry(target.common_attr['PosX'], 400 - target.common_attr['PosY'], target.common_attr['SizeX'], target.common_attr['SizeY'])

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
        elif self.widget_dict[target] == 'A661_PUSH_BUTTON':
            for key, value in source['model_prop']['prop'].items():
                if key in target.button_attr.keys():
                    target.button_attr[key] = value
                    # append model row
                    if key in XMLA661Parser.widget_properties.keys():
                        target.model.appendRow([QStandardItem(XMLA661Parser.widget_properties[key]), QStandardItem(str(value))])
        # print(f'key:{target}, value:{self.widget_dict[target]}')

    def add_tab(self, file_name):
        # container
        container_widget = QWidget(self)
        layout = QHBoxLayout()


        self.display_widget = AppContainer(self)
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
