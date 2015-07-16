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
from core.handler import Handler
from core.model import stdModel
from report.reportservice import ReportService
from task.taskservice import TaskService
import web
from contact.contactservice import ContactService


class ReportBaseDataHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        std = stdModel()
        if self._get_bool_parameter("ws", False):
            std.worksheets = self._loadWorksheets()
        if self._get_bool_parameter("gr", False):
            std.groups = self._loadGroups()
        if self._get_bool_parameter("as", False):
            std.assignees = self._loadAssignees()
        rtn.set_data(std)
        return rtn.to_json()
    
    
    def _loadWorksheets(self):
        worksheets = TaskService.get_instance().fetch_my_worksheets(self._get_user_id())
        return worksheets
    
    def _loadGroups(self):
        groups = ContactService.get_instance().fetch_my_groups(self._get_user_id())
        return groups
        
    def _loadAssignees(self):
        assignees = ContactService.get_instance().fetch_my_contacts(self._get_user_id())
        return assignees
        

class RptAllocationChartHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        group_id = self._get_int_parameter("groupKey", None)
        start_date = self._get_date_parameter("startDate", conf.get_date_py_format())
        end_date = self._get_date_parameter("endDate", conf.get_date_py_format())
        worksheet_ids = self._get_str_parameter("worksheetKeys")
        worksheet_ids = map(int, worksheet_ids.split(",")) if worksheet_ids is not None else None
        assignee_ids = self._get_str_parameter("assigneeKeys")
        assignee_ids = map(int, assignee_ids.split(",")) if assignee_ids is not None else None
        data = ReportService.get_instance().get_allocation_data(self._get_user_id(), group_id, start_date, end_date, worksheet_ids, assignee_ids)
        rtn.set_data(data)
        return rtn.to_json()

class RptProgressChartHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        group_id = self._get_int_parameter("groupKey", None)
        worksheet_ids = self._get_str_parameter("worksheetKeys")
        worksheet_ids = map(int, worksheet_ids.split(",")) if worksheet_ids is not None else None
        assignee_ids = self._get_str_parameter("assigneeKeys")
        assignee_ids = map(int, assignee_ids.split(",")) if assignee_ids is not None else None
        start_date = self._get_date_parameter("startDate", conf.get_date_py_format())
        end_date = self._get_date_parameter("endDate", conf.get_date_py_format())
        data = ReportService.get_instance().get_progress_data(self._get_user_id(), start_date, end_date, worksheet_ids, group_id=group_id, assignee_ids=assignee_ids)
        rtn.set_data(data)
        return rtn.to_json()
