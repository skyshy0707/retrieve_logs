# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 22:59:05 2021

@author: SKY_SHY
"""

from unittest import TestCase
from unittest.mock import Mock
import unittest

from sort_items import sorted_logs

import re
import json
import os

logs = sorted_logs




#5. API для тестирования данных в логах:
    
    
errors_count = 0
    
class TestLogs(TestCase):
    

    logs = []
    
    def setUp(self,):
        self.logs = logs
        
    
    def get_mock_obj(self, log):
        mock = Mock()
        mock.log = log
        return mock
   
    def exixting_allFields(self, mock):
        expected_fields = {'user_id', 
                           'first_name', 
                           'second_name',
                           'created_at', 
                           'message'
                           }
        self.assertSetEqual(expected_fields, set(mock.log.keys()),)



        
        
    def int_format(self, mock):
        user_id = mock.log['user_id']
        self.assertIsInstance(int(user_id), int)
        
        
    def date_ISO8601(self, mock):
        created_at = mock.log['created_at']
        self.assertTrue(re.fullmatch('\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d',
                                     created_at
                                     )
                        )
     
    
      
    def test_existing_allFields(self,):
        global errors_count
        for log in self.logs:
            mock = self.get_mock_obj(log)
            try:
                self.exixting_allFields(mock)
            except:
                errors_count +=1
    
    def test_perform_to_int_formats(self,):
        global errors_count
        for log in self.logs:
            mock = self.get_mock_obj(log)
            try:
                self.int_format(mock)
            except:
                errors_count +=1
            
    def test_date_ISO8601(self,):
        global errors_count
        for log in self.logs:
            mock = self.get_mock_obj(log)
            try:
                self.date_ISO8601(mock)
            except:
                errors_count +=1
    
    
    
    @classmethod
    def deleting_JSON(self):
        if os.path.isfile("logs.json"): 
            os.remove("logs.json")
    
    @classmethod
    def delete_JSON(self,):
        try:
            self.deleting_JSON()
        except PermissionError:
            print("Файл занят другим процессом")
    
    
    @classmethod
    def export_to_JSON(self,):
        with open("logs.json", "w") as w_file:
            json.dump(logs, w_file)
            
    @classmethod
    def tearDownClass(self,):
        global errors_count
        self.delete_JSON()
        if errors_count == 0:
            self.export_to_JSON()
    
            
 
if __name__ == "__main__":
    unittest.main()
 
