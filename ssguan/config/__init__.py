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
import os

from ssguan.commons import typeutils, ioutils, funcutils


LOGGER_COMMONS = "comm"

ID_SYSTEM = "system"

MODULE_MQUEUE = "mque"
MODULE_AUTH = "auth"
MODULE_LOGGINGG = "logg"
MODULE_UPDATE = "upda"
MODULE_SCHEDULE = "sche"
MODULE_CONFIG = "conf"
MODULE_WEBB = "webb"
MODULE_FILEE = "file"
MODULE_LABELL = "labl"
MODULE_ENTITY = "enti"

MODULE_DATABASE = "database"


_root_dbconfig = typeutils.Storage()
_debug_config = typeutils.Storage()
_cache_config = typeutils.Storage()


def fileConfig(filepath, defaults=None):
    cp = ioutils.get_configparser(filepath, defaults=defaults)
    section = dbCFG.SECTION_ROOT
    if cp.has_option(section, DbInfo.CONNECTION_CONV):
        conv = typeutils.json_to_object(
            cp.get(section, DbInfo.CONNECTION_CONV))
    else:
        conv = None
    _root_dbconfig.update({
        DbInfo.CONNECTION_HOST: cp.get(section, DbInfo.CONNECTION_HOST),
        DbInfo.CONNECTION_PORT: cp.get(section, DbInfo.CONNECTION_PORT),
        DbInfo.CONNECTION_USERNAME: cp.get(section, DbInfo.CONNECTION_USERNAME),
        DbInfo.CONNECTION_PASSWORD: cp.get(section, DbInfo.CONNECTION_PASSWORD),
        DbInfo.CONNECTION_DBTYPE: cp.get(section, DbInfo.CONNECTION_DBTYPE),
        DbInfo.CONNECTION_DBNAME: cp.get(section, DbInfo.CONNECTION_DBNAME),
        DbInfo.CONNECTION_CONV: conv
    })
    debug = cp.get(debugCFG.SECTION_DEBUGDB, debugCFG.KEY_DEBUGDB)
    _debug_config.update({debugCFG.KEY_DEBUGDB: debug})
    lazymode = cp.get(cacheCFG.SECTION_CACHE, cacheCFG.KEY_LAZYMODE)
    tagprefix = cp.get(cacheCFG.SECTION_CACHE, cacheCFG.KEY_TAG_PREFIX)
    ckd = cp.get(cacheCFG.SECTION_CACHE, cacheCFG.KEY_CACHE_KEY_DELIMITER)
    dct = cp.get(cacheCFG.SECTION_CACHE, cacheCFG.KEY_DEFAULT_CACHE_TIMEOUT)
    dca = cp.get(cacheCFG.SECTION_CACHE, cacheCFG.KEY_DEFAULT_CACHE_ALIAS)
    _cache_config.update({cacheCFG.KEY_LAZYMODE: lazymode,
                          cacheCFG.KEY_TAG_PREFIX: tagprefix,
                          cacheCFG.KEY_CACHE_KEY_DELIMITER: ckd,
                          cacheCFG.KEY_DEFAULT_CACHE_TIMEOUT: dct,
                          cacheCFG.KEY_DEFAULT_CACHE_ALIAS: dca})


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


class _DbCfgHelper(object):

    ROOT_DBKEY = "rootdb"

    SECTION_ROOT = ROOT_DBKEY
    _SECTION_CONNECTION = "connection"
    _SECTION_MODELDB = "modeldb"

    @classmethod
    def get_dbinfo(cls, model_class):
        if model_class == None:
            model_name = None
        elif type(model_class) == str:
            model_name = model_class
        else:
            model_name = model_class.get_modelname()
        from ssguan.modules import sysprop
        if model_name is None or model_name == sysprop.SysProp.get_modelname():
            dbkey = cls.ROOT_DBKEY
        else:
            dbkey = cls.get_model_dbkey(model_name)
        if dbkey == cls.ROOT_DBKEY:
            return cls.get_root_dbinfo()
        else:
            dbf = sysprop.get_sysprop_value(dbkey, ID_SYSTEM)
            return DbInfo.new_one(dbf)

    @classmethod
    def get_root_dbinfo(cls):
        return DbInfo.new_one(_root_dbconfig)

    @classmethod
    def fetch_dbinfos(cls):
        dbinfos = []
        from ssguan.modules import sysprop
        dbfs = sysprop.fetch_sysprops(
            MODULE_DATABASE, cls._SECTION_CONNECTION, ID_SYSTEM, value_dict=True)
        for dbf in dbfs.values():
            dbinfos.append(DbInfo.new_one(dbf))
        return dbinfos

    @classmethod
    def add_dbconfig(cls, dbkey, host, port, username, password, dbname, dbtype, conv=None):
        cfg = {DbInfo.CONNECTION_HOST: host,
               DbInfo.CONNECTION_PORT: port,
               DbInfo.CONNECTION_USERNAME: username,
               DbInfo.CONNECTION_PASSWORD: password,
               DbInfo.CONNECTION_DBTYPE: dbtype,
               DbInfo.CONNECTION_CONV: conv,
               }
        from ssguan.modules import sysprop
        sysprop.add_sysprop(dbkey, cfg, MODULE_DATABASE,
                            cls._SECTION_CONNECTION, ID_SYSTEM)
        return dbkey

    @classmethod
    def add_model_dbkey(cls, modelname, dbkey):
        k = "mdb_%s" % modelname
        from ssguan.modules import sysprop
        if modelname.endswith("_*"):
            k = "mdb_m_%s" % modelname[:-2]
        sysprop.add_sysprop(k, dbkey, MODULE_DATABASE,
                            cls._SECTION_MODELDB, ID_SYSTEM)
        return k

    @classmethod
    def get_model_dbkey(cls, modelname):
        if modelname is None:
            return cls.ROOT_DBKEY
        from ssguan.modules import sysprop
        k = "mdb_%s" % modelname
        dbkey = None
        if sysprop.has_sysprop(k, ID_SYSTEM):
            dbkey = sysprop.get_sysprop_value(k, ID_SYSTEM)
        else:
            k = modelname.split("_")[0]
            dbkey = sysprop.get_sysprop_value(k, ID_SYSTEM)
        if dbkey is None:
            dbkey = cls.ROOT_DBKEY
        return dbkey

    @classmethod
    def delete_model_dbkey(cls, modelname):
        k = "mdb_%s" % modelname
        from ssguan.modules import sysprop
        if modelname.endswith("_*"):
            k = "mdb_m_%s" % modelname[:-2]
        sysprop.delete_sysprop(k, ID_SYSTEM)
        return True


