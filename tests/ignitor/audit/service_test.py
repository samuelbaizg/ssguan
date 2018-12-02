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

import unittest

from ssguan.ignitor.audit.model import MCLog
from ssguan.ignitor.orm import  dbpool, config as orm_config, properti, update
from ssguan.ignitor.orm.model import Model


class McLogTest(unittest.TestCase):
    
    class MCModel(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        f_str = properti.StringProperty()
        f_int = properti.IntegerProperty()
        f_bool = properti.BooleanProperty()
        f_float = properti.FloatProperty()
        f_date = properti.DateProperty()
        f_datetime = properti.DateTimeProperty()
        f_v = properti.StringProperty(length=8)
        f_str1 = properti.StringProperty(persistent=False)
        f_str_logged = properti.StringProperty(logged=True)
        f_float_logged = properti.FloatProperty(logged=True)
        f_json = properti.DictProperty()
    
    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
        update.install()
        update.upgrade('ignitor.audit')
        cls.MCModel.create_schema()
        
    def test_add_mclog(self):
        tmodel = self.MCModel()
        tmodel.f_str = "abcd"
        tmodel.f_int = 100
        tmodel.f_float = 1000.0
        tmodel.f_bool = False
        tmodel.f_float_logged = 1.0
        tmodel.f_str_logged = "1234"
        tmodel.create(2)
        tmodel.f_str = 'abcd1'
        tmodel.f_float = 1001.0
        tmodel.f_float_logged = 2.0
        tmodel.f_str_logged = "123456"
        tmodel.update(2)
        query = MCLog.all()
        self.assertEqual(query.count(), 1)
        mclog = query.get()
        self.assertEqual(len(mclog.change_props), 2)
        
    @classmethod
    def tearDownClass(cls):
        cls.MCModel.delete_schema()
        dbpool.drop_db(orm_config.get_default_dbinfo())
