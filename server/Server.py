import socket
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
from widget.Label import A661Label
from widget.ComboBox import A661ComboBox


class ServerListenerThread(QThread):
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


class ServerWindow(QWidget):
    disable_client_state_signal = pyqtSignal(bool)
    def __init__(self, title, original_label, udp_port, target_port):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(230, 290, 500, 500)
        self.label = self.copy_label(original_label)
        self.setWindowIcon(QIcon(r'C:\work\TestBenchV1.0.6\TestBenchV1.0.6\eclipse\configuration\org.eclipse.osgi\169\0\.cp\icons\connet-logo-16.png'))



        self.udp_port = udp_port
        self.target_port = target_port

        # UI
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # udp thread
        self.listener_thread = ServerListenerThread(self.udp_port)
        self.listener_thread.start()

    def closeEvent(self, event):
        self.listener_thread.stop()
        self.disable_client_state_signal.emit(False)
        super().closeEvent(event)

    def copy_label(self, original_label: A661Label):
        new_label = A661Label()
        new_label.setGeometry(original_label.geometry())
        new_label.setFrameStyle(original_label.frameStyle())

        for combo in original_label.findChildren(A661ComboBox):
            new_combo = A661ComboBox(new_label)
            new_combo.resize(combo.size())
            new_combo.move(combo.pos())
            new_combo.addItems([combo.itemText(i) for i in range(combo.count())])
            new_combo.setCurrentIndex(combo.currentIndex())
            
            new_combo.movable = False

        return new_label