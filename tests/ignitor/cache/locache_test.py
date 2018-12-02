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

from ssguan.ignitor.audit.model import MCLog
from ssguan.ignitor.cache import service as cache_service, locache

class LoMemCacheTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.cache = cache_service.get_cache("lotest") 
        pass

    def test_put_get_default(self):
        self.cache.put("aaaa", [1, 2, 3])
        self.assertEqual(self.cache.get("aaaa"), [1, 2, 3])
        self.assertIn('lotest:default:aaaa', locache._locmem_caches)
        self.assertNotIn('aaaa', locache._locmem_caches)
        self.assertNotIn('lotest:aaaa', locache._locmem_caches)
        self.assertNotIn('default:aaaa', locache._locmem_caches)
        mclog = MCLog(modelname='ffadsf', change_props={'adf':'fdff'})
        self.cache.put("aaaa", [mclog])
        aaaa = self.cache.get("aaaa")
        self.assertEqual(aaaa[0].modelname, mclog.modelname)
        self.assertEqual(aaaa[0].change_time, mclog.change_time)
        self.assertEqual(aaaa[0].change_props, mclog.change_props)
        self.assertEqual(self.cache.has_key("aaaa"), True)
    
    def test_has_key(self):
        self.cache.put("11", [1, 2, 3], container='buck')
        self.assertEqual(self.cache.has_key("11"), False)
        self.assertEqual(self.cache.has_key("11", container='buck'), True)
        self.assertEqual(self.cache.has_key("22", container='buck'), False)
        self.assertEqual(self.cache.has_key("cc"), False)

    
    def test_put_get_container(self):
        self.cache.put("bbbb", [1, 2, 3], container='buck')
        self.assertEqual(self.cache.has_key("bbbb"), False)
        self.assertEqual(self.cache.has_key("bbbb", container='buck'), True)
        
    def test_timeout(self):
        self.cache.put("ccc", [1, 2, 3])
        time.sleep(1.2)
        self.assertFalse(self.cache.get("ccc"))
        self.assertIsNone(self.cache.get("ccc"), True)
    
    def test_delete(self):
        self.cache.put("ddddd", [1, 2, 3])
        self.cache.put("ddddd", [1, 2, 3], container='second')
        self.cache.delete("ddddd")
        self.assertFalse(self.cache.get("ddddd"))
        self.assertIsNone(self.cache.get("ddddd"), True)
        self.assertTrue(self.cache.get("ddddd" , container='second'))
        
    def test_clear(self):
        self.cache.put("ddddd", [1, 2, 3])
        self.cache.put("zz", 'fff')
        self.cache.clear()
        self.assertFalse(self.cache.get("zz"))
        self.assertFalse(self.cache.get("ddddd"))
    
    @classmethod
    def tearDownClass(cls):
        pass
        
