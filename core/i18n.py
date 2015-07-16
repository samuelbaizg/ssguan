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
import conf
from core.error import CoreError
from db import dbutil
import dtutil
import strutil


I18N_TABLENAME = "core_i18n"

CACHESPACE_I18NLIST = "i18nlist"
CACHESPACE_I18NONE = "i18none"


def __get_conn():
    conn = dbutil.get_dbconn()
    return conn
 
def get_i18n_message(language, key, arguments=None):
    if language not in conf.get_supported_languages() == 0:
        raise CoreError("language %s is not founded.", language)
    
    cachekey = "%s:%s" % (language , key)
    
    i1 = cache.get(CACHESPACE_I18NONE, cachekey)
    
    if i1 != None:
        return i1.i1_message
    
    sql = "SELECT i1_message from %s where i1_key = $mn and i1_locale = $lang" % I18N_TABLENAME
    conn = __get_conn()
    result = conn.query(sql, vars={'mn':key, 'lang' : language})
    
    if len(result) > 0:
        i1 = result[0]
        msg = i1.i1_message
        if arguments != None:
            for key, value in arguments.items():
                msg = msg.replace("{{%s}}" % key, str(value))
        cache.put(CACHESPACE_I18NONE, cachekey, i1)
        return msg
    else:
        return None

def get_i18n_messages(language, i1_type, rtn_dict=False):
    if language not in conf.get_supported_languages() == 0:
        raise CoreError("language %s is not founded.", language)
    
    i18ns = fetch_i18ns(language, i1_type)
    if rtn_dict:
        results = {}
        for i18n in i18ns:            
            results[i18n.i1_key] = i18n.i1_message
    else:
        results = []
        for i1 in i18ns:
            rst = i1.i1_message
            results.append(rst)
    return results

def has_i18n(key, language):
    conn = __get_conn()
    sql = "SELECT i1_message from %s where i1_key = $mn and i1_locale = $lang" % I18N_TABLENAME
    
    result = conn.query(sql, vars={'mn':key, 'lang' : language})
    return len(result) > 0

def create_i18n(key, message, locale, i1_type, modifier_id):
    if strutil.is_empty(key):
        raise CoreError("key can't be empty.")
    if strutil.is_empty(message):
        raise CoreError("Message value can't be empty.")
    if locale not in conf.get_supported_languages() == 0:
        raise CoreError("language %s is not founded.", locale)
    conn = __get_conn()
    conn.insert(I18N_TABLENAME, i1_key=key, i1_locale=locale, i1_message=message, i1_type=i1_type, created_time=dtutil.utcnow(), modified_time=dtutil.utcnow(), creator_id=modifier_id, modifier_id=modifier_id, row_version=1)

def update_i18n(key, message, locale, i1_type, modifier_id):
    if strutil.is_empty(key):
        raise CoreError("key can't be empty.")
    if strutil.is_empty(message):
        raise CoreError("Message value can't be empty.")
    if locale not in conf.get_supported_languages() == 0:
        raise CoreError("language %s is not founded.", locale)
    
    if has_i18n(key, locale) is None:
        raise CoreError("the key %s for language %s of i18n does not existed." , key, locale)
    
    conn = __get_conn()
    sql = "SELECT row_version from %s where i1_key = $mn and i1_locale = $lang" % I18N_TABLENAME
    result = conn.query(sql, vars={'mn':key, 'lang' : locale})
    row_version = result[0].row_version
    conn.update(I18N_TABLENAME, i1_key=key, i1_message=message, i1_locale=locale, i1_type=i1_type, modified_time=dtutil.utcnow(), modifier_id=modifier_id, row_version=row_version + 1)
    
def delete_i18n(key, language, modifier_id):
    if strutil.is_empty(key):
        raise CoreError("key can't be empty.")
    if language not in conf.get_supported_languages() == 0:
        raise CoreError("language %s is not founded.", language)
    conn = __get_conn()
    conn.delete(I18N_TABLENAME, where="i1_key='%s' and i1_locale='%s'" % (key, language))

def fetch_i18ns(locale=None, i1_type=None, return_dic=False):
    cachekey = "i18ns_%s_%s_%r" % (locale, i1_type, return_dic)
    results = cache.get(CACHESPACE_I18NLIST, cachekey)
    if results == None:
        conn = __get_conn()
        sql = "select i1_key, i1_locale,i1_message,i1_type, modifier_id, created_time, modified_time from %s" % I18N_TABLENAME
        results = conn.query(sql)
        wheres = []
        if i1_type is not None:
            wheres.append("i1_type = '%s'" % i1_type)
        if locale is not None:
            wheres.append("i1_locale = '%s'" % locale)
        if len(wheres) > 0:
            sql += " where "
            for where in wheres:
                sql += " %s and" % where
            sql = sql[:-4]
            
        i18ns = conn.query(sql)
        if return_dic:
            results = {}
            for result in i18ns:
                results[result.i1_key] = result.i1_message
        else:
            results = []
            for result in i18ns:
                results.append(result)
        cache.put(CACHESPACE_I18NLIST, cachekey, results)
    return results
     
        
