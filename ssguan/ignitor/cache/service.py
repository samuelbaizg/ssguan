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

from ssguan.ignitor.base.error import NoFoundError, NoSupportError
from ssguan.ignitor.cache import config as cache_config
from ssguan.ignitor.cache.locache import LoMemCache
from ssguan.ignitor.utility import parallel


__caches = {}
__lock = parallel.create_lock()

def get_cache(cache_name=None):
    """
        Return the Instance of sub-class of BaseClass
    """
    cacheinfo = cache_config.get_default_cacheinfo()   if cache_name is None else cache_config.get_cacheinfo(cache_name)
    if cacheinfo is None:
        raise NoFoundError("Cache", cache_name)
    if cache_name in __caches:
        return __caches[cache_name]
    else:
        __lock.acquire()
        try:
            __caches[cache_name] = __new_cache(cacheinfo)
        finally:
            __lock.release()
        return __caches[cache_name]

def put(key, value, lifespan=None, container=None, cache_name=None):
    """
        put a value to cache.
    """
    return get_cache(cache_name).put(key, value, lifespan=lifespan, container=container)

def get(key, container=None, cache_name=None):
    """
        get the value from cache.
    """
    return get_cache(cache_name).get(key, container=container)
    
def delete(key, container=None, cache_name=None):
    """
        delete the value from cache.
    """
    return get_cache(cache_name).delete(key, container=container)

def has_key(key, container=None, cache_name=None):
    """
        check if the key is existed.
    """
    return get_cache(cache_name).has_key(key, container=container)

def clear(container=None, cache_name=None):
    """
        clear all cached values of container.
    """
    return get_cache(cache_name).clear(container)

def __new_cache(cacheinfo):
    if cacheinfo.is_locache():
        return LoMemCache(cacheinfo)
    raise NoSupportError("Cache Type", cacheinfo.cache_type)
