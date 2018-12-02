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

import platform

from tornado.ioloop import IOLoop, PeriodicCallback

from ssguan.ignitor.base import context
from ssguan.ignitor.orm.model import Model
from ssguan.ignitor.sched import logger
from ssguan.ignitor.sched.cronjob import CronJob
from ssguan.ignitor.sched.error import SchedRunningError
from ssguan.ignitor.utility import kind, parallel, reflect


class Scheduler(object):
    
    _lock = parallel.create_rlock(process=False)
    
    def __new__(cls, node):  
        with cls._lock:
            if not hasattr(cls, '_instances'):
                cls._instances = {}
            if not node in cls._instances:
                orig = super(Scheduler, cls) 
                instance = orig.__new__(cls)
                instance._node = node
                instance._periodic_callback = None
                cls._instances[node] = instance  
        return cls._instances[node]
    
    def start(self, interval, io_loop=None):
        if self.is_running():
            raise SchedRunningError()
        func = reflect.wrap_func(self.run_once, Model.NULL_USER_ID)
        self._periodic_callback = PeriodicCallback(func, interval * 1000)                
        self._periodic_callback.start()
        if io_loop is None:
            io_loop = IOLoop.current()
        logger.info("Scheduler %s is running per %d seconds." % (self._node, interval))
        io_loop.start()
    
    def stop(self):
        if self.is_running():
            self._periodic_callback.stop()
            self._periodic_callback = None
        else:
            self._periodic_callback = None
            
    def is_running(self):
        state = False
        if self._periodic_callback is None:
            state = False
        else:
            state = self._periodic_callback.is_running()
        return state
    
    def run_all(self, caller, broken=None):
        query = CronJob.all()    
        query.filter("job_node =", self._node)        
        query.filter("next_run_time <=", kind.utcnow())
        if broken is not None:
            query.filter("broken =", broken)
        cronjobs = query.fetch()
        for cronjob in cronjobs:
            cronjob.run_once(caller)
    
    def run_once(self, job_id, caller):
        cronjob = CronJob.get_by_key(job_id)
        cronjob.run_once(caller)

def create_cronjob(job_name, job_desc, job_runner, job_node, job_group=None, run_params=None, broken=False, logged=True, singleton=True, fire_year='*', fire_month=1, fire_day=1, fire_week='*', fire_dayofweek='*', fire_hour=0, fire_minute=0, fire_second=0, start_time=None, end_time=None, timezone=kind.tz_utc()):
    cronjob = CronJob(job_name=job_name, job_runner=job_runner)
    cronjob.job_desc = job_desc
    cronjob.job_node = job_node
    cronjob.job_group = job_group
    cronjob.run_params = run_params
    cronjob.broken = broken
    cronjob.logged = logged
    cronjob.singleton = singleton
    cronjob.fire_year = fire_year
    cronjob.fire_month = fire_month
    cronjob.fire_day = fire_day
    cronjob.fire_week = fire_week
    cronjob.fire_dayofweek = fire_dayofweek
    cronjob.fire_hour = fire_hour
    cronjob.fire_minute = fire_minute
    cronjob.fire_second = fire_second
    cronjob.start_time = start_time
    cronjob.end_time = end_time
    cronjob.timezone = timezone
    cronjob.previous_run_time = None
    if not broken:
        cronjob.next_run_time = cronjob.get_next_fire_time(None, kind.utcnow())
    else:
        cronjob.next_run_time = None
    cronjob.create(context.get_user_id())
    return cronjob

def get_cronjob(job_id=None, job_name=None):
    cronjob = None
    if job_id is not None:
        cronjob = CronJob.get_by_key(job_id)            
    if cronjob is None and job_name is not None:
        cronjob = CronJob.get_by_name(job_name)
    return cronjob
    
def break_cronjob(job_id, broken):
    cronjob = CronJob.get_by_key(job_id)
    cronjob.broken = broken
    cronjob = cronjob.update(context.get_user_id())
    return cronjob
    
def delete_cronjob(job_id):
    cronjob = CronJob.get_by_key(job_id)
    return cronjob.delete(context.get_user_id())

def fetch_cronjobs(job_name=None, job_node=None, job_group=None, broken=None):
    query = CronJob.all()
    if job_name is not None:
        query.filter("job_name like", '%%%s%%' % job_name)
    if job_node is not None:
        query.filter("job_node =", job_node)
    if job_group is not None:
        query.filter("job_group =", job_group)
    if broken is not None:
        query.filter("broken =", broken)
    return query.fetch()

def start(node, interval=1, io_loop=None):
    node = platform.node() if node is None else node
    scheduler = Scheduler(node)
    scheduler.start(interval, io_loop=io_loop)



