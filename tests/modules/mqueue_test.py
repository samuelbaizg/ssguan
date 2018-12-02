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

from ssguan import config
from ssguan.commons import  database, loggingg, error, typeutils
from ssguan.commons.dao import UniqueError
from ssguan.commons.error import NoFoundError
from ssguan.modules import sysprop, mqueue, schedule
from ssguan.modules.auth import User
from ssguan.modules.mqueue import QTRunner, WrongRunParamError


_logger = loggingg.get_logger("mqueue_test_test")

class QTRunner1(QTRunner):
    
    def __init__(self, cronjob):
        super(QTRunner1, self).__init__(cronjob)
        
    def do(self, qtask):
        _logger.info("qtrunner1___do_____%s", qtask.payload)
        if str(qtask.payload) != 'eee':
            raise AssertionError("qtask is not the expected one.")

class QTRunner2(QTRunner):
    
    def __init__(self, cronjob):
        super(QTRunner2, self).__init__(cronjob)
        
    def do(self, qtask):
        _logger.info("QTRunner2===%s", qtask.payload)  

class QTRunnerError(QTRunner):
    
    def __init__(self, cronjob):
        super(QTRunnerError, self).__init__(cronjob)
        
    def do(self, qtask):
        raise error.RunError("error of qtask")

class MQueueTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module() 
        loggingg.install_module()
        mqueue.install_module()
        schedule.install_module()
           
    def test_new_queue(self):
        q = mqueue.create_queue("aaaaa", "tt", User.ID_ROOT, max_attempts=9, queue_burst=102.0, queue_rate=2)
        self.assertEqual(q.max_attempts, 9)
        self.assertEqual(q.queue_rate, 2)
        self.assertEqual(q.queue_burst, 102.0)
        mqueue.create_queue("bbbbb", "ddd", User.ID_ROOT)
        try:
            mqueue.create_queue("aaaaa", "tt", User.ID_ROOT)
        except UniqueError:
            self.assertTrue(True)
        query = mqueue.Queue.all()
        query.filter("queue_name =", 'bbbbb')
        query.filter("queue_desc =", 'ddd')        
        c = query.count()
        self.assertEqual(c, 1)
        
    def test_get_queue(self):
        qid = mqueue.create_queue("aacaaa", "tt", User.ID_ROOT).key()
        qu = mqueue.get_queue(User.ID_ROOT, queue_id=qid)
        self.assertEqual("aacaaa", qu.queue_name)
        qid = mqueue.create_queue("acccc", "tt", User.ID_ROOT).key()
        qu = mqueue.get_queue(User.ID_ROOT, queue_name="acccc")
        self.assertEqual(qu.key(), qid)
        q = mqueue.get_queue(User.ID_ROOT, queue_id="c")
        self.assertIsNone(q)
        q = mqueue.get_queue(User.ID_ROOT, queue_name="c")
        self.assertIsNone(q)    
    
    def test_delete_queue(self):
        qid = mqueue.create_queue("aacadfaa", "tt", User.ID_ROOT).key()
        b = mqueue.delete_queue(qid, User.ID_ROOT)
        self.assertTrue(b)
        queue = mqueue.create_queue("aacadfaa1", "tt", User.ID_ROOT)
        queue.put_qtask("eee")
        qtask = queue.next_qtask("ccc")
        qtask.complete("ccc")
        b = mqueue.delete_queue(queue.key(), User.ID_ROOT)
        self.assertTrue(b)
            
    def test_fetch_queues(self):
        mqueue.create_queue("aacafffdfaa", "tt", User.ID_ROOT).key()
        mqueue.create_queue("aacafffdfaa2", "tt", User.ID_ROOT).key()
        mqueue.create_queue("aacafffdfaa3", "tt", User.ID_ROOT).key()
        queues = mqueue.fetch_queues(User.ID_ROOT)
        self.assertGreaterEqual(len(queues), 3)
    
    def assert_job_equal(self, job, data):
        for k, v in data.items():
            self.assertEqual(job.payload[k], v)

    def test_put_next(self):
        queue = mqueue.create_queue("testqueue", "tt", User.ID_ROOT) 
        data = {"context_id": "alpha",
                "data": [1, 2, 3],
                "more-data": typeutils.time_seconds()}
        queue.put_qtask(dict(data))
        job = queue.next_qtask('qc')
        self.assert_job_equal(job, data)
        self.assertEqual(queue.size(), 1)
        queue.put_qtask(dict(data))
        job = queue.next_qtask('qc')
        self.assert_job_equal(job, data)
        self.assertEqual(queue.size(), 2)
        job.complete('qc')
        self.assertEqual(queue.size(), 1)
        queue.put_qtask(data, topic="zzyy")
        self.assertEqual(queue.size(), 2)
        job = queue.next_qtask('qc')
        self.assertIsNone(job)
        job = queue.next_qtask('qc', topic="zzyy")
        self.assert_job_equal(job, data)
        self.assertEqual(queue.size(), 2)
        job.complete('qc')
        self.assertEqual(queue.size(), 1)

    def test_get_empty_queue(self):
        queue = mqueue.create_queue("testqueue2", "tt", User.ID_ROOT)  
        job = queue.next_qtask('qc2')
        self.assertEqual(job, None)
        
    def test_bucket(self):
        queue = mqueue.create_queue("testbucket", "tt", User.ID_ROOT, queue_burst=1.0, queue_rate=1)
        queue.put_qtask("aaa") 
        queue.put_qtask("bbb")
        queue.put_qtask("ccc")
        t1 = queue.next_qtask("a")
        self.assertIsNotNone(t1)
        t2 = queue.next_qtask("a")
        self.assertIsNone(t2)
        t3 = queue.next_qtask("a")
        self.assertIsNone(t3)
        time.sleep(1)
        t2 = queue.next_qtask("a")
        self.assertIsNotNone(t2)
        t3 = queue.next_qtask("a")
        self.assertIsNone(t3)
        queue.queue_burst = 3.0
        queue = queue.update(None)
        queue.put_qtask("ddd")
        queue.put_qtask("eee")
        queue.put_qtask("fff")
        t1 = queue.next_qtask("a")
        self.assertIsNotNone(t1)
        t2 = queue.next_qtask("a")
        self.assertIsNotNone(t2)
        t3 = queue.next_qtask("a")
        self.assertIsNotNone(t3)
        t4 = queue.next_qtask("a")
        self.assertIsNone(t4)
        
    def test_topic(self):
        topicqueue = mqueue.create_queue("testtopicqueue", "tt", User.ID_ROOT) 
        topicqueue.put_qtask("asdfdf1")
        topicqueue.put_qtask("asdfdf2")
        topicqueue.put_qtask("asdfdf21", topic="z")
        topicqueue.put_qtask("asdfdf22", topic="z")
        topicqueue.next_qtask("tqc")
        topicqueue.next_qtask("tqc")
        qtask = topicqueue.next_qtask("tqc")
        self.assertIsNone(qtask)
        qtask21 = topicqueue.next_qtask("tqc", topic="z")
        if str(qtask21.payload) == 'asdfdf21' or str(qtask21.payload) == 'asdfdf22':            
            self.assertTrue(True)
        else:
            self.assertTrue(False)
        qtask = topicqueue.next_qtask("tqc", topic="y")
        self.assertIsNone(qtask)
        

    def test_priority(self):
        queue = mqueue.create_queue("testqueue3", "tt", User.ID_ROOT)
        queue.put_qtask({"name": "alice"}, priority=1)
        queue.put_qtask({"name": "bob"}, priority=2)
        queue.put_qtask({"name": "mike"}, priority=0)
        qtask = queue.next_qtask('qc3')
        self.assertEqual(qtask.payload['name'], 'bob')
        qtask = queue.next_qtask('qc3')
        self.assertEqual(qtask.payload['name'], 'alice')
        qtask = queue.next_qtask('qc3')
        self.assertEqual(qtask.payload['name'], 'mike')
        

    def test_complete(self):
        queue = mqueue.create_queue("testqueue4", "tt", User.ID_ROOT)
        data = {"context_id": "alpha",
                "data": [1, 2, 3],
                "more-data": typeutils.utcnow()}

        queue.put_qtask(data)
        self.assertEqual(queue.size(), 1)
        job = queue.next_qtask("qc4")
        job.complete("qc4")
        self.assertEqual(queue.size(), 0)
        queue.put_qtask(data)
        job = queue.next_qtask('qc4')
        self.assertEqual(queue.size(), 1)
        job.complete("qc3")
        self.assertEqual(queue.size(), 1)
        
    def test_release(self):
        queue = mqueue.create_queue("testqueue5", "tt", User.ID_ROOT)
        data = {"context_id": "alpha",
                "data": [1, 2, 3],
                "more-data": typeutils.time_seconds()}

        queue.put_qtask(data)
        job = queue.next_qtask('qc5')
        job.release('qc5')
        self.assertEqual(queue.size(), 1)
        job = queue.next_qtask('qc5')
        self.assert_job_equal(job, data)
        self.assertEqual(queue.size(), 1)

    def test_error(self):
        errorqueue = mqueue.create_queue("erroqueue", "tt", User.ID_ROOT)
        errorqueue.put_qtask({"dddd":"errromems"})
        job = errorqueue.next_qtask('qce')
        job.error("qce", "this is error msg 1")
        job = errorqueue.next_qtask('qce')
        self.assert_job_equal(job, {"dddd":"errromems"})
        self.assertEqual(job.last_error, "this is error msg 1")
        self.assertEqual(job.attempts, 1)
        job = job.error("qce", "this is error msg 1")
        job = errorqueue.get_qtask(job.key())
        self.assertEqual(job.attempts, 2)        
        job = errorqueue.next_qtask('qce')
        self.assertEqual(job.attempts, 2)     
    
    def test_clear(self):
        queue = mqueue.create_queue("testqueue8", "t", User.ID_ROOT)    
        data = {"context_id": "alpha"}
        queue.put_qtask(data)
        queue.put_qtask(data)
        queue.put_qtask(data)
        self.assertEqual(queue.size(), 3)
        queue.clear()
        self.assertEqual(queue.size(), 0)
        
    def test_update_progress(self):
        queue = mqueue.create_queue("testqueue6", "tt", User.ID_ROOT)  
        queue.put_qtask({"dddd":"fadfasdf"})
        job = queue.next_qtask('qc6')
        job = job.update_progress('qc6', 50)
        job = job.update_progress('qccccc', 60)            
        job = queue.get_qtask(job.key())
        self.assertEqual(job.progress, 50)
        
    def test_stats(self):
        queue = mqueue.create_queue("testqueue7", "tt", User.ID_ROOT)  
        for i in range(5):
            data = {"context_id": "alpha%d" % i,
                    "data": [1, 2, 3],
                    "more-data": typeutils.time_seconds()}
            queue.put_qtask(data)
        job = queue.next_qtask('qc7')
        job.error("qc7", "problem")
        queue.next_qtask("qc7")
        queue.next_qtask("qc7")
        stats = queue.stats()
        self.assertEqual(stats.available, 3)
        self.assertEqual(stats.total, 5)
        self.assertEqual(stats.locked, 2)
        self.assertEqual(stats.error, 1)
        
    def test_qtrunner_run_params(self):
        try:
            schedule.create_cronjob("job1qtrun", "job1qtrun", "tests.modules.mqueue_test.QTRunner1", "cjnode1", User.ID_ROOT,
                                              fire_year="2009/2",
                                              fire_month="1",
                                              fire_day="5")
            self.assertTrue(False)
        except WrongRunParamError, e:
            self.assertIn("queue_name", str(e))
        try:
            schedule.create_cronjob("job1qtrun2", "job1qtrun", "tests.modules.mqueue_test.QTRunner1", "cjnode1", User.ID_ROOT,
                                              fire_year="2009/2",
                                              fire_month="1",
                                              fire_day="5",
                                              run_params={
                                                          "queue_name": "aaa"})
            self.assertTrue(False)
        except WrongRunParamError, e:
            self.assertIn("consumer_name", str(e))
        
        try:
            schedule.create_cronjob("job1qtrun3", "job1qtru3n", "tests.modules.mqueue_test.QTRunner1", "cjnode1", User.ID_ROOT,
                                              fire_year="2009/2",
                                              fire_month="1",
                                              fire_day="5",
                                              run_params={
                                                          "queue_name": "aaa",
                                                          "consumer_name": "eee"})
            self.assertTrue(False)
        except NoFoundError, e:
            self.assertTrue(True)
        mqueue.create_queue("xxx", "xxx", User.ID_ROOT)
        cj = schedule.create_cronjob("job1qtrurn3", "job1qtru32n", "tests.modules.mqueue_test.QTRunner1", "cjnode1", User.ID_ROOT,
                                              fire_year="2009/2",
                                              fire_month="1",
                                              fire_day="5",
                                              run_params={
                                                          "queue_name": "xxx",
                                                          "consumer_name": "eee"})
        self.assertEqual(cj.job_name, "job1qtrurn3")
    
    def test_qtrunner_run(self):
        queue = mqueue.create_queue("xxxyyy", "xxxyyy", User.ID_ROOT)
        cronjob = schedule.create_cronjob("job1qtrurrrr3", "job1qtrurrrr3", "tests.modules.mqueue_test.QTRunner1", "cjnode1", User.ID_ROOT,
                                              fire_year="2009/2",
                                              fire_month="1",
                                              fire_day="5",
                                              run_params={
                                                          "queue_name": "xxxyyy",
                                                          "consumer_name": "eee"})
        queue.put_qtask("eee")
        cronjob.run_once("www")
        logs = loggingg.fetch_logs(keywords="qtrunner1___do_____")
        self.assertEqual(logs.count, 1)
        cronjob.run_once("ww2")        
        logs = loggingg.fetch_logs(keywords="qtrunner1___do_____")
        self.assertEqual(logs.count, 1)
        queue.put_qtask("eee")
        cronjob.run_once("ww2")
        logs = loggingg.fetch_logs(keywords="qtrunner1___do_____")
        self.assertEqual(logs.count, 2)
        queue.put_qtask("ffff")
        cronjob.run_once("ww3")
        self.assertTrue(True)
    
    @classmethod
    def tearDownClass(cls):
        loggingg.uninstall_module()
        mqueue.uninstall_module()
        schedule.uninstall_module()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())        
        
    
