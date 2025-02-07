import socket
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QFile
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QTableWidget

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
        self.right_container = QWidget(self)
        self.right_container.setLayout(v_right_layout)
        h_splitter.addWidget(self.right_container)

        container_layout.addWidget(h_splitter)
        container_widget.setLayout(container_layout)

        self.tab_widget.addTab(container_widget, "Tree")


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

    def on_request_table_widget_item_clicked(self, item):
        if item.text() == "A661_REQ_FOCUS_ON_WIDGET":
            self.req_focus_on_widget_details.setVisible(True)
        else:
            self.req_focus_on_widget_details.setVisible(False)

    def on_layer_tree_widget_item_clicked(self, item):
        index = item.data(0, Qt.UserRole)
        if index is None:
            return
        self.message_commands_widget.setCurrentIndex(index)

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
        message_title = QTreeWidgetItem(["Message"])
        message_title.setData(0, Qt.UserRole, 0)
        self.message_tree_widget.addTopLevelItem(message_title)

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
        request_table_widget.setItem(0, 0, req_layer_active_item)
        req_layer_inactive_item = QTableWidgetItem("A661_REQ_LAYER_INACTIVE")
        request_table_widget.setItem(1, 0, req_layer_inactive_item)
        req_layer_visible_item = QTableWidgetItem("A661_REQ_LAYER_VISIBLE")
        request_table_widget.setItem(2, 0, req_layer_visible_item)
        req_focus_on_widget_item = QTableWidgetItem("A661_REQ_FOCUS_ON_WIDGET")
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
        message_widget = QWidget(self)
        message_widget_layout = QVBoxLayout()
        message_widget.setLayout(message_widget_layout)

        widget_type = self.parsed_xml['a661_widget'][0]['widget_prop']['type']
        widget_id = self.parsed_xml['a661_widget'][0]['model_prop']['prop']['WidgetIdent']
        message_widget_layout.addWidget(QLabel(f'{widget_type} ID:{widget_id}'))

        message_box = QGroupBox("Messages")
        message_box_layout = QVBoxLayout()
        message_box.setLayout(message_box_layout)

        message_table_widget = QTableWidget(10, 1)
        message_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        message_table_widget.horizontalHeader().setVisible(False)
        message_table_widget.verticalHeader().setVisible(False)

        message_box_layout.addWidget(message_table_widget)

        self.message_commands_widget.addWidget(message_widget)

    def init_message_commands_widget(self):
        self.init_blank_widget()
        self.init_request_widget()
        self.init_widgets_message_widget()

    def closeEvent(self, event):
        self.listener_thread.stop()
        self.disable_client_state_signal.emit(False)
        super().closeEvent(event)