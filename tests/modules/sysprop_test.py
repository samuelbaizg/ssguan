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
from ssguan.commons import database, typeutils
from ssguan.commons.dao import UniqueError
from ssguan.commons.error import ProgramError
from ssguan.modules import sysprop
from ssguan.modules.auth import User
from ssguan.modules.sysprop import SysProp


class SysPropTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
    
    def test_get_sysprop_value(self):
        sysprop.add_sysprop("00", "cc", "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("00", User.ID_ROOT)
        self.assertEqual(value, "cc")
    
    def test_add_sysprop(self):
        query = SysProp.all()
        query.delete(None)
        sysprop.add_sysprop("111", 111, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("111", User.ID_ROOT)
        self.assertEqual(value, 111)
        sysprop.add_sysprop("33", [1, 2, 3], "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("33", User.ID_ROOT)
        self.assertItemsEqual(value, [1, 2, 3])
        sysprop.add_sysprop("44", True, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("44", User.ID_ROOT)
        self.assertEqual(value, True)
        sysprop.add_sysprop("55", False, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("55", User.ID_ROOT)
        self.assertEqual(value, False)
        try:
            sysprop.add_sysprop("111", 22, "tst", None, User.ID_ROOT)
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)
        try:
            sysprop.add_sysprop("111", 3434, "ccccc", None, User.ID_ROOT)
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)
        
        sysprop.add_sysprop("66", {"a":1, "b":2, "c":"cccc", "d":False}, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("66", User.ID_ROOT)
        self.assertDictEqual(value, {"a":1, "b":2, "c":"cccc", "d":False})
        now = typeutils.utctoday()
        sysprop.add_sysprop("77", now, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("77", User.ID_ROOT)
        self.assertEqual(value, now)
        now = typeutils.utcnow()
        sysprop.add_sysprop("88", now, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("88", User.ID_ROOT)
        self.assertEqual(value, now)
        
    def test_has_sysprop(self):
        query = SysProp.all()
        query.delete(None)
        sysprop.add_sysprop("88", "eeee", "tst", None, User.ID_ROOT)
        sysprop.add_sysprop("99", "eeee", "tst", None, User.ID_ROOT)
        result = sysprop.has_sysprop("88", User.ID_ROOT)
        self.assertTrue(result)
        result = sysprop.has_sysprop("888", User.ID_ROOT)
        self.assertFalse(result)
        
    def test_update_sysprop(self):
        
        query = SysProp.all()
        query.delete(None)
        sysprop.add_sysprop("11", 11, "tst", None, User.ID_ROOT)
        sysprop.update_sysprop("11", 111, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("11", User.ID_ROOT)
        self.assertEqual(value, 111)
        sysprop.add_sysprop("33", [1, 2, 3], "tst", None, User.ID_ROOT)
        sysprop.update_sysprop("33", [1, 2, 3, 4], "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("33", User.ID_ROOT)
        self.assertItemsEqual(value, [1, 2, 3, 4])
        sysprop.add_sysprop("44", True, "tst", None, User.ID_ROOT)
        sysprop.update_sysprop("44", False, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("44", User.ID_ROOT)
        self.assertEqual(value, False)
        sysprop.add_sysprop("55", False, "tst", None, User.ID_ROOT)
        sysprop.update_sysprop("55", True, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("55", User.ID_ROOT)
        self.assertEqual(value, True)
        sysprop.add_sysprop("66", {"a":1, "b":2, "c":"cccc", "d":False}, "tst", None, User.ID_ROOT)
        sysprop.update_sysprop("66", {"a":1, "b":3, "c":"ddd", "d":True, "e":"zzz"}, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("66", User.ID_ROOT)
        self.assertDictEqual(value, {"a":1, "b":3, "c":"ddd", "d":True, "e":"zzz"})
        now = typeutils.utctoday()
        sysprop.add_sysprop("77", now, "tst", None, User.ID_ROOT)
        sysprop.update_sysprop("77", now, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("77", User.ID_ROOT)
        self.assertEqual(value, now)
        now1 = typeutils.utcnow()
        sysprop.add_sysprop("88", now1, "tst", None, User.ID_ROOT)
        now2 = typeutils.utcnow()
        sysprop.update_sysprop("88", now2, "tst", None, User.ID_ROOT)
        value = sysprop.get_sysprop_value("88", User.ID_ROOT)
        self.assertEqual(value, now2)
        try:
            value = sysprop.update_sysprop("No", 1, "tst", None, User.ID_ROOT)
            self.assertTrue(False)
        except ProgramError, e:
            self.assertIn("does not existed", str(e))
      
    def test_remove_sysprop(self):
        query = SysProp.all()
        query.delete(None)
        sysprop.add_sysprop("111", 111, "tst", None, User.ID_ROOT)
        sysprop.remove_sysprop("111", True, User.ID_ROOT)
        result = sysprop.has_sysprop("111", User.ID_ROOT)
        self.assertFalse(result)
    
    def test_fetch_sysprops(self):
        query = SysProp.all()
        query.delete(None)
        sysprop.add_sysprop("111", 111, "tst", None, User.ID_ROOT)
        sysprop.add_sysprop("33", [1, 2, 3], "tst", None, User.ID_ROOT)
        sysprop.add_sysprop("44", True, "tst", None, User.ID_ROOT)
        sysprop.remove_sysprop("44", True, User.ID_ROOT)
        sysprops = sysprop.fetch_sysprops(None, None, User.ID_ROOT)
        self.assertEqual(len(sysprops), 2)
        sysprops = sysprop.fetch_sysprops(None, None, User.ID_ROOT, removed=True)
        self.assertEqual(len(sysprops), 1)
        sysprops = sysprop.fetch_sysprops(None, None, User.ID_ROOT, removed=None)
        self.assertEqual(len(sysprops), 3)
        sysprop.add_sysprop("11ee1", 111, "le1", None, User.ID_ROOT)
        sysprops = sysprop.fetch_sysprops("le1", None, User.ID_ROOT, removed=False)
        self.assertEqual(len(sysprops), 1)
        
    def test_remove_sysprops(self):
        query = SysProp.all()
        query.delete(None)
        sysprop.add_sysprop("111", "2323", "group6", None, User.ID_ROOT)
        sysprop.add_sysprop("222", "fadsf", "group6", None, User.ID_ROOT)
        sysprop.remove_sysprops("group6", None, True, User.ID_ROOT)
        ss = sysprop.fetch_sysprops(None, None, User.ID_ROOT, removed=True)
        self.assertEqual(len(ss), 2)
        
    def test_delete_sysprops(self):
        query = SysProp.all()
        query.delete(None)
        sysprop.add_sysprop("111", "223", "group6", "1", User.ID_ROOT)
        sysprop.add_sysprop("222", "fasd", "group6", "2", User.ID_ROOT)
        sysprop.delete_sysprops("group6", "1", User.ID_ROOT)
        self.assertEqual(query.count(), 1)
        sp = query.get()
        self.assertEqual(sp.p_key, "222")
        sysprop.delete_sysprops("group6", None, User.ID_ROOT)
        query = SysProp.all()
        self.assertEqual(query.count(), 0)
    
    def test_delete_sysprop(self): 
        sysprop.add_sysprop("asdfdsf", "223", "group6", "1", User.ID_ROOT)
        sysprop.delete_sysprop("asdfdsf", User.ID_ROOT)
        s = sysprop.get_sysprop("asdfdsf", User.ID_ROOT)
        self.assertIsNone(s)
        
    @classmethod
    def tearDownClass(cls):
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())
