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
import os
import sys
import unittest

from ssguan.ignitor.orm import dbpool, config as orm_config
from ssguan.ignitor.web import config as web_config
from ssguan.ignitor.asyn import config as asyn_config
from ssguan.ignitor.cache import config as cache_config
from ssguan.ignitor.vfs import config as fs_config
from ssguan.ignitor.utility import log
####load log_test.ini
path = "config%slog_test.ini" % os.sep
path = os.path.dirname(__file__) + os.sep + path
log.file_config(path)
####load orm_test.ini
path = "config%sorm_test.ini" % os.sep
path = os.path.dirname(__file__) + os.sep + path
orm_config.file_config(path)
####load web_test.ini
path = "config%sweb_test.ini" % os.sep
path = os.path.dirname(__file__) + os.sep + path
web_config.file_config(path)

path = "config%sasyn_test.ini" % os.sep
path = os.path.dirname(__file__) + os.sep + path
asyn_config.file_config(path)

path = "config%scache_test.ini" % os.sep
path = os.path.dirname(__file__) + os.sep + path
cache_config.file_config(path)

path = "config%svfs_test.ini" % os.sep
path = os.path.dirname(__file__) + os.sep + path
fs_config.file_config(path)

def discover(relative_dir, file_name):
    abs_path = os.path.dirname(__file__) + os.sep + relative_dir
    return unittest.TestLoader().discover(abs_path, file_name)

all_suite = discover('.', "*_test.py")
# all_suite = discover('ignitor', "*_test.py")
# all_suite = discover('ignitor/audit', "service_test.py")
# all_suite = discover('ignitor/orm', "dbpool_test.py")
# all_suite = discover('ignitor/orm', "properti_test.py")
# all_suite = discover('ignitor/orm', "model_test.py")
# all_suite = discover('ignitor/utility', "crypt_test.py")
# all_suite = discover('ignitor/utility', "kind_test.py")
# all_suite = discover('ignitor/web', "client_test.py")
# all_suite = discover('ignitor/web', "handler_test.py")
# all_suite = discover('ignitor/web', "session_test.py")
# all_suite = discover('ignitor/web', "restapi_test.py")
# all_suite = discover('ignitor/auth', "service_test.py")
# all_suite = discover('ignitor/auth', "handler_test.py")
# all_suite = discover('ignitor/asyn', "dbconduit_test.py")
# all_suite = discover('ignitor/cache', "locache_test.py")
# all_suite = discover('ignitor/cache', "decorator_test.py")
# all_suite = discover('ignitor/sched', "cronjob_test.py")
# all_suite = discover('ignitor/sched', "scheduler_test.py")
# all_suite = discover('ignitor/vfs', "lofs_test.py")
# all_suite = discover('ignitor/registry', "service_test.py")
# all_suite = discover('ignitor/etl', "functor_test.py")
# all_suite = discover('ignitor/etl', "etfunctor_test.py")
# all_suite = discover('ignitor/etl', "tffunctor_test.py")
all_suite = discover('ignitor/etl', "service_test.py")