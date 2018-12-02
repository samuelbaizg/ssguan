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

from ssguan.ignitor.cache.error import KeyLengthError, KeyCharError

class BaseCache(object):
    """
    Base Cache class.
    """

    def __init__(self, cacheinfo):
        self._cacheinfo = cacheinfo
    
    @property
    def cacheinfo(self):
        """
            Return CacheInfo instance.
        """
        return self._cacheinfo
    
    def make_key(self, key, container=None):
        """Constructs the key used by all other methods. By default it
        uses the key_func to generate a key (which, by default,
        prepends the `key_prefix' and 'version'). A different key
        function can be provided at the time of cache construction;
        alternatively, you can subclass the cache backend to provide
        custom key making behavior.
        """
        container = self._cacheinfo.default_container if container is None else container
        return '%s%s%s%s%s' % (self._cacheinfo.cache_name, self._cacheinfo.key_delimiter, container, self._cacheinfo.key_delimiter, key)

    def put(self, key, value, lifespan=None, container=None):
        """
        Set a value in the cache. If
        lifespan is given, that lifespan will be used for the key; otherwise
        the default cache lifespan will be used.
        :param container|str: container name
        :param key|str: container name
        :rtype bool: Returns True if the value was stored, False otherwise.
        """
        raise NotImplementedError(
            'subclasses of BaseCache must provide an add() method')

    def get(self, key, container=None):
        """
        Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        """
        raise NotImplementedError(
            'subclasses of BaseCache must provide a get() method')

    def delete(self, key, container=None):
        """
        Delete a key from the cache, failing silently.
        """
        raise NotImplementedError(
            'subclasses of BaseCache must provide a delete() method')

    def has_key(self, key, container=None):
        """
        Returns True if the key is in the cache and has not expired.
        """
        return self.get(container, key) is not None

    
    def __contains__(self, key, container=None):
        """
        Returns True if the key is in the cache and has not expired.
        """
        # This is a separate method, rather than just a copy of has_key(),
        # so that it always has the same functionality as has_key(), even
        # if a subclass overrides it.
        return self.has_key(key, container=container)
    
    def clear(self, container=None):
        """Remove *all* values from the cache at once."""
        raise NotImplementedError(
            'subclasses of BaseCache must provide a clear() method')

    def validate_key(self, key):
        """
        Verify if keys that would not be portable to the backend.
        """
        if len(key) > self._cacheinfo.max_key_length:
            raise KeyLengthError(key, self._cacheinfo.max_key_length)
        for char in key:
            if ord(char) < 33 or ord(char) == 127:
                raise KeyCharError(key, char)
    
    def get_expired_time(self, lifespan):
        """
            Compute expired_time
            :rtype long: Return the expired timestamp
        """
        if lifespan is None:
            lifespan = self._cacheinfo.default_lifespan
        
        return time.time() + lifespan
        

