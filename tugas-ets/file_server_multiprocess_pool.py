from concurrent.futures import ProcessPoolExecutor
import socket
import logging
from file_protocol import FileProtocol

MAX_WORKERS = 4

def process_command(data: str) -> str:
    """Function to be executed in the process pool"""
    fp = FileProtocol()  # must be created inside the worker
    result = fp.proses_string(data)
    return result + "\r\n\r\n"

def handle_client(connection, address, executor):
    """Handle client connection in the main thread; delegate CPU-bound task to process pool"""
    logging.warning(f"Handling connection from {address}")
    try:
        d = ""
        while True:
            data = connection.recv(52428800)  # 50MB max read size
            if not data:
                break
            d += data.decode()

            while "\r\n\r\n" in d:
                cmd, d = d.split("\r\n\r\n", 1)
                future = executor.submit(process_command, cmd)
                result = future.result()
                connection.sendall(result.encode())
    except Exception as e:
        logging.warning(f"Error handling {address}: {e}")
    finally:
        logging.warning(f"Closing connection from {address}")
        connection.close()

class Server:
    def __init__(self, ip='0.0.0.0', port=8000):
        self.ipinfo = (ip, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        logging.warning(f"Server running on {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)

        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            try:
                while True:
                    connection, address = self.my_socket.accept()
                    logging.warning(f"Accepted connection from {address}")
                    handle_client(connection, address, executor)
            except KeyboardInterrupt:
                logging.warning("Server shutting down")
            finally:
                self.my_socket.close()

def main():
    svr = Server(ip='0.0.0.0', port=8000)
    svr.run()

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    main()