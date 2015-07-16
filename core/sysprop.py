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
import cache
from core.db import dbutil
import dtutil
from error import CoreError
import strutil


SYSPROP_TABLENAME = "core_sysprop"
CACHESPACE_SYSPROP = "sysprop"

def __get_conn():
    conn = dbutil.get_dbconn()
    return conn

def get_sysprop_value(key, default=None, strict=True, fmt=None):
    if strutil.is_empty(key):
        raise CoreError("key can't be empty.")
    
    value = cache.get(CACHESPACE_SYSPROP, key)
    if value != None:
        return value
    
    conn = __get_conn()
    sql = "SELECT p_value from %s where p_key = $mn" % SYSPROP_TABLENAME
    results = conn.query(sql, vars={'mn':key})
    if len(results) > 0:
        value = results[0].p_value
        value = strutil.to_object(value, default=default, strict=strict, fmt=fmt)
        cache.put(CACHESPACE_SYSPROP, key, value)
    else:
        from model import SYSTEM_UID
        add_sysprop(key, default, SYSTEM_UID)
        value = get_sysprop_value(key, default)
    return value
    
def add_sysprop(key, value, modifier_id):
    if strutil.is_empty(key):
        raise CoreError("key can't be empty.")
    if strutil.is_empty(value):
        raise CoreError("value can't be empty.")
    conn = __get_conn()
    value1 = strutil.to_str(value)
    if not has_sysprop(key):
        conn.insert(SYSPROP_TABLENAME, p_key=key, p_value=value1, created_time=dtutil.utcnow(), modified_time=dtutil.utcnow(), modifier_id=modifier_id)
    else:
        conn.update(SYSPROP_TABLENAME, where="p_key = '%s'" % key, p_value=value1, modified_time=dtutil.utcnow(), modifier_id=modifier_id)
    cache.put(CACHESPACE_SYSPROP, key, value)
    return key

def update_sysprop(key, value, modifier_id):
    if strutil.is_empty(key):
        raise CoreError("key can't be empty.")
    if strutil.is_empty(value):
        raise CoreError("p_value can't be empty.")
    if has_sysprop(key) is None:
        raise CoreError("the key %s of sysprop does not existed.", key)
    value = strutil.to_str(value)
    conn = __get_conn()
    conn.update(SYSPROP_TABLENAME, where="p_key = '%s'" % key , p_value=value, modified_time=dtutil.utcnow(), modifier_id=modifier_id)
    cache.put(CACHESPACE_SYSPROP, key, value)

def delete_sysprop(key, modifier_id):
    if strutil.is_empty(key):
        raise CoreError("key can't be empty.")
    conn = __get_conn()
    conn.delete(SYSPROP_TABLENAME, where="key='%s'" % key)
    cache.delete(CACHESPACE_SYSPROP, key)
    return True

def has_sysprop(key):
    if strutil.is_empty(key):
        raise CoreError("key can't be empty.")
    sql = "SELECT p_value from %s where p_key = $mn" % SYSPROP_TABLENAME
    conn = __get_conn()
    results = conn.query(sql, vars={'mn':key})
    return len(results) > 0

def replace_sysprop(key, value, modifier_id):
    if not has_sysprop(key):
        add_sysprop(key, value, modifier_id)
    else:
        update_sysprop(key, value, modifier_id)
        
def fetch_sysprops():
    conn = __get_conn()
    sql = "select p_key, p_value, modifier_id, created_time, modified_time from %s" % SYSPROP_TABLENAME
    results = conn.query(sql)
    return results

