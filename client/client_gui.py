import sys
import threading
import queue
import logging
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer
from pynput import keyboard

from client import RAT_CLIENT
from globals import request_queue, response_queue  # 导入全局变量

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_request_queue)
        self.timer.start(500)  # 每秒检查一次队列
        self.rat = RAT_CLIENT()
    
    def init_ui(self):
        self.setWindowTitle("NCCRAT CLIENT")
        self.setGeometry(500, 500, 300, 200)
        
        layout = QVBoxLayout()
        
        self.ip_label = QLabel("IP Address:")
        layout.addWidget(self.ip_label)

        self.ip_input = QLineEdit(self)
        self.ip_input.setText("127.0.0.1")
        layout.addWidget(self.ip_input)

        self.port_label = QLabel("Port:")
        layout.addWidget(self.port_label)

        self.port_input = QLineEdit(self)
        self.port_input.setText("4444")
        layout.addWidget(self.port_input)
        
        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_to_server)
        layout.addWidget(self.connect_button)
        
        self.setLayout(layout)
        
    def connect_to_server(self):
        host = self.ip_input.text()
        port = int(self.port_input.text())
        
        try:
            self.rat.bind(host, port)
            self.rat.build_connection()
            threading.Thread(target=self.rat.excute).start()
            QMessageBox.information(self, "Success!", f"Connected to {host}:{port}!")
        except Exception as e:
            QMessageBox.information(self, "Error", f"Failed to connect to {host}:{port}: {e}")
            
    def show_permission_dialog(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setText("是否允许启动键盘记录器？")
        msg_box.setWindowTitle("权限请求")
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return msg_box.exec() == QMessageBox.StandardButton.Yes

    def check_request_queue(self):
        while not request_queue.empty():
            msg = request_queue.get()
            logging.debug(f"Clientgui: received message: {msg}")  # 输出日志信息

            if msg == 'start_keylogger':
                if (self.show_permission_dialog()):
                    response_queue.put("clientgui_yes")
                else:
                    response_queue.put("clientgui_no")

    
    
def main():
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()