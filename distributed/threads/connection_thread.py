import threading
import socket
import sys

from room import Room
from threads.room_thread import *

class ConnectionThread(threading.Thread):
    def __init__(self, room:Room) -> None:
        super().__init__()
        self.room_thread = RoomThread(room)
        self.room_thread.daemon = True
        self.host = self.room_thread.room.central_address
        self.port = self.room_thread.room.central_port

    def create_con(self):
        self.central_soc = socket.create_connection((self.host, self.port))
        self.send_message(self.room_thread.room.name)
        print(f'conectado a {self.host}')

    def send_message(self, message):
        self.central_soc.send(bytes(message, encoding='utf-8'))

    def run(self):
        self.create_con()
        self.room_thread.start()
        print('\naguardando...')
        while True:
            request = self.central_soc.recv(1024).decode('utf-8')

            if request == 'SD':
                print('servidor desligado')
                sys.exit()

            elif request == 'update':
                message = self.room_thread.get_json_dump()
                self.send_message(message)
                print('dados enviados')
            
            elif request == 'L_ON':
                self.room_thread.room.set_high('L_01')
                self.room_thread.room.set_high('L_02')
                self.send_message('luzes ligadas com sucesso')
                print('todas as luzes estão ligadas')

            elif request == 'L_OFF':
                self.room_thread.room.set_low('L_01')
                self.room_thread.room.set_low('L_02')
                self.send_message('luzes desligadas com sucesso')
                print('todas as luzes foram desligadas')

            elif request == 'AC' or request == 'PR' or request == 'L_01' or request == 'L_02':
                self.room_thread.room.switch(request)
                self.send_message('funcionalidade requisitada trocada com sucesso')
                print(f'{request} trocado')

            elif request == 'all_off':
                self.room_thread.room.all_off()
                print('todos os retornos estão desligados')

            elif request == 'switch_alarm':
                if self.room_thread.room.alarm_on: 
                    self.room_thread.room.alarm_on = False
                    self.send_message('alarme desligado com sucesso')
                else:
                    self.room_thread.room.alarm_on = True
                    self.send_message('alarme ligado com sucesso')
                    print('alarme acionado')

