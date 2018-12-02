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

from ssguan.ignitor.audit import service as audit_service
from ssguan.ignitor.orm import dbpool, config as orm_config, update
from ssguan.ignitor.sched import scheduler
from ssguan.ignitor.sched.cronjob import CJRunner, CronJob, CJRunLog
from ssguan.ignitor.sched.error import CronExprError, CJNotSavedError
from ssguan.ignitor.utility import  kind


class CJRunner1(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunner1, self).__init__(cronjob)
        
    def run(self, run_params, cjrunlog, caller):        
        print("runonce")
    
    
class CJRunnerR1(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerR1, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        cjrunlog.update_progress("22.3", "22.dddd", caller)

class CJRunnerFail(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerFail, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        1 / 0

class CronJobTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
        update.install()
        update.upgrade('ignitor.audit')
        update.upgrade('ignitor.sched')        
        
    def setUp(self):
        self.timezone = kind.tz_china()
    
    def assertDtEqual(self, cronjob, previous_time, now_time, correct_time):
        next_time = cronjob.get_next_fire_time(previous_time, now_time)
        self.assertEqual(next_time , correct_time)
        
    def new_datetime(self, year, month, day, hour=0, minute=0, second=0, tzinfo=kind.tz_utc()):
        dt = datetime.datetime(year, month, day, hour=hour, minute=minute, second=second, tzinfo=tzinfo)
        utcdt = kind.local_to_utc(dt)
        return kind.utc_to_local(utcdt, tzinfo)
    
    def test_cronjob_fire_year(self):
        cronjob = scheduler.create_cronjob("job1", "job1", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5")
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 12, 1), self.new_datetime(2009, 1, 5))
        self.assertDtEqual(cronjob, self.new_datetime(2009, 1, 5), self.new_datetime(2009, 12, 1), self.new_datetime(2011, 1, 5))
        cronjob.fire_year = "2009-2011"
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 12, 1) , self.new_datetime(2009, 1, 5))
        self.assertDtEqual(cronjob, self.new_datetime(2009, 1, 5), self.new_datetime(2010, 1, 1) , self.new_datetime(2010, 1, 5))
        self.assertDtEqual(cronjob, self.new_datetime(2010, 1, 5), self.new_datetime(2010, 2, 1) , self.new_datetime(2011, 1, 5))
        self.assertDtEqual(cronjob, self.new_datetime(2011, 1, 5), self.new_datetime(2011, 2, 1) , None)
        cronjob.fire_year = "2019,2021"
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 12, 1) , self.new_datetime(2019, 1, 5))
        self.assertDtEqual(cronjob, None, self.new_datetime(2019, 1, 5) , self.new_datetime(2019, 1, 5))
        self.assertDtEqual(cronjob, None, self.new_datetime(2019, 1, 6) , self.new_datetime(2021, 1, 5))
        self.assertDtEqual(cronjob, self.new_datetime(2019, 8, 6), self.new_datetime(2020, 1, 6) , self.new_datetime(2021, 1, 5))

    def test_cronjob_fire_month(self):
        cronjob = scheduler.create_cronjob("jobmon", "jobmon", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="2/5",
                                          fire_day="5")
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 1, 1), self.new_datetime(2008, 2, 5))
        self.assertDtEqual(cronjob, self.new_datetime(2008, 1, 5), self.new_datetime(2007, 1, 1), self.new_datetime(2007, 2, 5))
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 2, 1), self.new_datetime(2008, 2, 5))
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 2, 6), self.new_datetime(2008, 7, 5))
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 8, 6), self.new_datetime(2008, 12, 5))
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 12, 6), self.new_datetime(2009, 2, 5))
        cronjob.fire_month = "3-10"
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 10, 6), self.new_datetime(2009, 3, 5))
        cronjob.fire_month = "3-10,1-2"
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 10, 6), self.new_datetime(2009, 1, 5))

    def test_cronjob_fire_day(self):
        cronjob = scheduler.create_cronjob("jobday", "jobday", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="5",
                                          fire_day="5")
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 1, 1), self.new_datetime(2008, 5, 5))
        self.assertDtEqual(cronjob, None, self.new_datetime(2008, 6, 1), self.new_datetime(2009, 5, 5))
        self.assertDtEqual(cronjob, self.new_datetime(2006, 6, 1), self.new_datetime(2008, 6, 1), self.new_datetime(2007, 5, 5))
        self.assertDtEqual(cronjob, self.new_datetime(2008, 8, 1), self.new_datetime(2006, 6, 1), self.new_datetime(2007, 5, 5))
        cronjob.fire_month = "*"
        cronjob.fire_day = "5/8"
        self.assertDtEqual(cronjob, self.new_datetime(2008, 8, 1), self.new_datetime(2006, 6, 6), self.new_datetime(2006, 6, 13))
        self.assertDtEqual(cronjob, self.new_datetime(2006, 6, 13), self.new_datetime(2006, 6, 20), self.new_datetime(2006, 6, 21))
        self.assertDtEqual(cronjob, self.new_datetime(2006, 6, 24), self.new_datetime(2006, 6, 25), self.new_datetime(2006, 6, 29))
        self.assertDtEqual(cronjob, self.new_datetime(2006, 6, 30), self.new_datetime(2006, 6, 30), self.new_datetime(2006, 7, 5))
        cronjob.fire_day = "5-8"
        self.assertDtEqual(cronjob, self.new_datetime(2006, 6, 7), self.new_datetime(2006, 6, 30), self.new_datetime(2006, 6, 8))
        self.assertDtEqual(cronjob, self.new_datetime(2006, 6, 8), self.new_datetime(2006, 6, 30), self.new_datetime(2006, 7, 5))
        
    def test_cronjob_fire_dayofweek(self):
        cronjob = scheduler.create_cronjob("jobdayofweek", "jobdayofweek", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="5",
                                          fire_day="5",
                                          fire_dayofweek="3")
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6), self.new_datetime(2011, 5, 5))
        cronjob.fire_month = "*"
        cronjob.fire_day = "*"
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 6, 6), self.new_datetime(2016, 6, 9))
        cronjob.fire_dayofweek = "3/3"
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 6, 6), self.new_datetime(2016, 6, 9))
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 6, 10), self.new_datetime(2016, 6, 12))
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 6, 13), self.new_datetime(2016, 6, 16))
    
    def test_cronjob_fire_week(self):
        cronjob = scheduler.create_cronjob("jobweek", "jobweek", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_week="3",
                                          fire_day="*")
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 1, 6), self.new_datetime(2016, 1, 18))
        cronjob.fire_week = '8/2'
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 1, 6), self.new_datetime(2016, 2, 22))
    
    def test_cronjob_fire_hour(self):
        cronjob = scheduler.create_cronjob("jobdayofhour", "jobdayofhour", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="0/3")
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2), self.new_datetime(2006, 6, 6, hour=3))
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=4), self.new_datetime(2006, 6, 6, hour=6))
        cronjob.fire_hour = "0-12"
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=13), self.new_datetime(2006, 6, 7, hour=0))
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=9, minute=30), self.new_datetime(2006, 6, 6, hour=10))
        
    def test_cronjob_fire_minute(self):
        cronjob = scheduler.create_cronjob("jobdayofminute", "jobdayofminute", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="2")
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2, minute=1), self.new_datetime(2006, 6, 6, hour=2, minute=2))
        cronjob.fire_minute = "2/5"
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2, minute=53), self.new_datetime(2006, 6, 6, hour=2, minute=57))
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2, minute=59), self.new_datetime(2006, 6, 6, hour=3, minute=2))
        cronjob.fire_minute = "3,10,12,18,19,21"
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2, minute=11), self.new_datetime(2006, 6, 6, hour=2, minute=12))
        self.assertDtEqual(cronjob, self.new_datetime(2006, 6, 6, hour=2, minute=11), self.new_datetime(2006, 6, 6, hour=2, minute=14), self.new_datetime(2006, 6, 6, hour=2, minute=12))
        self.assertDtEqual(cronjob, self.new_datetime(2006, 6, 6, hour=2, minute=22), self.new_datetime(2006, 6, 6, hour=2, minute=28), self.new_datetime(2006, 6, 6, hour=3, minute=3))
    
    def test_cronjob_fire_second(self):
        cronjob = scheduler.create_cronjob("jobdayofsecond", "jobdayofsecond", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="10/5")
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2, minute=1, second=0), self.new_datetime(2006, 6, 6, hour=2, minute=1, second=10))
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2, minute=1, second=11), self.new_datetime(2006, 6, 6, hour=2, minute=1, second=15))
        cronjob.fire_minute = '12'
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2, minute=1, second=11), self.new_datetime(2006, 6, 6, hour=2, minute=12, second=10))
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2, minute=18, second=11), self.new_datetime(2006, 6, 6, hour=3, minute=12, second=10))
        cronjob.fire_month = '5'
        self.assertDtEqual(cronjob, None, self.new_datetime(2006, 6, 6, hour=2, minute=18, second=11), self.new_datetime(2007, 5, 1, hour=0, minute=12, second=10))
        self.assertDtEqual(cronjob, None, self.new_datetime(2007, 5, 6, hour=2, minute=18, second=11), self.new_datetime(2007, 5, 6, hour=3, minute=12, second=10))
        self.assertDtEqual(cronjob, self.new_datetime(2007, 5, 6, hour=3, minute=12, second=23), self.new_datetime(2007, 5, 6, hour=3, minute=12, second=13), self.new_datetime(2007, 5, 6, hour=3, minute=12, second=15))
        cronjob.fire_minute = "1/5"
        cronjob.fire_second = "2/6"
        cronjob.fire_month = "*"
        cronjob.fire_day = "*"
        cronjob.fire_hour = "*"
        self.assertDtEqual(cronjob, None, self.new_datetime(2007, 5, 6, hour=3, minute=12, second=13), self.new_datetime(2007, 5, 6, hour=3, minute=16, second=2))
        self.assertDtEqual(cronjob, None, self.new_datetime(2007, 5, 6, hour=3, minute=16, second=13), self.new_datetime(2007, 5, 6, hour=3, minute=16, second=14))
        cronjob.fire_hour = "1/3"
        self.assertDtEqual(cronjob, None, self.new_datetime(2007, 5, 6, hour=3, minute=16, second=13), self.new_datetime(2007, 5, 6, hour=4, minute=1, second=2))
        self.assertDtEqual(cronjob, None, self.new_datetime(2007, 5, 6, hour=4, minute=17, second=13), self.new_datetime(2007, 5, 6, hour=4, minute=21, second=2))
        self.assertDtEqual(cronjob, None, self.new_datetime(2007, 5, 6, hour=4, minute=22, second=22), self.new_datetime(2007, 5, 6, hour=4, minute=26, second=2))
        self.assertDtEqual(cronjob, None, self.new_datetime(2007, 5, 6, hour=4, minute=26, second=22), self.new_datetime(2007, 5, 6, hour=4, minute=26, second=26))
    
    def test_cronjob_start_end_time(self):
        cronjob = scheduler.create_cronjob("jobdayofstartend", "jobdayofstartend", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="10/5",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=self.new_datetime(2016, 10, 20))
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 5, 6), self.new_datetime(2016, 10, 8, second=10))
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 10, 12, second=24), self.new_datetime(2016, 10, 12, second=25))
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 10, 19, hour=0, minute=0, second=54), self.new_datetime(2016, 10, 19, second=55))
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 10, 19, hour=23, minute=59, second=57), None)
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 10, 21, second=24), None)
        
    def test_cronjob_get_fire_period(self):
        cronjob = scheduler.create_cronjob("jobfireperiod", "jobfireperiod", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="10/5",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=self.new_datetime(2016, 10, 20))
        (st, et, tz) = cronjob.get_fire_period()
        self.assertEqual(st, self.new_datetime(2016, 10, 8))
        self.assertEqual(et, self.new_datetime(2016, 10, 20))
        self.assertEqual(tz, kind.tz_utc())
        cronjob.start_time = self.new_datetime(2018, 1, 1, hour=2, tzinfo=kind.tz_china())
        cronjob.end_time = self.new_datetime(2018, 8, 1, hour=2, tzinfo=kind.tz_china())
        cronjob.update(None)
        (st, et, tz) = cronjob.get_fire_period()
        self.assertEqual(st, self.new_datetime(2018, 1, 1, hour=2))
        self.assertEqual(et, self.new_datetime(2018, 8, 1, hour=2))
        self.assertEqual(tz, kind.tz_utc())
        cronjob.timezone = kind.tz_china()
        cronjob.start_time = self.new_datetime(2018, 1, 1, hour=2)
        cronjob.end_time = self.new_datetime(2018, 8, 1, hour=2)
        cronjob.update(None)
        (st, et, tz) = cronjob.get_fire_period()
        self.assertEqual(tz, kind.tz_china())
        self.assertEqual(st, self.new_datetime(2018, 1, 1, hour=2, tzinfo=kind.tz_china()))
        self.assertEqual(et, self.new_datetime(2018, 8, 1, hour=2, tzinfo=kind.tz_china()))
        
    def test_cronjob_timezone(self):
        cronjob = scheduler.create_cronjob("jobtimezone", "jobtimezone", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="10/5",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=self.new_datetime(2016, 10, 20),
                                          timezone=kind.tz_china())
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 10, 9, hour=2, tzinfo=kind.tz_china()), self.new_datetime(2016, 10, 8, hour=18, second=10, tzinfo=kind.tz_utc()))
        cronjob.fire_hour = "2/5"
        cronjob.fire_second = "*"
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 10, 9, hour=3, tzinfo=kind.tz_china()), self.new_datetime(2016, 10, 8, hour=23, tzinfo=kind.tz_utc()))
        self.assertDtEqual(cronjob, self.new_datetime(2016, 10, 19, hour=23, minute=35, tzinfo=kind.tz_china()), self.new_datetime(2016, 10, 19, hour=23, tzinfo=kind.tz_china()), None)
        self.assertDtEqual(cronjob, self.new_datetime(2016, 10, 18, hour=23, minute=35, tzinfo=kind.tz_china()), self.new_datetime(2016, 10, 19, hour=23, tzinfo=kind.tz_china()), self.new_datetime(2016, 10, 19, hour=2, minute=0, tzinfo=kind.tz_china()))
        self.assertDtEqual(cronjob, self.new_datetime(2016, 10, 18, hour=10, minute=35, tzinfo=kind.tz_utc()), self.new_datetime(2016, 10, 19, hour=23, tzinfo=kind.tz_china()), self.new_datetime(2016, 10, 18, hour=14, minute=0, tzinfo=kind.tz_utc()))
        self.assertDtEqual(cronjob, self.new_datetime(2016, 10, 18, hour=10, minute=35, tzinfo=kind.tz_utc()), self.new_datetime(2016, 10, 19, hour=23, tzinfo=kind.tz_china()), self.new_datetime(2016, 10, 18, hour=22, minute=0, tzinfo=kind.tz_china()))
    
    def test_cronjob_wrongexpr(self):
        cronjob = scheduler.create_cronjob("jobwrongexpr", "jobwrongexpr", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="10/5",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=self.new_datetime(2016, 10, 20),
                                          timezone=kind.tz_china())
        try:
            cronjob.fire_year = "1--33"
            cronjob.get_next_fire_time(None, kind.utcnow())
            self.assertTrue(False)
        except CronExprError:
            self.assertTrue(True)
        cronjob.fire_second = "-1"
        try:
            self.assertDtEqual(cronjob, self.new_datetime(2006, 6, 8), self.new_datetime(2006, 6, 30), self.new_datetime(2006, 7, 5))
            self.assertFalse(True)
        except CronExprError:
            self.assertTrue(True)
    
    def test_cronjob_changelog(self):
        cronjob = scheduler.create_cronjob("jobchangelog", "jobchangelog", "tests.ignitor.sched.cronjob_test.CJRunner1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="10/5",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=self.new_datetime(2016, 10, 20),
                                          timezone=kind.tz_china())
        cronjob.fire_year = "2008"
        cronjob.fire_month = "1"
        cronjob.fire_day = "1"
        cronjob.fire_hour = "2"
        cronjob.fire_minute = "2"
        cronjob.fire_second = "3"
        cronjob.fire_dayofweek = "3"
        cronjob.fire_week = "2"
        cronjob.job_name = "adasdf"
        cronjob.job_group = "aaaaaa"
        cronjob.job_desc = "adffffasdf"
        cronjob.job_node = "aaaaa"
        cronjob.job_runner = "tests.ignitor.sched.cronjob_test.CJRunnerR1"
        cronjob.run_params = {"run_params":"a"}
        cronjob.broken = True
        cronjob.singleton = False        
        cronjob.start_time = kind.utcnow()
        cronjob.end_time = kind.utcnow()
        cronjob.timezone = kind.tz_china()
        cronjob.update(None)
        mclogs = audit_service.fetch_mclogs(CronJob.get_modelname(), cronjob.key())
        self.assertEqual(len(mclogs), 1)
        mclog = mclogs[0]
        self.assertEqual(len(mclog.change_props), 18)
        cronjob.timezone = kind.tz_utc()
        cronjob.update(None)
        mclogs = audit_service.fetch_mclogs(CronJob.get_modelname(), cronjob.key())
        self.assertEqual(len(mclogs), 2)
        cronjob.logged = False        
        cronjob.update(None)
        mclogs = audit_service.fetch_mclogs(CronJob.get_modelname(), cronjob.key())
        self.assertEqual(len(mclogs), 3)
    
    def test_cronjob_run_once(self):
        cronjob = scheduler.create_cronjob("jobrunonce", "jobrunonce", "tests.ignitor.sched.cronjob_test.CJRunnerR1", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/8",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=None,
                                          timezone=kind.tz_china())
        cronjob.run_once("system2")
        self.assertFalse(cronjob.is_running())
        self.assertIsNotNone(cronjob.previous_run_time)
        next_run_time = cronjob.get_next_fire_time(cronjob.previous_run_time, kind.utcnow())
        self.assertEqual(cronjob.next_run_time, next_run_time)
        query = CJRunLog.all()
        query.filter("modified_by =", "system2")
        cjrunlog = query.get()
        self.assertEqual(cjrunlog.job_id, cronjob.key())
        self.assertIsNotNone(cjrunlog.start_time)
        self.assertIsNotNone(cjrunlog.end_time)
        self.assertEqual(cjrunlog.run_flag, CronJob.RUN_FLAG_SUCCESS)
        self.assertEqual(len(cjrunlog.run_progress), 1)
        self.assertEqual(cjrunlog.run_progress[0][0], "22.3")
        self.assertEqual(cjrunlog.run_progress[0][1], "22.dddd")
        cronjob.run_params = {"tt":"1a-1"}
        next_run_time = cronjob.get_next_fire_time(cronjob.previous_run_time, kind.utcnow())
        cronjob.run_once("system3")
        self.assertEqual(cronjob.next_run_time, next_run_time)
        cj = CronJob()
        try:
            cj.run_once("s")
            self.assertTrue(False)
        except CJNotSavedError:
            self.assertTrue(True)

    def test_cronjob_run_failure(self):
        cronjob = scheduler.create_cronjob("jobrunfailure", "jobrunfailure", "tests.ignitor.sched.cronjob_test.CJRunnerFail", "cjnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="8/2",
                                          fire_second="*",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=None,
                                          timezone=kind.tz_china())
        cronjob.run_once("sysss")
        self.assertIsNotNone(cronjob.previous_run_time)
        next_run_time = cronjob.get_next_fire_time(cronjob.previous_run_time, kind.utcnow())
        self.assertEqual(cronjob.next_run_time, next_run_time)
        query = CJRunLog.all()
        query.filter("modified_by =", "sysss")
        cjrunlog = query.get()
        self.assertEqual(cjrunlog.job_id, cronjob.key())
        cronjob.run_once("sysss233")
        next_run_time = cronjob.get_next_fire_time(cronjob.previous_run_time, kind.utcnow())
        self.assertEqual(cronjob.next_run_time, next_run_time)
        query = CJRunLog.all()
        query.filter("modified_by =", 'sysss233')
        query.filter("job_id =", cronjob.key())
        cjlog = query.get()
        self.assertEqual(cjlog.run_flag, CronJob.RUN_FLAG_FAILED)
    
    @classmethod
    def tearDownClass(cls):
        dbpool.drop_db(orm_config.get_default_dbinfo())
