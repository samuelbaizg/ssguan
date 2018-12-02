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
from core.db import dbutil
from core.migration import Version
from core.model import I18n


class V2(Version):
    
    def _upgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        b = self._exist_column('task_task', 't_type')
        if b is True:
            sql = "ALTER TABLE task_task DROP t_type;"
            conn.query(sql)
        
        b = self._exist_column('task_task', 't_status')
        if b is True:
            sql = "ALTER TABLE task_task CHANGE t_status t_status_code VARCHAR(20);"
            conn.query(sql)
        b = self._exist_column('task_task', 't_priority')
        if b is True:
            sql = "ALTER TABLE task_task CHANGE t_priority t_priority_code VARCHAR(20);"
            conn.query(sql)
            
        b = self._exist_column('task_task', 'due_starttime')
        if b is True:
            sql = "ALTER TABLE task_task CHANGE due_starttime due_startdate DATE;"
            conn.query(sql)
            
        b = self._exist_column('task_task', 'due_finishtime')
        if b is True:
            sql = "ALTER TABLE task_task CHANGE due_finishtime due_finishdate DATE;"
            conn.query(sql)
            
        sql = "delete from core_i18n where i1_type = 'task_type_code'"
        conn.query(sql)
        sql = "delete from core_userprop where p_key = 'TASK_TYPE_OPTIONS'"
        conn.query(sql)
        sql = "delete from core_userprop where p_key = 'TASK_PRIORITY_OPTIONS'"
        conn.query(sql)
        sql = "delete from core_userprop where p_key = 'TASK_STATUS_OPTIONS'"
        conn.query(sql)
        
    def _downgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        b = self._exist_column('task_task', 't_type')
        if b is False:
            sql = "ALTER TABLE task_task ADD t_type VARCHAR(20) NOT NULL DEFAULT 0 AFTER uid;"
            conn.query(sql)
        
        b = self._exist_column('task_task', 't_status_code')
        if b is False:
            sql = "ALTER TABLE task_task CHANGE t_status_code t_status VARCHAR(20);"
            conn.query(sql)
        b = self._exist_column('task_task', 't_priority_code')
        if b is True:
            sql = "ALTER TABLE task_task CHANGE t_priority_code t_priority VARCHAR(20);"
            conn.query(sql)
        
        b = self._exist_column('task_task', 'due_startdate')
        if b is True:
            sql = "ALTER TABLE task_task CHANGE due_startdate due_starttime DATE;"
            conn.query(sql)
            
        b = self._exist_column('task_task', 'due_finishdate')
        if b is True:
            sql = "ALTER TABLE task_task CHANGE due_finishdate due_finishtime DATE;"
            conn.query(sql)
            
            
    def _get_roles(self):
        return []
    
    def _get_operations(self):
        operations = []
        return operations
    
    def _get_roleoperations(self):
        roleoperations = []       
        return roleoperations
    
    def _get_i18ns(self):
        i18ns = []
        i18ns.append(I18n(i1_key="core_error_compare", i1_locale=conf.LANG_EN, i1_message=u"The value of {{label}} must {{operator}} {{limitlabel}}{{limit}}."))
        i18ns.append(I18n(i1_key="core_error_compare", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}} 必须 {{operator}} {{limitlabel}}{{limit}}。"))
        return i18ns
