import os
import socket
import selectors
import logging
from glob import glob
from datetime import datetime
import sys

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain',
            '.html': 'text/html',
        }

    def proses(self, data):
        requests = data.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n != '']
        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            if method == 'GET':
                object_address = j[1].strip()
                return self.http_get(object_address, all_headers)
            elif method == 'POST':
                object_address = j[1].strip()
                return self.http_post(object_address, all_headers)
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})
        
    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n".format(kode, message))
        resp.append("Date: {}\r\n".format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n".format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n".format(kk, headers[kk]))
        resp.append("\r\n")

        response_headers = ''.join(resp)
        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def http_get(self, object_address, headers):
        files = glob('./*')
        thedir = './'
        if object_address == '/':
            return self.response(200, 'OK', 'Ini Adalah web Server percobaan', {})

        if object_address == '/video':
            return self.response(302, 'Found', '', {'Location': 'https://youtu.be/katoxpnTf04'})

        if object_address == '/santai':
            return self.response(200, 'OK', 'santai saja', {})

        object_address = object_address[1:]
        if thedir + object_address not in files:
            return self.response(404, 'Not Found', '', {})
        with open(thedir + object_address, 'rb') as fp:
            isi = fp.read()

        fext = os.path.splitext(thedir + object_address)[1]
        content_type = self.types.get(fext, 'application/octet-stream')

        headers = {'Content-type': content_type}
        return self.response(200, 'OK', isi, headers)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 thread_server.py <port>")
        sys.exit(1)

    portnumber = int(sys.argv[1])
    httpserver = HttpServer()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', portnumber))
    server_socket.listen(100)

    logging.warning(f"HTTP Server running on port {portnumber}")

    sel = selectors.DefaultSelector()
    sel.register(server_socket, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    client_socket, addr = server_socket.accept()
                    logging.info(f'Accepted connection from {addr}')
                    client_socket.setblocking(False)
                    sel.register(client_socket, selectors.EVENT_READ, data=httpserver)
                else:
                    client_socket = key.fileobj
                    httpserver = key.data
                    data = client_socket.recv(1024)
                    if data:
                        response = httpserver.proses(data.decode())
                        client_socket.sendall(response)
                    sel.unregister(client_socket)
                    client_socket.close()
    except KeyboardInterrupt:
        logging.info("Server stopped")
    finally:
        sel.close()

if __name__ == "__main__":
    main()
