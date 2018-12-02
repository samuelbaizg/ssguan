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
import unittest

from tornado.ioloop import IOLoop

from ssguan.ignitor.orm import dbpool, config as orm_config, update
from ssguan.ignitor.sched import scheduler
from ssguan.ignitor.sched.cronjob import CronJob, CJRunner
from ssguan.ignitor.utility import  kind


class CJRunner1(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunner1, self).__init__(cronjob)
        
    def run(self, run_params, cjrunlog, caller):        
        print("runonce")

class CJRunnerRALL1(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerRALL1, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        '_logger.info("CJRunnerRALL1l===%s===%s", caller, self.cronjob.run_params)'
        
class CJRunnerRALL2(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerRALL2, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        '_logger.info("CJRunnerRALL22===%s===%s", caller)'    

class CJRunnerROnce1(CJRunner):
    
    def __init__(self, cronjob):
        super(CJRunnerROnce1, self).__init__(cronjob)
        
    def run(self, cjrunlog, caller):        
        '_logger.info("CJRunnerROnce1===%s===%s", caller, self.cronjob.run_params)'

class SchedulerTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
        update.install()
        update.upgrade('ignitor.audit')
        update.upgrade('ignitor.sched')
        
    def test_create_cronjob(self):
        cronjob = scheduler.create_cronjob("jobcreate", "jobcredeeate", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnode1cc",
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
        cronjob = scheduler.create_cronjob("jobcreate2", "jobcredeeate2", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnode1cc",
                                          job_group="deadadf", logged=False)
        self.assertIsNotNone(cronjob.next_run_time)
        self.assertEqual(cronjob.job_group, "deadadf")
        self.assertFalse(cronjob.logged)        
        self.assertEqual(cronjob.job_node, "cjnode1cc")
        
    
    def test_delete_cronjob(self):
        cronjob = scheduler.create_cronjob("jobde", "jobde", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnode1cc",
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        scheduler.delete_cronjob(cronjob.key())
        job = scheduler.get_cronjob(job_id=cronjob.key())
        self.assertIsNone(job)
        
    def test_get_cronjob(self):
        cronjob = scheduler.create_cronjob("jobdeccc", "jobdeeeee", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnode1cc",
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        job2 = scheduler.get_cronjob(job_id=cronjob.key())
        self.assertEqual(job2.job_name, cronjob.job_name)
        job2 = scheduler.get_cronjob(job_name="jobdeccc")
        self.assertEqual(job2.job_name, cronjob.job_name)
        self.assertEqual(job2.key(), cronjob.key())
    
    def test_break_cronjob(self):
        cronjob = scheduler.create_cronjob("cjnode1bre", "cjnode1bre", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnode1bre",
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        job = scheduler.break_cronjob(cronjob.key(), True)
        self.assertTrue(job.broken)
        job = scheduler.break_cronjob(cronjob.key(), False)
        self.assertFalse(job.broken)
    
    def test_fetch_cronjobs(self):
        query = CronJob.all()
        query.delete(None)
        scheduler.create_cronjob("cjnodefetchcjs", "cjnodefetchcjs", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnodefetchcjs",
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        scheduler.create_cronjob("2fffasdf22", "cjnodefetc22hcjs2", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnodefetchcjs",
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*", broken=True)
        scheduler.create_cronjob("fa2e32323", "22323", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnodefetchcjs",
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        scheduler.create_cronjob("fa2e3aad2323", "2ddd2323", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnodefetchcjs222",
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        cj = scheduler.create_cronjob("3222323fff", "asdfdf", "tests.ignitor.sched.scheduler_test.CJRunner1", "cjnodefetchcjs222",
                                          fire_year="2009/2",
                                          fire_month="1",
                                          fire_day="5",
                                          fire_hour="2-3",
                                          fire_minute="*")
        cjs = scheduler.fetch_cronjobs()
        self.assertEqual(len(cjs), 5)
        cjs = scheduler.fetch_cronjobs(job_name='cjnodefetchc')
        self.assertEqual(len(cjs), 1)
        cjs = scheduler.fetch_cronjobs(job_node="cjnodefetchcjs222")
        self.assertEqual(len(cjs), 2)
        cjs = scheduler.fetch_cronjobs(job_node="cjnodefetchcjs222", broken=True)
        self.assertEqual(len(cjs), 0)
        cj.broken = True
        cj.update(None)
        cjs = scheduler.fetch_cronjobs(job_node="cjnodefetchcjs222", broken=True)
        self.assertEqual(len(cjs), 1)
        
    def test_scheduler_new(self):
        cjnode1 = scheduler.Scheduler("cjnodenew1")
        cjnode12 = scheduler.Scheduler("cjnodenew1")        
        self.assertEqual(cjnode1, cjnode12)
        self.assertEqual(cjnode12._node, "cjnodenew1")
        cjnode2 = scheduler.Scheduler("cjnodenew2")
        self.assertNotEqual(cjnode1, cjnode2)
        self.assertEqual(cjnode2._node, "cjnodenew2")
        
    def test_scheduler_run_all(self):
        cj1 = scheduler.create_cronjob("runall1", "runall1", "tests.ignitor.sched.scheduler_test.CJRunnerRALL1", "runallnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/5")
        cj2 = scheduler.create_cronjob("runall2", "runall2", "tests.ignitor.sched.scheduler_test.CJRunnerRALL2", "runallnode1",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/3",
                                          broken=True)
        scheduler.create_cronjob("runall3", "runall3", "tests.ignitor.sched.scheduler_test.CJRunnerRALL2", "runallnode2",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/2")
        def update_next_time():
            q1 = cj1.all()
            q1.filter("_id =", cj1.key())
            q1.set("next_run_time", kind.utcnow() - timedelta(seconds=10))
            q1.update(None)        
            q2 = cj1.all()
            q2.filter("_id =", cj2.key())
            q2.set("next_run_time", kind.utcnow() - timedelta(seconds=12))
            q2.update(None)
        update_next_time()        
        scher = scheduler.Scheduler("runallnode1")
        scher.run_all(None, broken=False)
        scheduler.break_cronjob(cj2.key(), False)
        update_next_time()
        scher.run_all(None)
        
    def test_scheduler_run_once(self):
        cj1 = scheduler.create_cronjob("runonce1", "runonce1", "tests.ignitor.sched.scheduler_test.CJRunnerROnce1", "runallnode222",
                                          fire_year="*",
                                          fire_month="*",
                                          fire_day="*",
                                          fire_hour="*",
                                          fire_minute="*",
                                          fire_second="0/5")
        scher = scheduler.Scheduler("runallnode222")
        scher.run_once(cj1.key(), None)
        scher.run_once(cj1.key(), None)
        scher.run_once(cj1.key(), None)
    
    def test_scheduler_running(self):
        cjnode1 = scheduler.Scheduler("cjnodenew1")
        self.assertFalse(cjnode1.is_running())
        cjnode12 = scheduler.Scheduler("cjnodenew1")
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
        dbpool.drop_db(orm_config.get_default_dbinfo())