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



import imp
import os
import sys
import time

import six

from ssguan import config
from ssguan.commons import loggingg, dao, typeutils, funcutils
from ssguan.commons.dao import Model, UniqueValidator, RangeValidator
from ssguan.commons.error import Error, ProgramError, ExceptionWrap, NoFoundError
from ssguan.modules import auth
from ssguan.modules.auth import User, RoleOperation, UnauthorizedError
from ssguan.modules.schedule import CJRunner


_logger = loggingg.get_logger(config.MODULE_MQUEUE)

    
class WrongRunParamError(Error):
    
    def __init__(self, label):
        super(WrongRunParamError, self).__init__("Run Parameters {{label}} is not configured." , label=label)
        
    @property
    def code(self):
        return 1131
    
class QTRunner(CJRunner):
    
    def __init__(self, cronjob):
        """
            run_params must includes queue_name, consumer_name and include topic optionally.
        """
        super(QTRunner, self).__init__(cronjob)
        params = self.cronjob.run_params
        params = {} if params is None else params
        if not params.has_key("queue_name"):
            raise WrongRunParamError("queue_name")
        if not params.has_key("consumer_name"):
            raise WrongRunParamError("consumer_name")
        queue_name = params['queue_name']
        queue = get_queue(User.ID_SYSTEM, queue_name=queue_name)
        if queue is None:
            raise NoFoundError("Queue", queue_name)
        else:
            self._queue = queue
        self._consumer_name = params['consumer_name']
        if not params.has_key("topic"):
            self._topic = None
        else:
            self._topic = params["topic"] 
        
    @property
    def queue(self):
        return self._queue
    
    def run(self, cjrunlog, caller):
        qtask = self._queue.next_qtask(self._consumer_name, topic=self._topic)
        if qtask == None:
            return None
        try:
            self.do(qtask)
        except Exception:
            raise ExceptionWrap(sys.exc_info(), qtask=qtask)
        return qtask
    
    def run_success_cb(self, result, cjrunlog, caller):
        if result is None:
            return None
        try:
            return result.complete(self._consumer_name)
        except Exception, e:
            _logger.error(e.message, exc_info=1)
            return e.message
            
    def run_failure_cb(self, exception, cjrunlog, caller):
        try:
            qtask = exception.data['qtask']                
            qtask.error(self._consumer_name, str(exception.message))
            _logger.error("failed to run qtask\n%s", exception.message_tb)
        except Exception , e:
            _logger.error(e.message, exc_info=1)
    
    def do(self, qtask):
        """
            To be implemented by the sub-class
        """
        raise NotImplementedError("QTRunner.do")
    
        

class Bucket(object):

    def __init__(self, rate=1, burst=None):
        """
            traffic flow control with token bucket
        """
        self.rate = float(rate)
        if burst is None:
            self.burst = float(rate) * 10
        else:
            self.burst = float(burst)
        self.mutex = funcutils.create_lock(False)
        self.bucket = self.burst
        self.last_update = time.time()

    def get(self):
        '''Get the number of tokens in bucket'''
        now = time.time()
        if self.bucket >= self.burst:
            self.last_update = now
            return self.bucket
        bucket = self.rate * (now - self.last_update)
        self.mutex.acquire()
        if bucket > 1:
            self.bucket += bucket
            if self.bucket > self.burst:
                self.bucket = self.burst
            self.last_update = now
        self.mutex.release()
        return self.bucket

    def set(self, value):
        '''Set number of tokens in bucket'''
        self.bucket = value

    def desc(self, value=1):
        '''Use value tokens'''
        self.bucket -= value

