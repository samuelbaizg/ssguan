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
class MemStore:
    
    def __init__(self):
        self._store = {}
        self._hits = {}
        
    def __contains__(self, key):
        return self._store.has_key(key)

    def __getitem__(self, key):
        if self.__contains__(key):
            self._update_hits(key)
            return self._store.get(key)
        else:
            return None 

    def __setitem__(self, key, value):
        self._store[key] = value
        self._update_hits(key)
                
    def __delitem__(self, key):
        self._store.pop(key)
        self._hits.pop(key)

    def cleanup(self):
        del self._store
        del self._hits
        self._store = {}
        self._hits = {}
        
    def populate(self):
        caches = []
        for key, value in self._store.items():
            c = {}
            c['key'] = key
            c['value'] = value
            c['hits'] = self._hits[key]
            caches.append(c)
        return caches
    
    def _update_hits(self, key):
        if self._hits.has_key(key):
            self._hits[key] = self._hits[key] + 1
        else:
            self._hits[key] = 0

_memstore = MemStore()

    
def get(space, key):
    key = _generate_key(space, key)
    value = _memstore[key]
    if value != None:
        return value 
    else:
        return None
    
def put(space, key, value):
    key = _generate_key(space, key)
    _memstore[key] = value

def delete(space, key):
    key = _generate_key(space, key)
    _memstore.pop(key)
    
def empty():
    _memstore.cleanup()
    
def populate():
    return _memstore.populate()

def _generate_key(space, key):
    return "%s:%s" % (str(space), str(key))




    
    
