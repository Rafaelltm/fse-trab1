import threading
import json
import sys
import os

from datetime import datetime
from threads.states_thread import *

ROOMS ="""
Salas Conectadas:
"""
CONSOLE ="""
Painel de Controle:
Aperte Enter para atualizar a lista de salas
Digite o nome da sala para checar seus estados

    [1] ligar alarme
    [2] Ligar as lâmpadas
    [3] Desligar tudo do prédio
    [0] Sair
"""
CONSOLE_ROOM ="""
Painel de Controle:
Aperte Enter para atualizar estados

    [1] Ligar lâmpadas
    [2] Ligar ar-condicionado
    [3] Ligar projetor
    [4] Desligar estados
    [0] Voltar

"""
LIGHTS ="""
Acionar Lâmpadas:
Aperte Enter para atualizar estados

    [1] Lâmpada 1
    [2] Lâmpada 2
    [3] Ligar todas
    [4] Desligar todas
    [0] Retornar

"""

class ConsoleThread(threading.Thread):
    sockets: dict
    alarm: bool
    global_count: int

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.st = StatesThread(host, port)
        self.st.daemon = True
        self.alarm = False
        self.sockets = {}
        self.global_count = 0

    def send_req(self, destiny, message) -> None:
        self.sockets[destiny].send(bytes(message, encoding='utf-8'))

    def wait_resp(self, board) -> str:
        response = self.sockets[board].recv(4096).decode('utf-8')
        print(response)
        return response

    def print_dict(self, dic:dict) -> None:
        print()
        for item in dic:
            if item == 'Placa':
                print(f'{item}: \t\t{dic[item]}')
            else:
                print(f'{item}: \t{dic[item]}')

    def print_connected_boards(self, sockets) -> None:
        print(ROOMS)
        for board in sockets:
            print(board)
        print(CONSOLE)

    def clear(self) -> None:
        os.system('clear')

    def update_states(self, board) -> None:
        self.send_req(board, 'update')
        self.st.states[board] = json.loads(self.sockets[board].recv(4096).decode('utf-8'))
    
    def check_sensors(self, board) -> bool:
        dic = self.st.states[board]

        if dic['Sensor de Presença'] == 'Ligado' or\
        dic['Sensor de Fumaça'] == 'Ligado' or\
        dic['Sensor da Janela'] == 'Ligado' or\
        dic['Sensor da Porta'] == 'Ligado':
            return True
        else: return False

    def lights_console(self, board) -> str:
        self.clear()
        self.print_dict(self.st.states[board])
        choice = input(LIGHTS)

        if choice == '0': return ''
        elif choice == '1':
            msg = 'L_01'
            log = f'{board},{msg} acionado'
            self.write_log(log)
            return msg
        elif choice == '2':
            msg = 'L_02'
            log = f'{board},{msg} acionado'
            self.write_log(log)
            return msg
        elif choice == '3':
            msg = 'L_ON'
            log = f'{board},lampadas ligadas'
            self.write_log(log)
            return msg
        elif choice == '4':
            msg = 'L_OFF'
            log = f'{board},lampadas desligadas'
            self.write_log(log)
            return msg

    def room_console(self, board) -> None:
        while True:
            self.print_dict(self.st.states[board])
            choice = input(CONSOLE_ROOM)

            if(choice == '0'):
                self.clear()
                return
            elif choice == '1': msg = self.lights_console(board)
            elif choice == '2':
                msg = 'AC'
                log = f'{board},{msg} acionado'
                self.write_log(log)
            elif choice == '3': 
                msg = 'PR'
                log = f'{board},{msg} acionado'
                self.write_log(log)
            elif choice == '4':
                msg = 'all_off'
                log = f'{board},tudo desligado'
                self.write_log(log)
            if choice == '': self.clear()
            else:
                self.send_req(board, msg)
                self.clear()
                self.wait_resp(board)
                self.update_states(board)
    
    def print_numb_ppl(self, sockets) -> None:
        self.global_count = 0
        for board in sockets:
            self.global_count += int(self.st.states[board]['Pessoas'])
        print(f'Qtd de pessoas no prédio: {self.global_count}\n')

    def write_log(self, event:str) -> None:
        with open('log.csv', 'a', encoding='UTF8') as f:
            f.write(f'{event},{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')

    def run(self):
        self.st.start()
        log = f'central,servidor iniciado'
        self.write_log(log)
        self.clear()
        while True:
            self.sockets = self.st.sockets
            if self.sockets:
                for board in self.sockets:
                    self.update_states(board)

                self.print_connected_boards(self.sockets)
                if self.alarm: print('Estado do alarme: Ligado')
                else:print('Estado do alarme: Desligado')
                self.print_numb_ppl(self.sockets)

                choice = input()

                if choice == '0': # exit
                    for board in self.sockets:
                        self.send_req(board, 'SD')
                    log = f'central,servidor terminado'
                    self.write_log(log)
                    sys.exit()
                elif choice == '1': # activate alarm
                    for board in self.sockets:
                        if self.check_sensors(board):
                            self.clear()
                            print('há sensores ativos, alarme não pode ser acionado')
                        else:
                            self.send_req(board, 'switch_alarm')
                            self.clear()
                            self.wait_resp(board)
                    if self.st.states:
                        if self.alarm:
                            self.alarm = False
                            log = f'central,sistema de alarme desligado'
                            self.write_log(log)
                        else: 
                            self.alarm = True
                            log = f'central,sistema de alarme ligado'
                            self.write_log(log)
                elif choice == '2': # all lights on
                    for board in self.sockets:
                        self.send_req(board, 'L_ON')
                        self.clear()
                        self.wait_resp(board)
                        log = f'{board},luzes acionadas'
                        self.write_log(log)
                elif choice == '3': # all charges off
                    for board in self.sockets:
                        self.send_req(board, 'all_off')
                        self.clear()
                        self.wait_resp(board)
                        log = f'{board},cargas desligadas'
                        self.write_log(log)
                else: 
                    self.clear()
                    for board in self.sockets:
                        if choice == board:
                            self.room_console(board)

