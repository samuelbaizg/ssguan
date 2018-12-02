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

from ssguan.ignitor.base.error import ProgramError
from ssguan.ignitor.orm.basedb import BaseDB
from ssguan.ignitor.orm.sqlclient import sqlclient
from ssguan.ignitor.base import struct

class SqlDB(BaseDB):
    
    def __init__(self, dbinfo):
        BaseDB.__init__(self, dbinfo)
        self.__sqlclient = self.__get_sqlclient(dbinfo)
    
    def get_dbclient(self):
        return self.__sqlclient
    
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
            self.__sqlclient.query(sql)
            return True
        else:
            return False
    
    def delete_schema(self, model_class):
        sql = 'DROP TABLE IF EXISTS %s;' % model_class.get_modelname()
        self.__sqlclient.query(sql)
        return True
    
    def has_schema(self, model_class):
        sql = "SHOW TABLES LIKE '%s'" % model_class.get_modelname()
        result = self.__sqlclient.query(sql)
        return result.length > 0
    
    def exist_property(self, model_class, property_name):
        sql = "SHOW COLUMNS FROM %s LIKE '%s'" % (model_class.get_modelname(), property_name)
        result = self.__sqlclient.query(sql)
        return result.length > 0
    
    def add_property(self, model_class, property_name, property_instance):
        if not self.exist_property(model_class, property_name):
            sql = "ALTER TABLE %s ADD %s %s" % (model_class.get_modelname(), property_name, property_instance.db_data_type())
            self.__sqlclient.query(sql)
            return True
        else:
            return False
    
    def change_property(self, model_class, old_property_name, new_property_name, property_instance):
        if not self.exist_property(model_class, old_property_name):
            raise ProgramError("%s doesn't exist property - %s", model_class.get_modelname(), old_property_name)
        else:
            sql = "ALTER TABLE %s CHANGE %s %s %s" % (model_class.get_modelname(), old_property_name, new_property_name, property_instance.db_data_type())
            self.__sqlclient.query(sql)
            return True     
    
    def drop_property(self, model_class, property_name):
        if not self.exist_property(model_class, property_name):
            raise ProgramError("%s doesn't exist property - %s", model_class.get_modelname(), property_name)
        else:
            sql = "ALTER TABLE %s DROP %s;" % (model_class.get_modelname(), property_name)
            self.__sqlclient.query(sql)
            return True
            
    def drop_index(self, model_class, index_name):
        sql = "DROP INDEX %s ON %s" % (index_name, model_class.get_modelname())
        self.__sqlclient.query(sql)
        return True
    
    def insert(self, model_name, **props):
        key = self.__sqlclient.insert(model_name, **props)
        return key
        
    def update_by_key(self, model_name, keyname, keyvalue, **props):
        keyvalue = self._normalize_keyvalue(keyvalue)
        rowcount = self.__sqlclient.update(model_name, where="%s = %s" % (keyname, keyvalue), **props)
        return int(rowcount)
    
    def delete_by_key(self, model_name, keyname, keyvalue):
        keyvalue = self._normalize_keyvalue(keyvalue)
        results = self.__sqlclient.delete(model_name, where="%s = %s" % (keyname, keyvalue))
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
        result = self.__sqlclient.query(sql, args=dict(where_vars, **set_clause[1]))
        return result
    
    def delete_multiple(self, query, **props):
        ql = query.get_ql()
        results = None
        if ql != None:
            sql = self._to_sql(query) if ql is None else ql[0]
            sql_vars = None if ql is None or len(ql) == 1 else ql[1]
            results = self.__sqlclient.query(sql, sql_vars)
        else:
            sfrom = self._from_clause(query, aliased=True)
            (where, where_vars) = self._where_clause(query, aliased=True)
            if len(where) == 0:
                # raise ProgramError("where can't be empty when batch deleting records.")
                results = self.__sqlclient.delete(sfrom, "1 = 1")
            else:
                results = self.__sqlclient.delete(sfrom, where, args=where_vars)
        return results
    
    def get_by_key(self, model_class, keyvalue):
        keyvalue = self._normalize_keyvalue(keyvalue)
        what = ",".join(model_class.get_properties(persistent=True).keys())
        
        result = self.__sqlclient.select(model_class.get_modelname(), what=what, where="%s = %s" % (model_class.get_keyname(), keyvalue))
        if result.length > 0:
            m = result[0]
            mo = model_class(entityinst=True, **m)
            return mo._to_non_entityinst()
        else:
            return None
    
    def find(self, query, limit, offset=0, paging=False, metadata=None, mocallback=None):
        (sql, sql_vars) = self._get_sql(query)
        if paging is False:
            results_sql = sql + " LIMIT %d OFFSET %d" % (limit, offset)
            results = self.__sqlclient.query(results_sql, sql_vars)
            results = self._transform_found_results(query, results, results.length, metadata, mocallback)
            return results
        else:
            page = offset if offset > 0 else 1
            offset = limit * (page - 1)
            results_sql = sql + " LIMIT %d OFFSET %d" % (limit, offset)
            results = self.__sqlclient.query(results_sql, sql_vars)
            results = self._transform_found_results(query, results, results.length, metadata, mocallback)
            
            fromindex = sql.upper().find("FROM")
            count_sql = "SELECT COUNT(*) AS count %s" % sql[fromindex:]
            count = self.__sqlclient.query(count_sql, sql_vars)[0].count
            return struct.gen_pager(page, count, limit, results)
        
    def _find_one_and_update(self, query, new=False, metadata=None, mocallback=None):
        rtnmodel = None
        if query.count() > 0:
            rtnmodel = query.get()
            set_clause = self._set_clause(query)
            sql = "UPDATE %s SET %s" % (rtnmodel.get_modelname(), set_clause[0])
            sql += " WHERE %s = %s " % (rtnmodel.get_keyname(), self._normalize_keyvalue(rtnmodel.key()))
            self.__sqlclient.query(sql, args=set_clause[1])
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
        quanity = self.__sqlclient.query(count_sql, args=sql_vars)[0].count
        return quanity
    
    
    @classmethod    
    def _normalize_keyvalue(cls, keyvalue):
        value = keyvalue
        if isinstance(value, str):
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
                if isinstance(value, str):
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
    
    def __get_sqlclient(self, dbinfo):
        convs = None
        if dbinfo.conv is None:
            from MySQLdb.constants import FIELD_TYPE
            from MySQLdb.converters import conversions
            convs = conversions.copy()
            convs[FIELD_TYPE.DECIMAL] = float
            convs[FIELD_TYPE.NEWDECIMAL] = float
        else:
            convs = dbinfo.get_conv()
        if dbinfo.dbname is None or dbinfo.dbname == '':
            dbdriver = sqlclient(dbn=dbinfo.dbtype, host=dbinfo.host, port=int(dbinfo.port), user=dbinfo.username, pw=dbinfo.password, conv=convs)
        else:
            dbdriver = sqlclient(dbn=dbinfo.dbtype, host=dbinfo.host, port=int(dbinfo.port), user=dbinfo.username, pw=dbinfo.password, conv=convs, db=dbinfo.dbname)
        return dbdriver
