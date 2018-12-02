# -*- coding: utf-8 -*-

#  Copyright 2015 www.suishouguan.com
#
#  Licensed under the Private License (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://github.com/samuelbaizg/ssguan/blob/master/LICENSE
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import time
import unittest

from ssguan.ignitor.asyn import sender, config as asyn_config
from ssguan.ignitor.asyn.conduit import Processor
from ssguan.ignitor.asyn.error import MaxLengthError
from ssguan.ignitor.orm import  dbpool, config as orm_config, properti
from ssguan.ignitor.orm.model import Model
from ssguan.ignitor.utility import kind
from ssguan.ignitor.base.error import NoFoundError


class AsyncModel(Model):
       
    tckey = properti.StringProperty()
    data = properti.ObjectProperty()
   
    @classmethod
    def meta_domain(cls):
        return "TEST"
   
    @classmethod
    def get_by_tckey(cls, tckey):
        query = cls.all()
        query.filter('tckey =', tckey)
        return query.get()
    @classmethod
    def fetch_by_tckey(cls, tckey):
        query = cls.all()
        query.filter('tckey =', tckey)
        return query.fetch()
    @classmethod
    def create_asyncmodel(cls, tckey, data):
        model = cls(tckey=tckey, data=data)
        model.create(None)
        return model
    @classmethod
    def update_asyncmodel(cls, key, data):
        model = cls.get_by_key(key)        
        model.data = data
        model.update(None)
        return model
    @classmethod
    def delete_asyncmodel(cls, key):
        model = cls.get_by_key(key)
        model.delete(None)
    @classmethod    
    def delete_asyncmodels(cls, tckey):
        query = cls.all()
        query.filter("tckey =", tckey)
        return query.delete(None)
        
class AsyncTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
        AsyncModel.create_schema()
    
    @classmethod
    def tearDownClass(cls): 
        AsyncModel.delete_schema()
        dbpool.drop_db(orm_config.get_default_dbinfo())
        
    def assert_async_data_equal(self, tckey, data):
        time.sleep(0.1)
        model = AsyncModel.get_by_tckey(tckey)
        while(model is None):
            model = AsyncModel.get_by_tckey(tckey)
            time.sleep(0.1)
        self.assertEqual(model.data.content, data)
    
    def get_asyncmodel(self, tckey):
        time.sleep(0.1)
        model = AsyncModel.get_by_tckey(tckey)
        while(model is None):
            model = AsyncModel.get_by_tckey(tckey)
            time.sleep(0.1)
        return model
            
class Processor1(Processor):
    
    def process(self, message):
        AsyncModel.create_asyncmodel("send_msg", message)

class Processor2(Processor):
    
    def process(self, message):
        AsyncModel.create_asyncmodel("send_msg2", message)
        
class Processor3(Processor):
    
    def process(self, message):
        AsyncModel.create_asyncmodel("send_msg3", message)

class Processor4(Processor):
    
    def process(self, message):
        AsyncModel.create_asyncmodel("send_msg4", message)
        raise Exception("test error")
     
class DBConduitTest(AsyncTestCase):
    
    @classmethod
    def setUpClass(cls):
        AsyncTestCase.setUpClass()
        cls.conduit1 = asyn_config.get_conduit('message_type_1')
        cls.conduit1.start()
        cls.conduit2 = asyn_config.get_conduit('message_type_2')
        cls.conduit2.start()
        cls.conduit3 = asyn_config.get_conduit('message_type_3')
        cls.conduit3.start()
        cls.conduit4 = asyn_config.get_conduit('message_type_4')
        cls.conduit4.start()
    
    def test_send_message(self):
        data = {"context_id": "alpha",
                "data": [1, 2, 3],
                "more-data": kind.time_seconds()}
        sender.send_message('message_type_1', data)
        self.assert_async_data_equal('send_msg', data)
        
    def test_get_message(self):
        sender.send_message('message_type_2', '56rt')
        model = self.get_asyncmodel('send_msg2')
        msgid = model.data.id
        message = self.conduit2.get_message(msgid)
        self.assertEqual(message.content, '56rt')
        model = self.conduit2._DBConduit__msgclazz.get_by_key(msgid)
        self.assertEqual(model.attempts, 0)
        self.assertEqual(model.consume_flag, True)
        self.assertIsNotNone(model.pull_time)
        self.assertIsNone(model.consume_error)
        self.assertEqual(model.pull_flag, True)
        
    def test_send_message_maxlength(self):
        try:
            sender.send_message('message_type_3', "adfasdfasdfsdf")
            self.assertTrue(False)
        except MaxLengthError:
            self.assertTrue(True)
        try:
            sender.send_message('message_type_3', "adf45")
            self.assertTrue(True)
        except MaxLengthError:
            self.assertTrue(False)
            
    def test_consume_message(self):
        self.conduit3.stop()
        self.conduit3.clear()
        sender.send_message('message_type_3', "1")
        sender.send_message('message_type_3', "2")
        self.assertEqual(self.conduit3.size(), 2)
        self.conduit3.start()
        time.sleep(0.1)
        ams  = AsyncModel.fetch_by_tckey('send_msg3')
        while (len(ams) < 2):
            ams  = AsyncModel.fetch_by_tckey('send_msg3')
            time.sleep(0.1)
        msg = self.conduit3.next_message()
        self.assertIsNone(msg)
    
    def test_error(self):
        sender.send_message('message_type_4', "1")
        am = self.get_asyncmodel('send_msg4')
        while am is None:
            am = self.get_asyncmodel('send_msg4')
        message = am.data
        msgmodel = self.conduit4._DBConduit__msgclazz.get_by_key(message.id)
        self.assertEqual(msgmodel.attempts,1)
        self.assertIsNotNone(msgmodel.consume_time)
        self.assertEqual(msgmodel.consume_flag,False)
        self.assertIn('raise Exception("test error")',msgmodel.consume_error)
        time.sleep(2)
        msgmodel = self.conduit4._DBConduit__msgclazz.get_by_key(message.id)
        self.assertEqual(msgmodel.attempts,2)
        time.sleep(3)
        msgmodel = self.conduit4._DBConduit__msgclazz.get_by_key(message.id)
        self.assertEqual(msgmodel.attempts,2)
        
    def test_retry(self):
        self.conduit4.clear()
        AsyncModel.delete_asyncmodels('send_msg4')
        self.assertEqual(self.conduit4.size(), 0)
        sender.send_message('message_type_4', "re")
        am = self.get_asyncmodel('send_msg4')
        while am is None:
            am = self.get_asyncmodel('send_msg4')
        time.sleep(3)
        self.assertEqual(self.conduit4.size(), 1)
        b = self.conduit4.retry(am.data.id)
        self.assertTrue(b)
        message = self.conduit4.next_message()
        self.assertIsNotNone(message)
        try:
            self.conduit4.retry('nofoundid')
            self.assertTrue(False)
        except NoFoundError:
            self.assertTrue(True)
   
    def test_clear(self):        
        sender.send_message('message_type_3', "a")
        self.assertEqual(self.conduit3.size(), 1)
        self.conduit3.clear()
        self.assertEqual(self.conduit3.size(), 0)        

    @classmethod
    def tearDownClass(cls):        
        cls.conduit1.stop()
        cls.conduit2.stop()
        cls.conduit3.stop()        
        cls.conduit4.stop()
        AsyncTestCase.tearDownClass()        
        
    
