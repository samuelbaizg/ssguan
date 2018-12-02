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

from ssguan.ignitor.base.error import RequiredError, ChoiceError, TypeStrError, CompareError
from ssguan.ignitor.etl import etltask
from ssguan.ignitor.etl.tffunctor import StripTF, ElicitTF


class SetTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        try:
            task.set(5, 1)
            self.assertTrue(False)
        except ChoiceError:
            pass
        try:
            task.set()
            self.assertTrue(False)
        except RequiredError:
            pass
    
    def test_set_one_value(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        task.set('a', 3)
        self.assertEqual(task.next(), {'a':3})
        self.assertEqual(task.next(), {'a':3})
        self.assertIsNone(task.next())
    
    def test_set_dict_value(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        task.set({'b':6})
        self.assertEqual(task.next(), {'a':1, 'b':6})
        self.assertEqual(task.next(), {'a':2, 'b':6})
        self.assertIsNone(task.next())
    
class MoveTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        try:
            task.move(5, 1)
            self.assertTrue(False)
            task.move('5', 1)
            self.assertTrue(False)
        except TypeStrError:
            pass
        try:
            task.move()
            self.assertTrue(False)
            task.move('a')
            self.assertTrue(False)
        except RequiredError:
            pass
        
        try:
            task.move('a', 'a')
            self.assertTrue(False)           
        except CompareError:
            pass
    
    def test_move_no_old(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        task.move('b', 'c')
        self.assertEqual(task.next(), {'a':1, 'c':None})
        self.assertEqual(task.next(), {'a':2, 'c':None})
        self.assertIsNone(task.next())
    
    def test_move_new(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        task.move('a', 'c')
        self.assertEqual(task.next(), {'c':1})
        self.assertEqual(task.next(), {'c':2})
        self.assertIsNone(task.next())
    
class CopyTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        try:
            task.copy(5, 1)
            self.assertTrue(False)
            task.move('5', 1)
            self.assertTrue(False)
        except TypeStrError:
            pass
        try:
            task.copy()
            self.assertTrue(False)
            task.copy('a')
            self.assertTrue(False)
        except RequiredError:
            pass
        
        try:
            task.copy('a', 'a')
            self.assertTrue(False)           
        except CompareError:
            pass
    
    def test_copy_no_old(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        task.move('b', 'c')
        self.assertEqual(task.next(), {'a':1, 'c':None})
        self.assertEqual(task.next(), {'a':2, 'c':None})
        self.assertIsNone(task.next())
        
    def test_copy_new(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        task.copy('a', 'c')
        self.assertEqual(task.next(), {'a':1, 'c':1})
        self.assertEqual(task.next(), {'a':2, 'c':2})
        self.assertIsNone(task.next())
    
class RemoveTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':1}, {'a':2}]
        task = etltask.create_task().join(l)
        try:
            task.remove(5)
            self.assertTrue(False)            
        except ChoiceError:
            pass
    
    def test_remove_nothing(self):
        l = [{'a':1, 'b':2}, {'a':2, 'b':3}]
        task = etltask.create_task().join(l)
        task.remove('c')
        self.assertEqual(task.next(), {'a':1, 'b':2})
        self.assertEqual(task.next(), {'a':2, 'b':3})
        self.assertIsNone(task.next())
        
    def test_remove_one_column(self):
        l = [{'a':1, 'b':2}, {'a':2, 'b':3}]
        task = etltask.create_task().join(l)
        task.remove('b')
        self.assertEqual(task.next(), {'a':1})
        self.assertEqual(task.next(), {'a':2})
        self.assertIsNone(task.next())
    
    def test_remove_multiple_columns(self):
        l = [{'a':1, 'b':2, 'c':1}, {'a':2, 'b':3, 'c':3}]
        task = etltask.create_task().join(l)
        task.remove(['a', 'b'])
        self.assertEqual(task.next(), {'c':1})
        self.assertEqual(task.next(), {'c':3})
        self.assertIsNone(task.next())
        
class SplitTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        try:
            task.split(5)
            self.assertTrue(False)
        except RequiredError:
            pass
        try:
            task.split(5, 2)
            self.assertTrue(False)
        except TypeStrError:
            pass
        try:
            task.split('a', 3)
            self.assertTrue(False)       
        except TypeStrError:
            pass
        
    def test_split(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        task.split('a', ',')
        self.assertEqual(task.next(), {'a':['b', 'c']})
        self.assertEqual(task.next(), {'a':['5', '6']})
        self.assertIsNone(task.next())

class ReplaceTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        try:
            task.replace()
            self.assertTrue(False)
            task.replace('a')
            self.assertTrue(False)
            task.replace('a', 'c')
            self.assertTrue(False)
        except RequiredError:
            pass
        try:
            task.replace(5, 'a', 'b')
            self.assertTrue(False)
            task.replace('a', 2)
            self.assertTrue(False)
            task.replace('a', 'b', 1)
            self.assertTrue(False)
        except TypeStrError:
            pass
    
    def test_replace(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        task.replace('a', ',', '-')
        self.assertEqual(task.next(), {'a':'b-c'})
        self.assertEqual(task.next(), {'a':'5-6'})
        self.assertIsNone(task.next())

class SubTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        try:
            task.sub()
            self.assertTrue(False)
            task.sub('a')
            self.assertTrue(False)            
        except RequiredError:
            pass
        try:
            task.sub(5, 'a')
            self.assertTrue(False)
            task.sub('a', 2)
            self.assertTrue(False)            
        except TypeStrError:
            pass
    
    def test_sub(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        task.sub('a', '[0-9],[0-9]', '=')
        self.assertEqual(task.next(), {'a':'b,c'})
        self.assertEqual(task.next(), {'a':'='})
        self.assertIsNone(task.next())

class FindallTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        try:
            task.findall()
            self.assertTrue(False)
            task.findall('a')
            self.assertTrue(False)            
        except RequiredError:
            pass
        try:
            task.findall(5, 'a')
            self.assertTrue(False)
            task.findall('a', 2)
            self.assertTrue(False)        
            task.findall('a', 2, 66)
            self.assertTrue(False)            
        except TypeStrError:
            pass       
    
    def test_findall(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        task.findall('a', '[0-9],[0-9]')
        self.assertEqual(task.next(), {'a':[]})
        self.assertEqual(task.next(), {'a':['5,6']})
        self.assertIsNone(task.next())
    
class FindnumTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        try:
            task.findnum()
            self.assertTrue(False)
            task.findnum('a')
            self.assertTrue(False)            
        except RequiredError:
            pass
        try:
            task.findnum(5)
            self.assertTrue(False)
        except TypeStrError:
            pass       
    
    def test_findnum(self):
        l = [{'a':'b,c'}, {'a':'5,6'}, {'a':'6'}]
        task = etltask.create_task().join(l)
        task.findnum('a')
        self.assertEqual(task.next(), {'a':[]})
        self.assertEqual(task.next(), {'a': [('5', ''), ('6', '')]})
        self.assertEqual(task.next(), {'a':[('6', '')]})
        self.assertIsNone(task.next())

class StripTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        try:
            task.strip()
            self.assertTrue(False)
            task.strip('a')
            self.assertTrue(False)      
            task.strip('a', ' ')
            self.assertTrue(False)
        except RequiredError:
            pass
        try:        
            task.strip('a', 2)
            self.assertTrue(False)       
        except TypeStrError:
            pass      
        try:
            task.strip(5, 'a')
            self.assertTrue(False)
            task.strip('a', '2', 'cc')
            self.assertTrue(False)       
        except ChoiceError:
            pass       
    
    def test_strip(self):
        l = [{'a':'zzb,czz'}]
        task = etltask.create_task().join(l)
        task.strip('a', 'zz')
        self.assertEqual(task.next(), {'a':'b,c'})
        self.assertIsNone(task.next())
        task = etltask.create_task().join(l)
        task.strip('a', 'zz', StripTF.MODE_STRIP)
        self.assertEqual(task.next(), {'a':'b,c'})
        self.assertIsNone(task.next())
    
    def test_strip_left(self):
        l = [{'a':'zzb,czz'}]
        task = etltask.create_task().join(l)
        task.strip('a', 'zz', StripTF.MODE_LSTRIP)
        self.assertEqual(task.next(), {'a':'b,czz'})
        self.assertIsNone(task.next())
    
    def test_strip_right(self):
        l = [{'a':'zzb,czz'}]
        task = etltask.create_task().join(l)
        task.strip('a', 'zz', StripTF.MODE_RSTRIP)
        self.assertEqual(task.next(), {'a':'zzb,c'})
        self.assertIsNone(task.next())

class ElicitTFTest(unittest.TestCase):
    
    def test_validate_args(self):
        l = [{'a':'b,c'}, {'a':'5,6'}]
        task = etltask.create_task().join(l)
        try:
            task.elicit()
            self.assertTrue(False)
            task.elicit('a')
            self.assertTrue(False)
        except RequiredError:
            pass
        try:
            task.elicit('a', left=2, right='3')
            self.assertTrue(False)     
            task.elicit('a', left='3', right=2)
            self.assertTrue(False)       
            task.elicit('a', left='3', right='22')
            self.assertTrue(False)
        except TypeStrError:
            pass
        try:
            task.elicit('a', left='a', right='b', mode='ccc')
            self.assertTrue(False)
        except ChoiceError:
            pass       
    
    def test_elicit_no_margin(self):
        l = [{'a':'zb,cb'}, {'a':'z5,6c'}]
        task = etltask.create_task().join(l)
        task.elicit('a', left='z', right='b')
        self.assertEqual(task.next(), {'a':'b,c'})
        self.assertEqual(task.next(), {'a':'z5,6c'})
        self.assertIsNone(task.next())
        
    def test_elicit_include_margin(self):
        l = [{'a':'zb,cb'}, {'a':'z5,6c'}]
        task = etltask.create_task().join(l)
        task.elicit('a', left='z', right='b',mode=ElicitTF.MODE_MARGIN)
        self.assertEqual(task.next(), {'a':'zb,cb'})
        self.assertEqual(task.next(), {'a':'z5,6c'})
        self.assertIsNone(task.next())
    
    def test_elicit_left_margin(self):
        l = [{'a':'zb,cb'}, {'a':'z5,6c'}]
        task = etltask.create_task().join(l)
        task.elicit('a', left='z', right='b',mode=ElicitTF.MODE_MARGIN_LEFT)
        self.assertEqual(task.next(), {'a':'zb,c'})
        self.assertEqual(task.next(), {'a':'z5,6c'})
        self.assertIsNone(task.next())
    
    def test_elicit_right_margin(self):
        l = [{'a':'zb,cb'}, {'a':'z5,6c'}]
        task = etltask.create_task().join(l)
        task.elicit('a', left='z', right='b',mode=ElicitTF.MODE_MARGIN_RIGHT)
        self.assertEqual(task.next(), {'a':'b,cb'})
        self.assertEqual(task.next(), {'a':'z5,6c'})
        self.assertIsNone(task.next())
