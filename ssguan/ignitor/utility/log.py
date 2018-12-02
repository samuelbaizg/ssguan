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

from tornado.log import LogFormatter as _LogFormatter

class LogFormatter(_LogFormatter, object):
    """Init tornado.log.LogFormatter from loggingg.fileConfig"""
    def __init__(self, fmt=None, datefmt=None, color=True, *args, **kwargs):
        if fmt is None:
            fmt = _LogFormatter.DEFAULT_FORMAT
        super(LogFormatter, self).__init__(color=color, fmt=fmt, *args, **kwargs)

def get_logger(name=None):
    logger = logging.getLogger(name)
    return logger

def file_config(filepath, defaults=None):
    from logging import config as lc
    lc.fileConfig(filepath, defaults=defaults, disable_existing_loggers=False)
