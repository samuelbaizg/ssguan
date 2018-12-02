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

from ssguan.ignitor.base.error import NoFoundError
from ssguan.ignitor.orm import config as orm_config, dbpool, update
from ssguan.ignitor.orm.error import UniqueError
from ssguan.ignitor.registry import service as registry_service
from ssguan.ignitor.registry.model import Registry
from ssguan.ignitor.utility import kind


class RegistryTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
        update.install()
        update.upgrade('ignitor.registry')
    
    def test_get_item_value(self):
        registry_service.create_item("00", "cc", "tst")
        value = registry_service.get_item_value("00")
        self.assertEqual(value, "cc")
    
    def test_create_item(self):
        query = Registry.all()
        query.delete(None)
        registry_service.create_item("111", 111, "tst")
        value = registry_service.get_item_value("111")
        self.assertEqual(value, 111)
        registry_service.create_item("33", [1, 2, 3], "tst")
        value = registry_service.get_item_value("33")
        self.assertSequenceEqual(value, [1, 2, 3])
        registry_service.create_item("44", True, "tst")
        value = registry_service.get_item_value("44")
        self.assertEqual(value, True)
        registry_service.create_item("55", False, "tst")
        value = registry_service.get_item_value("55")
        self.assertEqual(value, False)
        try:
            registry_service.create_item("111", 22, "tst")
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)
        try:
            registry_service.create_item("111", 3434, "ccccc")
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)
        
        registry_service.create_item("66", {"a":1, "b":2, "c":"cccc", "d":False}, "tst")
        value = registry_service.get_item_value("66")
        self.assertDictEqual(value, {"a":1, "b":2, "c":"cccc", "d":False})
        now = kind.utctoday()
        registry_service.create_item("77", now, "tst")
        value = registry_service.get_item_value("77")
        self.assertEqual(value, now)
        now = kind.utcnow()
        registry_service.create_item("88", now, "tst")
        value = registry_service.get_item_value("88")
        self.assertEqual(value, now)
        
    def test_has_item(self):
        query = Registry.all()
        query.delete(None)
        registry_service.create_item("88", "eeee", "tst")
        registry_service.create_item("99", "eeee", "tst")
        result = registry_service.has_item("88")
        self.assertTrue(result)
        result = registry_service.has_item("888")
        self.assertFalse(result)
        
    def test_update_item(self):
        query = Registry.all()
        query.delete(None)
        registry_service.create_item("11", 11, "tst")
        registry_service.update_item("11", 111, "tst", Registry.ROOT_KEY, True)
        value = registry_service.get_item_value("11")
        self.assertEqual(value, 111)
        registry_service.create_item("33", [1, 2, 3], "tst")
        registry_service.update_item("33", [1, 2, 3, 4], "tst", Registry.ROOT_KEY, True)
        value = registry_service.get_item_value("33")
        self.assertSequenceEqual(value, [1, 2, 3, 4])
        registry_service.create_item("44", True, "tst")
        registry_service.update_item("44", False, "tst", Registry.ROOT_KEY, True)
        value = registry_service.get_item_value("44")
        self.assertEqual(value, False)
        registry_service.create_item("55", False, "tst")
        registry_service.update_item("55", True, "tst", Registry.ROOT_KEY, True)
        value = registry_service.get_item_value("55")
        self.assertEqual(value, True)
        registry_service.create_item("66", {"a":1, "b":2, "c":"cccc", "d":False}, "tst")
        registry_service.update_item("66", {"a":1, "b":3, "c":"ddd", "d":True, "e":"zzz"}, "tst", Registry.ROOT_KEY, True)
        value = registry_service.get_item_value("66")
        self.assertDictEqual(value, {"a":1, "b":3, "c":"ddd", "d":True, "e":"zzz"})
        now = kind.utctoday()
        registry_service.create_item("77", now, "tst")
        registry_service.update_item("77", now, "tst", Registry.ROOT_KEY, True)
        value = registry_service.get_item_value("77")
        self.assertEqual(value, now)
        now1 = kind.utcnow()
        registry_service.create_item("88", now1, "tst")
        now2 = kind.utcnow()
        registry_service.update_item("88", now2, "tst", Registry.ROOT_KEY, True)
        value = registry_service.get_item_value("88")
        self.assertEqual(value, now2)
        try:
            value = registry_service.update_item("No", 1, "tst", Registry.ROOT_KEY, True)
            self.assertTrue(False)
        except NoFoundError:
            self.assertTrue(True)
      
    def test_invalid_item(self):
        query = Registry.all()
        query.delete(None)
        registry_service.create_item("111", 111, "tst")
        registry_service.invalid_item("111", False)
        result = registry_service.has_item("111", valid_flag=True)
        self.assertFalse(result)
    
    def test_fetch_items(self):
        query = Registry.all()
        query.delete(None)
        registry_service.create_item("111", 111, "tst", parent_key="bbb")
        registry_service.create_item("33", [1, 2, 3], "tst", parent_key="bbb")
        registry_service.create_item("44", True, "tst", parent_key="bbb")
        registry_service.invalid_item("44", False)
        sysprops = registry_service.fetch_items("bbb", valid_flag=True)
        self.assertEqual(len(sysprops), 2)
        sysprops = registry_service.fetch_items("bbb", valid_flag=False)
        self.assertEqual(len(sysprops), 1)
        sysprops = registry_service.fetch_items(None, valid_flag=None)
        self.assertEqual(len(sysprops), 3)
        registry_service.create_item("11ee1", 111, "le1")
        sysprops = registry_service.fetch_items(Registry.ROOT_KEY)
        self.assertEqual(len(sysprops), 1)
    
    def test_delete_item(self): 
        registry_service.create_item("asdfdsf", "223", "group6")
        registry_service.delete_item("asdfdsf")
        s = registry_service.get_item("asdfdsf")
        self.assertIsNone(s)
        
    @classmethod
    def tearDownClass(cls):
        dbpool.drop_db(orm_config.get_default_dbinfo())