class Queue(Model):
    
    queue_name = dao.StringProperty("queueName", required=True, validator=UniqueValidator("queue_name"))
    queue_rate = dao.IntegerProperty("queueRate", required=True, default=1, validator=RangeValidator(1))
    queue_burst = dao.FloatProperty("queueBurst", required=True, default=10.0)
    max_attempts = dao.IntegerProperty("maxAttempts", required=True, default=3)
    queue_desc = dao.StringProperty("queueDesc", required=True)
    
    def __init__(self, entityinst=False, **kwds):
        super(Queue, self).__init__(entityinst=entityinst, **kwds)
        if not kwds.has_key("queue_name"):
            raise ProgramError("queue_name is not set.")
        if not kwds.has_key("queue_rate"):
            raise ProgramError("queue_rate is not set.")
        if not kwds.has_key("queue_burst"):
            raise ProgramError("queue_burst is not set.")
        self.queue_name = kwds["queue_name"]
        self.queue_burst = kwds['queue_burst']
        self.queue_rate = kwds['queue_rate']
        self._qtclazz = self._gen_qtclazz(self.queue_name)        
        if not self._qtclazz.has_schema():
            self._qtclazz.create_schema()
        self._bucket = Bucket(rate=self.queue_rate, burst=self.queue_burst)
        self._mutex = funcutils.create_rlock()
    
    @classmethod
    def meta_domain(cls):
        return config.MODULE_MQUEUE
    
    @property
    def name(self):
        return self.queue_name
    
    @classmethod
    def get_by_name(cls, queue_name):
        query = Queue.all()
        query.filter("queue_name =", queue_name)
        return query.get()
    
    def _gen_qtclazz(self, qname):
        qclazzcode = """
from ssguan.modules.mqueue import QTaskBase
class %s (QTaskBase):
    ''''''
        """ % (qname)
        qclazz = compile(qclazzcode, '<%s>' % qname, 'exec')
        mod = imp.new_module('ssguan.modules.mqueue.gen')
        mod.__file__ = '<%s>' % os.path.join(os.path.dirname(__file__) , 'mqueue')
        mod.__loader__ = __name__
        mod.__package__ = 'ssguan.modules.mqueue'
        six.exec_(qclazz, mod.__dict__)
        qclazz = mod.__dict__.get('%s' % qname)        
        return qclazz
    
    def _before_update(self, dbconn=None):
        lastmodel = self.get_by_key(self.key())
        self.queue_name = lastmodel.queue_name        
    
    def _after_update(self, dbconn=None):
        self._bucket = Bucket(rate=self.queue_rate, burst=self.queue_burst)
    
    def _after_delete(self, dbconn=None):
        self._qtclazz.delete_schema(dbconn=dbconn)
    
    def put_qtask(self, payload, topic=None, priority=0):
        job = self._qtclazz()
        job.priority = priority
        job.payload = payload
        job.topic = topic
        job.attempts = 0
        job.locked_by = None
        job.locked_time = None
        job.last_error = None
        job = job.create(None)
        return job

    def next_qtask(self, consumer_name, topic=None):
        if self._bucket.get() < 1:
            return None
        self._mutex.acquire()        
        query = self._qtclazz.all()
        query.filter("locked_by is", None)
        query.filter("locked_time is", None)
        query.filter("attempts <", self.max_attempts)
        query.filter("topic =", topic)
        query.order("-priority")
        query.order("attempts")
        query.set("locked_by", consumer_name)
        query.set("locked_time", typeutils.utcnow())       
        qtask = query.find_one_and_update(None, new=True)
        self._bucket.desc()
        self._mutex.release()
        return qtask
    
    def get_qtask(self, key):
        qtask = self._qtclazz.get_by_key(key)
        return qtask
    
    def clear(self):
        query = self._qtclazz.all()
        return query.delete(None)
    
    def size(self):
        query = self._qtclazz.all()
        return query.count()

    def stats(self):
        """
            Get statistics on the queue.
            :rtype typeutils.Storge: Return typeutils.Storage {avaiable:x, locked:x, error: x, total: x}
        """
        stat = typeutils.Storage()
        stat.available = 0
        stat.locked = 0
        stat.error = 0
        stat.total = 0
        query = self._qtclazz.all()
        query.filter("locked_by =", None)
        stat.available = query.count()
        query = self._qtclazz.all()
        query.filter("locked_by !=", None)
        stat.locked = query.count()
        query = self._qtclazz.all()
        query.filter("attempts >=", 1)
        stat.error = query.count()
        query = self._qtclazz.all()
        stat.total = query.count()
        return stat
    
