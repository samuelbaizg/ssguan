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

import datetime

import pymongo

from ssguan.ignitor.base.error import ProgramError
from ssguan.ignitor.orm.basedb import BaseDB
from ssguan.ignitor.utility import kind
from ssguan.ignitor.base import struct

class MongoDB(BaseDB):
    
    def __init__(self, dbinfo):
        BaseDB.__init__(self, dbinfo)
        self.__mongoclient = self.__get_mongoclient(dbinfo)
        
    def get_dbclient(self):
        return self.__mongoclient
    
    def create_schema(self, model_class):
        if not self.has_schema(model_class):
            self.__mongoclient.create_collection(model_class.get_modelname())
            return True
        else:
            return False
    
    def delete_schema(self, model_class):
        self.__mongoclient.drop_collection(model_class.get_modelname())
        return True
    
    def has_schema(self, model_class):
        collection_names = self.__mongoclient.collection_names()
        return model_class.get_modelname() in collection_names
    
    def exist_property(self, model_class, property_name):
        return self.__mongoclient[model_class.get_modelname()].find_one({property_name:{'$exists':True}})
    
    def add_property(self, model_class, property_name, property_instance):
        if not self.exist_property(model_class, property_name):
            self.__mongoclient[model_class.get_modelname()].update_many(
                {}, { "$set": { property_name: property_instance.default_value() } }
            )
            return True
        else:
            return False
        
    
    def change_property(self, model_class, old_property_name, new_property_name, property_instance):
        if not self.exist_property(model_class, old_property_name):
            raise ProgramError("%s doesn't exist property - %s", model_class.get_modelname(), old_property_name)
        else:
            self.drop_property(model_class, old_property_name)
            self.add_property(model_class, new_property_name, property_instance)
            return True
    
    def drop_property(self, model_class, property_name):
        if not self.exist_property(model_class, property_name):
            raise ProgramError("%s doesn't exist property - %s", model_class.get_modelname(), property_name)
        else:
            self.__mongoclient[model_class.get_modelname()].update_many({}, {"$unset":{property_name:""}})
            return True
    
    def insert(self, model_name, **props):
        """
            Return key
        """
        indata = self._serialize_props(props)
        result = self.__mongoclient[model_name].insert_one(indata)
        return result
    
    def update_by_key(self, model_name, keyname, keyvalue, **props):
        """
            Return rowcount of being updated
        """
        updata = self._serialize_props(props)
        result = self.__mongoclient[model_name].update_one({keyname:{'$eq':keyvalue}}, {'$set':updata})
        return result.modified_count
    
    def delete_by_key(self, model_name, keyname, keyvalue):
        """
            Return rowcount of being deleted
        """
        result = self.__mongoclient[model_name].delete_one({keyname:keyvalue})
        return result.deleted_count
    
    def get_by_key(self, model_class, keyvalue):
        result = self.__mongoclient[model_class.get_modelname()].find({model_class.get_keyname(): keyvalue})
        if result.count() > 0:
            m = result[0]
            mo = model_class(entityinst=True, **m)
            return mo._to_non_entityinst()
        else:
            return None
    
    def update_multiple(self, query):
        """
            Return rowcount of being updated
        """
        update = self._set_clause(query)
        result = self.__mongoclient[query.get_model_name_alias()[0]].update_many(self._where_clause(query, aliased=True), update)
        return result.matched_count
        
    def delete_multiple(self, query):
        """
            Return rowcount of being deleted
        """
        result = self.__mongoclient[query.get_model_name_alias()[0]].delete_many(self._where_clause(query, aliased=True))
        return result.deleted_count
    
    def find(self, query, limit, offset=0, paging=False, metadata=None, mocallback=None):
        """
            Return [Model]
        """
        ql = query.get_ql()
        if ql is None:
            ql = (self._where_clause(query, aliased=True), self._what_clause(query))
        
        groups = query.get_groupings()
        if groups is not None:
            results = self.__mongoclient[query.get_model_name_alias()[0]].aggregate(*groups)
            results = self._transform_found_results(query, results, results.count(), metadata, mocallback)
            return results
        results = self.__mongoclient[query.get_model_name_alias()[0]].find(*ql)
        order = self._order_clause(query)
        if len(order) > 0:
            results = results.sort(order)
                
        if paging is False:
            results = results.limit(limit).skip(offset)
            results = self._transform_found_results(query, results, results.count(), metadata, mocallback)
            return results
        else:
            page = offset if offset > 0 else 1
            offset = limit * (page - 1)
            results = results.limit(limit).skip(offset)
            results = self._transform_found_results(query, results, results.count(), metadata, mocallback)
            count = self.__mongoclient[query.get_model_name_alias()[0]].count(ql[0])
            return struct.gen_pager(page, count, limit, results)
    
    def _find_one_and_update(self, query, new=False, metadata=None, mocallback=None):
        where = self._where_clause(query, aliased=True)
        order = self._order_clause(query)
        whats = self._what_clause(query)
        collection = self.__mongoclient[query.get_model_name_alias()[0]]
        update = self._set_clause(query)
        result = collection.find_one_and_update(where,
                                    update,
                                    sort=None if len(order) == 0 else order,
                                    new=new,
                                    projection=whats)
        if result is not None:
            result = self._transform_found_results(query, [result], 1, metadata, mocallback)
            result = result[0]
        return result
    
    def _find_one_and_delete(self, query, metadata=None, mocallback=None):
        where = self._where_clause(query, aliased=True)
        order = self._order_clause(query)
        whats = self._what_clause(query)
        collection = self.__mongoclient[query.get_model_name_alias()[0]]
        result = collection.find_one_and_delete(where,
                                        sort=None if len(order) == 0 else order,
                                        projection=whats)
        if result is not None:
            result = self._transform_found_results(query, [result], 1, metadata, mocallback)
            result = result[0]
        return result
        
    def count(self, query):
        ql = query.get_ql()
        if ql is None:
            filter1 = self._where_clause(query, aliased=True)
            result = self.__mongoclient[query.get_model_name_alias()[0]].count(filter1)
        else:
            result = self.__mongoclient[query.get_model_name_alias()[0]].count(*ql)
        return result
    
    def _what_clause(self, query):
        mw = {}
        for what in query.get_whats():
            tmp = what[0]
            i = tmp.find('.')
            if i >= 0:
                tmp = tmp[i + 1:]
            mw[tmp] = 1
        return mw
        
    def _where_clause(self, query, aliased=False):
        
        def __get_segment(query_set):
            def __get_propname(propname):
                if propname == 'ex':
                    propname = ''
                return propname
            
            def __get_operator(operator):
                valid_operators = {"<":"$lt", "<=":"$lte", ">":"$gt", ">=":"$gte", "=":"$eq", "!=":"$ne", "in":"$in", "not in":"$nin", "is":"$eq", "is not":"$ne", "like":"like"}
                if operator in valid_operators:
                    return valid_operators[operator]
                else:
                    raise ProgramError("Mangodb doesn't support the comparison %s" , operator)
            
            def __get_value(value, wrapper):
                return self._wrap_query_parameter(value, wrapper)
            dot = query_set[6]
            propname = __get_propname(query_set[0])
            propname = '' if propname == 'ex' else propname
            if "." not in propname:
                propname = "%s.%s" % (query.get_model_name_alias()[1], propname)
            propname = propname if (aliased is False or dot) else propname.split(".")[1]
                
            operator = __get_operator(query_set[1])
            value = __get_value(query_set[2], query_set[3])
            
            if operator == 'like':
                if "%" in value:
                    value = value.replace("%", ".*")
                    value = "%s" % value
                    if value[0] != '%':
                        value = "^%s" % value
                    if value[len(value) - 1] != '%':
                        value = "%s$" % value
                    value = {'$regex':value}
                segment = {propname: value}                
            else:
                segment = {propname:{operator:value}}
            return segment
        
        def __to_middle_expr(query_sets):
            middle_expr = []
            for query_set in query.get_query_sets():
                segment = __get_segment(query_set)
                logic = query_set[4]
                parenthsis = '' if query_set[5] is None else query_set[5] 
                if parenthsis == '':
                    middle_expr.append(logic)
                    middle_expr.append(segment)
                elif parenthsis == '(':
                    middle_expr.append(logic)
                    middle_expr.append(parenthsis)
                    middle_expr.append(segment)
                elif len(parenthsis) > 1:
                    if  parenthsis[0] == '(':
                        middle_expr.append(logic)
                        for ch in parenthsis:
                            middle_expr.append(ch)
                        middle_expr.append(segment)
                    else:
                        middle_expr.append(logic)
                        middle_expr.append(segment)
                        for ch in parenthsis:
                            middle_expr.append(ch)
                else:
                    middle_expr.append(logic)
                    middle_expr.append(segment)
                    middle_expr.append(parenthsis)
            if len(query_sets) > 0:
                middle_expr.pop(0)
            return middle_expr
        
        def __to_right_expr(middle_expr):
            right_expr = []
            stack = struct.Stack([])
            for elmt in middle_expr:
                if elmt == '(':
                    stack.push(elmt)
                elif elmt == ')':
                    while stack.size() > 0  and stack.peek() != '(':
                        tmp = stack.pop()
                        right_expr.append(tmp)
                    if stack.size() > 0 and stack.peek() == '(':
                        stack.pop()
                elif elmt == 'and':
                    if stack.is_empty() or stack.peek() == 'or' or stack.peek() == '(':
                        stack.push(elmt)
                    else:
                        while stack.size() > 0 and stack.peek() == 'and':
                            tmp = stack.pop()
                            right_expr.append(tmp)
                        stack.push(elmt)
                elif elmt == 'or':
                    if stack.is_empty() or stack.peek() == '(':
                        stack.push(elmt)
                    else:
                        while stack.size() > 0 and (stack.peek() == 'and' or stack.peek() == 'or'):
                            tmp = stack.pop()
                            stack.push(tmp)
                        stack.push(elmt)
                else:
                    right_expr.append(elmt)
            while stack.size() > 0:
                tmp = stack.pop()
                right_expr.append(tmp)
            return right_expr
        
        middle_expr = __to_middle_expr(query.get_query_sets())
        right_expr = __to_right_expr(middle_expr)
        stack = struct.Stack([])
        for seg in right_expr:
            if seg == 'and' or seg == 'or':
                elmt_2 = stack.pop()
                elmt_1 = stack.pop()
                elmt = {'$%s' % seg :[elmt_1, elmt_2]}
                stack.push(elmt)
            else:
                stack.push(seg)
        return {} if stack.is_empty() else stack.pop()
    
    def _order_clause(self, query):
        order = []
        for ordering in query.get_orderings():
            order .append((ordering[0], 1 if query.ASCENDING == ordering[1] else -1))
        return order
    
    def _group_clause(self, query):
        raise NotImplementedError("MongoDB._group_clause")
        
        
    def _wrap_query_parameter(self, value, wrapper):
            if wrapper is not True:
                return value
            if type(value) == datetime.date:
                value = kind.date_to_datetime(value)
            elif isinstance(value, bool):
                if value == True:
                    value = 1
                else:
                    value = 0
            return value   
    
    def _serialize_props(self, props):
        for key, value in props.items():
            if type(value) == datetime.date:
                props[key] = kind.date_to_datetime(value)
        return props
    
    def _set_clause(self, query):
        update_sets = query.get_update_sets()
        if len(update_sets) == 0:
            raise ProgramError("fields to modify must be set through Query.set method.")
        upsets = {}
        incsets = {}
        mulsets = {}
        update = {}
        for up in update_sets:
            if up[1] == 'set':
                upsets[up[0]] = up[2]
            elif up[1] == 'inc':
                incsets[up[0]] = up[2]
            elif up[1] == 'mul':
                mulsets[up[0]] = up[2]
        if len(upsets) > 0:
            update['$set'] = upsets
        if len(incsets) > 0:
            update['$inc'] = incsets
        if len(mulsets) > 0:
            update['$mul'] = mulsets
        return update
    
    def __get_mongoclient(self, dbinfo):        
        url = "mongodb://%s:%s@%s" % (dbinfo.username, dbinfo.password, dbinfo.host)
        if dbinfo.conv is not None:
            dbclient = MongoClient(host=url, port=dbinfo.port, **dbinfo.conv)
        else:
            dbclient = MongoClient(host=url, port=dbinfo.port)
        if dbinfo.dbname is not None and dbinfo.dbname != '':
            dbclient = MongoDatabase(dbclient, dbinfo.dbname)
        return dbclient
    
MongoClient = pymongo.MongoClient
MongoDatabase = pymongo.database.Database