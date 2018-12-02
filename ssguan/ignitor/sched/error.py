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

from ssguan.ignitor.base.error import Error



class CronExprError(Error):
    
    def __init__(self, field, expr):
        super(CronExprError, self).__init__('Unrecognized expression "{{expression}}" for field "{{propName}}"' , expression=expr, propName=field)
    
    @property
    def code(self):
        return 1140

class CJRunningError(Error):
    def __init__(self, job_id, job_name):
        super(CJRunningError, self).__init__("CronJob {{jobId}} {{jobName}} is running." , jobId=job_id, jobName=job_name)
        
    @property
    def code(self):
        return 1141

class SchedRunningError(Error):
    
    def __init__(self):
        super(SchedRunningError, self).__init__("Scheduler is already running.")
        
    @property
    def code(self):
        return 1132

class CJNotSavedError(Error):
    def __init__(self):
        super(CJNotSavedError, self).__init__("Cronjob is not saved.")
        
    @property
    def code(self):
        return 1133