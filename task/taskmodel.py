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
from datetime import timedelta

import conf
from core import properti, dtutil, i18n, user
from core.model import Model
from core.properti import UniqueValidator


TASK_MODULE_NAME = "task"

class Worksheet(Model):
    MODULE = TASK_MODULE_NAME
    ws_name = properti.StringProperty("worksheetName", required=True, length=80, validator=[properti.IllegalValidator(), UniqueValidator("ws_name", scope="creator_id")])
    ws_order = properti.IntegerProperty("worksheetOrder", required=False, default=0)
    group_id = properti.IntegerProperty("groupKey", required=False)
    
    def to_dict(self):
        self.creatorDisplayName = user.get_user_display_name(self.creator_id)
        from contact.contactservice import ContactService
        self.groupName = ContactService.get_instance().get_group_name(self.group_id)
        return Model.to_dict(self)
  
class Task(Model):
    MODULE = TASK_MODULE_NAME
    t_subject = properti.StringProperty("taskSubject", required=True, length=512, validator=properti.IllegalValidator(), logged=True)
    t_description = properti.StringProperty("taskDescription", required=False, length=4294967295, validator=properti.IllegalValidator(), logged=False)    
    assignee_id = properti.IntegerProperty("taskAssigneeKey", required=True, logged=True)    
    worksheet_id = properti.IntegerProperty("worksheetKey", required=True, logged=True)
    t_status_code = properti.StringProperty("taskStatusCode", length=20, required=True, default="task_code_open", logged=True)
    t_priority_code = properti.StringProperty("taskPriorityCode", length=20, required=True, default="task_code_p3", logged=True)
    t_type_code = properti.StringProperty("taskTypeCode", length=20, required=True, default="task_code_task", logged=True)
    due_startdate = properti.DateProperty("dueStartdate", required=True, fmt=conf.get_date_py_format(), logged=True)
    due_finishdate = properti.DateProperty("dueFinishdate", required=True, fmt=conf.get_date_py_format(), validator=[properti.CompareValidator(">=", property_name="due_startdate")], logged=True)
    actual_progress = properti.IntegerProperty("actualProgress", required=True, default=0, validator=[properti.RangeValidator(0, 100)], logged=True)
    actual_startdate = properti.DateProperty("actualStartdate", required=False, fmt=conf.get_date_py_format(), logged=True)
    actual_finishdate = properti.DateProperty("actualFinishdate", required=False, fmt=conf.get_date_py_format(), validator=[properti.CompareValidator(">=", property_name="actual_startdate")], logged=True)
    story_points = properti.FloatProperty("storyPoints", required=True, logged=True)
    is_trashed = properti.BooleanProperty("isTrashed", default=False, logged=True)
    
    def get_plan_progress(self):
        planprogress = 'NA'
        if self.due_finishdate is not None and self.due_startdate is not None:
            starttime = self.due_startdate
            finishtime = self.due_finishdate
            plantd = finishtime - starttime + timedelta(days=1)
            now = dtutil.localtoday(conf.get_preferred_timezone())
            nowtd = now - starttime
            if starttime < now :
                if plantd.total_seconds() != 0:
                    planprogress = round(nowtd.total_seconds() / plantd.total_seconds(), 3) * 100
                    if planprogress > 100:
                        ps = round(plantd.total_seconds() * (planprogress - 100) / (100 * 60 * 60 * 24), 1)
                        planprogress = "100%%+%0.0f%s" % (ps, i18n.get_i18n_message(conf.get_preferred_language(), "core_label_day"))
                    else:
                        planprogress = "%0.0f%%" % planprogress            
                else:
                    planprogress = "100%"
            else:
                planprogress = "0%"
        self.planProgress = planprogress
        return planprogress
    
    def get_plan_progress_int(self):
        progress = self.get_plan_progress()
        if progress == 'NA':
            progress = 110
        elif progress.endswith("%"):
            progress = int(progress[:-1])
        else:
            progress = 100
        return progress
    
    def to_dict(self):
        self.planProgress = self.get_plan_progress()
        self.creatorDisplayName = user.get_user_display_name(self.creator_id)
        from contact.contactservice import ContactService
        self.taskAssigneeName = ContactService.get_instance().get_contact_name(self.assignee_id)
        from task.taskservice import TaskService
        self.componentKeys = map(lambda x: x.component_id, TaskService.get_instance().fetch_taskcomponents(self.key()))
        self.affectedVersionKeys = map(lambda x: x.version_id, TaskService.get_instance().fetch_taskversions(self.key(), True))
        self.fixedVersionKeys = map(lambda x: x.version_id, TaskService.get_instance().fetch_taskversions(self.key(), False))
        
        tdt = Model.to_dict(self)
        tdt['storyPoints'] = "%0.1f" % self.story_points if self.story_points is not None else ""
        return tdt
    
class TaskComment(Model):
    MODULE = TASK_MODULE_NAME
    task_id = properti.IntegerProperty("taskKey", required=True)
    tc_content = properti.StringProperty("tcContent", required=True, length=4294967295, validator=properti.IllegalValidator())

class TaskVersion(Model):    
    MODULE = TASK_MODULE_NAME
    task_id = properti.IntegerProperty("taskKey", required=True)
    version_id = properti.IntegerProperty("versionKey", required=True)
    is_affected = properti.BooleanProperty("isAffected", required=True, default=False)
    
class TaskComponent(Model):
    MODULE = TASK_MODULE_NAME
    task_id = properti.IntegerProperty("taskKey", required=True)
    component_id = properti.IntegerProperty("componentKey", required=True)

