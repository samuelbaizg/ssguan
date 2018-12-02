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


import random

from ssguan.commons import typeutils, funcutils
from ssguan.commons.error import InvalidParamError
from ssguan.commons.fetch import Fetcher
from ssguan.modules.schedule import CJRunner


RANDOM_PROXY = "RANDOM"

class CrawlerParam(object):
    
    USER_AGENT_CANDIDATES = ['Mozilla/5.0 (Windows NT 5.1; rv:27.0) Gecko/20100101 Firefox/27.0', ]
    
    def __init__(self, url=None, callback=None, headers={}, options={}, async=False, user_agent=None, pool_size=100, proxy=None, **kwargs):
        if typeutils.str_is_empty(url):
            raise InvalidParamError("url")
        self._url = url
        self._callback = callback
        self._headers = headers
        self._options = options        
        self._async = async
        self._user_agent = user_agent
        self._pool_size = pool_size
        self._proxy = proxy
        self._kwargs = kwargs
    
    @property
    def url(self):
        return self._url
    
    @property
    def callback(self):
        if typeutils.str_is_empty(self._callback):
            return None
        return funcutils.import_module(self._callback)
    
    @property
    def headers(self):
        if self._headers is None:
            return None
        return typeutils.json_to_object(self._headers)
    
    @property
    def options(self):
        if self._options is None:
            return None
        return typeutils.json_to_object(self._options)
    
    @property
    def async(self):
        return self._async if self._async is not None else False
    
    @property
    def user_agent(self):
        if typeutils.str_is_empty(self._user_agent):
            i = random.randint(0, len(self.USER_AGENT_CANDIDATES) - 1)
            return self.USER_AGENT_CANDIDATES[i]
        return self._user_agent

    @property
    def pool_size(self):
        return self._pool_size if self._pool_size is not None else 100
    
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
        if not run_params.has_key("url") or typeutils.str_is_empty(run_params['url']):
            raise InvalidParamError("run_param.url")
        if not run_params.has_key("model")or typeutils.str_is_empty(run_params['model']):
            raise InvalidParamError("run_param.model")        
        self._param = CrawlerParam(**self._cronjob.run_params)
        self._fetcher = Fetcher(user_agent=self._param.user_agent, pool_size=self._param.pool_size, proxy=self._param.proxy, async=self._param.async)
        self._model = self._param['model']
        self._model = funcutils.import_module(self._model)
            
    def callback(self, result):
        if self._param.callback is not None:
            self._param.callback(result.content_json)
    
    def run(self, cjrunlog, caller):
        self._fetcher.http_fetch(self._param.url, self.callback, headers=self._param.headers, options=self._param.options)
