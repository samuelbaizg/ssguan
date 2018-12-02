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

from ssguan import config
from ssguan.commons import database


class DBUtilTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        dbinfo = config.dbCFG.get_root_dbinfo()
        dbinfo.dbname = "database_test"
        cls.dbinfo = dbinfo
    
    def test_01_has_db(self):
        has = database.has_db(self.dbinfo)
        if has:
            database.drop_db(self.dbinfo)
        has = database.has_db(self.dbinfo)
        self.assertFalse(has)
    
    def test_02_create_db(self):
        database.create_db(self.dbinfo)
        has = database.has_db(self.dbinfo)
        self.assertTrue(has)
        
    def test_03_get_dbconn(self):
        db1 = database.get_dbconn(None)
        self.assertIsNotNone(db1)
        
    def test_10_drop_db(self):
        database.drop_db(self.dbinfo)
        has = database.has_db(self.dbinfo)
        self.assertFalse(has)
    
    @classmethod
    def tearDownClass(cls):
        if database.has_db(cls.dbinfo):
            database.drop_db(cls.dbinfo)
    
    
    