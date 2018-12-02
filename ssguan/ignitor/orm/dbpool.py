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


from ssguan.ignitor.base.error import ProgramError
from ssguan.ignitor.orm import  config as orm_config
from ssguan.ignitor.orm.mongodb import MongoDB
from ssguan.ignitor.orm.sqldb import SqlDB


class DbConnPool(object):
        def __init__(self):
            self.__connections = {}
        
        def get_connection(self, dbinfo):
            if dbinfo is None:
                raise ProgramError("dbinfo can't be none when get db connection.")
            key = dbinfo.get_key()
            if key in self.__connections:
                return self.__connections[key]
            else:
                if dbinfo.is_mysql():
                    dbclient = SqlDB(dbinfo)
                elif dbinfo.is_mongo():
                    dbclient = MongoDB(dbinfo)
                else:
                    raise ProgramError("%s is not supported." , dbinfo.dbtype)
                self.__connections[key] = dbclient
                return dbclient
        
        def clearup(self):
            self.__connections.clear()
            self.__connections = {}

__dbconnPool = DbConnPool()

def get_dbconn(model_class): 
    dbinfo = orm_config.get_dbinfo(model_class)
    return __dbconnPool.get_connection(dbinfo)

def has_db(dbinfo):
    if dbinfo.is_mysql():
        if dbinfo.dbname is None and dbinfo.dbname == '':
            raise ProgramError("dbinfo.dbname can not be None.")
        sql = "USE %s;" % dbinfo.dbname
        try:
            dbinfo = dbinfo.copy(dbname="")
            __get_dbclient(dbinfo).query(sql)
            return True
        except:
            return False
    elif dbinfo.is_mongo():
        dbname = dbinfo.dbname
        dbinfo = dbinfo.copy(dbname="")
        dbnames = __get_dbclient(dbinfo).database_names()
        return dbname in dbnames
    else:
        return True

def create_db(dbinfo, dropped=False):
    """
        param:dropped|bool True means drop database first then create.
    """ 
    if not has_db(dbinfo):
        if dbinfo.is_mysql():
            dbname = dbinfo.dbname
            dbinfo = dbinfo.copy(dbname="")
            sql = 'CREATE DATABASE /*!32312 IF NOT EXISTS*/`%s` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;' % dbname
            __get_dbclient(dbinfo).query(sql)
        elif dbinfo.is_mongo():
            __get_dbclient(dbinfo).create_collection("__auto_created_for_db_creation")
            __get_dbclient(dbinfo).drop_collection("__auto_created_for_db_creation")
    else:
        if dropped:
            drop_db(dbinfo)
            create_db(dbinfo, dropped=False)
    return True

def drop_db(dbinfo):
    if dbinfo.is_mysql():
        sql = 'DROP DATABASE IF EXISTS %s' % dbinfo.dbname
        __get_dbclient(dbinfo).query(sql)
    elif dbinfo.is_mongo():
        __get_dbclient(dbinfo).command("dropDatabase")

def __get_dbclient(dbinfo):
    if dbinfo.is_mysql():
        dbclient = SqlDB(dbinfo).get_dbclient()
    else:
        dbclient = MongoDB(dbinfo).get_dbclient()
    return dbclient