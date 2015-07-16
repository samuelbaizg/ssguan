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
import conf
from contact.contactservice import ContactService
from core import jsonutil, i18n, mclog
from core import strutil, model
from core import user
from core.error import RequiredError
from core.handler import Handler
from core.model import stdModel
from task.taskmodel import Task, Worksheet, TaskComment
from task.taskservice import TaskService
import web


class WorksheetSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        worksheet = self._get_model_parameter(Worksheet)
        if strutil.is_empty(worksheet.key()):
            worksheet.creator_id = self._get_user_id()
            worksheet = TaskService.get_instance().create_worksheet(worksheet, self._get_user_id())
        else:
            worksheet = TaskService.get_instance().update_worksheet(worksheet, self._get_user_id())
        rtn.set_data(worksheet)
        return rtn.to_json()

class WorksheetDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        worksheet_id = self._get_int_parameter("worksheetKey")
        status = TaskService.get_instance().delete_worksheet(worksheet_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class TaskEmptyTrashHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        status = TaskService.get_instance().empty_trash(self._get_user_id(), self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class WorksheetListHandler(Handler):
    
    def execute(self):        
        rtn = self._new_rtn()
        worksheets = TaskService.get_instance().fetch_worksheets(self._get_user_id())
        std = stdModel()
        workbasket = Worksheet()
        workbasket.uid = model.EMPTY_UID
        workbasket.ws_name = i18n.get_i18n_message(conf.get_preferred_language(), "task_label_workbasket")
        workbasket.taskcount = TaskService.get_instance().get_taskcount(False, self._get_user_id(), worksheet_id=model.EMPTY_UID)
        workbasket.creator_id = self._get_user_id()
        worksheets.insert(0, workbasket)
        
        trash = Worksheet()
        trash.uid = -100
        trash.ws_name = i18n.get_i18n_message(conf.get_preferred_language(), "task_label_recyclebin")
        trash.taskcount = TaskService.get_instance().get_taskcount(True, self._get_user_id())
        trash.creator_id = self._get_user_id()
        worksheets.append(trash)
        
        std.worksheets = worksheets
        
        std.contactGroups = ContactService.get_instance().fetch_my_groups(self._get_user_id())
        
        stmworksheets = TaskService.get_instance().fetch_worksheets(self._get_user_id(), sharetome=True)
        std.worksheets.extend(stmworksheets)
        
        std.worksheetComponents = {}
        std.worksheetVersions = {}
        std.worksheetContacts = {}
        
        for worksheet in std.worksheets:
            if worksheet.group_id != None and worksheet.group_id != model.EMPTY_UID:
                std.worksheetComponents[worksheet.key()] = ContactService.get_instance().fetch_groupcomponents(worksheet.group_id)
                std.worksheetVersions[worksheet.key()] = ContactService.get_instance().fetch_groupversions(worksheet.group_id)
                std.worksheetContacts[worksheet.key()] = ContactService.get_instance().fetch_contacts_by_group(worksheet.group_id)
            else:
                myself = ContactService.get_instance().get_myself(self._get_user_id())
                if myself is not None:
                    std.worksheetContacts[worksheet.key()] = [myself]
        rtn.set_data(std)
        return rtn.to_json()

class TaskListHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        offset = self._get_int_parameter('offset', 1)
        limit = self._get_int_parameter('limit', 20)
        filters = self._get_str_parameter('filters')
        filters = jsonutil.to_dict(filters)
        pager = TaskService.get_instance().fetch_tasks(self._get_user_id(), filters=filters, limit=limit, offset=offset)            
        rtn.set_data(pager)
        return rtn.to_json()
        
class TaskSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        task = self._get_model_parameter(Task)
        affectedVersionKeys = self._get_str_parameter("affectedVersionKeys", '')
        task.affected_version_ids = map(int, affectedVersionKeys.split(",")) if affectedVersionKeys.strip() != '' else []
        fixedVersionKeys = self._get_str_parameter("fixedVersionKeys", '')
        task.fixed_version_ids = map(int, fixedVersionKeys.split(",")) if fixedVersionKeys.strip() != '' else []
        componentKeys = self._get_str_parameter("componentKeys", '')
        task.component_ids = map(int, componentKeys.split(",")) if componentKeys.strip() != '' else []
        
        if strutil.is_empty(task.key()):
            task.creator_id = self._get_user_id()
            task = TaskService.get_instance().create_task(task, self._get_user_id())
            task.taskComments = []
            task.mclogs = []
        else:
            task = TaskService.get_instance().update_task(task, self._get_user_id())
            task.taskComments = TaskService.get_instance().fetch_taskcomments(task.key())
            task.mclogs = mclog.fetch_mclogs(Task.get_modelname(), task.key(), worksheet_id=TaskService.get_instance().get_worksheet_name, assignee_id=ContactService.get_instance().get_contact_name)
        
        rtn.set_data(task)
        return rtn.to_json()

class TaskDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        task_id = self._get_int_parameter("taskKey")
        status = TaskService.get_instance().delete_task(task_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class TaskRecoverHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        task_id = self._get_int_parameter("taskKey")
        worksheet_id = self._get_int_parameter("worksheetKey", default=model.EMPTY_UID)
        status = TaskService.get_instance().recover_task(task_id, worksheet_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()
    

class TaskCommentSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        taskcomment = self._get_model_parameter(TaskComment)
        t = taskcomment.tc_content.replace("&nbsp;", "")
        if strutil.is_empty(t):
            raise RequiredError("task_label_tccontent")
        if strutil.is_empty(taskcomment.key()):
            taskcomment.creator_id = self._get_user_id()
            taskcomment = TaskService.get_instance().create_taskcomment(taskcomment, self._get_user_id())
        else:
            taskcomment = TaskService.get_instance().update_taskcomment(taskcomment, self._get_user_id())
        taskcomment.userName = user.get_user_display_name(taskcomment.creator_id)
        
        rtn.set_data(taskcomment)
        return rtn.to_json()

class TaskCommentDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        comment_id = self._get_int_parameter("commentKey")
        status = TaskService.get_instance().delete_taskcomment(comment_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()
