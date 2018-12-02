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


queue_rate = properti.IntegerProperty("queueRate", required=True, default=1, validator=RangeValidator(1))
    queue_burst = properti.FloatProperty("queueBurst", required=True, default=10.0)
    
    def __init__(self, entityinst=False, **kwds):
        super(Queue, self).__init__(entityinst=entityinst, **kwds)
        if not "queue_name" in kwds:
            raise ProgramError("queue_name is not set.")
        if not "queue_rate" in kwds:
            raise ProgramError("queue_rate is not set.")
        if not "queue_burst" in kwds:
            raise ProgramError("queue_burst is not set.")
        self.queue_name = kwds["queue_name"]
        self.queue_burst = kwds['queue_burst']
        self.queue_rate = kwds['queue_rate']
        self._qtclazz = self._gen_qtclazz(self.queue_name)        
        if not self._qtclazz.has_schema():
            self._qtclazz.create_schema()
        self._bucket = Bucket(rate=self.queue_rate, burst=self.queue_burst)
        self._mutex = funcutils.create_rlock()
        
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
    
import random

from ssguan.ignitor.utility import type,func
from ssguan.ignitor.base.error import InvalidParamError
from ssguan.wheels.schedule import CJRunner


RANDOM_PROXY = "RANDOM"

class CrawlerParam(object):
    
    USER_AGENT_CANDIDATES = ['Mozilla/5.0 (Windows NT 5.1; rv:27.0) Gecko/20100101 Firefox/27.0', ]
    
    def __init__(self, url=None, callback=None, headers={}, options={}, async=False, user_agent=None, max_clients=100, proxy=None, **kwargs):
        if type.str_is_empty(url):
            raise InvalidParamError("url")
        self._url = url
        self._callback = callback
        self._headers = headers
        self._options = options        
        self._async = async
        self._user_agent = user_agent
        self._max_clients = max_clients
        self._proxy = proxy
        self._kwargs = kwargs
    
    @property
    def url(self):
        return self._url
    
    @property
    def callback(self):
        if type.str_is_empty(self._callback):
            return None
        return reflect.import_module(self._callback)
    
    @property
    def headers(self):
        if self._headers is None:
            return None
        return type.json_to_object(self._headers)
    
    @property
    def options(self):
        if self._options is None:
            return None
        return type.json_to_object(self._options)
    
    @property
    def async(self):
        return self._async if self._async is not None else False
    
    @property
    def user_agent(self):
        if type.str_is_empty(self._user_agent):
            i = random.randint(0, len(self.USER_AGENT_CANDIDATES) - 1)
            return self.USER_AGENT_CANDIDATES[i]
        return self._user_agent

    @property
    def max_clients(self):
        return self._max_clients if self._max_clients is not None else 100
    
    @property
    def proxy(self):
        if self._proxy == RANDOM_PROXY:
            """Todo"""
        return self._proxy
    
    @property
    def kwargs(self):
        return self._kwargs
    

class JsonCrawler(CJRunner):
    
    def __init__(self, cronjob):
        super(JsonCrawler, self).__init__(cronjob)
        run_params = self._cronjob.run_params
        if run_params is None or type(self._cronjob.run_params) != dict:
            raise InvalidParamError("run_param")
        if not "url" in run_params or type.str_is_empty(run_params['url']):
            raise InvalidParamError("run_param.url")
        if not "model" in run_params or type.str_is_empty(run_params['model']):
            raise InvalidParamError("run_param.model")        
        self._param = CrawlerParam(**self._cronjob.run_params)
        self._model = self._param['model']
        self._model = reflect.import_module(self._model)
            
    def callback(self, result):
        if self._param.callback is not None:
            self._param.callback(result.content_json)
    
    def run(self, cjrunlog, caller):
        self._fetcher.http_fetch(self._param.url, self.callback, headers=self._param.headers, options=self._param.options)


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