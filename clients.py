import logging
import random
import socket
import time
from socketserver import TCPServer, BaseRequestHandler
from threading import Thread

base_address = "127.0.0.3"

class Handler(BaseRequestHandler):
    def handle(self):
        self.request.settimeout(4)
        while True:
            try:
                self.data = self.request.recv(count_read_bytes).strip()
            except TimeoutError:
                logging.info("Server timeout, RST attack successful")
                break
            self.request.sendto(
                    transform_string(self.client_address[0], self.client_address[1]),
                    self.client_address)
            logging.info(f"Server finished iteration")

count_read_bytes = 4096
def transform_string(addr, port):
    return f"{addr}+{port}".encode("utf-8")

def a_start(sock: socket.socket, addr: (int, int)):
    while True:
        try:
            sock.sendall(b'important message')
        except ConnectionResetError:
            logging.info("Successful RST attack!!!!!")
            break
        logging.info(f"from {addr} sent")
        data = sock.recv(count_read_bytes)
        if not data:
            break
        time.sleep(1)
    sock.close()

def b_start(server: TCPServer):
    server.serve_forever()

used_ports = set()

def create_port():
    while True:
        port = random.randrange(800, 8100)
        if port not in used_ports:
            break
    used_ports.add(port)
    return port

def address_create():
    return base_address, create_port()

def clients_attack(a_address, b_address):
    logging.info(f"{a_address} aaa")
    logging.info(f"{b_address} bbb")
    server = TCPServer(b_address, Handler, True)
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    a_socket.bind(a_address)
    a_socket.connect(b_address)
    a = Thread(target=a_start, args=[a_socket, a_address], daemon=True)
    b = Thread(target=b_start, args=[server], daemon=True)
    a.start()
    b.start()
    a.join(10)
    b.join(10)

if __name__ == '__main__':
    clients_attack(address_create(), address_create())