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

import conf
from contact.contactmodel import ContactGroup
from contact.contactservice import ContactService
from core import dtutil, i18n
from core.error import RequiredError, CompareError, UnauthorizedError
from core.model import stdModel
from core.service import Service
from task.taskmodel import Task, Worksheet
from task.taskservice import TaskService


class ReportService(Service):
    
    def get_progress_data(self, user_id, start_date, end_date, worksheet_ids, group_id=None, assignee_ids=None):
        
        if worksheet_ids is None or len(worksheet_ids) == 0:
            raise RequiredError("task_label_worksheet") 
        if start_date is None:
            raise RequiredError(label="rept_label_startdate")
        if end_date is None:
            raise RequiredError(label="rept_label_enddate")
        if end_date <= start_date:
            raise CompareError(label="rept_label_enddate", limitlabel="rept_label_startdate", limit=start_date, operator=">")
        
        
        today = dtutil.localtoday(conf.get_preferred_timezone())
        finishtaskcount = 0
        progressLine = stdModel(plan={}, actual={}, forecast={})
        progressBar = {}
        for priority in i18n.get_i18n_messages(conf.get_preferred_language(), "task_priority_code", rtn_dict=True).keys():
            statusTaskCount = [0, 0, 0]  # planFinishCount, actualFinishCount, cancelCount
            progressBar[priority] = statusTaskCount
            
        rtn = stdModel(progressLine=progressLine, progressBar=progressBar, deviationTasks=[])
        
        dates = self.get_workdates(start_date, end_date, group_id)
        for date in dates:
            progressLine.plan[date] = [date, 0]  # [date, finish count]
            if date <= today:
                progressLine.actual[date] = [date, 0]  # [date, finish count]
            else:
                progressLine.forecast[date] = [date, 0]  # [date, finish count]
        
        tasks = self.fetch_tasks(user_id, None, worksheet_ids, assignee_ids)
        
        for task in tasks:
            for date, planstd in progressLine.plan.items():
                if date <= today and task.t_status_code == 'task_code_closed' and task.actual_finishdate <= date:
                        progressLine.actual[date][1] += 1
                if task.due_finishdate <= date and task.t_status_code != 'task_code_cancel':
                    planstd[1] += 1
            
            if task.t_status_code != 'task_code_closed' and task.t_status_code != 'task_code_cancel':
                progress = task.get_plan_progress_int()
                if progress > task.actual_progress:
                    task.deviationStatus = "rept_label_deviationdelay"
                elif progress < task.actual_progress:
                    task.deviationStatus = "rept_label_deviationadvance"
                    
                if progress != task.actual_progress:
                    task.assigneeName = ContactService.get_instance().get_contact_name(task.assignee_id)
                    comments = TaskService.get_instance().fetch_taskcomments(task.key(), limit=1)
                    task.lastComment = comments[0].tc_content if len(comments) > 0 else ""
                    rtn.deviationTasks.append(task)
            else:
                if task.t_status_code == 'task_code_closed' and task.actual_startdate >= start_date and task.actual_finishdate <= today:
                    finishtaskcount += 1
            
            statusTaskCount = progressBar[task.t_priority_code]
            if task.due_finishdate <= end_date:
                if task.t_status_code == 'task_code_cancel':
                    statusTaskCount[2] += 1
                else:
                    statusTaskCount[0] += 1
                    
            if task.t_status_code == 'task_code_closed':
                statusTaskCount[1] += 1
            
            
        speed = finishtaskcount / float(self.get_workdays(start_date, today, None, None))
        for date, forestd in progressLine.forecast.items():
            forestd[1] = finishtaskcount + speed * ((date - today).days + 1)
        if end_date > today:
            progressLine.forecast[today] = [today, float(progressLine.actual[today][1])]
        
        progressLine.plan = progressLine.plan.values()
        progressLine.actual = progressLine.actual.values()
        progressLine.forecast = progressLine.forecast.values()
        
        return rtn
    
    
    def get_allocation_data(self, user_id, group_id, start_date, end_date, worksheet_ids, assignee_ids):
        
        if group_id is None:
            raise RequiredError(label="cont_label_group")
        if start_date is None:
            raise RequiredError(label="rept_label_startdate")
        if end_date is None:
            raise RequiredError(label="rept_label_enddate")
        if worksheet_ids is None or len(worksheet_ids) == 0:
            raise RequiredError(label="task_label_worksheet")
        if assignee_ids is None or len(assignee_ids) == 0:
            raise RequiredError(label="rept_label_assignee")
        assignee_linedata = {}
        for assignee_id in assignee_ids:
            std = stdModel()
            std.assigneeName = ContactService.get_instance().get_contact_name(assignee_id)
            std.totalTaskCount = 0
            std.totalTaskDays = 0
            std.statusTaskCounts = {}
            for status in i18n.get_i18n_messages(conf.get_preferred_language(), "task_status_code", rtn_dict=True).keys():
                std.statusTaskCounts[status] = 0
            std.plan = {}
            dates = self.get_workdates(start_date, end_date, group_id)
            for date in dates:
                std.plan[date] = [date, 0]  # [date, finish count]
            assignee_linedata[assignee_id] = std
        
        tasks = self.fetch_tasks(user_id, group_id, worksheet_ids, assignee_ids)
        for task in tasks:
            assigneedata = assignee_linedata[task.assignee_id]
            for date, plan in assigneedata.plan.items():
                if task.due_startdate <= date and date <= task.due_finishdate:
                    plan[1] += 1
                    
            if task.due_finishdate <= end_date and task.due_startdate >= start_date:
                assigneedata.totalTaskCount += 1
                assigneedata.totalTaskDays += self.get_workdays(task.due_startdate, task.due_finishdate, group_id, task.assignee_id)
                assigneedata.statusTaskCounts[task.t_status_code] += 1
        
        sum1 = stdModel(totalTaskCount=0, totalTaskDays=0, totalWorkdays=0, totalIdleDays=0, totalBusyDays=0)
        for assignee_id, ad in assignee_linedata.items():
            ad.plan = ad.plan.values()
            idleDates = []
            busyDates = []
            for p in ad.plan:
                if p[1] == 0:
                    idleDates.append(p[0])
                elif p[1] >= 2 :
                    busyDates.append(p[0])
            ad.idlePeriod = self.get_period(idleDates, group_id, assignee_id)
            ad.busyPeriod = self.get_period(busyDates, group_id, assignee_id)
            ad.totalWorkdays = self.get_workdays(start_date, end_date, group_id, assignee_id)
            
            sum1.totalTaskCount += ad.totalTaskCount
            sum1.totalTaskDays += ad.totalTaskDays
            sum1.totalWorkdays += ad.totalWorkdays
            sum1.totalIdleDays += ad.idlePeriod.totalDays
            sum1.totalBusyDays += ad.busyPeriod.totalDays
        
        std = stdModel()
        std.details = assignee_linedata.values()
        std.sum = sum1
        return std
    
    def get_burndown_data(self, user_id, group_id, start_date, end_date, worksheet_ids=None, assignee_ids=None):
        if group_id is None:
            raise RequiredError(label="cont_label_group")
        if start_date is None:
            raise RequiredError(label="rept_label_startdate")
        if end_date is None:
            raise RequiredError(label="rept_label_enddate")
        
        today = dtutil.localtoday(conf.get_preferred_timezone())
        daysBurndownLine = stdModel(guide=[], actual=[], forecast=[], teamEffort=[], requireRate=[])
        
        workdates = self.get_workdates(start_date, end_date, group_id)
        for date in workdates:
            daysBurndownLine.guide[date] = [date, 0]  # [date, days]
            if date <= today:
                daysBurndownLine.actual[date] = [date, 0]  # [date, days]
            else:
                daysBurndownLine.forecast[date] = [date, 0]  # [date, days]
            daysBurndownLine.teamEffort = [date, 0]  # [date, days]
            daysBurndownLine.requireRate = [date, 0]  # [date, rate]
        
        tasks = self.fetch_tasks(user_id, group_id, worksheet_ids, assignee_ids)
        duration = self.get_workdays(start_date, end_date, group_id)
        for task in tasks:
            if task.due_startdate >= start_date and task.due_finishdate <= end_date:
                for date, guidearr in daysBurndownLine.guide.items():
                    task_workdays = self.get_workdays(task.due_startdate, task.due_finishdate, group_id)
                    if task.t_status_code != 'task_code_cancel':
                        days = (duration - (date - start_date).days) / duration * task_workdays
                        guidearr[1] += days
                    
                    if date <= today and task.actual:
                        """"""
                
                
        
    
    def fetch_tasks(self, user_id, group_id, worksheet_ids, assignee_ids):
        
        if group_id is not None:
            my_group_ids = ContactService.get_instance().fetch_my_groups(user_id, onlyrtnids=True)
            if group_id not in my_group_ids:
                raise UnauthorizedError()
            worksheet_ids = self.fetch_worksheet_ids(group_id, worksheet_ids=worksheet_ids)
            assignee_ids = self.fetch_assignee_ids(group_id, assignee_ids=assignee_ids)
        else:
            my_worksheet_ids = TaskService.get_instance().fetch_my_worksheets(user_id, onlyrtnids=True)
            worksheet_ids = list(set(worksheet_ids).intersection(set(my_worksheet_ids)))
        
        query = Task.all("a")
        query.what("a.uid")
        query.what("a.t_subject")
        query.what("a.due_startdate")
        query.what("a.due_finishdate")
        query.what("a.actual_progress")
        query.what("a.actual_startdate")
        query.what("a.actual_finishdate")
        query.what("a.t_status_code")
        query.what("a.assignee_id")
        if worksheet_ids != None and len(worksheet_ids) > 0:
            query.filter("a.worksheet_id in", worksheet_ids, wrapper=False)
        if assignee_ids != None and len(assignee_ids) > 0:
            query.filter("a.assignee_id in", assignee_ids, wrapper=False)
        tasks = query.fetch()
        return tasks
        
    def fetch_assignee_ids(self, group_id, assignee_ids=None):
        query = ContactGroup.all()
        query.what("contact_id")
        query.select("DISTINCT")
        query.filter("group_id =", group_id)
        
        contactgroups = query.fetch()
        aids = map(lambda x: x.contact_id, contactgroups)
        
        if assignee_ids is not None:
            aids = list(set(aids).intersection(set(assignee_ids)))
        return aids
           
    
    def fetch_worksheet_ids(self, group_id, worksheet_ids=None):
        query = Worksheet.all()
        query.what("uid")
        query.filter("group_id =", group_id)
        wids = []
        worksheets = query.fetch()
        for ws in worksheets:
            wids.append(ws.key())
        
        if worksheet_ids != None:
            wids = list(set(wids).intersection(set(worksheet_ids)))    
        return wids
    
    def get_workdates(self, start_date, end_date, group_id, assignee_id=None):
        workdates = []
        tmp_start_date = start_date
        while (end_date - tmp_start_date).days >= 0:
            workdates.append(tmp_start_date)
            tmp_start_date += datetime.timedelta(days=1)
        return workdates
    
    def get_workdays (self, start_date, end_date, group_id, assignee_id=None):
        return (end_date - start_date).days + 1
    
    def get_period(self, dates, group_id, assignee_id=None):
        rtn = stdModel(totalDays=0, periods=[])
        if dates == None or len(dates) == 0:
            return rtn
        period = stdModel()
        dates.sort()
        date = dates[0]
        period.startDate = date
        
        def _append_period(peroid, end_date):
            period.endDate = end_date
            period.days = self.get_workdays(period.startDate, period.endDate, group_id, assignee_id=assignee_id)
            rtn.totalDays += period.days
            rtn.periods.append(period)
            
        for i in range(1 , len(dates)):
            if date + datetime.timedelta(days=1) == dates[i]:
                date = dates[i]
                if i == len(dates) - 1:
                    _append_period(period, date)
            else:
                _append_period(period, date)
                date = dates[i]
                period = stdModel()
                period.startDate = date
            
        return rtn