class _CacheCfgHelper(object):

    SECTION_CACHE = "cache"
    KEY_LAZYMODE = "lazy_mode"
    KEY_TAG_PREFIX = "tag_prefix"
    KEY_CACHE_KEY_DELIMITER = "cache_key_delimiter"
    KEY_DEFAULT_CACHE_TIMEOUT = "default_cache_timeout"
    KEY_DEFAULT_CACHE_ALIAS = "default_cache_alias"

    @classmethod
    def is_lazymode(cls):
        return typeutils.str_to_bool(_cache_config[cls.KEY_LAZYMODE], False)

    @classmethod
    def get_tag_prefix(cls):
        tag_prefix = _cache_config[cls.KEY_TAG_PREFIX]
        return "tag" if tag_prefix is None else tag_prefix

    @classmethod
    def get_cache_key_delimiter(cls):
        cache_key_delimiter = _cache_config[cls.KEY_CACHE_KEY_DELIMITER]
        return ":" if cache_key_delimiter is None else cache_key_delimiter

    @classmethod
    def get_default_cache_timeout(cls):
        """
            Unit is second
        """
        default_cache_timeout = _cache_config[cls.KEY_DEFAULT_CACHE_TIMEOUT]
        return 600 if default_cache_timeout is None else int(default_cache_timeout)

    @classmethod
    def get_default_cache_alias(cls):
        default_cache_alias = _cache_config[cls.KEY_DEFAULT_CACHE_ALIAS]
        return "DEFAULT_CACHE" if default_cache_alias is None else default_cache_alias


class _DebugCfgHelper(object):

    SECTION_DEBUGDB = "debug"
    KEY_DEBUGDB = "debug_db"

    @classmethod
    def is_debugdb(cls):
        return typeutils.str_to_bool(_debug_config[cls.KEY_DEBUGDB], False)


