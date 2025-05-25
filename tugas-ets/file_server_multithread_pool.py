from socket import *
import socket
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

from file_protocol import FileProtocol
fp = FileProtocol()

MAX_WORKERS = 5

def handle_client(connection, address):
    """Handle client connection in a worker thread from the pool"""
    logging.warning(f"handling connection from {address}")
    try:
        d = ""
        while True:
            data = connection.recv(52428800)
            if data:
                d += data.decode()
                while "\r\n\r\n" in d:
                    cmd, d = d.split("\r\n\r\n", 1)
                    hasil = fp.proses_string(cmd)
                    hasil = hasil + "\r\n\r\n"
                    connection.sendall(hasil.encode())
            else:
                break
    except Exception as e:
        logging.warning(f"Error: {str(e)}")
    finally:
        logging.warning(f"closing connection from {address}")
        connection.close()

class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=8889):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        threading.Thread.__init__(self)
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        
    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        
        try:
            while True:
                connection, client_address = self.my_socket.accept()
                logging.warning(f"connection from {client_address}")
                
                # Submit the client handling task to the thread pool
                self.executor.submit(handle_client, connection, client_address)
        except KeyboardInterrupt:
            logging.warning("Server shutting down")
        finally:
            self.executor.shutdown(wait=True)
            self.my_socket.close()

def main():
    svr = Server(ipaddress='0.0.0.0', port=8000)
    svr.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()