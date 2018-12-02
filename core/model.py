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
from decimal import Decimal
import re

import conf
from core.error import RequiredError, CoreError, DataExpiredError
from core.properti import UniqueValidator
from db import dbutil
import dtutil
import properti


EMPTY_UID = -1
SYSTEM_UID = -2

CORE_MODULE_NAME = "core"
AUTO_INCREMENT_KEY_NAME = "uid"
DEFAULT_FETCH_LIMIT = 100000000


class PropertiedClass(type):
    def __init__(cls, name, bases, dct, map_kind=True):
        super(PropertiedClass, cls).__init__(name, bases, dct)
        _initialize_properties(cls, name, bases, dct)

def _initialize_properties(model_class, name, bases, dct):
    model_class._properties = {}
    property_source = {}
    
    def get_attr_source(name, cls):
        for src_cls  in cls.mro():
            if name in src_cls.__dict__:
                return src_cls

    defined = set()
    for base in bases:
        if hasattr(base, '_properties'):
            property_keys = set(base._properties.keys())
            duplicate_property_keys = defined & property_keys
            for dupe_prop_name in duplicate_property_keys:
                old_source = property_source[dupe_prop_name] = get_attr_source(
                    dupe_prop_name, property_source[dupe_prop_name])
                new_source = get_attr_source(dupe_prop_name, base)
                if old_source != new_source:
                    raise CoreError(
                      'Duplicate property, %s, is inherited from both %s and %s.',
                      dupe_prop_name, old_source.__name__, new_source.__name__)
    
            property_keys -= duplicate_property_keys
            if property_keys:
                defined |= property_keys
                property_source.update(dict.fromkeys(property_keys, base))
                model_class._properties.update(base._properties)
                
    for attr_name in dct.keys():
        attr = dct[attr_name]
        if isinstance(attr, properti.Property):
            if attr_name in defined:
                raise CoreError('Duplicate property: %s' % attr_name)
            defined.add(attr_name)
            model_class._properties[attr_name] = attr
            attr.__property_config__(model_class, attr_name)

