import socket
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QFile
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QTableWidget
from client.Messages import *
from widget.A661CommonParams import *



class ClientListenerThread(QThread):
    message_received = pyqtSignal(str)
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", self.port))
        self.sock.settimeout(1)
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                self.message_received.emit(data.decode("utf-8"))
            except socket.timeout:
                continue
            except OSError:
                break

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
        self.quit()
        self.wait()


class ClientWindow(QMainWindow):
    disable_client_state_signal = pyqtSignal(bool)
    def __init__(self, title, data, udp_port, target_port):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(1040, 140, 800, 800)

        self.udp_port = udp_port
        self.target_port = target_port

        self.parsed_xml = data

        self.message_buffer = {
            'self': None,
            'parents': [],
            'command': None,
            'command_value': None
        }

        self.tree_node_selected = None

        # UI
        menubar = self.menuBar()
        maps_menu = menubar.addMenu("Maps")
        open_xml_action = maps_menu.addAction("Open XML")
        save_as_xml_action = maps_menu.addAction("Save as XML")

        script_menu = menubar.addMenu("Scripting")
        manage_scripts_action = script_menu.addAction("Manage Scripts")
        open_script_action = script_menu.addAction("Open Script")
        open_user_view_action = script_menu.addAction("Open User View")
        script_menu.addSeparator()
        activate_script_action = script_menu.addAction("Activate Script")
        script_menu.addSeparator()
        load_scripts_configuration_action = script_menu.addAction("Load Scripts Configuration")
        save_scripts_configuration_action = script_menu.addAction("Save Scripts Configuration")

        scenarios_menu = menubar.addMenu("Scenarios")
        create_new_scenario_action = scenarios_menu.addAction("Create New Scenario")
        open_existing_scenario_action = scenarios_menu.addAction("Open Existing Scenario")
        options_action = scenarios_menu.addAction("Options")

        communication_bar = self.addToolBar("Communication Bar")
        communication_bar.setAllowedAreas(Qt.TopToolBarArea)
        communication_bar.setMovable(False)

        load_data_action = communication_bar.addAction("Load")
        connect_action = communication_bar.addAction("Connect")

        self.tab_widget = QTabWidget(self)
        
        self.setCentralWidget(self.tab_widget)

        # layout
        container_widget = QWidget(self)
        container_layout = QVBoxLayout()

        h_splitter = QSplitter(Qt.Horizontal)
        v_splitter = QSplitter(Qt.Vertical)

        self.layer_tree_widget = QTreeWidget(self)
        v_splitter.addWidget(self.layer_tree_widget)
        self.init_layer_tree_widget()

        self.message_tree_widget = QTreeWidget(self)
        v_left_layout = QVBoxLayout()
        v_left_layout.addWidget(self.message_tree_widget)

        v_left_layout.setContentsMargins(0, 0, 0, 0)
        v_left_layout.setSpacing(0)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.on_clicked_clear_button)
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.on_clicked_remove_button)
        v_left_layout.addWidget(remove_button)
        v_left_layout.addWidget(clear_button)
        send_button = QPushButton("Send")
        v_left_layout.addWidget(send_button)
        left_container = QWidget(self)
        left_container.setLayout(v_left_layout)
        v_splitter.addWidget(left_container)
        self.init_message_tree_widget()

        h_splitter.addWidget(v_splitter)
        self.message_commands_widget = QStackedWidget(self)
        self.init_message_commands_widget()
        v_right_layout = QVBoxLayout()
        v_right_layout.addWidget(self.message_commands_widget)

        v_right_layout.setContentsMargins(0, 0, 0, 0)
        v_right_layout.setSpacing(0)

        add_button = QPushButton("Add")
        v_right_layout.addWidget(add_button)
        add_button.clicked.connect(self.on_clicked_add_button)
        self.right_container = QWidget(self)
        self.right_container.setLayout(v_right_layout)
        h_splitter.addWidget(self.right_container)

        container_layout.addWidget(h_splitter)
        container_widget.setLayout(container_layout)

        self.tab_widget.addTab(container_widget, "Communication")


        file = QFile(r'C:\Users\shconnet\Downloads\Integrid\Integrid.qss')
        file.open(QFile.ReadOnly)
        style_sheet = file.readAll()
        self.setStyleSheet(str(style_sheet, encoding='utf-8'))

        # udp thread
        self.listener_thread = ClientListenerThread(self.udp_port)
        self.listener_thread.start()

    # def send_message(self):
    #     message = f"from port {self.udp_port}:"
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     sock.sendto(message.encode("utf-8"), ("127.0.0.1", self.target_port))
    #     self.text_edit.append(f"send message: {message}")

    def on_clicked_clear_button(self):
        root = self.message_tree_widget.topLevelItem(0)
        if root:
            root.takeChildren()

    def on_clicked_remove_button(self):
        root = self.message_tree_widget.topLevelItem(0)

        if root == self.tree_node_selected:
            return

        if not self.tree_node_selected:
            print("do not select")
            return
        
        for i in range(root.childCount()):
            layers = root.child(i)
            if layers == self.tree_node_selected:
                root.takeChild(i)
                return

            for j in range(layers.childCount()):
                widget = layers.child(j)
                if widget == self.tree_node_selected:
                    root.takeChild(i)
                    return
                
                for k in range(widget.childCount()):
                    command = widget.child(k)
                    if command == self.tree_node_selected:
                        root.takeChild(i)
                        return



    def on_request_table_widget_item_clicked(self, item):
        if item.text() == "A661_REQ_FOCUS_ON_WIDGET":
            self.req_focus_on_widget_details.setVisible(True)
        else:
            self.req_focus_on_widget_details.setVisible(False)

    def on_layer_tree_widget_item_clicked(self, item):
        index = item.data(0, Qt.UserRole)
        if index is None:
            return
        self.message_buffer['self'] = item.text(0)
        self.message_buffer['parents'] = []
        item = item.parent()
        while item:
            if item.text(0) == 'Layers':
                break
            self.message_buffer['parents'].append(item.text(0))
            item = item.parent()
        self.message_commands_widget.setCurrentIndex(index)

    def on_combo_box_current_index_changed(self, index):
        combo_box = self.sender()
        current_value = combo_box.currentText()
        print(f"Combo box current index changed: {current_value}")

        table_widget = combo_box.parent().parent()
        index = table_widget.indexAt(combo_box.pos())

        if index.isValid() and index.column() > 0:
            left_item = table_widget.item(index.row(), index.column() - 1)
            if left_item:
                self.message_buffer['command'] = left_item.text()
                self.message_buffer['command_value'] = current_value
                print(f"command: {left_item.text()}")
            else:
                print("null left item")
        else:
            print("not valid index")
    
    def on_message_table_widget_item_clicked(self, item):
        print(f"Item '{item.text()}' clicked.")

        index = item.data(Qt.UserRole)
        message_detail_box = item.data(Qt.UserRole + 1)
        single_command_detail_container = item.data(Qt.UserRole + 2)

        if index is None or message_detail_box is None or single_command_detail_container is None:
            print(f"Item '{item.text()}' is not integrated")
            return
        
        message_command_table = single_command_detail_container.widget(index).findChild(QTableWidget)

        if message_command_table is None:
            print(f"Table widget not found for item '{item.text()}'")
            return
        
        property = message_command_table.item(0, 0).text()

        cell_widget = message_command_table.cellWidget(0, 1)
        if isinstance(cell_widget, QComboBox):
            value = cell_widget.currentText()
        elif isinstance(message_command_table.item(0, 1), QTableWidgetItem):
            value = message_command_table.item(0, 1).text()
        else:
            value = ''
        self.message_buffer['command'] = property
        self.message_buffer['command_value'] = value
        
        name = item.text()
        for key, values in MESSAGE_TYPE.items():
            if name in values:
                message_detail_box.setTitle(key)
                break

        if not message_detail_box.isVisible():
            message_detail_box.setVisible(True)

        single_command_detail_container.setCurrentIndex(index)

    def on_message_tree_widget_item_clicked(self, item, column):
        self.tree_node_selected = item

    def on_clicked_add_button(self):
        try:
            all_parents_num = len(self.message_buffer['parents'])

            for index, parent in enumerate(reversed(self.message_buffer['parents'])):
                next_node = QTreeWidgetItem([parent])
                self.title_item.addChild(next_node)
                next_node.setData(0, Qt.UserRole, index)
                if index == all_parents_num - 1:
                    sender = QTreeWidgetItem([self.message_buffer['self']])
                    sender.setData(0, Qt.UserRole, all_parents_num)
                    next_node.addChild(sender)
                    command = QTreeWidgetItem([self.message_buffer['command']])
                    command.setData(0, Qt.UserRole, all_parents_num + 1)
                    sender.addChild(command)

            self.message_tree_widget.expandAll()
        except Exception as e:
            print(f'Error rendering message tree widget: {e}')



    def init_blank_widget(self):
        blank_widget = QWidget(self)
        blank_layout = QVBoxLayout()
        blank_widget.setLayout(blank_layout)
        self.message_commands_widget.addWidget(blank_widget)

    def init_layer_tree_widget(self):
        try:
            self.layer_tree_widget.setHeaderHidden(True)
            self.layer_tree_widget.itemClicked.connect(self.on_layer_tree_widget_item_clicked)


            layer_title = QTreeWidgetItem(["Layers"])
            layer_title.setData(0, Qt.UserRole, 0)
            self.layer_tree_widget.addTopLevelItem(layer_title)

            # get all Layer info and add into tree
            layers = self.parsed_xml['a661_layer']
            for index, layer in enumerate(layers):
                layer_name = layer['layer_prop']['name']
                layer_item = QTreeWidgetItem(['Layer ' + str(layer_name)])
                layer_item.setData(0, Qt.UserRole, index + 1)
                layer_title.addChild(layer_item)

                # get Layer all Widgets info belong to layer and add into tree
                widgets = self.parsed_xml['a661_widget']
                for index, widget in enumerate(widgets):
                    widget_name = widget['widget_prop']['name']
                    widget_item = QTreeWidgetItem([str(widget_name)])
                    widget_item.setData(0, Qt.UserRole, len(self.parsed_xml['a661_layer']) + index + 1)
                    layer_item.addChild(widget_item)

            self.layer_tree_widget.expandAll()

        except Exception as e:
            print(f'Error rendering layer tree widget: {e}')

    def init_message_tree_widget(self):
        self.message_tree_widget.setHeaderHidden(True)
        self.message_tree_widget.itemClicked.connect(self.on_message_tree_widget_item_clicked)
        self.title_item = QTreeWidgetItem(["Message"])
        self.message_tree_widget.addTopLevelItem(self.title_item)

    def init_request_widget(self):
        request_widget = QWidget(self)
        request_layout = QVBoxLayout()
        request_widget.setLayout(request_layout)
        appli_id = self.parsed_xml['a661_df']['model_prop']['ApplicationId']
        layer_id = self.parsed_xml['a661_layer'][0]['model_prop']['LayerId']
        title_label = QLabel(f'appliID:{appli_id} layerID:{layer_id}')
        title_label.setStyleSheet('color: black;')
        request_layout.addWidget(title_label)

        request_box = QGroupBox("Request")
        request_box_layout = QVBoxLayout()
        request_box.setLayout(request_box_layout)
        request_layout.addWidget(request_box)

        request_table_widget = QTableWidget(4, 1)
        request_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        request_table_widget.horizontalHeader().setVisible(False)
        request_table_widget.verticalHeader().setVisible(False)
        req_layer_active_item = QTableWidgetItem("A661_REQ_LAYER_ACTIVE")
        req_layer_active_item.setFlags(req_layer_active_item.flags() & ~Qt.ItemIsEditable)
        request_table_widget.setItem(0, 0, req_layer_active_item)
        req_layer_inactive_item = QTableWidgetItem("A661_REQ_LAYER_INACTIVE")
        req_layer_inactive_item.setFlags(req_layer_inactive_item.flags() & ~Qt.ItemIsEditable)
        request_table_widget.setItem(1, 0, req_layer_inactive_item)
        req_layer_visible_item = QTableWidgetItem("A661_REQ_LAYER_VISIBLE")
        req_layer_visible_item.setFlags(req_layer_visible_item.flags() & ~Qt.ItemIsEditable)
        request_table_widget.setItem(2, 0, req_layer_visible_item)
        req_focus_on_widget_item = QTableWidgetItem("A661_REQ_FOCUS_ON_WIDGET")
        req_focus_on_widget_item.setFlags(req_focus_on_widget_item.flags() & ~Qt.ItemIsEditable)
        request_table_widget.setItem(3, 0, req_focus_on_widget_item)
        request_table_widget.itemClicked.connect(self.on_request_table_widget_item_clicked)
        request_box_layout.addWidget(request_table_widget)

        self.req_focus_on_widget_details = QGroupBox("Request A661_ParametersStructure_1Byte")   
        req_focus_on_widget_details_layout = QVBoxLayout()
        self.req_focus_on_widget_details.setLayout(req_focus_on_widget_details_layout)

        req_details_table_widget = QTableWidget()
        req_details_table_widget.setColumnCount(2)
        req_details_table_widget.setHorizontalHeaderLabels(["WidgetName", "WidgetId"])
        req_details_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        req_details_table_widget.verticalHeader().setVisible(False)
        for widget_data in self.parsed_xml['a661_widget']:
            widget_name = widget_data.get('widget_prop', {}).get('name', '')
            widget_id = widget_data.get('model_prop', {}).get('prop', {}).get('WidgetIdent', '')

            if widget_name or widget_id:
                current_row = req_details_table_widget.rowCount()
                req_details_table_widget.insertRow(current_row)
                req_details_table_widget.setItem(current_row, 0, QTableWidgetItem(widget_name))
                req_details_table_widget.setItem(current_row, 1, QTableWidgetItem(widget_id))

        req_focus_on_widget_details_layout.addWidget(req_details_table_widget)
        request_layout.addWidget(self.req_focus_on_widget_details)
        self.message_commands_widget.addWidget(request_widget)

        self.req_focus_on_widget_details.setVisible(False)

    def init_widgets_message_widget(self):
        for widget in self.parsed_xml['a661_widget']:
            widget_type = widget['widget_prop']['type']
            widget_id = widget['model_prop']['prop']['WidgetIdent']

            # messages
            message_widget = QWidget(self)
            message_widget_layout = QVBoxLayout()
            message_widget.setLayout(message_widget_layout)
            message_label = QLabel(f'{widget_type} ID:{widget_id}')
            message_label.setStyleSheet('color: black;')
            message_widget_layout.addWidget(message_label)

            message_box = QGroupBox("Messages")
            message_box_layout = QVBoxLayout()
            message_box.setLayout(message_box_layout)
            message_widget_layout.addWidget(message_box)

            message_table_widget = QTableWidget(10, 1)
            message_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            message_table_widget.horizontalHeader().setVisible(False)
            message_table_widget.verticalHeader().setVisible(False)
            message_table_widget.setObjectName('message_table_widget')
            if widget_type == 'A661_COMBO_BOX':
                for index, message in enumerate(A661_COMBO_BOX):
                    message_item = QTableWidgetItem(message)
                    message_item.setFlags(message_item.flags() & ~Qt.ItemIsEditable)
                    message_item.setData(Qt.UserRole, index) # bind every stackedwidget index for message item
                    message_table_widget.setItem(index, 0, message_item)
            message_table_widget.itemClicked.connect(self.on_message_table_widget_item_clicked)
            message_box_layout.addWidget(message_table_widget)

            # message commands
            message_detail_box = QGroupBox('default')
            message_detail_box_layout = QVBoxLayout()
            message_detail_box.setLayout(message_detail_box_layout)
            single_command_detail_container = QStackedWidget()
            message_detail_box_layout.addWidget(single_command_detail_container)
            message_widget_layout.addWidget(message_detail_box)

            for type, messages in MESSAGE_TYPE.items():
                for message in messages:
                    if type == 'Message A661_ParameterStructure_1Byte':
                        message_command_widget = QWidget()
                        message_command_layout = QVBoxLayout()
                        message_command_widget.setLayout(message_command_layout)

                        message_command_table = QTableWidget(1,2)
                        message_command_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                        message_command_table.verticalHeader().setVisible(False)
                        message_command_table.setHorizontalHeaderLabels(['Property', 'Value'])
                        message_command_table.setItem(0, 0, QTableWidgetItem(f'{message}'))
                        command_combobox = QComboBox()
                        if message == 'A661_ENABLE':
                            command_combobox.addItems(A661_ENABLE.keys())
                            command_combobox.setCurrentIndex(0)
                            command_combobox.currentIndexChanged.connect(self.on_combo_box_current_index_changed)
                        elif message == 'A661_VISIBLE':
                            command_combobox.addItems(A661_VISIBLE.keys())
                            command_combobox.setCurrentIndex(0)
                            command_combobox.currentIndexChanged.connect(self.on_combo_box_current_index_changed)
                        elif message == 'A661_ENTRY_VALID':
                            command_combobox.addItems(A661_ENTRY_VALID.keys())
                            command_combobox.setCurrentIndex(1)
                            command_combobox.currentIndexChanged.connect(self.on_combo_box_current_index_changed)
                        elif message == 'A661_AUTO_FOCUS_MOTION':
                            command_combobox.addItems(A661_AUTO_FOCUS_MOTION.keys())
                            command_combobox.setCurrentIndex(1)
                            command_combobox.currentIndexChanged.connect(self.on_combo_box_current_index_changed)

                        message_command_table.setCellWidget(0, 1, command_combobox)
                        message_command_layout.addWidget(message_command_table)
                        single_command_detail_container.addWidget(message_command_widget)

                    elif type == 'Message A661_ParameterStructure_2Byte':
                        message_command_widget = QWidget()
                        message_command_layout = QVBoxLayout()
                        message_command_widget.setLayout(message_command_layout)

                        message_command_table = QTableWidget(1,2)
                        message_command_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                        message_command_table.verticalHeader().setVisible(False)
                        message_command_table.setHorizontalHeaderLabels(['Property', 'Value'])
                        message_command_table.setItem(0, 0, QTableWidgetItem(f'{message}'))
                        
                        if message == 'A661_NEXT_FOCUSED_WIDGET':
                            value = widget['model_prop']['prop']['NextFocusedWidget']
                            value_item = QTableWidgetItem(value)
                        elif message == 'A661_NUMBER_OF_ENTRIES':
                            value = widget['model_prop']['prop']['NumberOfEntries']
                            value_item = QTableWidgetItem(value)
                        elif message == 'A661_OPENING_ENTRY':
                            value = widget['model_prop']['prop']['OpeningEntry']
                            value_item = QTableWidgetItem(value)
                        elif message == 'A661_SELECTED_ENTRY':
                            value = widget['model_prop']['prop']['SelectedEntry']
                            value_item = QTableWidgetItem(value)
                        elif message == 'A661_STYLE_SET':
                            value = widget['model_prop']['prop']['StyleSet']
                            value_item = QTableWidgetItem(value)

                        message_command_table.setItem(0, 1, value_item)
                        message_command_layout.addWidget(message_command_table)
                        single_command_detail_container.addWidget(message_command_widget)

                    elif type == 'Message A661_ParameterStructure_StringArray':
                        value = widget['model_prop']['arrayprop']

                        message_command_widget = QWidget()
                        message_command_layout = QVBoxLayout()
                        message_command_widget.setLayout(message_command_layout)


                        message_command_table = QTableWidget(len(value), 2)
                        message_command_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                        message_command_table.verticalHeader().setVisible(False)
                        message_command_table.setHorizontalHeaderLabels(['Index', 'String'])
                        message_command_table.setObjectName(message)
                        for idx, val in enumerate(value):
                            message_command_table.setItem(idx, 0, QTableWidgetItem(str(idx)))
                            message_command_table.setItem(idx, 1, QTableWidgetItem(str(val)))

                        message_command_layout.addWidget(message_command_table)
                        single_command_detail_container.addWidget(message_command_widget)
            

            for row in range(message_table_widget.rowCount()):
                item = message_table_widget.item(row, 0)
                if item:
                    item.setData(Qt.UserRole + 1, message_detail_box)
                    item.setData(Qt.UserRole + 2, single_command_detail_container)

            message_detail_box.setVisible(False)
            self.message_commands_widget.addWidget(message_widget)

    def init_message_commands_widget(self):
        self.init_blank_widget()
        self.init_request_widget()
        self.init_widgets_message_widget()

    def closeEvent(self, event):
        self.listener_thread.stop()
        self.disable_client_state_signal.emit(False)
        super().closeEvent(event)