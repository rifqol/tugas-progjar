import asyncio
import logging

class BackendList:
    def __init__(self):
        self.servers = [
            ('127.0.0.1', 9000),
            ('127.0.0.1', 9001),
            ('127.0.0.1', 9002)
        ]
        self.current = 0

    def getserver(self):
        s = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return s

class ProxyHandler:
    def __init__(self, client_reader, client_writer, backend_address):
        self.client_reader = client_reader
        self.client_writer = client_writer
        self.backend_address = backend_address
        self.backend_reader = None
        self.backend_writer = None

    async def handle_client(self):
        try:
            self.backend_reader, self.backend_writer = await asyncio.open_connection(
                *self.backend_address
            )

            client_to_backend = asyncio.create_task(self.transfer_data(self.client_reader, self.backend_writer))
            backend_to_client = asyncio.create_task(self.transfer_data(self.backend_reader, self.client_writer))

            await asyncio.gather(client_to_backend, backend_to_client)
        except Exception as e:
            logging.error(f'Error in handling client: {e}')
        finally:
            self.client_writer.close()
            await self.client_writer.wait_closed()
            if self.backend_writer:
                self.backend_writer.close()
                await self.backend_writer.wait_closed()

    async def transfer_data(self, reader, writer):
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                writer.write(data)
                await writer.drain()
        except Exception as e:
            logging.error(f'Error in transferring data: {e}')
        finally:
            writer.close()
            await writer.wait_closed()

class Server:
    def __init__(self, portnumber):
        self.portnumber = portnumber
        self.backend_list = BackendList()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, '0.0.0.0', self.portnumber)
        logging.warning(f'Load balancer running on port {self.portnumber}')

        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        backend_address = self.backend_list.getserver()
        logging.warning(f'Connection from {writer.get_extra_info("peername")} forwarded to {backend_address}')
        handler = ProxyHandler(reader, writer, backend_address)
        await handler.handle_client()

def main():
    portnumber = 44444
    
    # Konfigurasi logging untuk menyimpan ke file
    logging.basicConfig(level=logging.WARNING, filename='lb_async.log', filemode='a',
                        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    server = Server(portnumber)
    asyncio.run(server.start())

if __name__ == "__main__":
    main()
