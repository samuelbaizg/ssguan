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

import datetime
import unittest

from ssguan.ignitor.etl import service as etl_service
from ssguan.ignitor.orm import dbpool, config as orm_config, update
from ssguan.ignitor.utility import kind
from ssguan.ignitor.base.error import NoFoundError


class ETLService(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
        update.install()
        update.upgrade('ignitor.etl')
    
    def test_get_extract_timespan(self):
        # test first
        first_time = kind.local_to_utc(datetime.datetime(2018, 1, 1, 0, 0, 10))
        start_time , end_time = etl_service.get_extract_timespan("aaa", "de/f.a", first_time=first_time, start_delta=10, end_delta=5)
        should_start = first_time - datetime.timedelta(seconds=10)
        should_end = kind.datetime_floor(kind.utcnow() - datetime.timedelta(seconds=5))
        self.assertEqual(start_time, should_start)
        self.assertEqual(end_time, should_end)
        # test second
        start_time2 , end_time2 = etl_service.get_extract_timespan("aaa", "de/f.a")
        should_end2 = kind.utcnow() - datetime.timedelta(seconds=5)
        should_end2 = kind.datetime_floor(should_end2)
        self.assertEqual(start_time2, should_start)        
        self.assertEqual(end_time2, should_end2)
        # test after update last time of db
        etl_service.update_last_extr_time('aaa', end_time2)
        start_time3 , end_time3 = etl_service.get_extract_timespan("aaa", "de/f.a")
        should_start = should_end2 - datetime.timedelta(seconds=10)
        
        self.assertEqual(start_time3, should_start)
        should_end3 = kind.utcnow() - datetime.timedelta(seconds=5)
        should_end3 = kind.datetime_floor(should_end3)        
        self.assertEqual(end_time3, should_end3)
    
    def test_update_last_extr_time(self):
        try:
            etl_service.update_last_extr_time("ccc", kind.local_to_utc(datetime.datetime(2018, 5, 1, 0, 0, 10)))
            self.assertTrue(False)
        except NoFoundError:
            pass
        first_time = kind.local_to_utc(datetime.datetime(2018, 5, 1, 0, 0, 10))
        etl_service.get_extract_timespan("bbb", "def/fc.a", first_time=first_time, start_delta=8, end_delta=5)
        end_time = kind.local_to_utc(datetime.datetime(2018, 7, 1, 0, 0, 10))
        etl_service.update_last_extr_time("bbb", end_time)
        start_time  = etl_service.get_extract_timespan("bbb", "def/fc.a", first_time=first_time, start_delta=7, end_delta=5)[0]
        should_start = kind.local_to_utc(datetime.datetime(2018, 7, 1, 0, 0, 2))
        self.assertEqual(start_time, should_start)
    
    @classmethod
    def tearDownClass(cls):        
        dbpool.drop_db(orm_config.get_default_dbinfo())