class BaseModel(object):
    __metaclass__ = PropertiedClass
    
    MODULE = None
    KEYMETA = (AUTO_INCREMENT_KEY_NAME, False)
    
    uid = properti.IntegerProperty("key", length=20)
    
    def __new__(cls, *args, **unused_kwds):
        bm = super(BaseModel, cls).__new__(cls)
        if cls.KEYMETA[0] != AUTO_INCREMENT_KEY_NAME:
            if cls._properties.has_key(AUTO_INCREMENT_KEY_NAME):
                cls._properties.pop(AUTO_INCREMENT_KEY_NAME)
        return bm
    
    
    def __init__(self, entityinst=False, **kwds):
        self._extproperties = {}
        self._entityinst = entityinst
        for prop in self._properties.values():
            value = prop.default_value()
            if value != None:
                prop.__set__(self, value)
        
        if kwds != None:
            for (key, value) in kwds.items():
                setattr(self, key, value)
                    
    def __getattr__(self, name):
        if name != "_extproperties" and "__" not in name:
            tname = name
            
            if tname.find("_") == 0:
                tname = name[1:]
            if tname not in self._properties.keys():
                return self._extproperties[name]
            else:
                if hasattr(object, name):
                    return object.__getattr__(self, name)
                else:
                    return None
        else:
            return object.__getattr__(self, name)
    
    def __setattr__(self, name, value):
        if name != "_extproperties" and name != "_entityinst":
            value = self._normalize_property_value(name, value)
            tname = name
            if "__" not in tname and tname.find("_") == 0:
                tname = name[1:]
            if tname not in self._properties.keys():
                self._extproperties[name] = value
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)
            
    def __hasattr__(self, name):
        if self._properties.has_key(name):
            return True
        elif self._extproperties.has_key(name):
            return True
        else:
            return False
    
    @classmethod    
    def get_modelname(cls):
        if cls.MODULE is None:
            raise CoreError("MODULE is not defined in the model %s" , cls.__name__)
        return ("%s_%s" % (cls.MODULE , cls.__name__)).lower()

    @classmethod
    def get_keyname(cls):
        if cls.KEYMETA is None:
            raise CoreError("KEYMETA is not defined in the model %s" , cls.__name__)
        return cls.KEYMETA[0]
    
    @classmethod
    def is_auto_incr_key(cls):
        return cls.KEYMETA[1] is True
    
    def get_keyvalue(self):
        return getattr(self, self.get_keyname())
    
    @classmethod
    def create_table(cls, conn=None):
        sql = "SHOW TABLES LIKE '%s'" % cls.get_modelname()
        result = cls._get_conn(conn).query(sql)
        if len(result) == 0:
            sql = 'CREATE TABLE %s (' % cls.get_modelname()
            sqlp = cls._create_key_sqlp()
            comma = "," if len(sqlp) > 0 else ""
            sql += " %s%s" % (sqlp, comma)
            for pname in cls.get_properties(persistent=True):
                if pname != cls.get_keyname() and pname != AUTO_INCREMENT_KEY_NAME:
                    prop = getattr(cls, pname)
                    sql += " %s," % cls._create_property_sqlp(prop)
            sql += 'PRIMARY KEY (%s)' % cls.get_keyname()
            sqlp = cls._create_table_sqlp()
            comma = "," if len(sqlp) > 0 else ""
            sql += '%s%s' % (comma, sqlp)
            sql += ') DEFAULT CHARSET=utf8;'
            cls._get_conn(conn).query(sql)
    
    @classmethod
    def _create_key_sqlp(cls):
        keytype = getattr(cls, cls.get_keyname()).db_data_type()
        if cls.KEYMETA[1] is True:
            sql = '%s %s NOT NULL AUTO_INCREMENT' % (cls.get_keyname(), keytype)
        else:
            sql = '%s %s NOT NULL' % (cls.get_keyname(), keytype)
        return sql
    
    @classmethod
    def _create_property_sqlp(cls, prop):
        sql = '%s %s DEFAULT NULL' % (prop.name, prop.db_data_type())
        return sql
    
    @classmethod
    def _create_table_sqlp(cls):
        return ""
    
    @classmethod
    def get_properties(cls, persistent=None, labelkey=False):
        props = {}
        for key, prop in cls._properties.items():
            if not key.startswith("_") and (persistent is None or prop.persistent == persistent):
                if labelkey:
                    props[prop.get_label()] = prop
                else:
                    props[key] = prop
        return props
    
    @classmethod
    def get_property(cls, propname):
        return cls._properties[propname]
    
    @classmethod
    def is_persistent(cls, propname=None):
        if propname is not None:
            if not cls._properties.has_key(propname):
                raise CoreError("propname %s is not defined in the Model.", propname)
            return cls._properties[propname].persistent
        for prop in cls._properties.values():
            if prop.persistent is True:
                return True
        return False
    
    def key(self):
        return self.get_keyvalue()
    
    def to_dict(self):
        tdt = {}
        pd = self._properties
        for key, prop in pd.items():
            if not key.startswith("_"):
                tdt[prop.get_label()] = prop.normalize_value(getattr(self, key))
        for key, value in self._extproperties.items():
            if not key.startswith("_"):
                tdt[key] = value
        return tdt
    
    def _normalize_property_value(self, name, value):
        if isinstance(value, Decimal):
            value = float(value)
        return value
    
    @classmethod
    def delete_table(cls, conn=None):
        sql = 'DROP TABLE IF EXISTS %s;' % cls.get_modelname()
        cls._get_conn(conn).query(sql)
        if cls.get_keyname() == AUTO_INCREMENT_KEY_NAME:
            Uid.del_id(cls, conn)
    
    def create(self, conn=None):
        props = self.validate_props(persistent=True)
        if self.get_keyname() == AUTO_INCREMENT_KEY_NAME:    
            uid = Uid.new_id(self)
            setattr(self, self.get_keyname(), uid)
            props[self.get_keyname()] = uid
        else:
            if self.get_keyvalue() is None and not self.is_auto_incr_key():
                raise CoreError("Key value can't be None when you create a new non-uid-as-primary-key model %s.", self.get_modelname()) 
        
        key = self._get_conn(conn).insert(self.get_modelname(), **props)
        if self.is_auto_incr_key():
            setattr(self, self.get_keyname(), key)
        return self
        
    def update(self, conn=None):
        props = self.validate_props(persistent=True)
        value = self._normalize_keyvalue(self.get_keyvalue())
        self._get_conn(conn).update(self.get_modelname(), where="%s = %s" % (self.get_keyname(), value), **props)
        return self
        
    def delete(self, conn=None):
        value = self._normalize_keyvalue(self.get_keyvalue())
        self._get_conn(conn).delete(self.get_modelname(), where="%s = %s" % (self.get_keyname(), value))
    
    def put(self, conn=None):
        if self.get_keyname() != AUTO_INCREMENT_KEY_NAME:
            raise CoreError("Method put can't be called when model is not a non-uid-as-primary-key model.")
        
        if self.get_keyvalue() == None:
            self.create(conn=conn)
        else:
            self.update(conn=conn)
            
        return self
    
    def validate_props(self, persistent=None):
        props = {}
        for pname, value in self.get_properties(persistent).items():
            if pname != self.get_keyname() and pname != AUTO_INCREMENT_KEY_NAME:
                pvalue = getattr(self, pname)
                if value.empty(pvalue) and value.required:
                    raise RequiredError(value.get_label_i18n_key())
                if isinstance(value, properti.BooleanProperty):
                    if pvalue == True:
                        props[pname] = 1
                    else:
                        props[pname] = 0
                else:
                    props[pname] = pvalue
                
                value.validate(pvalue, model_instance=self)
        
        self.get_property(self.get_keyname()).validate(self.get_keyvalue(), model_instance=self)
        
        props[self.get_keyname()] = self.get_keyvalue()
        return props
    
    @classmethod
    def all(cls, alias=None):
        if alias is None:
            alias = cls.get_modelname()
        return BaseQuery(cls, alias)
    
    @classmethod
    def get_by_key(cls, keyvalue, conn=None):
        keyvalue = cls._normalize_keyvalue(keyvalue)
        what = ",".join(cls.get_properties(persistent=True).keys())    
        result = cls._get_conn(conn).select(cls.get_modelname(), what=what, where="%s = %s" % (cls.get_keyname(), keyvalue))
        if len(result) > 0:
            m = result[0]
            mo = cls(entityinst=True, **m)
            return mo._to_non_entityinst()
        else:
            return None
    
    @classmethod    
    def _normalize_keyvalue(cls, keyvalue):
        keyprop = cls.get_properties()[cls.get_keyname()]
        value = keyvalue
        if isinstance(keyprop, properti.StringProperty):
            value = "'" + value + "'"
        return value
    
    def _is_entityinst(self):
        return self._entityinst
    
    def _to_non_entityinst(self):
        self._entityinst = False
        return self
    
    @classmethod
    def _get_conn(cls, conn):
        if conn is None:
            return dbutil.get_dbconn()
        else:
            return conn