class QTaskBase(Model):
    
    priority = dao.IntegerProperty('priority', required=True)    
    attempts = dao.IntegerProperty('attempts', required=True, default=0)
    payload = dao.ObjectProperty('payload', required=False, length=4294967295)
    topic = dao.StringProperty('topic', required=False)
    progress = dao.IntegerProperty('progress', required=False, default=0)
    locked_by = dao.StringProperty('lockedBy', required=False, length=20)
    locked_time = dao.DateTimeProperty('lockedTime', required=False)
    last_error = dao.StringProperty('lastError', required=False, length=200)
    
    @classmethod
    def meta_domain(cls):
        return config.MODULE_MQUEUE + 't'
    
    def complete(self, consumer_name):
        """
            Marks a job as complete and removes it from the queue.
        """
        query = self.all()
        query.filter("%s =" % Model.DEFAULT_KEYNAME, self.key())
        query.filter("locked_by =", consumer_name)
        query.find_one_and_delete(None)
        return True

    def error(self, consumer_name, message=None):
        """
            Note an error processing a job, and return it to the queue.
        """
        query = self.all()
        query.filter("%s =" % Model.DEFAULT_KEYNAME, self.key())
        query.filter("locked_by =", consumer_name)
        query.set("locked_by set", None)
        query.set("locked_time set", None)
        query.set("last_error set", message)
        query.set("attempts inc", 1)
        query.find_one_and_update(None, new=True)        
        return self

    def update_progress(self, consumer_name, count=0):
        """
            Note progress on a long running task.
            Optionally takes a progress count integer, 
            notes progress on the job and resets the lock time.
        """
        query = self.all()
        query.filter("%s =" % Model.DEFAULT_KEYNAME, self.key())
        query.filter("locked_by =", consumer_name)
        query.set("locked_time set", typeutils.utcnow())
        query.set("progress set", count)
        query.find_one_and_update(None, new=True)
        return self

    def release(self, consumer_name):
        """
            Release a job back to the pool. The attempts counter is not modified.
        """
        query = self.all()
        query.filter("%s =" % self.DEFAULT_KEYNAME, self.key())
        query.filter("locked_by =", consumer_name)
        query.set("locked_by set", None)
        query.set("locked_time set", None)
        query.set("attempts inc", 1)
        query.find_one_and_update(None, new=True)
        return self  

def create_queue(queue_name, queue_desc, created_by, queue_rate=1, queue_burst=10.0, max_attempts=3):
    if not auth.has_permission(created_by, Queue, RoleOperation.OPERATION_CREATE):
        raise UnauthorizedError(RoleOperation.OPERATION_CREATE, Queue.get_modelname(), queue_name)
    queue = Queue(queue_name=queue_name, queue_rate=queue_rate, queue_burst=queue_burst)
    queue.queue_desc = queue_desc
    queue.max_attempts = max_attempts
    queue = queue.create(created_by)
    return queue

def delete_queue(queue_id, deleted_by):
    if not auth.has_permission(deleted_by, Queue, RoleOperation.OPERATION_DELETE):
        raise UnauthorizedError(RoleOperation.OPERATION_DELETE, Queue.get_modelname(), queue_id)
    queue = Queue.get_by_key(queue_id)
    return queue.delete(deleted_by)

def get_queue(read_by, queue_id=None, queue_name=None):
    if not auth.has_permission(read_by, Queue, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, Queue.get_modelname(), queue_id)
    queue = None
    if queue_id is not None:
        queue = Queue.get_by_key(queue_id)                    
    if queue is None and queue_name is not None:
        queue = Queue.get_by_name(queue_name)
    return queue

def fetch_queues(read_by):
    if not auth.has_permission(read_by, Queue, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, Queue.get_modelname(), "all queues")
    query = Queue.all()
    return query.fetch()

def install_module():
    Queue.create_schema()
    config.dbCFG.add_model_dbkey("%s_*" % config.MODULE_MQUEUE, config.dbCFG.ROOT_DBKEY)
    config.dbCFG.add_model_dbkey("%st_*" % config.MODULE_MQUEUE, config.dbCFG.ROOT_DBKEY)
    return True
    
def uninstall_module():
    Queue.delete_schema()
    config.dbCFG.delete_model_dbkey("%s_*" % config.MODULE_MQUEUE)
    config.dbCFG.delete_model_dbkey("%st_*" % config.MODULE_MQUEUE)
    return True
