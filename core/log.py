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

from db import dbutil
import dtutil
import conf

LOG_TABLENAME = "core_log"

class DBHandler(logging.Handler):
    
    def __init__(self, conn):
        logging.Handler.__init__(self)
        self.conn = conn
        
    def emit(self, record):
        try:
            global LOG_TABLENAME
            message = self.format(record)
            self.conn.insert(LOG_TABLENAME, l_level=record.levelname, l_message=message, logged_time=dtutil.utcnow())
            
        except:
            self.handleError(record)

def get_logger(name=None):
    conn = dbutil.get_dbconn()
    logger = logging.getLogger(name)
    logger.setLevel(conf.get_log_root_level())
    consoleFormatter = logging.Formatter(conf.get_log_console_format())
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(conf.get_log_console_level())
    consoleHandler.setFormatter(consoleFormatter)
    logger.addHandler(consoleHandler)
     
    dbFormatter = logging.Formatter(conf.get_log_db_format())
    dbHandler = DBHandler(conn)
    dbHandler.setLevel(conf.get_log_db_level())
    dbHandler.setFormatter(dbFormatter)
    logger.addHandler(dbHandler)
    return logger

def fetch_logs(level=None, limit=100, offset=0):
    from model import Log
    query = Log.all()
    if level is not None:
        query.filter("l_level =", level)
    query.order("-logged_time")
    return query.fetch(limit=limit, offset=offset, paging=True)
    
