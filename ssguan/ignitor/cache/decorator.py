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

from functools import wraps

from ssguan.ignitor.cache import service as cache_service, logger
from ssguan.ignitor.utility import parallel, crypt, reflect


_running = {}

def cached(lifespan=None, container=None, cache_name=None):
    """ 
        Caches result of decorated callable.
        Possible use-cases are:

        @cached()
        def func(...):  # cache function results based on all method parameters
           
        @cached(lifespan=300)  # +lifespan in seconds
        def func(a, b, c):
        
        @cached(lifespan=300, container='container')  # + container
        def func(a, b, c):

        @cached(lifespan=300, container='container', cache_name='cache_name')  # + cache_name
        def func(a, b, c):
        
    """
    def create_key(func, *args, **kwargs):
        key = reflect.get_function_path(func)
        param = ""
        for arg in args:
            param += "_%s" % str(arg)        
        for key, value in kwargs.items():
            param += '_%s_%s' % (str(key), str(value))
        param = crypt.str_to_md5_hex(param)
        key = key.replace(" ", "")
        key = "%s_%s" % (key, param)
        return key
            
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = create_key(func, *args, **kwargs)
            rkey = "%s_%s_%s_%s" % (cache_name, container, str(lifespan), key)
            cache = cache_service.get_cache(cache_name)
            data = None
            if not _running.get(rkey):
                _running[rkey] = parallel.create_lock()
            def update(block=False):
                if _running[rkey].acquire(block):
                    data = func(*args, **kwargs)
                    try:
                        cache.put(key, data, lifespan, container)
                    except:
                        logger.error('put key %s to cache.' % key, exc_info=1)
                    finally:
                        _running[rkey].release()
                    return data
            data = cache.get(key, container=container)
            if data is None: 
                data = update(block=True)            
            return data
        return wrapper
    return decorate

    
