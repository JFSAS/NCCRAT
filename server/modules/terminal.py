import socket
from tkinter import * 
import tkinter as tk
from queue import Queue
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
class Terminal: 
    '''
    开启一个终端窗口
    '''
    def __init__(self, master, client: socket.socket, send_buf: Queue, recv_buf: Queue):
        self.master = master
        self.client = client
        self.ip = client.getpeername()[0]
        self.remote_shell = RemoteShell(client,send_buf, recv_buf)
        self.create_terminal()
    
    def create_terminal(self):
        '''
        开启gui终端
        '''
        self.popup = Toplevel(self.master)
        self.popup.title(f"Terminal - {self.ip}")
        self.popup.geometry("800x600")
        self.popup.resizable(False, False)
        
        # 关闭窗口时关闭shell
        self.popup.protocol("WM_DELETE_WINDOW", self.close_shell)
        
        self.text_area = Text(self.popup, bg="black", fg="white", insertbackground="white", wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 滚动条
        scroll_bar = Scrollbar(self.text_area)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text_area.yview)
        
        # 输入框
        self.entry = tk.Entry(self.popup, bg="black", fg="white", insertbackground="white")
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        self.entry.bind("<Return>", self.execute_command)
        
    def execute_command(self, event):
        # 获取用户输入的命令
        command = self.entry.get().strip()
        if not command:
            return

        # 清空输入框
        self.entry.delete(0, tk.END)

        # 显示输入命令
        self.text_area.insert(tk.END, command + "\n")

        # 发送命令并显示返回结果
        result = self.remote_shell.send_command(command)
        # 输入exit时关闭
        if result == 'exit':
            self.popup.destroy()
        self.text_area.insert(tk.END, result + "\n")
        self.text_area.insert(tk.END, f"{self.remote_shell.ip}> ")

        # 自动滚动到最新内容
        self.text_area.see(tk.END)
        
    def close_shell(self):
        
        exit_result = self.remote_shell.send_command("exit")
        self.popup.destroy()
        
class RemoteShell:
    def __init__(self, client: socket.socket, send_buf: Queue, recv_buf: Queue):
        self.client = client
        self.ip = client.getpeername()[0]
        self.send_buf = send_buf
        self.recv_buf = recv_buf
    def send_command(self, command):
        command = '1' + command
        logging.debug(f"shell send: {command}")
        self.send_buf.put(command.encode())
        if command == '1exit':
            return 'exit'
        
        while True:
            if self.recv_buf.empty() is False and self.recv_buf.queue[0][:1] == b'1':
                result = self.recv_buf.get()[1:].decode()
                logging.debug(f"shell recv: {result}")
                return result