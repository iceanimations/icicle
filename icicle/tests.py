'''
Created on Oct 2, 2018

@author: qurban.ali
'''
from django.test import TestCase
from icicle import utilities as utils
from datetime import datetime, timedelta

class UtilitiesTestCase(TestCase):
    
    def test_timer_creation(self):
        now = datetime.now().replace(microsecond=0) + timedelta(minutes=1)
        utils.createTimer(self.hello, now.time())
        self.assertEqual(len(utils.timers), 1)


    def hello(self):
        print('hello world')
        print (datetime.now().time())