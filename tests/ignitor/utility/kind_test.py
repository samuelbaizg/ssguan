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

from ssguan.ignitor.utility import kind
import datetime


class KindTest(unittest.TestCase):
    
    def test_local_to_utc(self):
        x = datetime.datetime(2016, 8, 20, 10, 0, 0, 0, tzinfo=kind.tz_china())
        y = kind.local_to_utc(x)
        self.assertEqual("2016-08-20 02:00:00 UTC", datetime.datetime.strftime(y, "%Y-%m-%d %H:%M:%S %Z"))
        self.assertEqual(y.tzinfo, kind.tz_utc())
        x = datetime.datetime(2016, 8, 20, 10, 0, 0, 0, tzinfo=kind.tz_utc())        
        y = kind.local_to_utc(x)
        self.assertEqual(y.tzinfo, kind.tz_utc())
        self.assertEqual(x,y)
        x = datetime.datetime(2016, 8, 20, 10, 0, 0, 0, tzinfo=None)    
        y = kind.local_to_utc(x)
        self.assertEqual(y.tzinfo, kind.tz_utc())
        y = y.replace(tzinfo=None)
        self.assertEqual(x,y)
        
    def test_utc_to_local(self):
        x = datetime.datetime(2016, 8, 20, 10, 0, 0, 0, tzinfo=kind.tz_utc())
        y = kind.utc_to_local(x, tz=kind.tz_china())
        self.assertEqual("2016-08-20 18:00:00 CST", datetime.datetime.strftime(y, "%Y-%m-%d %H:%M:%S %Z"))
        x = datetime.datetime(2016, 8, 20, 10, 0, 0, 0, tzinfo=kind.tz_china())
        try:
            y = kind.utc_to_local(x, tz=kind.tz_china())
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)
        x = datetime.datetime(2016, 8, 20, 10, 1, 0, 0, tzinfo=None)
        y = kind.utc_to_local(x, tz=kind.tz_china())
        self.assertEqual(str(y.tzinfo), str(kind.tz_china()))
        self.assertEqual("2016-08-20 18:01:00 CST", datetime.datetime.strftime(y, "%Y-%m-%d %H:%M:%S %Z"))     
        
    def test_utcnow(self):
        now = kind.utcnow()
        self.assertEqual(kind.tz_utc(), now.tzinfo)