class _WebbCfgHelper(object):

    _SECTION_HANDLER = "handler"
    _SECTION_MODEL = "model"
    _SECTION_SESSION = "session"
    _SECTION_SETTING = "setting"
    _KEY_ROUTE_CONTEXT = "route_context"

    @classmethod
    def get_handlers(cls):
        hs = []
        from ssguan.modules import sysprop
        handlers = sysprop.fetch_sysprops(
            MODULE_WEBB, cls._SECTION_HANDLER, ID_SYSTEM, value_dict=True)
        ctx = sysprop.get_sysprop_value(cls._KEY_ROUTE_CONTEXT, ID_SYSTEM)
        for key, handler in handlers.items():
            handlerc = funcutils.import_module(handler)
            if handlerc is None:
                from ssguan.commons.error import NoFoundError
                raise NoFoundError("WebHandler", handler)
            hs.append(("%s%s" % (ctx, key), handlerc))
        return hs

    @classmethod
    def get_settings(cls):
        from ssguan.modules import sysprop
        settings = sysprop.fetch_sysprops(
            MODULE_WEBB, cls._SECTION_SETTING, ID_SYSTEM, value_dict=True)
        if settings.has_key("default_handler_class"):
            settings["default_handler_class"] = funcutils.import_module(
                settings["default_handler_class"])
        else:
            from ssguan.commons import webb
            settings["default_handler_class"] = webb.URINoFoundReqHandler
        return settings

    @classmethod
    def add_setting(cls, key, value):
        from ssguan.modules import sysprop
        sysprop.add_sysprop(key, value, MODULE_WEBB,
                            cls._SECTION_SETTING, ID_SYSTEM)
        return True

    @classmethod
    def update_setting(cls, key, value):
        from ssguan.modules import sysprop
        sysprop.update_sysprop(key, value, MODULE_WEBB,
                               cls._SECTION_SETTING, ID_SYSTEM)
        return True

    @classmethod
    def get_session_configs(cls):
        from ssguan.modules import sysprop
        return sysprop.fetch_sysprops(MODULE_WEBB, cls._SECTION_SESSION, ID_SYSTEM, value_dict=True)

    @classmethod
    def add_session_config(cls, key, value):
        from ssguan.modules import sysprop
        sysprop.add_sysprop(key, value, MODULE_WEBB,
                            cls._SECTION_SESSION, ID_SYSTEM)
        return True

    @classmethod
    def update_session_config(cls, key, value):
        from ssguan.modules import sysprop
        sysprop.update_sysprop(key, value, MODULE_WEBB,
                               cls._SECTION_SESSION, ID_SYSTEM)
        return True

    @classmethod
    def add_model(cls, alias, model):
        from ssguan.modules import sysprop
        sysprop.add_sysprop(alias, model, MODULE_WEBB,
                            cls._SECTION_MODEL, ID_SYSTEM)
        return True

    @classmethod
    def delete_model(cls, alias):
        from ssguan.modules import sysprop
        sysprop.delete_sysprop(alias, ID_SYSTEM)
        return True

    @classmethod
    def get_model(cls, alias):
        from ssguan.modules import sysprop
        model = sysprop.get_sysprop_value(alias, ID_SYSTEM)
        return funcutils.import_module(model)

    @classmethod
    def add_handler(cls, path, handler):
        from ssguan.modules import sysprop
        sysprop.add_sysprop(path, handler, MODULE_WEBB,
                            cls._SECTION_HANDLER, ID_SYSTEM)
        return True

    @classmethod
    def delete_handler(cls, path):
        from ssguan.modules import sysprop
        sysprop.delete_sysprop(path, ID_SYSTEM)
        return True


class _AuthCfgHelper(object):

    KEY_AUTHINTECEPTOR = "authinteceptor"
    _SECTION_INTECEPTOR = "inteceptor"

    @classmethod
    def get_authinteceptor(cls):
        from ssguan.modules import sysprop
        aic = sysprop.get_sysprop_value(cls.KEY_AUTHINTECEPTOR, ID_SYSTEM)
        return aic

    @classmethod
    def add_authinteceptor(cls, authinteceptor):
        from ssguan.modules import sysprop
        sysprop.add_sysprop(cls.KEY_AUTHINTECEPTOR, str(
            authinteceptor), MODULE_AUTH, cls._SECTION_INTECEPTOR, ID_SYSTEM)
        return True

    @classmethod
    def delete_authinteceptor(cls):
        from ssguan.modules import sysprop
        sysprop.delete_sysprop(cls.KEY_AUTHINTECEPTOR, ID_SYSTEM)
        return True


class _FileeCfgHelper(object):

    DEFAULT_FSKEY = "defaultfs"

    FS_ROOTPATH = "rootpath"
    FS_MAXSIZE = "maxsize"
    FS_OVERWRITE = "overwrite"

    _SECTION_FS = "fs"

    @classmethod
    def get_fsinfo(cls, fskey):
        k = "%s" % fskey
        from ssguan.modules import sysprop
        if not sysprop.has_sysprop(k, ID_SYSTEM):
            k = cls.DEFAULT_FSKEY
        fscfg = sysprop.get_sysprop_value(k, ID_SYSTEM)
        return fscfg

    @classmethod
    def add_fsinfo(cls, fskey, rootpath, maxsize=4 * 1024 * 1024 * 1024, overwrite=False, **kwargs):
        value = {}
        value[cls.FS_ROOTPATH] = rootpath
        value[cls.FS_MAXSIZE] = maxsize
        value[cls.FS_OVERWRITE] = overwrite
        value.update(kwargs)
        from ssguan.modules import sysprop
        sysprop.add_sysprop(fskey, value, MODULE_FILEE,
                            cls._SECTION_FS, ID_SYSTEM)
        if not os.path.exists(rootpath):
            os.makedirs(rootpath)
        return fskey

    @classmethod
    def delete_fsinfo(cls, fskey):
        from ssguan.modules import sysprop
        return sysprop.delete_sysprop(fskey, ID_SYSTEM)


class _FetchCfgHelper(object):

    @classmethod
    def get_user_agent(cls):
        import ssguan
        "ssguan/%s (+http://www.suishousguan.com/)" % ssguan.__version__


dbCFG = _DbCfgHelper
cacheCFG = _CacheCfgHelper
debugCFG = _DebugCfgHelper
webbCFG = _WebbCfgHelper
authCFG = _AuthCfgHelper
fetchCFG = _FetchCfgHelper
fileeCFG = _FileeCfgHelper
fetchCFG = _FetchCfgHelper
