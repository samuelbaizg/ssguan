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

from ssguan import config
from ssguan.commons import dbdriver, typeutils, funcutils
from ssguan.commons.error import ProgramError


class BaseDB(object):
    
    _find_and_delete_lock = funcutils.create_rlock(process=False)
    _find_and_update_lock = funcutils.create_rlock(process=False)
    
    def __init__(self, dbdriver1):
        self._dbdriver = dbdriver1
        dbdriver.config.debug = config.debugCFG.is_debugdb()
        
    def get_dbdriver(self):
        return self._dbdriver
    
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
        return typeutils.to_uuid_hex_40()
    
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
    
        
    def _transform_found_results(self, query, results, metadata, mocallback):
        models = []
        mocallback = mocallback if mocallback is not None else lambda mo:""""""
        if metadata is None:
            for result in results:
                mo = query.get_model_class()(entityinst=True, **result)
                mocallback(mo)
                models.append(mo._to_non_entityinst())
        else:
            for result in results:
                    for key, prop in metadata.items():
                        if result.has_key(key):
                            value = result.get(key)
                            value = prop.normalize_value(value)
                            setattr(result, key, value)
                    mo = query.get_model_class()(entityinst=True, **result)
                    mocallback(mo)
                    models.append(mo._to_non_entityinst())
                    
        return models
    

 
