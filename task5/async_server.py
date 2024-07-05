import asyncio
import logging
from process_server import HttpServer

httpserver = HttpServer()

class ClientHandler(asyncio.Protocol):
    def __init__(self):
        super().__init__()
        self.buffer = b""

    def connection_made(self, transport):
        self.transport = transport
        peername = transport.get_extra_info('peername')
        logging.info('Connection from {}'.format(peername))

    def data_received(self, data):
        self.buffer += data
        if self.buffer.endswith(b'\r\n\r\n'):
            response = httpserver.proses(self.buffer.decode())
            self.transport.write(response)
            self.transport.close()

async def main(portnumber):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(
        lambda: ClientHandler(),
        '127.0.0.1', portnumber
    )
    logging.warning("Running on port {}".format(portnumber))
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    import sys
    portnumber = 8000  # Use different ports for different backend servers
    try:
        portnumber = int(sys.argv[1])
    except:
        pass
    asyncio.run(main(portnumber))