class BaseResolver(object):
    
    def resolve(self, query, **kwargs):
        """To override by sub-class"""
        raise NotImplementedError()

class BaseQuery(object):
    
    DESCENDING = 'desc'
    ASCENDING = 'asc'
    
    _OPERATORS = ['ex', '<', '<=', '>', '>=', '=', '!=', 'in', 'not in', 'like', 'is']
    _FILTER_REGEX = re.compile(
    '^\s*([^\s]+)(\s+(%s)\s*)?$' % '|'.join(_OPERATORS),
    re.IGNORECASE | re.UNICODE)
    

    def __init__(self, model_class, alias):
        if model_class == None or isinstance(model_class, BaseModel):
            raise CoreError("model_class can't be None and non-sub-class-of-Model.")
        if alias == None or len(alias.strip()) == 0:
            raise CoreError("alias can't be None or empty.")
        self._model_class = model_class
        self._model_alias = alias
        self._query_sets = []
        self._orderings = []
        self._model_names = []
        self._select_exps = []
        self._update_sets = {}
        tablename = model_class.get_modelname()
        if tablename is not None and tablename != '':
            self.model(model_class.get_modelname(), alias)
        self._whats = []
        self._groupings = []
        
        self._sql = None
        self._sql_vars = None
        self._results = None
        
    def extend(self, resolvers, **kwargs):
        l = []
        if isinstance(resolvers, list):
            l.extend(resolvers)
        elif isinstance(resolvers, BaseResolver):
            l.append(resolvers)
        else:
            raise CoreError("%r is not instance of BaseResolver or List", resolvers)
        for resolver in l:
            resolver.resolve(self, **kwargs)
        return self

    def filter(self, property_operator, value, wrapper=True, logic="and", parenthesis=None, replace=False):
        match = self._FILTER_REGEX.match(property_operator)
        prop_name = ""
        logic = logic.lower()
        if logic != 'and' and logic != 'or':
            raise CoreError("logic %s is not and AND or" , logic)
        if parenthesis is not None and parenthesis != '(' and parenthesis != ")":
            raise CoreError("parenthesis %s is not ( or )" , parenthesis)
        if match != None and match.group(1) is not None:
            prop_name = match.group(1)
        else:
            raise CoreError('the property operator %s includes the illegal operator' , property_operator)
        
        if match.group(3) is not None:
            operator = match.group(3)
        else:
            operator = '='
            
        if property_operator != 'ex ex' and len(self._model_names) == 1 and self._model_class.is_persistent():
            pname = prop_name if "." not in prop_name else prop_name.split(".")[1]
            if not self._model_class.is_persistent(pname):
                raise CoreError('the property %s is not the persistent property in model %s ' , pname, self._model_class.__name__)
            
            prop = getattr(self._model_class, pname)
            if value != None and operator != 'in' and operator != 'not in' and wrapper and not isinstance(value, prop.data_type):
                raise CoreError('the value %s of the property %s  is not the type %s ' , str(value), pname, str(prop.data_type))     
        
        if operator.lower() == 'in' or operator.lower() == 'not in':
            if wrapper is True:
                if not isinstance(value, (list, tuple)):
                    raise CoreError('Argument to the "in" operator must be a list or wrapper=False')
                value = [self._normalize_query_parameter(v) for v in value]
            else:
                value = value
        else:
            if isinstance(value, (list, tuple)):
                raise CoreError('Filtering on lists is not supported for the operator %s', operator)
            else:
                value = self._normalize_query_parameter(value)
        self._append_query_set(prop_name, operator, value, wrapper, logic, parenthesis, replace)
        return self
    
    def has_filter(self, propname, operator=None):
        for query_set in self._query_sets:
            if query_set[0] == propname and (operator == None or query_set[1] == operator):
                return True
        return False
    
    def get_model_alias(self, model_name):
        alias = None
        for model in self._model_names:
            if model[0] == model_name:
                alias = model[1]
                break
        return alias
    
    def order(self, prop):
        order = BaseQuery.ASCENDING
        if prop.startswith('-'):
            prop = prop[1:]
            order = BaseQuery.DESCENDING
        self._orderings.append((prop, order))
        return self
    
    def select(self, expression):
        self._select_exps.append(expression)
        return self
    
    def what(self, name, alias=None):
        if alias == '':
            raise CoreError("alias can't be empty string")
        
        if alias == None:
            alias = name if "." not in name else name.split(".")[1]
        self._whats.append((name, alias))
        return self
    
    def group(self, prop):
        self._groupings.append(prop)
        return self
        
    def model(self, model_name, alias="", join=None, on=None):
        jt = ["LEFT", "RIGHT", "INNER", "OUTER"]
        if join is not None:
            join = join.upper()
            if join not in jt:
                raise CoreError('the value %s of the property %s is not in %s ' % (str(join), "".join(jt)))
            else:
                if on is None:
                    raise CoreError('the parameter on can not be None if join is not None ')
        self._model_names.append((model_name, alias, join, on))
        return self
    
    # Eg. "SELECT * FROM foo WHERE x = $x", vars=dict(x='f')    
    def sql(self, sql, sql_vars=None):
        self._sql = sql
        self._sql_vars = sql_vars
        return self
    
    # metadata is directory and the key, value is prop name, subclass of Property 
    # {'f_bool', properti.BooleanProperty()}
    def fetch(self, limit=DEFAULT_FETCH_LIMIT, offset=0, paging=False, metadata=None, model_proc=None, conn=None):
        sql = self._sql
        if sql is None:
            sql = self._to_sql()
        
        if paging is False:
            results_sql = sql + " LIMIT %d OFFSET %d" % (limit, offset)
            results = self._model_class._get_conn(conn).query(results_sql, self._sql_vars)
            self._results = self._transform_fetched_results(results, metadata, model_proc)
            return self._results
        else:
            page = offset if offset > 0 else 1
            offset = limit * (page - 1)
            results_sql = sql + " LIMIT %d OFFSET %d" % (limit, offset)
            results = self._model_class._get_conn(conn).query(results_sql, self._sql_vars)
            self._results = self._transform_fetched_results(results, metadata, model_proc)
            
            fromindex = sql.upper().find("FROM")
            count_sql = "SELECT COUNT(*) AS count %s" % sql[fromindex:]
            count = self._model_class._get_conn(conn).query(count_sql, self._sql_vars)[0].count
            total = int((count + limit - 1) / limit)
            pager = self.get_empty_pager()
            pager.total = total
            if page > total:
                page = total
            pager.page = page
            pager.count = count
            pager.records = self._results
            return pager
        
    def get_empty_pager(self):
        pager = stdModel()
        pager.total = 0
        pager.page = 1
        pager.count = 0
        pager.records = []
        return pager
    
    def update(self, conn=None):
        tablename = self._model_class.get_modelname()
        where = self._where_clause(aliased=False)
        if len(where) == 0:
            raise CoreError("where can't be empty when batch updating records.")
        result = self._model_class._get_conn(conn).update(tablename, where=where, **self._update_sets)
        return result
    
    def delete(self, conn=None):
        if self._sql != None:
            results = self._model_class._get_conn(conn).query(self._sql, self._sql_vars)
        else:
            sfrom = self._from_clause(aliased=True)
            where = self._where_clause(aliased=True)
            if len(where) == 0:
                raise CoreError("where can't be empty when batch deleting records.")
            results = self._model_class._get_conn(conn).delete(sfrom, where)
        results = int(results)
        return results
   
    
    def get(self, metadata=None, model_proc=None, conn=None):
        if self._results == None:
            self._results = self.fetch(1, metadata=metadata, model_proc=model_proc, conn=conn)
        if len(self._results) > 0:
            return self._results[0]
        else:
            return None
        
    def set(self, propname, value):
        if not self._model_class.get_properties().has_key(propname):
            raise CoreError("propname %s is not a property of model %s" % (propname, self._model_class))
        
        if not self._model_class.is_persistent(propname):
            raise CoreError("propname %s is not a persistent propperty." % propname)
        prop = self._model_class.get_properties()[propname]
        value = prop.validate(value, self)
        if isinstance(prop, properti.BooleanProperty):
            if value == True:
                value = 1
            else:
                value = 0
        value = self._normalize_query_parameter(value)
        self._update_sets[propname] = value
        
    
    def count(self, conn=None):
        quanity = 0
        if self._results == None:
            sql = self._sql
            if sql is None:
                sql = self._to_sql()
            fromindex = sql.upper().find("FROM")
            count_sql = "SELECT COUNT(*) AS count %s" % sql[fromindex:]
            quanity = self._model_class._get_conn(conn).query(count_sql, self._sql_vars)[0].count
        else:
            quanity = len(self._results)
        return quanity
    
    def clear(self):
        self._results = None
        self._query_sets = []
        self._orderings = []
    
    def _transform_fetched_results(self, results, metadata, model_proc):
        models = []
        if metadata is None:
            for result in results:
                mo = self._model_class(entityinst=True, **result)
                if model_proc is not None:
                        model_proc(mo)
                models.append(mo._to_non_entityinst())
        else:
            for result in results:
                    for key, prop in metadata.items():
                        if result.has_key(key):
                            value = result.get(key)
                            value = prop.normalize_value(value)
                            setattr(result, key, value)
                    mo = self._model_class(entityinst=True, **result)
                    if model_proc is not None:
                        model_proc(mo)
                    models.append(mo._to_non_entityinst())
        return models
            
    def _append_query_set(self, propname, operator, value, wrapper, logic, parenthesis, replace):
        if replace is True:
            query_sets = []
            if len(self._query_sets) == 0:
                self._query_sets.append((propname, operator, value, wrapper, logic, parenthesis))
            else:
                for query_set in self._query_sets:
                    if query_set[0] == propname:
                        query_set_1 = (propname, operator, value, wrapper, logic, parenthesis)
                        query_sets.append(query_set_1)
                    else:
                        query_sets.append(query_set)
                self._query_sets = query_sets
        else:
            self._query_sets.append((propname, operator, value, wrapper, logic, parenthesis))
            
        
    def _normalize_query_parameter(self, value):
        if (isinstance(value, datetime.date) and not isinstance(value, datetime.datetime)):
            value = datetime.date(value.year, value.month, value.day)
        elif isinstance(value, datetime.time):
            value = datetime.datetime(1970, 1, 1, value.hour, value.minute, value.second, value.microsecond)
        value = "null" if value is None else value
        return value
    
    def _wrap_query_parameter(self, value, wrapper):
        if wrapper is not True:
            return value
        if isinstance(value, basestring):
            value = "'%s'" % value
        elif isinstance(value, datetime.datetime):
            value = "'%s'" % value
        elif isinstance(value, datetime.date):
            value = "'%s'" % value
        elif isinstance(value, bool):
            if value == True:
                value = "%d" % 1
            else:
                value = "%d" % 0
        value = str(value)
        return value
    
    def _select_clause(self):
        select = ""
        for sel in self._select_exps:
            select += sel + " "
        return select
    
    def _what_clause(self):
        whats = self._whats
        if len(whats) == 0:
            for key in self._model_class.get_properties(persistent=True).keys():
                if key != AUTO_INCREMENT_KEY_NAME: 
                    self.what("%s.%s" % (self._model_alias, key), key)
                    
            if (self._model_class.get_keyname() == AUTO_INCREMENT_KEY_NAME):
                self.what("%s.%s" % (self._model_alias, AUTO_INCREMENT_KEY_NAME))
                    
        mw = []
        for what in whats:
            mw.append("%s AS %s" % (what[0], what[1]))
        return ",".join(mw)
    
    def _from_clause(self, aliased=False):
        length = len(self._model_names)
        if length == 0:
            self.model(self._model_class.get_modelname(), self._model_alias)
        mc = []
        on = []
        for ma in self._model_names:
            if length > 1 and len(ma[1]) == 0 and aliased is False:
                raise CoreError("%s doesn't has alias name. Alias name must be assigned when you query from multiple tables." % ma[0])
            if ma[2] is not None:
                mc.append(" %s JOIN %s %s" % (ma[2], ma[0], ma[1]))
                on.append(" %s AND" % ma[3])
            else:
                if aliased is True:
                    mc.append('%s,' % (ma[0]))
                else:
                    mc.append('%s %s,' % (ma[0], ma[1]))
        if len(on) == 0:
            return "".join(mc)[:-1]
        else:
            mc[0] = mc[0][:-1] + " "
            return " %s ON %s " % ("".join(mc) , "".join(on)[:-4])  
    
   
    def _where_clause(self, aliased=False):
        where = ""
        for query_set in self._query_sets:
            propname = query_set[0]
            operator = query_set[1]
            if propname == 'ex' and operator == 'ex':
                propname = ''
                operator = ''
            else:
                if "." not in propname:
                    propname = "%s.%s" % (self._model_alias, propname)
                propname = propname if aliased is False else propname.split(".")[1]
                
            value = query_set[2]
            wrapper = query_set[3]
            logic = query_set[4]
            parenthsis = query_set[5]
            leftpa = ''
            rightpa = ''
            if parenthsis != None and parenthsis == '(':
                leftpa = '('
            if parenthsis != None and parenthsis == ')':
                rightpa = ')'
            if isinstance(value, list):
                    tmp = "("
                    for val in value:
                        tmp += "%s, " % (self._wrap_query_parameter(val, wrapper))
                    tmp = tmp[0:-2] + ")"
                    value = tmp
            else:
                value = self._wrap_query_parameter(value, wrapper)
            where += "%s %s %s %s %s %s" % (logic, leftpa, propname, operator, value, rightpa)
        
        if len(where) > 0:
            if  where.startswith("and"):
                where = where[4:]
            elif where.startswith("or"):
                where = where[3:]
        return where
    
    def _order_clause(self):
        order = ""
        for ordering in self._orderings:
            order += "%s %s , " % (ordering[0], ordering[1])
        if len(order) > 0:
            order = order[0:-2]
        return order
    
    def _group_clause(self):
        group = ""
        for g in self._groupings:
            group += " %s , " % g
        if len(group) > 0:
            group = group[0:-2]
        return group
    
    def _to_sql(self, offset=0, limit=1000):
        select = self._select_clause()
        what = self._what_clause()
        sfrom = self._from_clause()
        sql = "SELECT %s %s FROM %s" % (select, what, sfrom)
        where = self._where_clause()
        order = self._order_clause()
        if len(where) > 0:
            sql += " WHERE %s" % where
        group = self._group_clause()
        if len(group) > 0:
            sql += " GROUP BY %s" % group
        if len(order) > 0:
            sql += " ORDER BY %s " % order
        return sql      

