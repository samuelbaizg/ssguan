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

import logging
import os

from tornado.log import LogFormatter as _LogFormatter

from ssguan import config
from ssguan.commons import  dao, typeutils
from ssguan.commons.dao import BaseModel


class Log(BaseModel):
    
    LEVEL_NAMES = {logging.DEBUG:"DEBUG",
             logging.INFO:"INFO",
             logging.WARN:"WARNING",
             logging.ERROR:"ERROR",
             logging.FATAL:"CRITICAL"
             }
    
    @classmethod
    def meta_domain(cls):
        return config.MODULE_LOGGINGG

    l_name = dao.StringProperty("logName", required=True, length=200)
    l_module = dao.StringProperty("logModule", required=True, length=200)
    l_level = dao.StringProperty("logLevel", required=True, length=10, choices=LEVEL_NAMES.values())
    l_pathname = dao.StringProperty("pathName", required=True, length=200)
    l_funcname = dao.StringProperty("funcName", required=True, length=200)
    l_lineno = dao.IntegerProperty("lineNo", required=True)
    l_message = dao.StringProperty("message", required=True, length=4294967295)
    l_processno = dao.IntegerProperty("processNo", required=True)
    l_processname = dao.StringProperty("processName", required=True, length=200)
    l_threadno = dao.IntegerProperty("threadNo", required=True)
    l_threadname = dao.StringProperty("threadName", required=True, length=200)
    logged_time = dao.DateTimeProperty("loggedTime", required=True, auto_utcnow=True)
    

class DBHandler(logging.Handler):
    
    def __init__(self):
        logging.Handler.__init__(self)
        
    def emit(self, record):
        try:
            model = Log()
            model.l_level = record.levelname
            pathname = self.replace_syspath(record.pathname)
            model.l_name = record.name
            model.l_module = record.module
            model.l_pathname = pathname            
            model.l_funcname = record.funcName
            model.l_lineno = record.lineno
            model.l_message = self.replace_syspath(record.message)
            model.l_processno = record.process
            model.l_processname = record.processName
            model.l_threadno = record.thread
            model.l_threadname = record.threadName            
            model.logged_time = typeutils.utcnow()
            model.create()
        except:
            self.handleError(record)
    
    def replace_syspath(self, text, new=""):
        paths = os.sys.path
        paths.sort(key=len, reverse=True)
        for p in paths:            
            text = text.replace(p + os.sep, new)
        return text
            

class LogFormatter(_LogFormatter, object):
    """Init tornado.log.LogFormatter from loggingg.fileConfig"""
    def __init__(self, fmt=None, datefmt=None, color=True, *args, **kwargs):
        if fmt is None:
            fmt = _LogFormatter.DEFAULT_FORMAT
        super(LogFormatter, self).__init__(color=color, fmt=fmt, *args, **kwargs)

def get_logger(name=None):
    logger = logging.getLogger(name)
    return logger

def fetch_logs(level=None, keywords=None, limit=100, offset=0):
    query = Log.all()
    if level is not None:
        query.filter("l_level =", Log.LEVEL_NAMES[level])
    if keywords is not None:
        query.filter("l_message like", "%%%s%%" % keywords)
    query.order("-logged_time")
    return query.fetch(limit=limit, offset=offset, paging=True)

class MCLog(BaseModel):
    
    @classmethod
    def meta_domain(cls):
        return config.MODULE_LOGGINGG
    
    modelname = dao.StringProperty("modelName", required=True, length=80)
    modelkey = dao.StringProperty("modelKey", required=True)
    user_id = dao.StringProperty("userKey", required=True)
    changed_props = dao.ListProperty("changedProps", required=True, length=4294967295)
    changed_time = dao.DateTimeProperty("changedTime", required=True, auto_utcnow=True)
    
def add_mclog(last_model, model, modified_by, dbconn=None):
    changedprops = []
    for key, prop in model.get_properties(persistent=True).items():
        value1 = getattr(last_model, key)
        value2 = getattr(model, key)
        if prop.logged is True and value1 != value2:
            changedprops.append((key, prop.get_label(), value1, value2))
    if len(changedprops) > 0:
        changelog = MCLog()
        changelog.modelname = model.get_modelname()
        changelog.modelkey = str(model.get_keyvalue())
        changelog.user_id = modified_by
        changelog.changed_props = []
        for cp in changedprops:
            cldetail = typeutils.Storage()            
            cldetail.field_name = cp[0]
            cldetail.field_label = cp[1]
            cldetail.fvalue_last = str(cp[2])
            cldetail.fvalue_present = str(cp[3])
            changelog.changed_props.append(cldetail)
        changelog.create(dbconn=dbconn)

def fetch_mclogs(model_name, model_key, **kwds):
    query = MCLog.all()
    query.filter("modelname =", model_name)
    query.filter("modelkey =", str(model_key))
    def mocb(mclog):
        from ssguan.modules import auth
        user1 = auth.get_user(auth.User.ID_SYSTEM, user_id=mclog.user_id)
        mclog.userDisplayName = user1.get_user_display_name() if user1 != None else None
    mclogs = query.fetch(mocallback=mocb)
    return mclogs
        
def delete_mclogs(model_name, model_key, modified_by, dbconn=None):
    query = MCLog.all()
    query.filter("modelname =", model_name)
    query.filter("modelkey =", str(model_key))
    query.delete(dbconn=dbconn)
        
def fileConfig(filepath, defaults=None, disable_existing_loggers=True):
    from logging import config as lc
    lc.fileConfig(filepath, defaults=defaults, disable_existing_loggers=disable_existing_loggers)

def install_module():
    Log.create_schema()
    MCLog.create_schema()
    config.dbCFG.add_model_dbkey("%s_*" % config.MODULE_LOGGINGG, config.dbCFG.ROOT_DBKEY)
    return True
    

def uninstall_module():
    Log.delete_schema()
    MCLog.delete_schema()
    config.dbCFG.delete_model_dbkey("%s_*" % config.MODULE_LOGGINGG)
    return True
