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
from contact.contactmodel import Contact
from contact.contactservice import ContactService
from core import tag, filex, user, model, dtutil, strutil, mclog, i18n, cache
from core.error import Error, CoreError
from core.model import EMPTY_UID, Resolver, stdModel
from core.service import Service
from task.taskmodel import TaskVersion, TaskComponent
from taskmodel import  Task, TaskComment, Worksheet


CACHESPACE_WORKSPACENAME = "worksheetname"

class TaskService(Service):
    
    def create_worksheet(self, worksheet, modifier_id):
        query = Worksheet.all()
        query.order("-ws_order")
        if query.count() > 0:
            worksheet.ws_order = query.get().ws_order + 1
        else:
            worksheet.ws_order = 1
        worksheet.put(modifier_id)
        return worksheet
    
    def update_worksheet(self, worksheet, modifier_id):
        worksheet.put(modifier_id)
        return worksheet
    
    def get_worksheet_name(self, worksheet_id):
        if worksheet_id == None or int(worksheet_id) == model.EMPTY_UID:
            return i18n.get_i18n_message(conf.get_preferred_language(), "task_label_workbasket")
        name = cache.get(CACHESPACE_WORKSPACENAME, worksheet_id)
        if name != None:
            return name
        else:
            worksheet = self.get_worksheet(worksheet_id)
            name = worksheet.ws_name if worksheet is not None else ''
            cache.put(CACHESPACE_WORKSPACENAME, worksheet_id, name)
            return name
        
    def delete_worksheet(self, worksheet_id, modifier_id):
        worksheet = Worksheet.get_by_key(worksheet_id)
        worksheet.delete(modifier_id)
        query = Task.all()
        query.filter("worksheet_id =", worksheet_id)
        query.set("worksheet_id", EMPTY_UID)
        query.set("is_trashed", True)
        query.update(modifier_id)
        query = Worksheet.all()
        return True
    
    def get_worksheet(self, worksheet_id):
        worksheet = Worksheet.get_by_key(worksheet_id)
        return worksheet
    
    def fetch_my_worksheets(self, user_id, onlyrtnids=False, include_self=True):
        stmworksheets = self.fetch_worksheets(user_id, sharetome=True, withtaskcount=False)
        if include_self:
            worksheets = self.fetch_worksheets(user_id, withtaskcount=False)
            stmworksheets.extend(worksheets)
        if onlyrtnids:
            wl = map(lambda x: x.key(), stmworksheets)
        else:
            wl = stmworksheets
        return wl
    
    def fetch_worksheets(self, user_id, sharetome=None, withtaskcount=True):
        query = Worksheet.all(alias="a")
        if sharetome:
            group_ids = ContactService.get_instance().fetch_my_groups(user_id, onlyrtnids=True, include_self=False)
            if len(group_ids) > 0:
                query.filter("group_id in", group_ids)
            else:
                return []
        else:
            query.filter("creator_id =", user_id)
        
        query.order("ws_order")
        def worksheet_proc(worksheet):
            if withtaskcount:
                worksheet.taskcount = self.get_taskcount(False, user_id, worksheet_id=worksheet.uid)
        
        worksheets = query.fetch(model_proc=worksheet_proc)
        return worksheets
    
    def create_task(self, task, modifier_id):
        task.is_trashed = False
        if task.t_status_code == 'task_code_inprogress':
            task.actual_startdate = dtutil.localtoday(conf.get_preferred_timezone())
        task.put(modifier_id)
        self.create_taskcomponents(task.key(), task.component_ids, modifier_id)
        self.create_taskversions(task.key(), task.affected_version_ids, True, modifier_id)
        self.create_taskversions(task.key(), task.fixed_version_ids, False, modifier_id)
        return task
    
    def update_task(self, task, modifier_id):
        nt = Task.get_by_key(task.uid)
        if task.creator_id != modifier_id and nt.worksheet_id != task.worksheet_id:
            raise Error("task_error_movesharedtask")
        if nt.is_trashed : 
            raise Error("task_error_trashed_update")
        if task.t_status_code == 'task_code_closed':
            task.actual_finishdate = dtutil.localtoday(conf.get_preferred_timezone())
            if nt.actual_startdate is None:
                task.actual_startdate = dtutil.localtoday(conf.get_preferred_timezone())
        else:
            task.actual_finishdate = None
       
        if task.t_status_code == 'task_code_inprogress' and nt.t_status_code != 'task_code_inprogress' and task.actual_startdate != None:
            task.actual_startdate = dtutil.localtoday(conf.get_preferred_timezone())
        task.put(modifier_id)
        self.create_taskcomponents(task.key(), task.component_ids, modifier_id)
        self.create_taskversions(task.key(), task.affected_version_ids, True, modifier_id)
        self.create_taskversions(task.key(), task.fixed_version_ids, False, modifier_id)
        return task
    
    def recover_task(self, task_id, worksheet_id, modifier_id):
        task = Task.get_by_key(task_id)
        task.is_trashed = False
        task.worksheet_id = worksheet_id
        task.put(modifier_id)
        return task
    
    def move_task(self, task_id, worksheet_id, modifier_id):
        task = Task.get_by_key(task_id)
        task.worksheet_id = int(worksheet_id)
        task.put(modifier_id)
        return task
    
    def get_task(self, task_id):
        task = Task.get_by_key(task_id)
        return task
            
    def trash_tasks(self, task_ids, is_trashed, modifier_id):
        for task_id in task_ids:
            task = Task.get_by_key(task_id)
            task.is_trashed = is_trashed
            task.put(modifier_id)
        return True
    
    def empty_trash(self, user_id, modifier_id):
        query = Task.all()
        query.filter("is_trashed =", True)
        query.filter("creator_id =", user_id)
        tasks = query.fetch()
        for task in tasks:
            self.delete_task(task.key(), modifier_id)
        return True
    
    def delete_task(self, task_id, modifier_id):
        task = Task.get_by_key(int(task_id))
        if task.is_trashed:
            tag.delete_tagmodels(modifier_id, model_nk=(Task.get_modelname(), task.uid), modifier_id=modifier_id)
            filex.delete_files(task.creator_id, model_nk=(Task.get_modelname(), task.uid), modifier_id=modifier_id)
            self.delete_taskcomments(task_id, modifier_id)
            self.delete_taskversions(modifier_id, task_id=task.key(), is_affected=None)
            self.delete_taskcomponents(modifier_id, task_id=task.key())
            mclog.delete_mclogs(Task.get_modelname(), task.key(), modifier_id)
            task.delete(modifier_id)
        else:
            if task.creator_id != modifier_id:
                raise Error("task_error_deletesharedtask")
            self.trash_tasks([task.uid], True, modifier_id)
        return True
    
    def fetch_tasks(self, user_id, whats=None, filters=None, limit=20, offset=0):
        def append_filters(query):
            for ft in filters:
                for (key, value) in ft.items():
                    for nr in TASKRESOLVERS:
                        nrinst = nr(key, value)
                        query.extend(nrinst, user_id=user_id)
        
        if whats == None:
            query = Task.all(alias="a")
            for key in Task.get_properties(persistent=True).keys():
                query.what("a.%s" % key, alias=key)
        else:
            query = stdModel.all()
            query.model(Task.get_modelname(), alias="a")
            for what in whats:
                query.what("a.%s" % what, alias=what)
        
        query.select("DISTINCT")
        query.what("a.uid", alias="uid")
        
        worksheet_ids = self.fetch_my_worksheets(user_id, onlyrtnids=True)
        if len(worksheet_ids) > 0:
            query.filter("a.worksheet_id in", worksheet_ids, parenthesis="(")
            query.filter("a.creator_id =", user_id, logic="or", parenthesis=")")
        else:
            query.filter("a.creator_id =", user_id)
        
        query.order("-a.uid")
        if filters is not None:
            append_filters(query)
        
        if not query.has_filter("a.is_trashed"):
            query = query.filter("a.is_trashed =", False)
        
        def task_proc(task):
            task.mclogs = mclog.fetch_mclogs(Task.get_modelname(), task.key(), worksheet_id=self.get_worksheet_name, assignee_id=ContactService.get_instance().get_contact_name)
            task.taskComments = self.fetch_taskcomments(task.key())
            
        pager = query.fetch(limit, offset, paging=True, model_proc=task_proc)
        return pager
    
    def get_taskcount(self, is_trashed, user_id, worksheet_id=None, is_complete=None , ex_assignee_id=None):
        query = Task.all()
        query.filter("is_trashed =", is_trashed)
        if worksheet_id != None and worksheet_id != model.EMPTY_UID:
            query.filter("worksheet_id =", worksheet_id)
        elif worksheet_id == model.EMPTY_UID:
            query.filter("worksheet_id =", worksheet_id)
            query.filter("creator_id =", user_id)
        else:
            query.filter("creator_id =", user_id)
        if is_complete != None and is_complete == True:
            query.filter("t_status_code =", 'task_code_closed')
        if is_complete != None and is_complete != True:
            query.filter("t_status_code !=", 'task_code_closed')
        if ex_assignee_id != None:
            query.filter("assignee_id !=", ex_assignee_id)
        
        return query.count()
    
    def create_taskcomment(self, taskcomment, modifier_id):
        taskcomment = taskcomment.put(modifier_id)
        return taskcomment
    
    def update_taskcomment(self, taskcomment, modifier_id):
        if taskcomment.creator_id != modifier_id:
            raise Error("task_error_udpateotherstaskcomment")
        return taskcomment.put(modifier_id)

    def delete_taskcomment(self, taskcoment_id, modifier_id):
        taskcomment = TaskComment.get_by_key(taskcoment_id)
        if taskcomment.creator_id != modifier_id:
            raise Error("task_error_deleteotherstaskcomment")
        if taskcomment.creator_id != modifier_id:
            raise Error("")
        taskcomment.delete(modifier_id)
        return True
    
    def delete_taskcomments(self, task_id, modifier_id):
        query = TaskComment.all()
        query.filter("task_id =", task_id)
        query.delete(modifier_id)
        return True
    
    def fetch_taskcomments(self, task_id, limit=model.DEFAULT_FETCH_LIMIT):
        query = TaskComment.all()
        query.order("-modified_time")
        def taskcomment_proc(taskcomment):
            taskcomment.userName = user.get_user_display_name(taskcomment.creator_id)
        query.filter("task_id =", task_id)
        return query.fetch(model_proc=taskcomment_proc, limit=limit)
    
    def create_taskversion(self, taskversion, modifier_id):
        taskversion.put(modifier_id)
        return taskversion
    
    def create_taskversions(self, task_id, version_ids, is_affected, modifier_id):
        old_vids = map(lambda x: x.version_id, self.fetch_taskversions(task_id, is_affected))
        in_ids = set(version_ids).intersection(old_vids)
        add_vids = set(version_ids) - in_ids
        del_vids = set(old_vids) - in_ids
        for vkey in add_vids:
            tav = TaskVersion(task_id=task_id, version_id=vkey, is_affected=is_affected)
            self.create_taskversion(tav, modifier_id)
        for vkey in del_vids:
            self.delete_taskversion(task_id, vkey, is_affected, modifier_id)
    
    def delete_taskversions(self, modifier_id, task_id=None, version_id=None, is_affected=None):
        if task_id is None and version_id is None:
            raise CoreError("the task_id and version_id can't be None at the same time.")
        query = TaskVersion.all()
        if task_id is not None:
            query.filter("task_id =", task_id)
        if version_id is not None:
            query.filter("version_id =", version_id)
        if is_affected != None:
            query.filter("is_affected =", is_affected)
        return query.delete(modifier_id)
    
    def delete_taskversion(self, task_id, version_id, is_affected, modifier_id):
        query = TaskVersion.all()
        query.filter("task_id =", task_id)
        query.filter("version_id =", version_id)
        query.filter("is_affected =", is_affected)
        return query.delete(modifier_id)
    
    def has_taskversion(self, task_id, version_id, is_affected):
        query = TaskVersion.all()
        query.filter("task_id =", task_id)
        query.filter("version_id =", version_id)
        query.filter("is_affected =", is_affected)
        return query.count() > 0
    
    def fetch_taskversions(self, task_id, is_affected):
        query = TaskVersion.all()
        query.filter("task_id =", task_id)
        query.filter("is_affected =", is_affected)
        return query.fetch()
    
    def create_taskcomponent(self, taskcomponent, modifier_id):
        taskcomponent.put(modifier_id)
        return taskcomponent
    
    def create_taskcomponents(self, task_id, component_ids, modifier_id):
        old_component_ids = map(lambda x: x.component_id, self.fetch_taskcomponents(task_id))
        c_c_ids = set(component_ids).intersection(set(old_component_ids))
        add_cids = set(component_ids) - c_c_ids
        del_cids = set(old_component_ids) - c_c_ids
        for ckey in add_cids:
            tc = TaskComponent(task_id=task_id, component_id=ckey)
            self.create_taskcomponent(tc, modifier_id)
        for ckey in del_cids:
            self.delete_taskcomponent(task_id, ckey, modifier_id)
    
    def delete_taskcomponents(self, modifier_id, task_id=None, component_id=None):
        if task_id is None and component_id is None:
            raise CoreError("the task_id and component_id can't be None at the same time.")
        query = TaskComponent.all()
        if task_id is not None:
            query.filter("task_id =", task_id)
        if component_id is not None:
            query.filter("component_id =", component_id)
        return query.delete(modifier_id)
    
    def delete_taskcomponent(self, task_id , component_id, modifier_id):
        query = TaskComponent.all()
        query.filter("task_id =", task_id)
        query.filter("component_id =", component_id)
        query.delete(modifier_id)
    
    def has_taskcomponent(self, task_id, component_id):
        query = TaskComponent.all()
        query.filter("task_id =", task_id)
        query.filter("component_id =", component_id)
        return query.count() > 0
    
    def fetch_taskcomponents(self, task_id):
        query = TaskComponent.all()
        query.filter("task_id =", task_id)
        return query.fetch()
    