class Uid(BaseModel):
    MODULE = CORE_MODULE_NAME
    
    model_name = properti.StringProperty(required=True, length=20, label="modelName")
    
    @classmethod
    def _create_key_sqlp(cls):
        keytype = getattr(cls, cls.get_keyname()).db_data_type()
        sql = '%s %s NOT NULL AUTO_INCREMENT' % (cls.get_keyname(), keytype)
        return sql
    
    @classmethod
    def _create_property_sqlp(cls, prop):
        sql = '%s %s NOT NULL' % (prop.name, prop.db_data_type())
        return sql
    
    @classmethod
    def _create_table_sqlp(cls):
        return 'UNIQUE KEY %s (%s)' % ('model_name', 'model_name')
    
    @classmethod
    def new_id(cls, model_class, conn=None):
        conn = cls._get_conn(conn)
        t = conn.transaction()
        try:
            sql = "REPLACE INTO %s (model_name) VALUES ('%s');" % (cls.get_modelname(), model_class.get_modelname())
            result = conn.query(sql)
            sql = "SELECT LAST_INSERT_ID() AS uid;"
            result = conn.query(sql)
            return result[0].uid
        except:
            t.rollback()
            raise
        else:
            t.commit()
    
    @classmethod
    def del_id(cls, model_class, conn=None):
        conn = cls._get_conn(conn)
        conn.delete(cls.get_modelname(), where="model_name='%s'" % model_class.get_modelname())

    
    def create(self):
        raise CoreError("please call new_id to generate a new id.")
    
    def put(self):
        raise CoreError("please call update to update key.")
    
