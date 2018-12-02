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

from functools import wraps

from ssguan.ignitor.base.error import RequiredError
from ssguan.ignitor.etl import service as etl_service
from ssguan.ignitor.etl.model import IncrExtract
from ssguan.ignitor.utility import reflect


def incr_extract(name, first_time=None, start_delta=IncrExtract.DEFAULT_START_DELTA,end_delta=IncrExtract.DEFAULT_END_DELTA):
    """
        Increment extract decorator to generate both start_time and end_time of extract.
        if the last extract time is not found in table, first_extr_time will be used. 
        :param name|str: the unique name of increment extract task.
        :param first_time|datetime: the first extract time and default is None. if first_time is None, first_time will be set to NOW - end_delta
        :param start_delta|float: the delta to compute extract start time.
        :param end_delta|float: the delta to compute extract end time. 
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            spec = reflect.get_function_args(func)
            if 'start_time' not in spec[0]:
                raise RequiredError("the argument with the name of 'start_time'")
            if 'end_time' not in spec[0]:
                raise RequiredError("the argument with the name of 'end_time'")
            (start_time, end_time) = etl_service.get_extract_timespan(name, reflect.get_function_path(func), first_time, start_delta, end_delta)
            data = func(start_time=start_time, end_time=end_time, *args, **kwargs)
            etl_service.update_last_extr_time(name, end_time)
            return data
        return wrapper
    return decorate