class SqlDB(BaseDB):
    
    def __init__(self, dbdriver):
        BaseDB.__init__(self, dbdriver)
    
    def create_schema(self, model_class):
        
        def __create_key_sqlp():
            keytype = getattr(model_class, model_class.get_keyname()).db_data_type()
            sql = '%s %s NOT NULL' % (model_class.get_keyname(), keytype)
            return sql
    
        def __create_property_sqlp(prop):
            sql = '%s %s DEFAULT NULL' % (prop.name, prop.db_data_type())
            return sql
        
        def __create_table_sqlp():
            return ""
        
        if not self.has_schema(model_class):
            sql = 'CREATE TABLE %s (' % model_class.get_modelname()
            sqlp = __create_key_sqlp()
            comma = "," if len(sqlp) > 0 else ""
            sql += " %s%s" % (sqlp, comma)
            for pname in model_class.get_properties(persistent=True):
                if pname != model_class.get_keyname() and pname != model_class.DEFAULT_KEYNAME:
                    prop = getattr(model_class, pname)
                    sql += " %s," % __create_property_sqlp(prop)
            sql += 'PRIMARY KEY (%s)' % model_class.get_keyname()
            sqlp = __create_table_sqlp()
            comma = "," if len(sqlp) > 0 else ""
            sql += '%s%s' % (comma, sqlp)
            sql += ') DEFAULT CHARSET=utf8;'
            self._dbdriver.query(sql)
            return True
        else:
            return False
    
    def delete_schema(self, model_class):
        sql = 'DROP TABLE IF EXISTS %s;' % model_class.get_modelname()
        self._dbdriver.query(sql)
        return True
    
    def has_schema(self, model_class):
        sql = "SHOW TABLES LIKE '%s'" % model_class.get_modelname()
        result = self._dbdriver.query(sql)
        return len(result) > 0
    
    def exist_property(self, model_class, property_name):
        sql = "SHOW COLUMNS FROM %s LIKE '%s'" % (model_class.get_modelname(), property_name)
        result = self._dbdriver.query(sql)
        return len(result) > 0
    
    def add_property(self, model_class, property_name, property_instance):
        if not self.exist_property(model_class, property_name):
            sql = "ALTER TABLE %s ADD %s %s" % (model_class.get_modelname(), property_name, property_instance.db_data_type())
            self._dbdriver.query(sql)
            return True
        else:
            return False
    
    def change_property(self, model_class, old_property_name, new_property_name, property_instance):
        if not self.exist_property(model_class, old_property_name):
            raise ProgramError("%s doesn't exist property - %s", model_class.get_modelname(), old_property_name)
        else:
            sql = "ALTER TABLE %s CHANGE %s %s %s" % (model_class.get_modelname(), old_property_name, new_property_name, property_instance.db_data_type())
            self._dbdriver.query(sql)
            return True     
    
    def drop_property(self, model_class, property_name):
        if not self.exist_property(model_class, property_name):
            raise ProgramError("%s doesn't exist property - %s", model_class.get_modelname(), property_name)
        else:
            sql = "ALTER TABLE %s DROP %s;" % (model_class.get_modelname(), property_name)
            self._dbdriver.query(sql)
            return True
        
    def insert(self, model_name, **props):
        key = self._dbdriver.insert(model_name, **props)
        return key
        
    def update_by_key(self, model_name, keyname, keyvalue, **props):
        keyvalue = self._normalize_keyvalue(keyvalue)
        rowcount = self._dbdriver.update(model_name, where="%s = %s" % (keyname, keyvalue), **props)
        return int(rowcount)
    
    def delete_by_key(self, model_name, keyname, keyvalue):
        keyvalue = self._normalize_keyvalue(keyvalue)
        results = self._dbdriver.delete(model_name, where="%s = %s" % (keyname, keyvalue))
        return int(results)
    
    def update_multiple(self, query):
        tablename = query.get_model_name_alias()[0]
        (where, where_vars) = self._where_clause(query, aliased=False)
        if len(where) == 0:
            raise ProgramError("where can't be empty when batch updating records.")
        set_clause = self._set_clause(query)
        sql = "UPDATE %s SET %s" % (tablename, set_clause[0])
        if len(where) > 0:
            sql += " WHERE %s" % where
        result = self._dbdriver.query(sql, vars=dict(where_vars, **set_clause[1]))
        return result
    
    def delete_multiple(self, query, **props):
        ql = query.get_ql()
        results = None
        if ql != None:
            sql = self._to_sql(query) if ql is None else ql[0]
            sql_vars = None if ql is None or len(ql) == 1 else ql[1]
            results = self._dbdriver.query(sql, sql_vars)
        else:
            sfrom = self._from_clause(query, aliased=True)
            (where, where_vars) = self._where_clause(query, aliased=True)
            if len(where) == 0:
                # raise ProgramError("where can't be empty when batch deleting records.")
                results = self._dbdriver.delete(sfrom, "1 = 1")
            else:
                results = self._dbdriver.delete(sfrom, where, vars=where_vars)
        return results
    
    def get_by_key(self, model_class, keyvalue):
        keyvalue = self._normalize_keyvalue(keyvalue)
        what = ",".join(model_class.get_properties(persistent=True).keys())
        
        result = self._dbdriver.select(model_class.get_modelname(), what=what, where="%s = %s" % (model_class.get_keyname(), keyvalue))
        if len(result) > 0:
            m = result[0]
            mo = model_class(entityinst=True, **m)
            return mo._to_non_entityinst()
        else:
            return None
    
    def find(self, query, limit, offset=0, paging=False, metadata=None, mocallback=None):
        (sql, sql_vars) = self._get_sql(query)
        if paging is False:
            results_sql = sql + " LIMIT %d OFFSET %d" % (limit, offset)
            results = self._dbdriver.query(results_sql, sql_vars)
            results = self._transform_found_results(query, results, metadata, mocallback)
            return results
        else:
            page = offset if offset > 0 else 1
            offset = limit * (page - 1)
            results_sql = sql + " LIMIT %d OFFSET %d" % (limit, offset)
            results = self._dbdriver.query(results_sql, sql_vars)
            results = self._transform_found_results(query, results, metadata, mocallback)
            
            fromindex = sql.upper().find("FROM")
            count_sql = "SELECT COUNT(*) AS count %s" % sql[fromindex:]
            count = self._dbdriver.query(count_sql, sql_vars)[0].count
            return typeutils.gen_pager(page, count, limit, results)
        
    def _find_one_and_update(self, query, new=False, metadata=None, mocallback=None):
        rtnmodel = None
        if query.count() > 0:
            rtnmodel = query.get()
            set_clause = self._set_clause(query)
            sql = "UPDATE %s SET %s" % (rtnmodel.get_modelname(), set_clause[0])
            sql += " WHERE %s = %s " % (rtnmodel.get_keyname(), self._normalize_keyvalue(rtnmodel.key()))
            self._dbdriver.query(sql, vars=set_clause[1])
            rtnmodel = rtnmodel if not new else self.get_by_key(query.get_model_class(), rtnmodel.key())
        mocallback = mocallback if mocallback is not None else lambda mo:""""""
        mocallback(rtnmodel)
        return rtnmodel
    
    def _find_one_and_delete(self, query, metadata=None, mocallback=None):
        rtnmodel = None
        if query.count() > 0:
            rtnmodel = query.get()
            self.delete_by_key(rtnmodel.get_modelname(), rtnmodel.get_keyname(), rtnmodel.key())
            mocallback = mocallback if mocallback is not None else lambda mo:""""""
            mocallback(rtnmodel)
        return rtnmodel
    
    def count(self, query):
        (sql, sql_vars) = self._get_sql(query)
        fromindex = sql.upper().find("FROM")
        count_sql = "SELECT COUNT(*) AS count %s" % sql[fromindex:]
        quanity = self._dbdriver.query(count_sql, vars=sql_vars)[0].count
        return quanity
    
    
    @classmethod    
    def _normalize_keyvalue(cls, keyvalue):
        value = keyvalue
        if isinstance(value, str) or isinstance(value, unicode):
            value = "'" + value + "'"
        return value
    
        
    def _wrap_query_parameter(self, value, wrapper):
            if isinstance(value, bool):
                if value == True:
                    value = "%d" % 1
                else:
                    value = "%d" % 0
            else:
                if wrapper is not True or value is None:
                    return value
                if isinstance(value, basestring):
                    value = "'%s'" % value
                elif isinstance(value, datetime.datetime):
                    value = "'%s'" % value
                elif isinstance(value, datetime.date):
                    value = "'%s'" % value
                value = str(value)
            return value
    
    def _what_clause(self, query):
        mw = []
        for what in query.get_whats():
            if what[1] == '':
                mw.append("%s" % what[0])
            else:
                mw.append("%s AS %s" % (what[0], what[1]))
        return ",".join(mw)
    
    def _from_clause(self, query, aliased=False):
        (name, alias) = query.get_model_name_alias()
        if aliased is False:
            return "%s %s" % (name, alias)
        else:
            return "%s" % name
   
    def _where_clause(self, query, aliased=False):
        where = ""
        where_vars = {}
        i = 0
        for query_set in query.get_query_sets():
            propname = query_set[0]
            operator = query_set[1]
            if propname == 'ex' and operator == 'ex':
                propname = ''
                operator = ''
            else:
                if "." not in propname:
                    propname = "%s.%s" % (query.get_model_name_alias()[1], propname)
                propname = propname if aliased is False else propname.split(".")[1]
                
            value = query_set[2]
            wrapper = query_set[3]
            logic = query_set[4]
            parenthsis = query_set[5]
            
            leftpa = parenthsis if parenthsis in ('(', "((", "(((") else ""
            rightpa = parenthsis if parenthsis in (')' , "))", ")))") else ""
            if isinstance(value, list):
                tmp = "("
                for val in value:
                    tmp += "%s, " % (self._wrap_query_parameter(val, wrapper))
                tmp = tmp[0:-2] + ")"
                value = tmp
                where += "%s %s %s %s %s %s" % (logic, leftpa, propname, operator, value, rightpa)                    
            else:                
                if wrapper is False:
                    value = self._wrap_query_parameter(value, wrapper)
                    where += "%s %s %s %s %s %s" % (logic, leftpa, propname, operator, value, rightpa)
                else:
                    value = self._wrap_query_parameter(value, False)
                    var_key = "whr_%s_%d" % (propname.replace(".", "_"), i)
                    where += "%s %s %s %s %s %s" % (logic, leftpa, propname, operator, "$%s" % var_key, rightpa)
                    where_vars[var_key] = value
            i += 1
        if len(where) > 0:
            if  where.startswith("and"):
                where = where[4:]
            elif where.startswith("or"):
                where = where[3:]
        return (where, where_vars)
    
    def _order_clause(self, query):
        order = ""
        for ordering in query.get_orderings():
            order += "%s %s , " % (ordering[0], ordering[1])
        if len(order) > 0:
            order = order[0:-2]
        return order
    
    def _group_clause(self, query):
        groups = query.get_groupings()
        if groups == None:
            return ""
        elif type(groups) == list:
            group = ""
            for g in groups:
                group += "%s , " % g
            if len(group) > 0:
                group = group[0:-2]
            return group
        else:
            return groups
        
    def _set_clause(self, query):
        update_sets = query.get_update_sets()
        if len(update_sets) == 0:
            raise ProgramError("fields to modify must be set through Query.set method.")
        upsets = []
        upvars = {}
        for up in update_sets:
            if up[1] == 'inc':
                upsets.append("%s = %s + %s" % (up[0], up[0], up[2]))
            elif up[1] == 'mul': 
                upsets.append("%s = %s * (%s)" % (up[0], up[0], up[2]))                              
            else:
                vk = '$up_%s' % up[0]
                upsets.append("%s = %s" % (up[0], vk))
                upvars["up_%s" % up[0]] = up[2]
        return (",".join(upsets), upvars)
    
    def _to_sql(self, query):
        """
            Return (where, where_vars dict)
        """
        what = self._what_clause(query)
        sfrom = self._from_clause(query)
        sql = "SELECT %s FROM %s" % (what, sfrom)
        where = self._where_clause(query)
        order = self._order_clause(query)
        if len(where[0]) > 0:
            sql += " WHERE %s" % where[0]
        group = self._group_clause(query)
        if len(group) > 0:
            sql += " GROUP BY %s" % group
        if len(order) > 0:
            sql += " ORDER BY %s " % order
        return (sql, where[1])
    
    def _get_sql(self, query):
        ql = query.get_ql()
        (sql1, sqlvars) = self._to_sql(query)
        if ql is None:            
            sql = sql1
            sql_vars = sqlvars
        else:
            sql = ql[0]
            sql_vars = None if len(ql) == 1 else ql[1]
        return (sql, sql_vars)
        
    
    
