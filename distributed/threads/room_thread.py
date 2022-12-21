import threading
import json

from time import sleep, time
from room import Room
import RPi.GPIO as GPIO

class RoomThread(threading.Thread):
    lights_timer : float
    recent_pres : bool

    def __init__(self, room: Room) -> None:
        super().__init__()
        self.room = room

    def turn_lights_on(self):
        self.room.set_high('L_01')
        self.room.set_high('L_02')
        self.lights_timer = time()
        self.recent_pres = True

    def timer_lights(self):
        if time() - self.lights_timer > 15.0:
            self.room.set_low('L_01')
            self.room.set_low('L_02')
            self.lights_timer = None
            self.recent_pres = False

    def get_states(self) -> dict:
        dic = {}

        for item in self.room.states:
            if item == 'L_01':
                dic['Lâmpada 01'] = self.room.states['L_01']
            elif item == 'L_02':
                dic['Lâmpada 02'] = self.room.states['L_02']
            elif item == 'PR':
                dic['Projetor'] = self.room.states['PR']
            elif item == 'AC':
                dic['Ar-Con'] = self.room.states['AC']
            elif item == 'AL_BZ':
                dic['Sirene'] = self.room.states['AL_BZ']
        return dic

    def check_sensors(self) -> bool:
        for sensor in self.room.sensors:
            if GPIO.input(self.room.inp[sensor]):
                return True
    
    def get_sensors(self) -> dict:
        dic = {}

        for sensor in self.room.sensors:
            if sensor == 'SP':
                name = 'Sensor de Presença'
            elif sensor == 'SF':
                name = 'Sensor de Fumaça'
            elif sensor == 'SJ':
                name = 'Sensor da Janela'
            elif sensor == 'SPr':
                name = 'Sensor da Porta'

            if GPIO.input(self.room.inp[sensor]):
                dic[name] = 'Ligado'
            else:
                dic[name] = 'Desligado'
        return dic

    def get_people_count(self) -> dict:
        dic = {'Pessoas': self.room.ppl_qty}
        return dic
    
    def get_temp_humd(self) -> dict:
        dic = {'Temperatura' : f'{self.room.temp} ºC', 'Umidade' : f'{self.room.humd}%',}
        return dic
    
    def get_json_dump(self) -> str:
        dic = {'Placa' : self.room.name}
        dic = dic | self.get_sensors() | self.get_temp_humd() | self.get_states() | self.get_people_count() 
        return json.dumps(dic)

    def run(self):
        self.recent_pres = False
        self.lights_timer = 0

        while True:
            self.room.count_ppl()
            self.room.check_temp()
            if self.check_sensors():
                if self.room.alarm_on:
                    self.room.set_high('AL_BZ')
                else:
                    if GPIO.input(self.room.inp['SP']):
                        self.turn_lights_on()

                    if GPIO.input(self.room.inp['SF']): 
                        self.room.set_high('AL_BZ')

            elif self.room.states['AL_BZ']:
                self.room.set_low('AL_BZ')
            
            if self.recent_pres:
                self.timer_lights()
            sleep(0.1)