# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 21:32:42 2021

@author: SKY_SHY
"""




import json
import requests


import configparser
config = configparser.ConfigParser()
config.read("config.ini") 





#1. API для получения логов по дате их добавления:
class Logs():
    
    

    def get_raw_logs_by_date(self, date_logs):
        return requests.get('http://www.dsdev.tech/logs/{}'.format(date_logs))
    
    def get_jsondata(self, raw_data):
        return json.loads(raw_data.text)
    
    def get_logs(self, json_data):
        return json_data['logs']
    
    
    
    #8. Точка входа: Публичный метод с параметром date_logs --- дата добавления лога:
    def logs(self, date_logs):
        raw_logs = self.get_raw_logs_by_date(date_logs)
        return self.get_logs(self.get_jsondata(raw_logs))





#2. API для сортировки логов по дате их добавления по возрастанию:
class Sort():
    
    def __init__(self, sequence):
        self.sequence = sequence[1:]
        self.i = 0
        self.stack = [sequence[0]]
        self.rest_part = []
        self.key = 'created_at'
        
    
    def set_key(self, key):
        self.key = key
        
        
    
    def h(self, s):
        if s[self.key] >= self.stack[self.i][self.key]:
            return -1
        return 1
        
        
     
    
    def step_sort(self,):
        for s in self.sequence:
            if self.h(s) != 1:
                self.stack.append(s)
                self.i += 1
            else:
                while self.h(s) == 1 and self.i >= 0:
                    self.rest_part.insert(0, self.stack[self.i])
                    self.i -= 1
                else:
                    self.stack =  self.stack[:self.i+1]
                    self.stack.append(s)
                    self.i += 1
                    
    def sort(self, key='created_at'):
        self.set_key(key)
        while True:
            self.step_sort()
            if not self.rest_part:
                break
            self.sequence = tuple(self.rest_part)
            self.rest_part = []
                

#1. Получение логов:
date_logs = config["logs"]["DATE_LOGS"]
logs = Logs()
logs = logs.logs(date_logs)


#2. Сортировка логов:
sorting = Sort(logs)
sorting.sort()
sorted_logs = sorting.stack

