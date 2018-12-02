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

from ssguan.ignitor.utility import io
from ssguan.ignitor.base import struct

__SECTION_DATABASES = 'databases'
__OPTION_DBKEYS = 'keys'
__SECTION_DB_PREFIX = 'db'
__SECTION_DB_DEFAULT = 'default'
__SECTION_MODEL_DBS = 'modeldb'

__dbinfos = struct.Storage()
__modeldbs = struct.Storage()

class DbInfo(object):

    CONNECTION_HOST = "host"
    CONNECTION_PORT = "port"
    CONNECTION_USERNAME = "username"
    CONNECTION_PASSWORD = "password"
    CONNECTION_DBNAME = "dbname"
    CONNECTION_DBTYPE = "dbtype"
    CONNECTION_CONV = "conv"

    def __init__(self, host, port, username, password, dbtype='mysql', dbname="", conv=None):
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.dbname = dbname
        self.conv = conv
        self.dbtype = dbtype

    @classmethod
    def new_one(cls, dbf):
        dbinfo = DbInfo(dbf[cls.CONNECTION_HOST],
                        dbf[cls.CONNECTION_PORT],
                        dbf[cls.CONNECTION_USERNAME],
                        dbf[cls.CONNECTION_PASSWORD],
                        dbtype=dbf[cls.CONNECTION_DBTYPE],
                        dbname=dbf[cls.CONNECTION_DBNAME],
                        conv=dbf[cls.CONNECTION_CONV],
                        )
        return dbinfo

    def is_mysql(self):
        return self.dbtype in ['mysql']

    def is_mongo(self):
        return self.dbtype in ["mongo"]

    def copy(self, host=None, port=None, username=None, password=None, dbtype=None, dbname=None, conv=None):
        if host is None:
            host = self.host
        if port is None:
            port = self.port
        if username is None:
            username = self.username
        if password is None:
            password = self.password
        if dbtype is None:
            dbtype = self.dbtype
        if conv is None:
            conv = self.conv
        return DbInfo(host, port, username, password, dbtype=dbtype, dbname=dbname, conv=conv)

    def get_key(self):
        dbname = self.dbname
        if dbname is None or dbname == '':
            dbname = "None"
        key = "%s_%s_%d_%s_%s" % (
            self.dbtype, self.host, self.port, self.username, dbname)
        return key

def file_config(filepath, defaults=None):
    parser = io.get_configparser(filepath, defaults=defaults)
    global __dbinfos, __modeldbs
    keys = parser.get(__SECTION_DATABASES, __OPTION_DBKEYS)
    keys = keys.split(",")
    for key in keys:
        section = __SECTION_DB_PREFIX + "_" + key
        __dbinfos[key] = __parse_dbinfo(parser, section)
    for (key, value) in parser.items(__SECTION_MODEL_DBS):
        __modeldbs[key] = value
    
def fetch_dbinfos(cls):
    return __dbinfos.values()

def get_default_dbinfo():
    return __dbinfos[__SECTION_DB_DEFAULT]

def get_dbinfo(model_class):
    if model_class == None:
        model_name = None
    elif type(model_class) == str:
        model_name = model_class
    else:
        model_name = model_class.get_modelname()
    if model_name in __modeldbs:
        return __dbinfos[model_name]
    else:
        return __dbinfos[__SECTION_DB_DEFAULT]
    
def __parse_dbinfo(parser, db_section):
    if parser.has_option(db_section, DbInfo.CONNECTION_CONV):
        conv = type.json_to_object(
            parser.get(db_section, DbInfo.CONNECTION_CONV))
    else:
        conv = None
        
    dbinfo = DbInfo.new_one({
        DbInfo.CONNECTION_HOST: parser.get(db_section, DbInfo.CONNECTION_HOST),
        DbInfo.CONNECTION_PORT: parser.get(db_section, DbInfo.CONNECTION_PORT),
        DbInfo.CONNECTION_USERNAME: parser.get(db_section, DbInfo.CONNECTION_USERNAME),
        DbInfo.CONNECTION_PASSWORD: parser.get(db_section, DbInfo.CONNECTION_PASSWORD),
        DbInfo.CONNECTION_DBTYPE: parser.get(db_section, DbInfo.CONNECTION_DBTYPE),
        DbInfo.CONNECTION_DBNAME: parser.get(db_section, DbInfo.CONNECTION_DBNAME),
        DbInfo.CONNECTION_CONV: conv
    })
    return dbinfo