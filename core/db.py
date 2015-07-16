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
from MySQLdb.constants import FIELD_TYPE
from MySQLdb.converters import conversions

import conf
from core.error import CoreError
import web


class DbInfo(object):
    
    def __init__(self, host, port, username, password, dbtype='mysql', dbname="", conv=None):
        self.__host = host
        self.__port = int(port)
        self.__username = username
        self.__password = password
        self.__dbtype = dbtype
        self.__dbname = dbname
        if conv is None:
            self.__conv = self._get_default_convs()
        else:
            self.__conv = conv

    def get_host(self):
        return self.__host
    
    def get_port(self):
        return self.__port
    
    def get_username(self):
        return self.__username
    
    def get_password(self):
        return self.__password
    
    def get_dbtype (self):
        return self.__dbtype
    
    def get_dbname(self):
        return self.__dbname
    
    def get_conv(self):
        return self.__conv
    
    def copy(self, host=None, port=None, username=None, password=None, dbtype=None, dbname=None, conv=None):
        if host is None:
            host = self.get_host()
        if port is None:
            port = self.get_port()
        if username is None:
            username = self.get_username()
        if password is None:
            password = self.get_password()
        if dbtype is None:
            dbtype = self.get_dbtype()
        if conv is None:
            conv = self.get_conv()
        return DbInfo(host, port, username, password, dbtype=dbtype, dbname=dbname, conv=conv)
    
    def get_key(self):
        dbname = self.__dbname
        if dbname is None or dbname == '':
            dbname = "None"
        key = "%s_%s_%d_%s_%s" % (self.__dbtype, self.__host, self.__port, self.__username, dbname)
        return key
    
    def _get_default_convs(self):
        convs = conversions.copy()
        convs[FIELD_TYPE.DECIMAL] = float
        convs[FIELD_TYPE.NEWDECIMAL] = float
        return convs
    
class DbConnPool(object):
    
    def __init__(self):
        self.__connections = {}
    
    def get_connection(self, dbinfo):
        if dbinfo is None:
            raise CoreError("dbinfo can't be none when get db connection.")
        key = dbinfo.get_key()
        if self.__connections.has_key(key):
            return self.__connections[key]
        else:
            if dbinfo.get_dbname() is None or dbinfo.get_dbname() == '':
                db = web.database(dbn=dbinfo.get_dbtype(), host=dbinfo.get_host(), port=int(dbinfo.get_port()), user=dbinfo.get_username(), pw=dbinfo.get_password(), conv=dbinfo.get_conv())
            else:
                db = web.database(dbn=dbinfo.get_dbtype(), host=dbinfo.get_host(), port=int(dbinfo.get_port()), user=dbinfo.get_username(), pw=dbinfo.get_password(), conv=dbinfo.get_conv(), db=dbinfo.get_dbname())
            self.__connections[key] = db
        return db
    
    def clearup(self):
        self.__connections.clear()
        self.__connections = {}
        
class dbutil:
    
    __master_dbinfo = None
    __dbconnPool = DbConnPool()
    
    @classmethod
    def has_db(cls, dbinfo):
        if dbinfo.get_dbname() is None and dbinfo.get_dbname() == '':
            raise CoreError("dbinfo.dbname can not be None.")
        sql = "USE %s;" % dbinfo.get_dbname()
        try:
            dbinfo = dbinfo.copy(dbname="")
            cls.get_dbconn(dbinfo).query(sql)
            return True
        except:
            return False
    
    @classmethod    
    def create_db(cls, dbinfo):
        if not cls.has_db(dbinfo):
            dbname = dbinfo.get_dbname()
            dbinfo = dbinfo.copy(dbname="")
            sql = 'CREATE DATABASE /*!32312 IF NOT EXISTS*/`%s` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;' % dbname
            cls.get_dbconn(dbinfo).query(sql)
    
    @classmethod    
    def drop_db(cls, dbinfo):
        sql = 'DROP DATABASE IF EXISTS %s' % dbinfo.get_dbname()
        cls.get_dbconn(dbinfo).query(sql)
    
    @classmethod
    def get_master_dbinfo(cls):
        if cls.__master_dbinfo is None:
            cls.__master_dbinfo = cls.__get_master_dbinfo()
        return cls.__master_dbinfo
    
    @classmethod
    def change_master_dbinfo(cls, dbinfo):
        cls.__master_dbinfo = dbinfo
    
    @classmethod
    def get_dbconn(cls, dbinfo=None):
        
        if dbinfo is None:
            dbinfo = cls.get_master_dbinfo()
            
        return cls.__dbconnPool.get_connection(dbinfo)
    
    @classmethod
    def __get_master_dbinfo(cls):
        dbinfo = DbInfo(conf.DB_MASTER['host'],
                            conf.DB_MASTER['port'],
                            conf.DB_MASTER['username'],
                            conf.DB_MASTER['password'],
                            dbname=conf.DB_MASTER['dbname'])
        return dbinfo