class MongoDB(BaseDB):
    def __init__(self, dbdriver):
        BaseDB.__init__(self, dbdriver)
    
    def create_schema(self, model_class):
        if not self.has_schema(model_class):
            self._dbdriver.create_collection(model_class.get_modelname())
            return True
        else:
            return False
    
    def delete_schema(self, model_class):
        self._dbdriver.drop_collection(model_class.get_modelname())
        return True
    
    def has_schema(self, model_class):
        collection_names = self._dbdriver.collection_names()
        return model_class.get_modelname() in collection_names
    
    def exist_property(self, model_class, property_name):
        return self._dbdriver[model_class.get_modelname()].find_one({property_name:{'$exists':True}})
    
    def add_property(self, model_class, property_name, property_instance):
        if not self.exist_property(model_class, property_name):
            self._dbdriver[model_class.get_modelname()].update_many(
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
            self._dbdriver[model_class.get_modelname()].update_many({}, {"$unset":{property_name:""}})
            return True
    
    def insert(self, model_name, **props):
        """
            Return key
        """
        indata = self._serialize_props(props)
        result = self._dbdriver[model_name].insert(indata)
        return result
    
    def update_by_key(self, model_name, keyname, keyvalue, **props):
        """
            Return rowcount of being updated
        """
        updata = self._serialize_props(props)
        result = self._dbdriver[model_name].update_one({keyname:{'$eq':keyvalue}}, {'$set':updata})
        return result.modified_count
    
    def delete_by_key(self, model_name, keyname, keyvalue):
        """
            Return rowcount of being deleted
        """
        result = self._dbdriver[model_name].delete_one({keyname:keyvalue})
        return result.deleted_count
    
    def get_by_key(self, model_class, keyvalue):
        result = self._dbdriver[model_class.get_modelname()].find({model_class.get_keyname(): keyvalue})
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
        result = self._dbdriver[query.get_model_name_alias()[0]].update_many(self._where_clause(query, aliased=True), update)
        return result.matched_count
        
    def delete_multiple(self, query):
        """
            Return rowcount of being deleted
        """
        result = self._dbdriver[query.get_model_name_alias()[0]].delete_many(self._where_clause(query, aliased=True))
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
            results = self._dbdriver[query.get_model_name_alias()[0]].aggregate(*groups)
            results = self._transform_found_results(query, results, metadata, mocallback)
            return results
        results = self._dbdriver[query.get_model_name_alias()[0]].find(*ql)
        order = self._order_clause(query)
        if len(order) > 0:
            results = results.sort(order)
                
        if paging is False:
            results = results.limit(limit).skip(offset)
            results = self._transform_found_results(query, results, metadata, mocallback)
            return results
        else:
            page = offset if offset > 0 else 1
            offset = limit * (page - 1)
            results = results.limit(limit).skip(offset)
            results = self._transform_found_results(query, results, metadata, mocallback)
            count = self._dbdriver[query.get_model_name_alias()[0]].count(ql[0])
            return typeutils.gen_pager(page, count, limit, results)
    
    def _find_one_and_update(self, query, new=False, metadata=None, mocallback=None):
        where = self._where_clause(query, aliased=True)
        order = self._order_clause(query)
        whats = self._what_clause(query)
        collection = self._dbdriver[query.get_model_name_alias()[0]]
        update = self._set_clause(query)
        result = collection.find_one_and_update(where,
                                    update,
                                    sort=None if len(order) == 0 else order,
                                    new=new,
                                    projection=whats)
        if result is not None:
            result = self._transform_found_results(query, [result], metadata, mocallback)
            result = result[0]
        return result
    
    def _find_one_and_delete(self, query, metadata=None, mocallback=None):
        where = self._where_clause(query, aliased=True)
        order = self._order_clause(query)
        whats = self._what_clause(query)
        collection = self._dbdriver[query.get_model_name_alias()[0]]
        result = collection.find_one_and_delete(where,
                                        sort=None if len(order) == 0 else order,
                                        projection=whats)
        if result is not None:
            result = self._transform_found_results(query, [result], metadata, mocallback)
            result = result[0]
        return result
        
    def count(self, query):
        ql = query.get_ql()
        if ql is None:
            filter1 = self._where_clause(query, aliased=True)
            result = self._dbdriver[query.get_model_name_alias()[0]].count(filter1)
        else:
            result = self._dbdriver[query.get_model_name_alias()[0]].count(*ql)
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
                if valid_operators.has_key(operator):
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
            stack = typeutils.Stack([])
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
        stack = typeutils.Stack([])
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
                value = typeutils.date_to_datetime(value)
            elif isinstance(value, bool):
                if value == True:
                    value = 1
                else:
                    value = 0
            return value   
    
    def _serialize_props(self, props):
        for key, value in props.items():
            if type(value) == datetime.date:
                props[key] = typeutils.date_to_datetime(value)
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
    
class DbConnPool(object):
        def __init__(self):
            self.__connections = {}
        
        def get_connection(self, dbinfo):
            if dbinfo is None:
                raise ProgramError("dbinfo can't be none when get db connection.")
            key = dbinfo.get_key()
            if self.__connections.has_key(key):
                return self.__connections[key]
            else:
                mongodriver = get_dbdriver(dbinfo)
                if dbinfo.is_mysql():
                    dbclient = SqlDB(mongodriver)
                elif dbinfo.is_mongo():
                    dbclient = MongoDB(mongodriver)
                else:
                    raise ProgramError("%s is not supported." , dbinfo.dbtype)
                self.__connections[key] = dbclient
                return dbclient
        
        def clearup(self):
            self.__connections.clear()
            self.__connections = {}

__dbconnPool = DbConnPool()

def get_dbdriver(dbinfo):
    if dbinfo.is_mysql():
        convs = None
        if dbinfo.conv is None:
            from MySQLdb.constants import FIELD_TYPE
            from MySQLdb.converters import conversions
            convs = conversions.copy()
            convs[FIELD_TYPE.DECIMAL] = float
            convs[FIELD_TYPE.NEWDECIMAL] = float
        else:
            convs = dbinfo.get_conv()
        from ssguan.commons.dbdriver import sqldriver
        if dbinfo.dbname is None or dbinfo.dbname == '':
            dbdriver = sqldriver(dbn=dbinfo.dbtype, host=dbinfo.host, port=int(dbinfo.port), user=dbinfo.username, pw=dbinfo.password, conv=convs)
        else:
            dbdriver = sqldriver(dbn=dbinfo.dbtype, host=dbinfo.host, port=int(dbinfo.port), user=dbinfo.username, pw=dbinfo.password, conv=convs, db=dbinfo.dbname)
    else:
        from ssguan.commons.dbdriver import MongoDriver, MongoDatabase
        url = "mongodb://%s:%s@%s" % (dbinfo.username, dbinfo.password, dbinfo.host)
        if dbinfo.conv is not None:
            dbdriver = MongoDriver(host=url, port=dbinfo.port, **dbinfo.conv)
        else:
            dbdriver = MongoDriver(host=url, port=dbinfo.port)
        if dbinfo.dbname is not None and dbinfo.dbname != '':
            dbdriver = MongoDatabase(dbdriver, dbinfo.dbname)
    return dbdriver

def has_db(dbinfo):
    if dbinfo.is_mysql():
        if dbinfo.dbname is None and dbinfo.dbname == '':
            raise ProgramError("dbinfo.dbname can not be None.")
        sql = "USE %s;" % dbinfo.dbname
        try:
            dbinfo = dbinfo.copy(dbname="")
            get_dbdriver(dbinfo).query(sql)
            return True
        except:
            return False
    elif dbinfo.is_mongo():
        dbname = dbinfo.dbname
        dbinfo = dbinfo.copy(dbname="")
        dbnames = get_dbdriver(dbinfo).database_names()
        return dbname in dbnames
    else:
        return True

"""
dropped == True means drop database first then create.
"""    
def create_db(dbinfo, dropped=False):
    if not has_db(dbinfo):
        if dbinfo.is_mysql():
            dbname = dbinfo.dbname
            dbinfo = dbinfo.copy(dbname="")
            sql = 'CREATE DATABASE /*!32312 IF NOT EXISTS*/`%s` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;' % dbname
            get_dbdriver(dbinfo).query(sql)
        elif dbinfo.is_mongo():
            get_dbdriver(dbinfo).create_collection("__auto_created_for_db_creation")
            get_dbdriver(dbinfo).drop_collection("__auto_created_for_db_creation")
    else:
        if dropped:
            drop_db(dbinfo)
            create_db(dbinfo, dropped=False)
    return True

def drop_db(dbinfo):
    if dbinfo.is_mysql():
        sql = 'DROP DATABASE IF EXISTS %s' % dbinfo.dbname
        get_dbdriver(dbinfo).query(sql)
    elif dbinfo.is_mongo():
        get_dbdriver(dbinfo).command("dropDatabase")

def get_dbconn(model_class):
    dbinfo = config.dbCFG.get_dbinfo(model_class)
    return __dbconnPool.get_connection(dbinfo)



