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

from ssguan.ignitor.cache.decorator import cached

_called = {"a":0, "b":0, "c":0, "d":0, "f":0}

class CachedTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        pass
    
    @cached()
    def func_1(self):
        _called['a'] = _called['a'] + 1     
        return "aaa"
    
    @cached()
    def func_2(self, a, b=None):
        _called['b'] = _called['b'] + 1     
        return 'p%s_%s' % (a, b)
    
    @cached(lifespan=1)
    def func_3(self, a):
        _called['c'] = _called['c'] + 1     
        return 'p%s' % (a)
    
    @cached(lifespan=500, container="z")
    def func_4(self, a):
        _called['d'] = _called['d'] + 1     
        return 'p%s' % (a)
    
    @cached(lifespan=10, cache_name="lotest")
    def func_5(self, a):
        _called['f'] = _called['f'] + 1     
        return 'p%s' % (a)
    
    def test_noargs_func(self):
        rtn = self.func_1()
        self.assertEqual(rtn, 'aaa')
        self.assertEqual(_called["a"], 1)
        rtn = self.func_1()
        self.assertEqual(rtn, 'aaa')
        self.assertEqual(_called["a"], 1)
    
    def test_args_func(self):
        rtn = self.func_2(1)
        self.assertEqual(rtn, 'p1_None')
        self.assertEqual(_called["b"], 1)
        rtn = self.func_2(1)
        self.assertEqual(rtn, 'p1_None')
        self.assertEqual(_called["b"], 1)
        rtn = self.func_2(1, b='abc')
        self.assertEqual(rtn, 'p1_abc')
        self.assertEqual(_called["b"], 2)
        rtn = self.func_2(1, b='abc')
        self.assertEqual(rtn, 'p1_abc')
        self.assertEqual(_called["b"], 2)
    
    def test_timeout(self):
        rtn = self.func_3(1)
        self.assertEqual(rtn, 'p1')
        self.assertEqual(_called["c"], 1)
        time.sleep(1.2)
        rtn = self.func_3(1)
        self.assertEqual(rtn, 'p1')
        self.assertEqual(_called["c"], 2)
    
    def test_container(self):
        rtn = self.func_4('bb')
        self.assertEqual(rtn, 'pbb')
        self.assertEqual(_called["d"], 1)
        rtn = self.func_4('bb')
        self.assertEqual(rtn, 'pbb')
        self.assertEqual(_called["d"], 1)
        
    def test_cache_name(self):
        rtn = self.func_5('2')
        self.assertEqual(rtn, 'p2')
        self.assertEqual(_called["f"], 1)
        rtn = self.func_5('2')
        self.assertEqual(rtn, 'p2')
        self.assertEqual(_called["f"], 1)
    
    @classmethod
    def tearDownClass(cls):
        pass
        
