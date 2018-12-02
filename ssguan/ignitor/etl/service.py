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

from ssguan.ignitor.base import context
from ssguan.ignitor.base.error import NoFoundError
from ssguan.ignitor.etl.model import IncrExtract, IncrExtractLog
from ssguan.ignitor.utility import kind, parallel


__lock = parallel.create_lock()

def get_extract_timespan(ie_name, code_path, first_time=None, start_delta=IncrExtract.DEFAULT_START_DELTA, end_delta=IncrExtract.DEFAULT_END_DELTA):
    """
        Get extract timespan. 
        :param ie_name|str: the incrment extract job name.
        :param code_path|str: the increment job code path.
        :param first_time|datetime: it will be converted to utc time to save.
        :param start_delta|float: the delta to compute extract start time.
        :param end_delta|float: the delta to compute extract end time.        
        :return tuple(datetime,datetime): return (start_time,end_time)
    """    
    query = IncrExtract.all()
    query.filter("ie_name =", ie_name)
    __lock.acquire()
    try:
        incrextr = query.get()    
        if incrextr is None:
            start_delta = IncrExtract.DEFAULT_START_DELTA if start_delta is None else float(start_delta)
            end_delta = IncrExtract.DEFAULT_END_DELTA if end_delta is None else float(end_delta)
            first_time = (kind.utcnow() - datetime.timedelta(seconds=end_delta)) if first_time is None else first_time
            first_time = kind.local_to_utc(first_time)
            first_time = kind.datetime_floor(first_time)
            last_time = first_time - datetime.timedelta(seconds=start_delta)
            last_time = kind.datetime_floor(first_time)
            incrextr = IncrExtract(ie_name=ie_name, code_path=code_path, first_time=first_time, start_delta=start_delta, end_delta=end_delta, last_time=last_time)
            incrextr = incrextr.create(context.get_user_id())                    
        start_time = incrextr.last_time - datetime.timedelta(seconds=incrextr.start_delta)
        end_time = kind.utcnow() - datetime.timedelta(seconds=incrextr.end_delta)
        end_time = kind.datetime_floor(end_time)
        return (start_time, end_time)
    finally:
        __lock.release()

def update_last_extr_time(ie_name, last_extr_time):
    """
        Update last extract time
        :param ie_nme|str: the extractor name
        :param last_extr_time|datetime: the last extract time        
    """
    query = IncrExtract.all()
    query.filter("ie_name =", ie_name)
    incrextr = query.get()
    if incrextr is None:
        raise NoFoundError('Extractor', ie_name)
    log = IncrExtractLog(ie_id=incrextr.key(), ie_name=ie_name, extr_time=last_extr_time)
    log.create(context.get_user_id())
    query.set("last_time set", last_extr_time)
    query.update(context.get_user_id())
    return True
