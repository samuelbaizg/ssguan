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

from ssguan.ignitor.utility import io
from ssguan.ignitor.base import struct

__SECTION_CACHES = "caches"
__OPTION_CACHEKEYS = 'keys'
__SECTION_CACHE_DEFAULT = "default"

__cacheinfos = struct.Storage()

def file_config(filepath, defaults=None):
    parser = io.get_configparser(filepath, defaults=defaults)
    global __cacheinfos
    keys = parser.get(__SECTION_CACHES, __OPTION_CACHEKEYS)
    keys = keys.split(",")
    for key in keys:
        __cacheinfos[key] = __parse_cacheinfo(parser, key)

def get_default_cacheinfo():
    """
        Return default CacheInfo
    """
    return __cacheinfos[__SECTION_CACHE_DEFAULT]

def get_cacheinfo(cache_name):
    """
        Return CacheInfo
        :param cache_name|str:
    """
    return __cacheinfos[cache_name]


def __parse_cacheinfo(parser, cache_name):
    cache_section = "cache_%s" % cache_name 
    lifespan = parser.get(cache_section, CacheInfo.CI_DEFAULT_LIFESPAN)
    container = parser.get(cache_section, CacheInfo.CI_DEFAULT_CONTAINER)
    cachetype = parser.get(cache_section, CacheInfo.CI_CACHE_TYPE)
    key_delimiter = parser.get(cache_section, CacheInfo.CI_KEY_DELIMITER)
    length = parser.get(cache_section, CacheInfo.CI_MAX_KEY_LENGTH)
    others = {}
    for (key, value) in parser.items(cache_section):
        if key not in (CacheInfo.CI_DEFAULT_LIFESPAN, CacheInfo.CI_DEFAULT_CONTAINER, CacheInfo.CI_KEY_DELIMITER, CacheInfo.CI_MAX_KEY_LENGTH, CacheInfo.CI_CACHE_TYPE):
            others[key] = value
    return CacheInfo(cache_name, cachetype, container, lifespan, length, key_delimiter, **others)

class CacheInfo(object):
    
    CI_DEFAULT_LIFESPAN = "default_lifespan"
    CI_DEFAULT_CONTAINER = "default_container"
    CI_KEY_DELIMITER = "key_delimiter"
    CI_MAX_KEY_LENGTH = "max_key_length"
    CI_CACHE_TYPE = "cache_type"
    def __init__(self, cache_name, cache_type, default_container, default_lifespan, max_key_length, key_delimiter, **kwargs):        
        self.__cache_name = cache_name
        self.__cache_type = cache_type
        self.__default_container = default_container
        self.__default_lifespan = default_lifespan
        self.__max_key_length = max_key_length
        self.__key_delimiter = key_delimiter
        self.__kwargs = kwargs
        
    @property
    def cache_name(self):
        return self.__cache_name
    
    @property
    def cache_type(self):
        return self.__cache_type
    
    @property
    def default_container(self):
        return self.__default_container
    
    def is_locache(self):
        """
            Cache in Local memory
        """
        return self.__cache_type == 'locache'
    
    def is_memcache(self):
        """
            Cache in memcache
        """
        return self.__cache_type == 'memcache'
    
    def is_redis(self):
        """
            Cache in redis
        """
        return self.__cache_type == 'redis'
    
    @property
    def default_lifespan(self):
        """
            Return default lifespan in seconds.
        """
        return int(self.__default_lifespan)
    
    @property
    def key_delimiter(self):
        return self.__key_delimiter
    
    @property
    def max_key_length(self):
        return int(self.__max_key_length)
    
    @property
    def kwargs(self):
        return self.__kwargs
    
