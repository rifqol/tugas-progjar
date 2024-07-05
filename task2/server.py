import socket
import threading
import logging
import datetime

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        try:
            while True:
                data = self.connection.recv(32)
                if not data:  # If no data is received, client disconnected
                    logging.warning(f"Client {self.address} disconnected.")
                    break
                
                # Decode received data
                received_message = data.decode().rstrip()

                # Check if the client wants to quit
                if received_message == "QUIT":
                    logging.warning(f"Client {self.address} requested to quit.")
                    break
                
                # Check if the client is requesting time
                elif received_message == "TIME":
                    now = datetime.datetime.now().strftime("%H:%M:%S")
                    response = f"JAM {now}\r\n"
                    self.connection.sendall(response.encode('utf-8'))
                
                # Handle unknown commands or invalid requests
                else:
                    logging.warning(f"Received unknown command from {self.address}: {received_message}")
        
        except Exception as e:
            logging.error(f"Error processing client {self.address}: {e}")
        
        finally:
            self.connection.close()
            logging.warning(f"Connection with client {self.address} closed.")

class Server(threading.Thread):
    def __init__(self, port):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.my_socket.bind(('0.0.0.0', self.port))
            self.my_socket.listen(5)
            logging.warning(f"Server listening on port {self.port}")
            while True:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"Connection from {client_address}")
                
                # Start a new thread to handle the client
                clt = ProcessTheClient(connection, client_address)
                clt.start()
                self.the_clients.append(clt)
        
        except Exception as e:
            logging.error(f"Server error: {e}")
        
        finally:
            # Close the server socket if running into any issues
            self.my_socket.close()

def main():
    port = 45000
    svr = Server(port)
    svr.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()

