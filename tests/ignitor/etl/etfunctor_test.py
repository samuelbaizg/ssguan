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

import os
import unittest

from ssguan.ignitor.base.error import ChoiceError, RequiredError, TypeIntError, \
    NoFoundError, InvalidError
from ssguan.ignitor.etl import etltask
from ssguan.ignitor.etl.functor import Extractor


class JoinETTest(unittest.TestCase):
    
    def test_list(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        self.assertEqual(task.next(), {'a':1})
        self.assertEqual(task.next(), {'a':2})
        self.assertIsNone(task.next())
        
    def test_generator(self):
        def gg():
            yield {'a':1}
            yield {'a':2}
        task = etltask.create_task().join(gg())
        self.assertEqual(task.next(), {'a':1})
        self.assertEqual(task.next(), {'a':2})
        self.assertIsNone(task.next())
        
    def test_append(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l).join(l)
        self.assertEqual(task.next(), {'a':1})
        self.assertEqual(task.next(), {'a':2})
        self.assertEqual(task.next(), {'a':1})
        self.assertEqual(task.next(), {'a':2})
        self.assertIsNone(task.next())
        
    def test_merge(self):
        l1 = [{'a':1}, {'a':2}]
        l2 = [{'b':3}]
        task = etltask.create_task().join(l1).join(l2, mode=Extractor.MODE_MERGE)
        self.assertEqual(task.next(), {'a':1, 'b':3})
        self.assertEqual(task.next(), {'a':2})
        self.assertIsNone(task.next())
    
    def test_cross(self):
        l1 = [{'a':1}, {'a':2}]
        l2 = [{'b':3}]
        task = etltask.create_task().join(l1).join(l2, mode=Extractor.MODE_CROSS)
        self.assertEqual(task.next(), {'a':1, 'b':3})
        self.assertEqual(task.next(), {'a':2, 'b':3})
        self.assertIsNone(task.next())
    
    def test_mix(self):
        l1 = [{'a':1}, {'a':2}]
        l2 = [{'b':3}]
        task = etltask.create_task().join(l1).join(l2, mode=Extractor.MODE_MIX)
        self.assertEqual(task.next(), {'a':1})        
        self.assertEqual(task.next(), {'b':3})
        self.assertEqual(task.next(), {'a':2})
        self.assertIsNone(task.next())
    
    def test_invalid_mode(self):
        try:
            t = etltask.create_task()
            t.join([], mode='222')
            self.assertFalse(True)
        except ChoiceError:
            pass
        

class RangeETTest(unittest.TestCase):
    
    def test_extract(self):
        task = etltask.create_task().range('a', 1, 3, 1)
        self.assertEqual(task.next(), {'a':1})
        self.assertEqual(task.next(), {'a':2})
        self.assertEqual(task.next(), None)
        task = etltask.create_task().range('a', 1, 3, 2)
        self.assertEqual(task.next(), {'a':1})        
        self.assertEqual(task.next(), None)
        task = etltask.create_task().range('a', 1, 1, 1)
        self.assertEqual(task.next(), None)
    
    def test_invalid_args(self):
        try:
            etltask.create_task().range('', 1, 3, 1)
            self.assertFalse(True)
        except RequiredError:
            pass
        try:
            etltask.create_task().range('bb', 'a', 3, 1)
        except TypeIntError:
            pass
        try:
            etltask.create_task().range('bb', 1, 'b', 1)
        except TypeIntError:
            pass
        try:
            etltask.create_task().range('bb', 1, 2, '1')
        except TypeIntError:
            pass
        
class ReadETTest(unittest.TestCase):
    
    def test_invalid_args(self):
        def aa():
            pass
        try:
            etltask.create_task().read('c:/b', aa)
            self.assertFalse(True)
        except NoFoundError:
            pass
        try:
            etltask.create_task().read(os.getcwd(), aa)
            self.assertFalse(True)
        except InvalidError:
            pass
        try:
            etltask.create_task().read(__file__, None)
            self.assertFalse(True)
        except RequiredError:
            pass
        
    def test_extract_file(self):
        def aa(line):
            if line.endswith('\n'):
                return {'line':int(line[:-1])}
            else:
                return {'line':int(line)}
        f = os.path.dirname(__file__)
        f = os.path.join(f, 'etfunctor_test.txt')
        task = etltask.create_task().read(f, aa)
        self.assertEqual(task.next(), {'line':1})
        self.assertEqual(task.next(), {'line':2})
    
    def test_extract_json(self):
        def aa(line):
            return line
        f = os.path.dirname(__file__)
        f = os.path.join(f, 'etfunctor_test.json')
        task = etltask.create_task().read(f, aa)
        self.assertEqual(task.next(), { "msg": "", "data": [1, 2]})
        self.assertEqual(task.next(), None)
        
    def test_extract_json_list(self):
        def aa(line):
            return line
        f = os.path.dirname(__file__)
        f = os.path.join(f, 'etfunctor_list_test.json')
        task = etltask.create_task().read(f, aa)
        self.assertEqual(task.next(), { "msg": "", "data": [1, 2]})
        self.assertEqual(task.next(), { "msg": "3", "data": [4, 5]})
        self.assertEqual(task.next(), None)
