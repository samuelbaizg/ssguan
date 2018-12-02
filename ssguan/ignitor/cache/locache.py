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
"""
     Global in-memory store of cache data. Keyed by name, to provide multiple named local memory caches.
"""

import pickle
import time

from ssguan.ignitor.cache.cache import BaseCache
from ssguan.ignitor.utility.parallel import RWLock
from ssguan.ignitor.base.struct import ThreadedDict


_locmem_caches = ThreadedDict()
_locmem_expire_info = ThreadedDict()
_locmem_locks = ThreadedDict()

class LoMemCache(BaseCache):
    def __init__(self, cacheinfo):
        BaseCache.__init__(self, cacheinfo)
        global _locmem_caches, _locmem_expire_info, _locmem_locks
        self.__cache = _locmem_caches
        self.__expire_info = _locmem_expire_info
        self.__lock = _locmem_locks.setdefault(cacheinfo.cache_name, RWLock())

    def put(self, key, value, lifespan=None, container=None):
        key = self.make_key(key, container=container)
        self.validate_key(key)
        pickled = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)        
        with self.__lock.writer():
            self.__cache[key] = pickled
            self.__expire_info[key] = self.get_expired_time(lifespan)
        return True

    def get(self, key, container=None):
        key = self.make_key(key, container=container)
        self.validate_key(key)
        pickled = None
        with self.__lock.reader():
            if not self.__has_expired(key):
                pickled = self.__cache[key]
        if pickled is not None:
            try:
                return pickle.loads(pickled)
            except pickle.PickleError:
                return None

        with self.__lock.writer():
            try:
                del self.__cache[key]
                del self.__expire_info[key]
            except KeyError:
                pass
            return None

    def has_key(self, key, container=None):
        key = self.make_key(key, container=container)
        self.validate_key(key)
        with self.__lock.reader():
            if not self.__has_expired(key):
                return True

        with self.__lock.writer():
            try:
                del self.__cache[key]
                del self.__expire_info[key]
            except KeyError:
                pass
            return False

    def __has_expired(self, key):
        exp = self.__expire_info.get(key, -1)
        if exp is None or exp > time.time():
            return False
        return True

    def delete(self, key, container=None):
        key = self.make_key(key, container=container)
        self.validate_key(key)
        with self.__lock.writer():
            try:
                del self.__cache[key]
            except KeyError:
                pass
            try:
                del self.__expire_info[key]
            except KeyError:
                pass
        return True

    def clear(self, container=None):
        if container is None:
            container = self._cacheinfo.default_container        
        keys = []
        for key in self.__cache.keys():
            if key.startswith("%s%s%s" % (self._cacheinfo.cache_name, self._cacheinfo.key_delimiter, container)):
                keys.append(key)
        with self.__lock.writer():
            for key in keys:
                del self.__cache[key]
                del self.__expire_info[key]
        return True
    
    def __str__(self, *args, **kwargs):
        return 'LoMemCache[%s]' % self.cacheinfo.cache_name
        
    