class WorksheetResolver(Resolver):
    
    TRASH_WORKSHEET_ID = -100
    
    def resolve(self, query, **kwargs):
        if self._key != "ws" or self._value == None or (not isinstance(self._value, int)):
            return query
        self._value = int(self._value)
        if self._value == self.TRASH_WORKSHEET_ID:
            query.filter("a.is_trashed =", True)
        else:
            query.filter("a.worksheet_id =", self._value)
        return query

class KeywordsResolver(Resolver):
    
    def resolve(self, query, **kwargs):
        if self._key != "kw":
            return query
        if self._value != None:
            query = query.filter("a.t_subject like ", ("%%%s%%" % self._value), parenthesis="(")
            if strutil.is_int(self._value):
                query = query.filter("a.uid = ", strutil.to_int(self._value), logic="or")
            query = query.filter("a.t_description like ", ("%%%s%%" % self._value), logic="or", parenthesis=")")
        return query

class AssigneeResolver(Resolver):
    
    ASSIGNED_TO_ME = -201
    
    def resolve(self, query, **kwargs):
        if self._key != "as":
            return query
        if self._value == model.EMPTY_UID:
            query.filter("a.assignee_id !=", model.EMPTY_UID)
        elif self._value == self.ASSIGNED_TO_ME:
            query.filter("a.assignee_id in", "(select uid from %s where bind_user_id = %d)" % (Contact.get_modelname(), kwargs["user_id"]), wrapper=False)
        else:
            query.filter("a.assignee_id =", int(self._value))
        return query

