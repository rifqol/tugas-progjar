from socket import *
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# Konfigurasi logging untuk menyimpan output ke file
logging.basicConfig(filename='lb_process.log', level=logging.WARNING,
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class BackendList:
    def __init__(self):
        self.servers = [
            ('127.0.0.1', 9000),
            # ('127.0.0.1', 9001),
            # ('127.0.0.1', 9002)
        ]
        self.current = 0

    def getserver(self):
        s = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return s

def forward_data(source, destination):
    try:
        while True:
            data = source.recv(4096)
            if data:
                destination.sendall(data)
            else:
                break
    except Exception as e:
        logging.warning(f"Error in forwarding data: {str(e)}")
    finally:
        source.close()
        destination.close()

def handle_client(client_socket, backend_address):
    backend_socket = socket(AF_INET, SOCK_STREAM)
    try:
        backend_socket.connect(backend_address)
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(forward_data, client_socket, backend_socket)
            executor.submit(forward_data, backend_socket, client_socket)
    except Exception as e:
        logging.warning(f"Error in handling client: {str(e)}")
        client_socket.close()
        backend_socket.close()

def Server():
    my_socket = socket(AF_INET, SOCK_STREAM)
    my_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    backend = BackendList()

    my_socket.bind(('0.0.0.0', 44444))
    my_socket.listen(5)
    logging.warning("Load balancer running on port 44444")

    with ThreadPoolExecutor(max_workers=400) as executor:
        while True:
            connection, client_address = my_socket.accept()
            backend_address = backend.getserver()
            logging.warning(f"{client_address} connecting to {backend_address}")
            executor.submit(handle_client, connection, backend_address)

def main():
    Server()

if __name__ == "__main__":
    main()