class stdModel(BaseModel):
    MODULE = CORE_MODULE_NAME
    KEYMETA = (None, False)
    """This is the generic model which can be used to store any values of any db query."""
    
    def __init__(self, entityinst=False, **kwds):
        super(stdModel, self).__init__(entityinst=False, **kwds)
    
    def create(self):
        raise CoreError("stdModel does not support create method.")
    
    def update(self):
        raise CoreError("stdModel does not support update method.")
    
    def delete(self):
        raise CoreError("stdModel does not support delete method.")
    
    def put(self):
        raise CoreError("stdModel does not support put method.")
    
    @classmethod
    def get_properties(cls, persistent=None):
        raise CoreError("stdModel does not support get_properties method.")
        
    @classmethod
    def get_keyname(cls):
        raise CoreError("stdModel does not support get_keyname method.")
    
    @classmethod
    def is_auto_incr_key(cls):
        raise CoreError("stdModel does not support is_auto_incr_key method.")
    
    def get_keyvalue(self):
        raise CoreError("stdModel does not support get_keyvalue method.")
    
    @classmethod
    def create_table(cls):
        raise CoreError("stdModel does not support create_table method.")
    
    @classmethod
    def delete_table(cls):
        raise CoreError("stdModel does not support delete_table method.")
    
    @classmethod
    def get_by_key(cls, keyvalue):
        raise CoreError("stdModel does not support get_by_key method.")
    
    
    @classmethod
    def get_modelname(cls):
        return None
    
    @classmethod
    def is_persistent(cls, propname=None):
        return False
    
    @classmethod
    def all(cls):
        return stdQuery(cls)

