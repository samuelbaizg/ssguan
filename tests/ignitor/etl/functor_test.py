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

from ssguan.ignitor.etl.functor import Extractor
from ssguan.ignitor.utility import kind


class ExtractorTest(unittest.TestCase):
    
    class AppendExtractor(Extractor):
        
        def extract(self):
            yield 3
            
    class MergeExtractor(Extractor):
        
        def extract(self):
            yield {'c':8}
            yield {'c': 9}
    
    class CrossExtractor(Extractor):
        
        def extract(self):
            yield {'c':8, 'd':10}
            yield {'c': 9, 'd': 11}
    
    class MixExtractor(Extractor):
        
        def extract(self):
            yield {'c':8, 'd':10}
            yield {'c': 9, 'd': 11}
            
    def test_none_generator(self):
        te = self.AppendExtractor()
        g = te.process(None)
        t = kind.generator_next(g)
        self.assertEqual(t, 3)
        try:
            t = g.__next__()
        except StopIteration:
            self.assertTrue(True)        
        
    def test_append_mode(self):
        
        def g1():
            yield 1
            yield 2        
        te = self.AppendExtractor()
        g = te.process(g1())
        t = kind.generator_next(g)
        self.assertEqual(t, 1)
        t = kind.generator_next(g)
        self.assertEqual(t, 2)
        t = kind.generator_next(g)
        self.assertEqual(t, 3)
        t = kind.generator_next(g)
        self.assertIsNone(t)        
        
    def test_merge_mode(self):
        def g1():
            yield {'a':1, 'b':2}
            yield {'a':3, 'b':4}

        te = self.MergeExtractor()
        te.init(mode=Extractor.MODE_MERGE)
        g = te.process(g1())
        t = kind.generator_next(g)
        self.assertEqual(t, {'a':1, 'b':2, 'c':8})
        t = kind.generator_next(g)
        self.assertEqual(t, {'a':3, 'b':4, 'c':9})
        t = kind.generator_next(g)
        self.assertIsNone(t)
    
    def test_cross_mode(self):
        def g1():
            yield {'a':1, 'b':2}
            yield {'a':3, 'b':4}
        te = self.CrossExtractor()
        te.init(mode=Extractor.MODE_CROSS)
        g = te.process(g1())
        t = kind.generator_next(g)
        self.assertEqual(t, {'a':1, 'b':2, 'c':8, 'd':10})
        t = kind.generator_next(g)
        self.assertEqual(t, {'a':1, 'b':2, 'c':9, 'd':11})
        t = kind.generator_next(g)
        self.assertEqual(t, {'a':3, 'b':4, 'c':8, 'd':10})
        t = kind.generator_next(g)
        self.assertEqual(t, {'a':3, 'b':4, 'c':9, 'd':11})
        t = kind.generator_next(g)
        self.assertIsNone(t)
        
    def test_mix_mode(self):
        def g1():
            yield {'a':1, 'b':2}
            yield {'a':3, 'b':4}
        te = self.MixExtractor()
        te.init(mode=Extractor.MODE_MIX)
        g = te.process(g1())
        t = kind.generator_next(g)
        self.assertEqual(t, {'a':1, 'b':2})
        t = kind.generator_next(g)
        self.assertEqual(t, {'c':8, 'd':10})
        t = kind.generator_next(g)
        self.assertEqual(t, {'a':3, 'b':4})
        t = kind.generator_next(g)
        self.assertEqual(t, {'c': 9, 'd': 11})
        t = kind.generator_next(g)
        self.assertIsNone(t)
