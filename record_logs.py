# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 23:01:22 2021

@author: SKY_SHY
"""


import configparser
config = configparser.ConfigParser()
config.read("config.ini") 

USERNAME = config["pgs_db"]["USERNAME"]
PASSWORD = config["pgs_db"]["PASSWORD"]
DB_NAME = config["pgs_db"]["NAME"]  
PORT = config["pgs_db"]["PORT"]
USERS_TAB = config["tab_names"]["USERS"]
LOGS_TAB = config["tab_names"]["LOGS"]

#3. Схема БД для записи логов
class CreateNewDB():
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.engine = None
        self.conn = None
        
    
    def create_connection(self, db_name='postgres'):
        return create_engine('postgresql://{}:{}@localhost:{}/{}'.\
                             format(
                               self.username, 
                               self.password,
                               PORT,
                               DB_NAME,
                               )
                            )
            
    def connect(self,):
        try:
            conn = self.engine.connect()
            conn.execute("COMMIT")
        except exc.OperationalError:
            pass
        else:
            return conn
        
    
    def set_default_connection(self,):
        self.engine = self.create_connection()
        self.conn = self.connect()
    
    def set_new_connection(self, db_name):
        self.engine = self.create_connection(db_name)
        self.conn = self.connect()


    def create_new_db(self, db_name):
        self.set_default_connection()
        try:
            self.conn.execute("CREATE DATABASE %s" % db_name)
            self.conn.execute("COMMIT")
        except exc.DatabaseError:
            pass
        except AttributeError:
            pass
            

from sqlalchemy import create_engine, Table, Column, Integer, String,\
    MetaData, Text, DateTime, Sequence, ForeignKey, exc
    
    
from sqlalchemy.orm import mapper, sessionmaker    
db = CreateNewDB(USERNAME, PASSWORD)

db.create_new_db(DB_NAME)
db.set_new_connection(DB_NAME)

engine = db.engine
conn = db.conn
Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()



class Log(object):
    def __init__(self, created_at, message, user_id):
        self.created_at = created_at
        self.message = message
        self.user_id = user_id

    
    def __repr__(self):
        return "<Log('%s', '%s', '%s')>" % (self.created_at, 
                                            self.message, 
                                            self.user_id,
                                            )


class User(object):
    def __init__(self, id_, first_name, second_name):
        self.id = id_
        self.first_name = first_name
        self.second_name = second_name

    
    def __repr__(self):
        return "<User('%s', '%s', '%s')>" % (self.id, 
                                             self.first_name, 
                                             self.second_name, 
                                             )

logs_tab = Table(LOGS_TAB, metadata, 
                 Column('id', Integer, Sequence('logs_id_seq'),
                        primary_key=True,
                        ),
                 Column('created_at', DateTime, nullable=False),
                 Column('message', Text, nullable=False),
                 Column('user_id', Integer, ForeignKey('users.id'), 
                        nullable=False
                        )
                 )

users_tab = Table(USERS_TAB, metadata,
                  Column('id', Integer, primary_key=True),
                  Column('first_name', String, nullable=False),
                  Column('second_name', String, nullable=False),
                  )


try:
    metadata.create_all(engine)
except exc.OperationalError:
    pass

mapper(Log, logs_tab)
mapper(User, users_tab)


#7. Нстройка логирования метода RecordLogs.record:
import logging
import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger('record_logs')



#4. API для записи логов в БД:
class CreateLog():
    
    def create(self, log):
        created_at, message, user_id =\
            log['created_at'], log['message'], log['user_id']
        return Log(created_at, message, user_id)
    
class CreateUser():
    
    def create(self, log):
        id_, first_name, second_name =\
            log['user_id'], log['first_name'], log['second_name']
        return User(id_, first_name, second_name)

class RecordLogs():
    
    
    def __init__(self,):
        self.types = []
        
    def set_types(self, list_types):
        self.types = list_types
    
    
    def create(self, type_, log):
        cls_ = globals()['Create'.join(('', type_,))]()
        return cls_.create(log)
    
    
    
    #7.реализация логирования:
    def add(self, obj):
        session.add(obj)
        try:
            session.commit()
        except exc.IntegrityError:
            logger.warning("Значение одного из полей объекта %s" % obj.__repr__() + 
                           " нарушает ограничение в уникальности значения " +
                           "этого поля"
                           )
            session.rollback()
        else:
            logger.info("Данные объекта {}".format(obj.__repr__()) + 
                        " были успешно записаны в базу данных {}".\
                            format(DB_NAME)
                            )

        
        
    #7.реализация логирования:
    def get_obj(self, type_, log):
        try:
            obj = self.create(type_, log)
        except KeyError:
            logger.error("В логе в наличии не все поля" +
                         "Фактически, в наличии только эти поля: %s" 
                         % set(log.keys()),
                         )
        else:
            logger.info("Инициализация объекта данных {}".format(type_))
            return obj

    
    #7.реализация логирования в связанных методах --- get_obj, add:
    def record(self, logs):
        for log in logs:
            for type_ in self.types:
                obj = self.get_obj(type_, log)
                self.add(obj)
                
        session.close()
        
    
    def recording(self, logs):
        try:
            self.record(logs)
        except exc.OperationalError:
            print("Неверная комбинация параметров подключения к postgres: "\
                  "username={}, password={}, port={}".format(
                      USERNAME, 
                      PASSWORD, 
                      PORT
                      )
                  )
            session.close()
        

import json


#4. Запись логов в БД:
    

try:
    file_json = open("logs.json", "r")
except FileNotFoundError:
    print("Объекты логов не прошли тестирование данных")
else:
    logs = json.load(file_json)
    record = RecordLogs()  
    record.set_types(['User', 'Log'])
    record.recording(logs)
    
    