class stdQuery(BaseQuery):
    
    def __init__(self, model_class):
        super(stdQuery, self).__init__(model_class, __name__)
        
    def set(self, propname, value):
        raise CoreError("stdQuery does not support set method.")
    
    def update(self):
        raise CoreError("stdQuery does not support update method.")
    
    def delete(self):
        raise CoreError("stdQuery does not support delete method.")
    
    def filter(self, property_operator, value, wrapper=True, logic="and", parenthesis=None, replace=False):
        if "." not in property_operator:
            raise CoreError("please add model alias name before %s when you use stdModel." % property_operator)
        return BaseQuery.filter(self, property_operator, value, wrapper=wrapper, logic=logic, parenthesis=parenthesis, replace=replace)
    
    def what(self, name, alias=None):
        if "." not in name:
            raise CoreError("please add model alias name before %s when you use stdModel." % name)
        return BaseQuery.what(self, name, alias=alias)
    
    def group(self, prop):
        if "." not in prop:
            raise CoreError("please add model alias name before %s when you use stdModel." % prop)
        return BaseQuery.group(self, prop)
    
    def order(self, prop):
        if "." not in prop:
            raise CoreError("please add model alias name before %s when you use stdModel." % prop)
        return BaseQuery.order(self, prop)
    
    def _what_clause(self):
        if len(self._whats) == 0:
            raise CoreError("please assign what when you use stdModel.")
        return BaseQuery._what_clause(self)

class Resolver(BaseResolver):
    
    def __init__(self, key, value):
        self._key = key
        self._value = value
    
    def resolve(self, query, **kwargs):
        """To override by sub-class"""
        raise NotImplementedError()
        
