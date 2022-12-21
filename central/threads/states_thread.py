import threading
import json

from server_thread import ServerThread
from time import sleep

class StatesThread(threading.Thread):
    states: dict
    sockets: dict

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.server = ServerThread(host, port)
        self.server.daemon = True
        self.states = {}
        self.sockets = {}

    def send_req(self, destiny, message) -> None:
        self.sockets[destiny].send(bytes(message, encoding='utf-8'))

    def run(self) -> None:
        self.server.start()
        while True:
            self.sockets = self.server.sockets
            for board in self.sockets:
                self.send_req(board, 'update')
                self.states[board] = json.loads(self.sockets[board].recv(4096).decode('utf-8'))
            sleep(2)