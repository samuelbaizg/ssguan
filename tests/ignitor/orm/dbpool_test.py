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

from ssguan.ignitor.orm import dbpool, config as orm_config


class DBUtilTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        dbinfo = orm_config.get_default_dbinfo()
        dbinfo = dbinfo.copy()
        dbinfo.dbname = "database_test2"
        cls.dbinfo = dbinfo
    
    def test_01_has_db(self):
        has = dbpool.has_db(self.dbinfo)
        if has:
            dbpool.drop_db(self.dbinfo)
        has = dbpool.has_db(self.dbinfo)
        self.assertFalse(has)
    
    def test_02_create_db(self):
        dbpool.create_db(self.dbinfo)
        has = dbpool.has_db(self.dbinfo)
        self.assertTrue(has)
        
    def test_03_get_dbconn(self):
        db1 = dbpool.get_dbconn(None)
        self.assertIsNotNone(db1)
        
    def test_10_drop_db(self):
        dbpool.drop_db(self.dbinfo)
        has = dbpool.has_db(self.dbinfo)
        self.assertFalse(has)
    
    @classmethod
    def tearDownClass(cls):
        if dbpool.has_db(cls.dbinfo):
            dbpool.drop_db(cls.dbinfo)
    
    
    