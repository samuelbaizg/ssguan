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

from datetime import timedelta
import datetime
import unittest

from tornado.ioloop import IOLoop

from ssguan import config
from ssguan.commons import database, loggingg, typeutils
from ssguan.modules import sysprop, schedule
from ssguan.modules.auth import User
from ssguan.modules.schedule import CJRunner, CronJob, CronExprError, CJRunLog, \
    CJNotSavedError


_logger = loggingg.get_logger("schedule_test_test")

class CJRunner1(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunner1, self).__init__(cronjob)
        
    def run(self, run_params, cjrunlog, caller):        
        print "runonce"
    
    
class CJRunnerR1(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerR1, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        _logger.info("CJRunnerR1===%s===%s", caller, self.cronjob.run_params)
        cjrunlog.update_progress("22.3", "22.dddd", caller)

class CJRunnerFail(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerFail, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        1 / 0

class CJRunnerRALL1(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerRALL1, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        _logger.info("CJRunnerRALL1l===%s===%s", caller, self.cronjob.run_params)
        
class CJRunnerRALL2(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerRALL2, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        _logger.info("CJRunnerRALL22===%s===%s", caller)    

class CJRunnerROnce1(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerROnce1, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        _logger.info("CJRunnerROnce1===%s===%s", caller, self.cronjob.run_params)

class CronJobTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()    
        loggingg.install_module()
        schedule.install_module()
        
    def setUp(self):
        self.timezone = typeutils.tz_china()
    
    def assertDtEqual(self, cronjob, previous_time, now_time, correct_time):
        next_time = cronjob.get_next_fire_time(previous_time, now_time)
        self.assertEqual(next_time , correct_time)
        
    def new_datetime(self, year, month, day, hour=0, minute=0, second=0, tzinfo=typeutils.tz_utc()):
        dt = datetime.datetime(year, month, day, hour=hour, minute=minute, second=second, tzinfo=tzinfo)
        utcdt = typeutils.local_to_utc(dt)
        return typeutils.utc_to_local(utcdt, tzinfo)
    
    def test_cronjob_fire_year(self):
        cronjob = schedule.create_cronjob("job1", "job1", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
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
        cronjob = schedule.create_cronjob("jobmon", "jobmon", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
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
        cronjob = schedule.create_cronjob("jobday", "jobday", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
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
        cronjob = schedule.create_cronjob("jobdayofweek", "jobdayofweek", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
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
        cronjob = schedule.create_cronjob("jobweek", "jobweek", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_week="3",
                                          fire_day="*")
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 1, 6), self.new_datetime(2016, 1, 18))
        cronjob.fire_week = '8/2'
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 1, 6), self.new_datetime(2016, 2, 22))
    
    def test_cronjob_fire_hour(self):
        cronjob = schedule.create_cronjob("jobdayofhour", "jobdayofhour", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
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
        cronjob = schedule.create_cronjob("jobdayofminute", "jobdayofminute", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
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
        cronjob = schedule.create_cronjob("jobdayofsecond", "jobdayofsecond", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
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
        cronjob = schedule.create_cronjob("jobdayofstartend", "jobdayofstartend", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
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
        cronjob = schedule.create_cronjob("jobfireperiod", "jobfireperiod", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
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
        self.assertEqual(tz, typeutils.tz_utc())
        cronjob.start_time = self.new_datetime(2018, 1, 1, hour=2, tzinfo=typeutils.tz_china())
        cronjob.end_time = self.new_datetime(2018, 8, 1, hour=2, tzinfo=typeutils.tz_china())
        cronjob.update(None)
        (st, et, tz) = cronjob.get_fire_period()
        self.assertEqual(st, self.new_datetime(2018, 1, 1, hour=2))
        self.assertEqual(et, self.new_datetime(2018, 8, 1, hour=2))
        self.assertEqual(tz, typeutils.tz_utc())
        cronjob.timezone = typeutils.tz_china()
        cronjob.start_time = self.new_datetime(2018, 1, 1, hour=2)
        cronjob.end_time = self.new_datetime(2018, 8, 1, hour=2)
        cronjob.update(None)
        (st, et, tz) = cronjob.get_fire_period()
        self.assertEqual(tz, typeutils.tz_china())
        self.assertEqual(st, self.new_datetime(2018, 1, 1, hour=2, tzinfo=typeutils.tz_china()))
        self.assertEqual(et, self.new_datetime(2018, 8, 1, hour=2, tzinfo=typeutils.tz_china()))
        
    def test_cronjob_timezone(self):
        cronjob = schedule.create_cronjob("jobtimezone", "jobtimezone", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="10/5",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=self.new_datetime(2016, 10, 20),
                                          timezone=typeutils.tz_china())
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 10, 9, hour=2, tzinfo=typeutils.tz_china()), self.new_datetime(2016, 10, 8, hour=18, second=10, tzinfo=typeutils.tz_utc()))
        cronjob.fire_hour = "2/5"
        cronjob.fire_second = "*"
        self.assertDtEqual(cronjob, None, self.new_datetime(2016, 10, 9, hour=3, tzinfo=typeutils.tz_china()), self.new_datetime(2016, 10, 8, hour=23, tzinfo=typeutils.tz_utc()))
        self.assertDtEqual(cronjob, self.new_datetime(2016, 10, 19, hour=23, minute=35, tzinfo=typeutils.tz_china()), self.new_datetime(2016, 10, 19, hour=23, tzinfo=typeutils.tz_china()), None)
        self.assertDtEqual(cronjob, self.new_datetime(2016, 10, 18, hour=23, minute=35, tzinfo=typeutils.tz_china()), self.new_datetime(2016, 10, 19, hour=23, tzinfo=typeutils.tz_china()), self.new_datetime(2016, 10, 19, hour=2, minute=0, tzinfo=typeutils.tz_china()))
        self.assertDtEqual(cronjob, self.new_datetime(2016, 10, 18, hour=10, minute=35, tzinfo=typeutils.tz_utc()), self.new_datetime(2016, 10, 19, hour=23, tzinfo=typeutils.tz_china()), self.new_datetime(2016, 10, 18, hour=14, minute=0, tzinfo=typeutils.tz_utc()))
        self.assertDtEqual(cronjob, self.new_datetime(2016, 10, 18, hour=10, minute=35, tzinfo=typeutils.tz_utc()), self.new_datetime(2016, 10, 19, hour=23, tzinfo=typeutils.tz_china()), self.new_datetime(2016, 10, 18, hour=22, minute=0, tzinfo=typeutils.tz_china()))
    
    def test_cronjob_wrongexpr(self):
        cronjob = schedule.create_cronjob("jobwrongexpr", "jobwrongexpr", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="10/5",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=self.new_datetime(2016, 10, 20),
                                          timezone=typeutils.tz_china())
        try:
            cronjob.fire_year = "1--33"
            cronjob.get_next_fire_time(None, typeutils.utcnow())
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
        cronjob = schedule.create_cronjob("jobchangelog", "jobchangelog", "tests.modules.schedule_test.CJRunner1", "cjnode1", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="10/5",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=self.new_datetime(2016, 10, 20),
                                          timezone=typeutils.tz_china())
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
        cronjob.job_runner = "tests.modules.schedule_test.CJRunnerR1"
        cronjob.run_params = {"run_params":"a"}
        cronjob.broken = True
        cronjob.singleton = False        
        cronjob.start_time = typeutils.utcnow()
        cronjob.end_time = typeutils.utcnow()
        cronjob.timezone = typeutils.tz_china()
        cronjob.update(None)
        mclogs = loggingg.fetch_mclogs(CronJob.get_modelname(), cronjob.key())
        self.assertEqual(len(mclogs), 1)
        mclog = mclogs[0]
        self.assertEqual(len(mclog.changed_props), 18)
        cronjob.timezone = typeutils.tz_utc()
        cronjob.update(None)
        mclogs = loggingg.fetch_mclogs(CronJob.get_modelname(), cronjob.key())
        self.assertEqual(len(mclogs), 2)
        cronjob.logged = False        
        cronjob.update(None)
        mclogs = loggingg.fetch_mclogs(CronJob.get_modelname(), cronjob.key())
        self.assertEqual(len(mclogs), 3)
    
    def test_cronjob_run_once(self):
        cronjob = schedule.create_cronjob("jobrunonce", "jobrunonce", "tests.modules.schedule_test.CJRunnerR1", "cjnode1", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/8",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=None,
                                          timezone=typeutils.tz_china())
        cronjob.run_once("system2")
        logs = loggingg.fetch_logs(keywords="CJRunnerR1===system2===")
        self.assertEqual(logs.count, 1)
        self.assertFalse(cronjob.is_running())
        self.assertIsNotNone(cronjob.previous_run_time)
        next_run_time = cronjob.get_next_fire_time(cronjob.previous_run_time, typeutils.utcnow())
        self.assertEqual(cronjob.next_run_time, next_run_time)
        query = CJRunLog.all()
        query.filter("modified_by =", "system2")
        cjrunlog = query.get()
        self.assertEqual(cjrunlog.job_id, cronjob.key())
        self.assertIsNotNone(cjrunlog.start_time)
        self.assertIsNotNone(cjrunlog.end_time)
        self.assertEqual(cjrunlog.run_status, CronJob.RUN_STATUS_SUCCESS)
        self.assertEqual(len(cjrunlog.run_progress), 1)
        self.assertEqual(cjrunlog.run_progress[0][0], "22.3")
        self.assertEqual(cjrunlog.run_progress[0][1], "22.dddd")
        cronjob.run_params = {"tt":"1a-1"}
        next_run_time = cronjob.get_next_fire_time(cronjob.previous_run_time, typeutils.utcnow())
        cronjob.run_once("system3")
        self.assertEqual(cronjob.next_run_time, next_run_time)
        logs = loggingg.fetch_logs(keywords="CJRunnerR1===system3==={'tt': '1a-1'}")
        self.assertEqual(logs.count, 1)
        cj = CronJob()
        try:
            cj.run_once("s")
            self.assertTrue(False)
        except CJNotSavedError:
            self.assertTrue(True)

    def test_cronjob_run_failure(self):
        cronjob = schedule.create_cronjob("jobrunfailure", "jobrunfailure", "tests.modules.schedule_test.CJRunnerFail", "cjnode1", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="8/2",
                                          fire_second="*",
                                          start_time=self.new_datetime(2016, 10, 8),
                                          end_time=None,
                                          timezone=typeutils.tz_china())
        cronjob.run_once("sysss")
        self.assertIsNotNone(cronjob.previous_run_time)
        next_run_time = cronjob.get_next_fire_time(cronjob.previous_run_time, typeutils.utcnow())
        self.assertEqual(cronjob.next_run_time, next_run_time)
        query = CJRunLog.all()
        query.filter("modified_by =", "sysss")
        cjrunlog = query.get()
        self.assertEqual(cjrunlog.job_id, cronjob.key())
        cronjob.run_once("sysss233")
        next_run_time = cronjob.get_next_fire_time(cronjob.previous_run_time, typeutils.utcnow())
        self.assertEqual(cronjob.next_run_time, next_run_time)
        query = CJRunLog.all()
        query.filter("modified_by =", 'sysss233')
        query.filter("job_id =", cronjob.key())
        cjlog = query.get()
        self.assertEqual(cjlog.run_status, CronJob.RUN_STATUS_FAILED)
    
    def test_create_cronjob(self):
        cronjob = schedule.create_cronjob("jobcreate", "jobcredeeate", "tests.modules.schedule_test.CJRunner1", "cjnode1cc", User.ID_ROOT,
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        self.assertEqual(cronjob.fire_year, "2009/2")
        self.assertEqual(cronjob.fire_hour, "2-3")
        self.assertEqual(cronjob.fire_minute, "*")
        self.assertEqual(cronjob.fire_second, 0)
        self.assertEqual(cronjob.job_desc, "jobcredeeate")
        self.assertEqual(cronjob.job_group, None)
        self.assertEqual(cronjob.job_node, "cjnode1cc")
        cronjob = schedule.create_cronjob("jobcreate2", "jobcredeeate2", "tests.modules.schedule_test.CJRunner1", "cjnode1cc", User.ID_ROOT,
                                          job_group="deadadf", logged=False)
        self.assertIsNotNone(cronjob.next_run_time)
        self.assertEqual(cronjob.job_group, "deadadf")
        self.assertFalse(cronjob.logged)        
        self.assertEqual(cronjob.job_node, "cjnode1cc")
        
    
    def test_delete_cronjob(self):
        cronjob = schedule.create_cronjob("jobde", "jobde", "tests.modules.schedule_test.CJRunner1", "cjnode1cc", User.ID_ROOT,
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        schedule.delete_cronjob(cronjob.key(), User.ID_ROOT)
        job = schedule.get_cronjob(User.ID_ROOT, job_id=cronjob.key())
        self.assertIsNone(job)
        
    def test_get_cronjob(self):
        cronjob = schedule.create_cronjob("jobdeccc", "jobdeeeee", "tests.modules.schedule_test.CJRunner1", "cjnode1cc", User.ID_ROOT,
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        job2 = schedule.get_cronjob(User.ID_ROOT, job_id=cronjob.key())
        self.assertEqual(job2.job_name, cronjob.job_name)
        job2 = schedule.get_cronjob(User.ID_ROOT, job_name="jobdeccc")
        self.assertEqual(job2.job_name, cronjob.job_name)
        self.assertEqual(job2.key(), cronjob.key())
    
    def test_break_cronjob(self):
        cronjob = schedule.create_cronjob("cjnode1bre", "cjnode1bre", "tests.modules.schedule_test.CJRunner1", "cjnode1bre", User.ID_ROOT,
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        job = schedule.break_cronjob(cronjob.key(), True, User.ID_ROOT)
        self.assertTrue(job.broken)
        job = schedule.break_cronjob(cronjob.key(), False, User.ID_ROOT)
        self.assertFalse(job.broken)
    
    def test_fetch_cronjobs(self):
        query = CronJob.all()
        query.delete(None)
        schedule.create_cronjob("cjnodefetchcjs", "cjnodefetchcjs", "tests.modules.schedule_test.CJRunner1", "cjnodefetchcjs", User.ID_ROOT,
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        schedule.create_cronjob("2fffasdf22", "cjnodefetc22hcjs2", "tests.modules.schedule_test.CJRunner1", "cjnodefetchcjs", User.ID_ROOT,
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*", broken=True)
        schedule.create_cronjob("fa2e32323", "22323", "tests.modules.schedule_test.CJRunner1", "cjnodefetchcjs", User.ID_ROOT,
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        schedule.create_cronjob("fa2e3aad2323", "2ddd2323", "tests.modules.schedule_test.CJRunner1", "cjnodefetchcjs222", User.ID_ROOT,
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        cj = schedule.create_cronjob("3222323fff", "asdfdf", "tests.modules.schedule_test.CJRunner1", "cjnodefetchcjs222", User.ID_ROOT,
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        cjs = schedule.fetch_cronjobs(User.ID_ROOT)
        self.assertEqual(len(cjs), 5)
        cjs = schedule.fetch_cronjobs(User.ID_ROOT, job_name='cjnodefetchc')
        self.assertEqual(len(cjs), 1)
        cjs = schedule.fetch_cronjobs(User.ID_ROOT, job_node="cjnodefetchcjs222")
        self.assertEqual(len(cjs), 2)
        cjs = schedule.fetch_cronjobs(User.ID_ROOT, job_node="cjnodefetchcjs222", broken=True)
        self.assertEqual(len(cjs), 0)
        cj.broken = True
        cj.update(None)
        cjs = schedule.fetch_cronjobs(User.ID_ROOT, job_node="cjnodefetchcjs222", broken=True)
        self.assertEqual(len(cjs), 1)
        
    def test_scheduler_new(self):
        cjnode1 = schedule.Scheduler("cjnodenew1")
        cjnode12 = schedule.Scheduler("cjnodenew1")        
        self.assertEqual(cjnode1, cjnode12)
        self.assertEqual(cjnode12._node, "cjnodenew1")
        cjnode2 = schedule.Scheduler("cjnodenew2")
        self.assertNotEqual(cjnode1, cjnode2)
        self.assertEqual(cjnode2._node, "cjnodenew2")
        
    def test_scheduler_run_all(self):
        cj1 = schedule.create_cronjob("runall1", "runall1", "tests.modules.schedule_test.CJRunnerRALL1", "runallnode1", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/5")
        cj2 = schedule.create_cronjob("runall2", "runall2", "tests.modules.schedule_test.CJRunnerRALL2", "runallnode1", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/3",
                                          broken=True)
        schedule.create_cronjob("runall3", "runall3", "tests.modules.schedule_test.CJRunnerRALL2", "runallnode2", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/2")
        def update_next_time():
            q1 = cj1.all()
            q1.filter("_id =", cj1.key())
            q1.set("next_run_time", typeutils.utcnow() - timedelta(seconds=10))
            q1.update(None)        
            q2 = cj1.all()
            q2.filter("_id =", cj2.key())
            q2.set("next_run_time", typeutils.utcnow() - timedelta(seconds=12))
            q2.update(None)
        update_next_time()        
        scher = schedule.Scheduler("runallnode1")
        scher.run_all(None,broken=False)
        logs = loggingg.fetch_logs(keywords="CJRunnerRALL")
        self.assertEqual(logs.count, 1)
        schedule.break_cronjob(cj2.key(), False, User.ID_ROOT)
        update_next_time()
        scher.run_all(None)
        logs = loggingg.fetch_logs(keywords="CJRunnerRALL")
        self.assertEqual(logs.count, 3)
        logs = loggingg.fetch_logs(keywords="CJRunnerRALL22")
        self.assertEqual(logs.count, 1)
        
    def test_scheduler_run_once(self):
        cj1 = schedule.create_cronjob("runonce1", "runonce1", "tests.modules.schedule_test.CJRunnerROnce1", "runallnode222", User.ID_ROOT,
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/5")
        scher = schedule.Scheduler("runallnode222")
        scher.run_once(cj1.key(),None)
        logs = loggingg.fetch_logs(keywords="CJRunnerROnce1")
        self.assertEqual(logs.count, 1)
        scher.run_once(cj1.key(),None)
        scher.run_once(cj1.key(),None)
        logs = loggingg.fetch_logs(keywords="CJRunnerROnce1")
        self.assertEqual(logs.count, 3)
    
    def test_scheduler_running(self):
        cjnode1 = schedule.Scheduler("cjnodenew1")
        self.assertFalse(cjnode1.is_running())
        cjnode12 = schedule.Scheduler("cjnodenew1")
        self.assertFalse(cjnode12.is_running())
        io_loop = IOLoop.current()
        def assert_running():
            self.assertTrue(cjnode1.is_running())
            self.assertTrue(cjnode12.is_running())
        io_loop.call_later(0.1, assert_running)
        io_loop.call_later(0.2, io_loop.stop)
        cjnode1.start(1, io_loop=io_loop)
        self.assertTrue(cjnode1.is_running())
        self.assertTrue(cjnode12.is_running())
        cjnode1.stop()
        self.assertFalse(cjnode1.is_running())
        self.assertFalse(cjnode12.is_running())
    
    @classmethod
    def tearDownClass(cls):
        loggingg.uninstall_module()
        schedule.uninstall_module()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())        
