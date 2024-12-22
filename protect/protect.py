import psutil
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PySide6.QtGui import QScreen
import logging


class Protect:
    def __init__(self):
        self.create_gui()

    def create_gui(self):
        app = QApplication([])
        window = QMainWindow()
        window.setWindowTitle("TCP Connections")

        # 设置窗口大小为800x600
        window.resize(800, 600)

        # 获取屏幕尺寸并计算窗口居中位置
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        window.move(x, y)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        tree = QTreeWidget()
        tree.setColumnCount(3)
        tree.setHeaderLabels(
            ["Index", "Local Address", "Remote Address", "Status"])

        # 插入数据并显示序号
        for index, conn in enumerate(self.list_tcp_connections(), start=1):
            laddr = f"{conn.laddr.ip}:{
                conn.laddr.port}" if conn.laddr else "N/A"
            raddr = f"{conn.raddr.ip}:{
                conn.raddr.port}" if conn.raddr else "N/A"
            print("index:", index)
            item = QTreeWidgetItem([str(index), laddr, raddr, conn.status])
            tree.addTopLevelItem(item)

        layout.addWidget(tree)
        window.setCentralWidget(central_widget)
        window.show()
        app.exec()

    def list_tcp_connections(self):
        connections = psutil.net_connections(kind='tcp')
        return connections


if __name__ == "__main__":
    protect = Protect()
