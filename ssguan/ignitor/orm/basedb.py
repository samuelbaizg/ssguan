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


from ssguan.ignitor.utility import kind, parallel

class BaseDB(object):
    
    _find_and_delete_lock = parallel.create_rlock(process=False)
    _find_and_update_lock = parallel.create_rlock(process=False)
    
    def __init__(self, dbinfo):
        self._dbinfo = dbinfo
        
    def get_dbinfo(self):
        return self._dbinfo
        
    def get_dbclient(self):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.get_dbclient")
    
    def create_schema(self, model_class):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.create_schema")
    
    def delete_schema(self, model_class):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.delete_schema")
    
    def has_schema(self, model_class):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.has_schema")
    
    def exist_property(self, model_class, property_name):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.exist_property")
    
    def add_property(self, model_class, property_name, property_instance):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.add_property")
    
    def change_property(self, model_class, old_property_name, new_property_name, property_instance):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.change_property")
    
    def drop_property(self, model_class, property_name):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.drop_property")
    
    def gen_key(self):
        return kind.uuid_hex_32()
    
    def insert(self, model_name, **props):
        """
            Return key
            To be implemented by sub-class
        """
        raise NotImplementedError("BaseDB.insert")
    
    def update_by_key(self, model_name, keyname, keyvalue, **props):
        """
            Return rowcount of being updated
            To be implemented by sub-class
        """
        raise NotImplementedError("BaseDB.update_by_key")
        
    def delete_by_key(self, model_name, keyname, keyvalue):
        """
            Return rowcount of being deleted
            To be implemented by sub-class
        """
        raise NotImplementedError("BaseDB.delete_by_key")
    
    def get_by_key(self, model_class, keyvalue):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.get_by_key")
    
    def update_multiple(self, query):
        """
            Return rowcount of being updated
            To be implemented by sub-class
        """
        raise NotImplementedError("BaseDB.update_multiple")
    
     
    def delete_multiple(self, query):
        """
            Return rowcount of being deleted
            To be implemented by sub-class
        """
        raise NotImplementedError("BaseDB.delete_multiple")
    
    def find(self, query, limit, offset=0, paging=False, metadata=None, mocallback=None):
        """
            Return [Model]
        """
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.find")
    
    def find_one_and_update(self, query, new=False, metadata=None, mocallback=None):
        """
            Modifies and returns a single model.
            query: filter method is used to select models, sort method is used to decide which one is updated. 
                    what method is subset of fields to return. set method is the value specifications to modify the selected record.   
            new : When true,  returns the modified than the original. 
            update: value specifications to modify the record
        """
        """To be implemented by sub-class"""
        try:
            self._find_and_update_lock.acquire()
            return self._find_one_and_update(query, new, metadata, mocallback)
        finally:
            self._find_and_update_lock.release()
    
    def find_one_and_delete(self, query, metadata=None, mocallback=None):
        """
            Delete and returns the deleted model.
            query: filter method is used to select models, sort method is used to decide which one is deleted. 
                    what method is subset of fields to return.   
        """
        """To be implemented by sub-class"""
        try:
            self._find_and_delete_lock.acquire()
            return self._find_one_and_delete(query, metadata, mocallback)
        finally:
            self._find_and_delete_lock.release()
    
    def _find_one_and_update(self, query, new=False, metadata=None, mocallback=None):
        raise NotImplementedError("BaseDB._find_one_and_update")
    
    def _find_one_and_delete(self, query, metadata=None, mocallback=None):
        raise NotImplementedError("BaseDB._find_one_and_delete")
    
    
    def count(self, query):
        """To be implemented by sub-class"""
        raise NotImplementedError("BaseDB.count")
    
        
    def _transform_found_results(self, query, results, length, metadata, mocallback):
        models = []
        mocallback = mocallback if mocallback is not None else lambda mo:""""""
        for i in range(0, length):
            result = results[i]
            if metadata is None:
                mo = query.get_model_class()(entityinst=True, **result)
                mocallback(mo)
                models.append(mo._to_non_entityinst())
            else:
                for key, prop in metadata.items():
                    if key in result:
                        value = result.get(key)
                        value = prop.normalize_value(value)
                        setattr(result, key, value)
                mo = query.get_model_class()(entityinst=True, **result)
                mocallback(mo)
                models.append(mo._to_non_entityinst())
        return models
