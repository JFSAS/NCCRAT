import tkinter as tk
from tkinter import messagebox, ttk
from queue import Queue
import socket
import time
import re

class Process:
    def __init__(self, master, client: socket.socket, send_buf: Queue, recv_buf: Queue):
        self.master = master
        self.client = client
        self.ip = client.getpeername()[0]
        self.send_buf = send_buf
        self.recv_buf = recv_buf

        self.process_window = tk.Toplevel(master)
        self.process_window.title(f"Process Management - {self.ip}")
        self.process_window.geometry("1000x800")

        self.scrollbar = tk.Scrollbar(self.process_window, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.process_list = ttk.Treeview(self.process_window, columns=("PID", "Name", "CPU", "Memory", "PWD"), show="headings", yscrollcommand=self.scrollbar.set)
        self.process_list.heading("PID", text="PID")
        self.process_list.heading("Name", text="名称")
        self.process_list.heading("CPU", text="CPU (%)")
        self.process_list.heading("Memory", text="内存 (MB)")
        self.process_list.heading("PWD", text="工作目录")
        self.process_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.scrollbar.config(command=self.process_list.yview)

        self.refresh_button = tk.Button(self.process_window, text="刷新", command=self.refresh_processes)
        self.refresh_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.kill_button = tk.Button(self.process_window, text="结束进程", command=self.kill_selected_process)
        self.kill_button.pack(side=tk.RIGHT, padx=10, pady=5)

        self.refresh_processes()


    def refresh_processes(self): 
        '''刷新进程列表'''
        self.send_buf.put("2list".encode())  # 请求进程列表
        time.sleep(5)
        self.process_list.delete(*self.process_list.get_children())  # 清空现有数据

        if self.recv_buf.empty() is False and self.recv_buf.queue[0][:1] == b'2':
            count = self.recv_buf.qsize()
            self.recv_buf.queue[0] = self.recv_buf.queue[0][1:]
            response = ''.join(self.recv_buf.get().decode() for i in range(count))
            process_data = response.split("\n")
            for process in process_data:
                match = re.match(r'(\d+): (.+?) \(CPU: ([0-9.]+)%, MEM: ([0-9.]+) MB, pwd: (.*)\)', process)
                if match:
                    pid, name, cpu, memory, pwd = match.groups()
                    self.process_list.insert("", tk.END, values=(pid, name, cpu, memory, pwd))


    def kill_selected_process(self):
        '''终止指定进程'''
        selected_item = self.process_list.selection()
        if not selected_item:
            messagebox.showerror("错误", "请先选择一个进程")
            return
        
        pid = self.process_list.item(selected_item[0], "values")[0]
        self.send_buf.put(f"2kill {pid}".encode())  # 向客户端发送结束进程命令
        self.refresh_processes()  # 刷新进程列表