class Model(BaseModel):
    
    created_time = properti.DateTimeProperty(required=True, auto_utcnow=True, label="createdTime")
    modified_time = properti.DateTimeProperty(required=True, auto_utcnow=True, label="modifiedTime")
    creator_id = properti.IntegerProperty(required=True, default=EMPTY_UID, label="creatorKey")
    modifier_id = properti.IntegerProperty(required=True, default=EMPTY_UID, label="modifierKey")
    row_version = properti.IntegerProperty(required=True, label="rowVersion", default=1)
    
    def __init__(self, entityinst=False, **kwds):
        super(Model, self).__init__(entityinst=entityinst, **kwds)
        
    @classmethod
    def all(cls, alias=None):
        if alias is None:
            alias = cls.get_modelname()
        return Query(cls, alias=alias)
    
    def delete(self, modifier_id, conn=None):
        if modifier_id is None:
            raise CoreError("modifier_id can't be empty when deleting a model.")
        BaseModel.delete(self, conn)
        self.get_keyvalue()
    
    def create(self, creator_id, conn=None):
        if creator_id is None or creator_id == EMPTY_UID:
            raise CoreError("modifier_id can't be empty when creating a model.")
        self.creator_id = creator_id
        self.modifier_id = creator_id
        self.created_time = dtutil.utcnow()
        self.modified_time = dtutil.utcnow()
        self.row_version = 1
        BaseModel.create(self, conn=conn)
    
    def update(self, modifier_id, conn=None):
        if modifier_id is None or modifier_id == EMPTY_UID:
            raise CoreError("modifier_id can't be empty when updating a model.")
        lastmodel = self.get_by_key(self.get_keyvalue(), conn)
        if lastmodel.row_version != self.row_version:
            raise DataExpiredError()
        self.update_timestamp(modifier_id)
        
        changedprops = []
        
        for key, prop in self.get_properties(persistent=True).items():
            value1 = getattr(lastmodel, key)
            value2 = getattr(self, key)
            if prop.logged is True and value1 != value2:
                changedprops.append((key, prop.get_label_i18n_key(), value1, value2))
                            
        BaseModel.update(self, conn=conn)
        if len(changedprops) > 0:
            self._add_mclog(changedprops, modifier_id, conn)
        
    def put(self, modifier_id, conn=None):
        if self.get_keyname() != AUTO_INCREMENT_KEY_NAME:
            raise CoreError("Put can't be called when model is not a non-uid-as-primary-key model.")
        
        if self.get_keyvalue() == None:
            self.create(modifier_id, conn=conn)
        else:
            self.update(modifier_id, conn=conn)
            
        return self
    
    def update_timestamp(self, modifier_id):
        self.modifier_id = modifier_id
        self.modified_time = dtutil.utcnow()
        self.row_version += 1
        
    def _add_mclog(self, changedprops, modifier_id, conn):
        changelog = MCLog()
        changelog.model_name = self.get_modelname()
        changelog.model_key = str(self.get_keyvalue())
        changelog.user_id = modifier_id
        changelog.create(conn=conn)
        for cp in changedprops:
            cldetail = MCLogDetail()
            cldetail.changelog_id = changelog.mclog_id
            cldetail.field_name = cp[0]
            cldetail.field_i18nkey = cp[1]
            cldetail.fvalue_last = str(cp[2])
            cldetail.fvalue_present = str(cp[3])
            cldetail.create(conn=conn)
     
    def to_dict(self):
        tdt = BaseModel.to_dict(self)
        tzstr = conf.get_preferred_timezone()
       
        ctp = self.get_property("created_time")
        ctp.fmt = conf.get_datesecond_py_format()
        created_time = dtutil.to_local(self.created_time, tzstr)
        tdt["createdTime"] = ctp.to_string(created_time)
        
        mtp = self.get_property("modified_time")
        mtp.fmt = conf.get_datesecond_py_format()
        modified_time = dtutil.to_local(self.modified_time, tzstr)
        tdt["modifiedTime"] = mtp.to_string(modified_time)
        
        return tdt
         
            
class Query(BaseQuery):
    
    def update(self, modifier_id, conn=None):
        if modifier_id == None or modifier_id == EMPTY_UID:
            raise CoreError("modifier_id can't be empty when deleting a model.")
        self.set("modified_time", datetime.datetime.utcnow())
        self.set("modifier_id", modifier_id)
        for key in self._update_sets.keys():
            if self._model_class.get_properties(True)[key].logged:
                raise CoreError("Query.update doesn't support to update the logged property %r" % key)
        result = BaseQuery.update(self, conn=conn)
        return result
    
    def delete(self, modifier_id, conn=None):
        if modifier_id == None or modifier_id == EMPTY_UID:
            raise CoreError("modifier_id can't be None when deleting a model.")
        result = BaseQuery.delete(self, conn=conn)
        return result
    
class Session(BaseModel):
    MODULE = CORE_MODULE_NAME
    KEYMETA = ("session_id", False)
    
    session_id = properti.StringProperty("sessionId", required=True, length=128)
    atime = properti.DateTimeProperty("aTime", required=True)
    data = properti.StringProperty("data", required=False, length=65535)
    
class Log(BaseModel):
    MODULE = CORE_MODULE_NAME
    KEYMETA = ("l_id", True)

    l_id = properti.IntegerProperty("logKey", required=False, length=20)
    l_level = properti.StringProperty("logLevel", required=True, length=10, choices=["DEBUG", "INFO", "WARN", "ERROR", "FATAL"])
    l_message = properti.StringProperty("message", required=True, length=4294967295)
    logged_time = properti.DateTimeProperty("loggedTime", required=True, auto_utcnow=True)

class MCLog(BaseModel):
    MODULE = CORE_MODULE_NAME
    KEYMETA = ("mclog_id", True)
    
    mclog_id = properti.IntegerProperty("cLogId", required=False, length=20)
    model_name = properti.StringProperty("modelName", required=True, length=80)
    model_key = properti.StringProperty("modelKey", required=True)
    user_id = properti.IntegerProperty("userKey", required=True)
    changed_time = properti.DateTimeProperty("changedTime", required=True, auto_utcnow=True)
    
class MCLogDetail(BaseModel):
    MODULE = CORE_MODULE_NAME
    KEYMETA = ("mclogdetail_id", True)
    
    mclogdetail_id = properti.IntegerProperty("logDetailId", required=False, length=20)
    changelog_id = properti.IntegerProperty("cLogId", required=True)
    field_name = properti.StringProperty("fieldName", required=True, length=80)
    field_i18nkey = properti.StringProperty("fieldI18nKey", required=True, length=80)
    fvalue_last = properti.StringProperty("lastValue", required=False, length=4294967295)
    fvalue_present = properti.StringProperty("presentValue", required=False, length=4294967295)
    model_name = properti.StringProperty("modelName", persistent=False)
    model_key = properti.StringProperty("modelKey", persistent=False)
    user_id = properti.IntegerProperty("userKey", persistent=False)
    changed_time = properti.DateTimeProperty("changedTime",persistent=False)

