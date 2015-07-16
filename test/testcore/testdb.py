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
from core.db import dbutil
class DBTestSuit(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self)
        modeltestsuit = unittest.makeSuite(DBUtilTest, 'test')
        self.addTest(modeltestsuit)

class DBUtilTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        dbinfo = dbutil.get_master_dbinfo()
        dbinfo = dbinfo.copy(dbname = "test_test_db")
        cls.dbinfo = dbinfo
    
    def test01HasDB(self):
        has = dbutil.has_db(self.dbinfo)
        self.assertFalse(has)
    
    def test02CreateDB(self):
        dbutil.create_db(self.dbinfo)
        has = dbutil.has_db(self.dbinfo)
        self.assertTrue(has)
        
    def test03GetConn(self):
        db1 = dbutil.get_dbconn(self.dbinfo)
        self.assertIsNotNone(db1)
        
    def test10DropDB(self):
        dbutil.drop_db(self.dbinfo)
        has = dbutil.has_db(self.dbinfo)
        self.assertFalse(has)
    
    @classmethod
    def tearDownClass(cls):
        if dbutil.has_db(cls.dbinfo):
            dbutil.drop_db(cls.dbinfo)
    
    
    