class TaskStatusResolver(Resolver):
    
    ACTIVE_TASKS = "active"
    
    def resolve(self, query, **kwargs):
        if self._key != "st":
            return query
        if self._value == self.ACTIVE_TASKS:
            query.filter("a.t_status_code !=", 'task_code_closed')        
            query.filter("a.t_status_code !=", 'task_code_cancel')            
        else:
            query.filter("a.t_status_code =", self._value)
        return query

class TaskTypeResolver(Resolver):
    
    def resolve(self, query, **kwargs):
        if self._key != "tt":
            return query
        query.filter("a.t_type_code =", self._value)
        return query
                        

class TaskPriorityResolver(Resolver):
    
    HIGHPRIORITY_TASKS = "high"
    
    def resolve(self, query, **kwargs):
        if self._key != "pr":
            return query
        if self._value == self.HIGHPRIORITY_TASKS:
            query.filter("a.t_priority_code =", 'task_code_p1', parenthesis="(")     
            query.filter("a.t_priority_code =", 'task_code_p2', logic="or", parenthesis=")")
            query.order("a.t_priority_code")
        else:
            query.filter("a.t_priority_code =", self._value)  
        query.filter("t_status_code !=", 'task_code_closed')
        return query

class DaysResolver(Resolver):
    
    OVERDUE_ID = -101
    NOTIMELIMIT_ID = -102
    
    def resolve(self, query, **kwargs):
        if self._key != "dt":
            return query
        today = dtutil.localtoday(conf.get_preferred_timezone())
        if self._value == self.OVERDUE_ID:
            query.filter('due_finishdate <', today)
            query.order('due_finishdate')
        elif self._value == self.NOTIMELIMIT_ID:
            query.filter("due_finishdate is", None, wrapper=False)
        else:
            query.filter('ex ex', "DATEDIFF(due_finishdate, '%s') <= %d" % (str(today), self._value), wrapper=False)
            query.order('due_finishdate')
        
        query.filter("t_status_code !=", 'task_code_closed')
        query.filter("t_status_code !=", 'task_code_cancel')
        return query
    
class VersionResolver(Resolver):
    
    def resolve(self, query, **kwargs):
        if self._key != "fv" and self._key != "av":
            return query
        if self._key == 'av':
            is_affected = True
        else:
            is_affected = False
        alias = query.get_model_alias(TaskVersion.get_modelname())
        if alias is None:
            query.model(TaskVersion.get_modelname(), alias="b", join="inner", on="a.uid=b.task_id")
        query.filter("b.is_affected =", is_affected)
        query.filter("b.version_id =", self._value)
        return query
    
class ComponentResolver(Resolver):
    
    def resolve(self, query, **kwargs):
        if self._key != "co":
            return query
        alias = query.get_model_alias(TaskComponent.get_modelname())
        if alias is None:
            query.model(TaskComponent.get_modelname(), alias="c", join="inner", on="a.uid=b.task_id")
        query.filter("b.component_id =", self._value)
        return query
    
            
TASKRESOLVERS = [WorksheetResolver, KeywordsResolver, AssigneeResolver, TaskPriorityResolver, TaskStatusResolver, TaskTypeResolver, DaysResolver, VersionResolver, ComponentResolver]