class Migration(Model):
    MODULE = CORE_MODULE_NAME
    KEYMETA = ("ver_id", False)
    
    ver_id = properti.IntegerProperty("versionId", length=4, required=True)
    is_upgraded = properti.BooleanProperty("isUpgraded", default=False)
    migration_time = properti.DateTimeProperty("migrationTime", auto_utcnow=True)
    
class SysProp(Model):
    MODULE = CORE_MODULE_NAME
    KEYMETA = ("p_key", False)
    
    p_key = properti.StringProperty("propKey", required=True)
    p_value = properti.StringProperty("propValue", required=True, length=255)

class I18n(Model):
    
    MODULE = CORE_MODULE_NAME
    KEYMETA = ("i1_id", True)
    
    i1_id = properti.IntegerProperty("id", required=False, length=20)
    i1_key = properti.StringProperty("key", required=True, length=40)
    i1_locale = properti.StringProperty("i18nLocale", required=True, length=4096)
    i1_type = properti.StringProperty("i18nType", required=False, length=20)
    i1_message = properti.StringProperty("i18nMessage", required=True, length=4096)
    
    
class User(Model):
    MODULE = CORE_MODULE_NAME
    ANONYMOUS_ACCOUNT_NAME = "anonymous"
    
    u_name = properti.StringProperty("userName", required=False, validator=[ properti.IllegalValidator()])
    u_email = properti.StringProperty("userEmail", required=False, validator=[properti.IllegalValidator()])
    u_account = properti.StringProperty("accountName", required=True, validator=[properti.UniqueValidator("u_account"), properti.IllegalValidator()])
    u_password = properti.StringProperty("password", required=True, validator=properti.IllegalValidator())
    is_disabled = properti.BooleanProperty("isDisabled", default=False)
    
    logined_times = properti.IntegerProperty("loginedTime", required=True, default=0)
    last_logined_time = properti.DateTimeProperty("lastLoginedTime", required=False, auto_utcnow=False)
    
    def is_anonymous(self):
        return self.u_name == self.ANONYMOUS_ACCOUNT_NAME
    
class UserProp(Model):
    MODULE = CORE_MODULE_NAME
    
    p_key = properti.StringProperty("propKey", required=True, validator=properti.IllegalValidator())
    p_value = properti.StringProperty("propValue", required=True, length=255, validator=properti.IllegalValidator())
    user_id = properti.IntegerProperty("userKey", required=True)

class Operation(Model):
    MODULE = CORE_MODULE_NAME
    KEYMETA = ("operation_key", False)
    operation_key = properti.StringProperty("operationKey", required=True, validator=[properti.UniqueValidator("operation_key")])
    resource_oql = properti.StringProperty("resourceOql", required=False, length=1024)
    handler_classes = properti.StringProperty("handleClasses", required=True, length=1024)
    
    def get_resource_oql_paramnames(self):
        rtn = []
        if self.resource_oql is None:
            return []
        oql = self.resource_oql.lower()
        i = oql.find("where")
        oql = self.resource_oql[i + 5:]
        params = oql.split(" ")
        
        for param in params:
            if param.startswith("$"):
                rtn.append(param[1:])
        return rtn
    
class Role(Model):
    MODULE = CORE_MODULE_NAME
    role_name = properti.StringProperty("roleName", required=True, validator=[properti.UniqueValidator("role_name")])
    
class RoleOperation(Model):
    MODULE = CORE_MODULE_NAME
    
    role_id = properti.IntegerProperty("roleId", required=True)
    operation_key = properti.StringProperty("operationKey", required=True)
    
class UserRole(Model):
    MODULE = CORE_MODULE_NAME
    
    role_id = properti.IntegerProperty("roleId", required=True)
    user_id = properti.IntegerProperty("userId", required=True)
    
class Filex(Model):
    MODULE = CORE_MODULE_NAME
    file_name = properti.StringProperty("fileName", required=True, length=255)
    file_type = properti.StringProperty("fileType", required=True, length=10)
    model_name = properti.StringProperty("modelName", required=True, length=80)
    model_key = properti.StringProperty("modelKey", required=True)
    vfs_path = properti.StringProperty("vfsPath", required=True, length=80)
    file_path = properti.StringProperty("filePath", required=True, length=80)
    file_size = properti.IntegerProperty("fileSize", required=True)
    file_hash = properti.StringProperty("fileHash", required=True, length=80)
    
class Tag(Model):
    MODULE = CORE_MODULE_NAME
    tag_name = properti.StringProperty("tagName", required=True, validator=[properti.IllegalValidator(), UniqueValidator("tag_name", scope=["creator_id", "model_name"])])
    model_name = properti.StringProperty("modelName", required=True, length=80)
    tag_order = properti.IntegerProperty("tagOrder", required=False)
 
class TagModel(Model):
    MODULE = CORE_MODULE_NAME
    tag_id = properti.IntegerProperty("tagId", required=True)
    model_name = properti.StringProperty("modelName", required=True, length=80)
    model_key = properti.StringProperty("modelKey", required=True)
    
    
    
