import tkinter as tk
from tkinter import ttk, messagebox
from queue import Queue
import socket
import os
import time

class File:
    def __init__(self, master, client: socket.socket, send_buf: Queue, recv_buf: Queue):
        self.master = master
        self.client = client
        self.ip = client.getpeername()[0]
        self.send_buf = send_buf
        self.recv_buf = recv_buf
        self.current_path = "此电脑"
        self.init_gui()
        self.get_drives()


    def init_gui(self):
        """初始化图形化界面"""
        self.window = tk.Toplevel(self.master)
        self.window.title(f"File Management - {self.ip}")
        self.window.geometry("600x400")

        # 路径框
        self.path_label = tk.Label(self.window, text="路径：")
        self.path_label.pack(anchor="w", padx=10, pady=5)
        self.path_entry = tk.Entry(self.window, state='readonly')
        self.path_entry.pack(fill="x", padx=10)
        self.path_entry.bind("<Button-1>", self.on_path_click)

        # 文件列表
        self.scrollbar = tk.Scrollbar(self.window, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.tree = ttk.Treeview(self.window, columns=("name", "date", "type", "size"), show="headings", yscrollcommand=self.scrollbar.set) 
        self.tree.heading("name", text="名称")
        self.tree.heading("date", text="修改日期")
        self.tree.heading("type", text="类型")
        self.tree.heading("size", text="大小")

        self.tree.column("name", width=200)
        self.tree.column("date", width=150)
        self.tree.column("type", width=80)
        self.tree.column("size", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.scrollbar.config(command=self.tree.yview)

    def get_drives(self):
        """获取客户端所有盘符"""
        self.send_buf.put("4start".encode())  # 发送请求获取盘符
        self.update_file_list("此电脑", [])  # 初始路径显示为空
        self.wait_for_response()

    def update_path(self, path):
        """更新路径框"""
        self.current_path = path
        self.path_entry.config(state='normal')
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)
        self.path_entry.config(state='readonly') 
    
    def on_path_click(self, event):
        """处理路径框点击事件"""
        path = self.path_entry.get()
        parts = path.split("\\")
        menu = tk.Menu(self.window, tearoff=0)
        for i in range(len(parts)):
            sub_path = "\\".join(parts[:i+1])
            menu.add_command(label=sub_path, command=lambda p=sub_path: self.navigate_to_path(p))
        menu.post(event.x_root, event.y_root)
    
    def navigate_to_path(self, path):
        """导航到指定路径"""
        self.send_buf.put(f"4search{path}".encode())
        self.update_path(path)
        self.wait_for_response()


    def on_item_double_click(self, event):
        """双击文件项触发的事件"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item_data = self.tree.item(selected_item)["values"]

        if self.current_path == "此电脑":
            # 双击盘符
            new_path = item_data[0] + "\\"
            self.send_buf.put(f"4search{new_path}".encode())
            self.update_path(new_path)
            self.wait_for_response()
        elif item_data[2] == "folder":
            # 双击文件夹
            new_path = os.path.abspath(os.path.join(self.current_path, item_data[0]))
            self.send_buf.put(f"4search{new_path}".encode())
            self.update_path(new_path)
            self.wait_for_response()
        elif item_data[2] == "file":
            # 双击文件，触发文件下载
            file_path = os.path.join(self.current_path, item_data[0])
            self.send_buf.put(f"4download{file_path}".encode())
            file_name = os.path.basename(file_path)
            messagebox.showinfo("文件下载", f"正在下载文件：{item_data[0]}......")
            time.sleep(5)
            self.receive_file(file_name)


    def wait_for_response(self):
        """等待服务器的消息并更新界面"""
        while True:
            if self.recv_buf.empty() is False and self.recv_buf.queue[0][:1] == b'4':
                count  = self.recv_buf.qsize()
                self.recv_buf.queue[0] = self.recv_buf.queue[0][1:]
                response = ''.join(self.recv_buf.get().decode() for i in range(count))
                file_data = response.split("\n")
                file_list = []
                for line in file_data:
                    if line:
                        parts = line.split("|")
                        file_list.append(parts)

                # 按文件夹和文件分类，并按名称排序
                folders = sorted([item for item in file_list if len(item) > 2 and item[2] == "folder"], key=lambda x: x[0].lower())
                files = sorted([item for item in file_list if len(item) > 2 and item[2] != "folder"], key=lambda x: x[0].lower())
                sorted_file_list = folders + files
                if self.current_path != "此电脑":
                    # 添加返回上级目录的选项
                    sorted_file_list.insert(0, ["..", "", "folder", ""])

                self.update_file_list(self.current_path, sorted_file_list)
                break

    def update_file_list(self, path, file_list):
        """更新文件列表界面"""
        self.current_path = path
        self.path_entry.config(state='normal')
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)
        self.path_entry.config(state='readonly')
        # 清空当前列表
        for row in self.tree.get_children():
            self.tree.delete(row)
        # 添加新列表
        for item in file_list:
            self.tree.insert("", "end", values=item)

    def receive_file(self, file_name):
        """接收文件事项"""
        while True:
            if self.recv_buf.empty() is False:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # 在当前目录下创建文件
                file_path = os.path.join(current_dir, file_name)
                with open(file_path, "wb") as f:
                    while True:
                        data = self.recv_buf.get()
                        if data == b"4Transfer_complete":
                            break
                        f.write(data)
                messagebox.showinfo("文件下载", f"文件下载完成：{os.path.basename(file_path)}")
                break