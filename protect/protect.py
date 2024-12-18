import psutil
import tkinter as tk
from tkinter import ttk

def list_tcp_connections():
    connections = psutil.net_connections(kind='tcp')
    return connections
    
def create_gui():
    root = tk.Tk()
    root.title("TCP Connections")

    # 设置窗口大小为800x600
    root.geometry("800x600")
    
    tree = ttk.Treeview(root, columns=("Local Address", "Remote Address", "Status"))
    tree.heading("#0", text="Index")
    tree.column("#0", anchor="center", width=50)
    tree.heading("Local Address", text="Local Address")
    tree.heading("Remote Address", text="Remote Address")
    tree.heading("Status", text="Status")
    
    # 插入数据并显示序号
    for index, conn in enumerate(list_tcp_connections(), start=1):
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
        print("index:", index)
        tree.insert("", "end", text=str(index),values=(laddr, raddr, conn.status))
        
    tree.pack(expand=True, fill="both")
    root.mainloop()
    
if __name__ == "__main__":
    create_gui()
        