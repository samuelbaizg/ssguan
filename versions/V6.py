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
from contact.contacthandler import GroupVersionSaveHandler, \
    GroupVersionListHandler, GroupVersionDeleteHandler, \
    GroupComponentSaveHandler, GroupComponentListHandler, \
    GroupComponentDeleteHandler, GroupExceptionListHandler, \
    GroupExceptionSaveHandler, GroupExceptionDeleteHandler, \
    GroupResourceDeleteHandler, GroupResourceSaveHandler, \
    GroupResourceListHandler, ContactLeaveSaveHandler, ContactLeaveDeleteHandler
from contact.contactmodel import ContactLeave, GroupVersion, GroupComponent, \
    GroupException
from core import user
from core.db import dbutil
from core.migration import Version
from core.model import I18n, Operation, RoleOperation
from task.taskhandler import TaskCommentDeleteHandler
from task.taskmodel import TaskComponent, TaskVersion


class V6(Version):
    
    def _upgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        ContactLeave.create_table(conn=conn)
        GroupVersion.create_table(conn=conn)
        GroupComponent.create_table(conn=conn)
        GroupException.create_table(conn=conn)
        TaskComponent.create_table(conn=conn)
        TaskVersion.create_table(conn=conn)
        sql = "UPDATE core_i18n SET i1_key = 'task_label_taskprioritycode' WHERE i1_key = 'task_label_taskpriority';"
        conn.query(sql)
        sql = "UPDATE core_i18n SET i1_key = 'task_label_taskstatuscode' WHERE i1_key = 'task_label_taskstatus';"
        conn.query(sql)
        sql = "UPDATE core_i18n SET i1_key = 'task_label_tasktypecode' WHERE i1_key = 'task_label_tasktype';"
        conn.query(sql)
        
        b = self._exist_column('task_task', 'story_points')
        if b is False:
            sql = "ALTER TABLE task_task ADD story_points FLOAT NULL"
            conn.query(sql)
            sql = "UPDATE task_task SET story_points = 1.0;"
            conn.query(sql)
            
        workday_weekdays = ['workday_monday', 'workday_tuesday', 'workday_wednesday', 'workday_thursday', 'workday_friday', 'workday_saturday', 'workday_sunday']
        
        for workday_weekday in workday_weekdays:
            b = self._exist_column('cont_group', workday_weekday)
            if b is False:
                sql = "ALTER TABLE cont_group ADD %s float" % workday_weekday
                conn.query(sql)
                sql = "UPDATE cont_group SET %s = 0;" % workday_weekday
                conn.query(sql)
                
        b = self._exist_column('cont_contactgroup', 'join_date')
        if b is False:
            sql = "ALTER TABLE cont_contactgroup ADD join_date DATE NULL"
            conn.query(sql)
        b = self._exist_column('cont_contactgroup', 'quit_date')
        if b is False:
            sql = "ALTER TABLE cont_contactgroup ADD quit_date DATE NULL"
            conn.query(sql)
        b = self._exist_column('cont_contactgroup', 'is_billable')
        if b is False:
            sql = "ALTER TABLE cont_contactgroup ADD is_billable tinyint(1) NULL"
            conn.query(sql)
            sql = "UPDATE cont_contactgroup SET is_billable = 0;"
            conn.query(sql)
        b = self._exist_column('cont_contactgroup', 'contact_level')
        if b is False:
            sql = "ALTER TABLE cont_contactgroup ADD contact_level int(4) NULL"
            conn.query(sql)
            sql = "UPDATE cont_contactgroup SET contact_level = 1;"
            conn.query(sql)
        b = self._exist_column('cont_contact', 'ct_company_website')
        if b is False:
            sql = "ALTER TABLE cont_contact ADD ct_company_website varchar(80) NULL"
            conn.query(sql)
            
        sql = "DELETE FROM core_i18n WHERE i1_key = 'note_label_zeronote'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'cont_label_zerocontact'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'task_label_zerotask'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'task_label_nocomment'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'cont_label_leavetype'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'cont_label_leaveenddate'"
        conn.query(sql)
            
    def _downgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        ContactLeave.delete_table(conn=conn)
        GroupVersion.delete_table(conn=conn)
        GroupComponent.delete_table(conn=conn)
        GroupException.delete_table(conn=conn)
        TaskComponent.delete_table(conn=conn)
        TaskVersion.delete_table(conn=conn)
        sql = "UPDATE core_i18n SET i1_key = 'task_label_taskpriority' WHERE i1_key = 'task_label_taskprioritycode';"
        conn.query(sql)
        sql = "UPDATE core_i18n SET i1_key = 'task_label_taskstatus' WHERE i1_key = 'task_label_taskstatuscode';"
        conn.query(sql)
        sql = "UPDATE core_i18n SET i1_key = 'task_label_tasktype' WHERE i1_key = 'task_label_tasktypecode';"
        conn.query(sql)
        b = self._exist_column('task_task', 'story_points')
        if b is True:
            sql = "ALTER TABLE task_task DROP story_points"
            conn.query(sql)
        
        workday_weekdays = ['workday_monday', 'workday_tuesday', 'workday_wednesday', 'workday_thursday', 'workday_friday', 'workday_saturday', 'workday_sunday']
        for workday_weekday in workday_weekdays:
            b = self._exist_column('cont_group', workday_weekday)
            if b is True:
                sql = "ALTER TABLE cont_group DROP %s;" % workday_weekday
                conn.query(sql)
        
        b = self._exist_column('cont_contactgroup', 'join_date')
        if b is True:
            sql = "ALTER TABLE cont_contactgroup DROP join_date"
            conn.query(sql)
        b = self._exist_column('cont_contactgroup', 'quit_date')
        if b is True:
            sql = "ALTER TABLE cont_contactgroup DROP quit_date"
            conn.query(sql)
        b = self._exist_column('cont_contactgroup', 'is_billable')
        if b is True:
            sql = "ALTER TABLE cont_contactgroup DROP is_billable"
            conn.query(sql)
        b = self._exist_column('cont_contactgroup', 'contact_level')
        if b is True:
            sql = "ALTER TABLE cont_contactgroup DROP contact_level"
            conn.query(sql)
        b = self._exist_column('cont_contact', 'ct_company_website')
        if b is True:
            sql = "ALTER TABLE cont_contact DROP ct_company_website"
            conn.query(sql)
            
    def _get_roles(self):
        return []

    def _get_operations(self):
        operations = []
        operations.append(Operation(operation_key="SETTINGS_GROUPVERSION", handler_classes=GroupVersionSaveHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPVERSION", handler_classes=GroupVersionListHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPVERSION", handler_classes=GroupVersionDeleteHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPCOMPONENT", handler_classes=GroupComponentSaveHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPCOMPONENT", handler_classes=GroupComponentListHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPCOMPONENT", handler_classes=GroupComponentDeleteHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPEXCEPTION", handler_classes=GroupExceptionSaveHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPEXCEPTION", handler_classes=GroupExceptionListHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPEXCEPTION", handler_classes=GroupExceptionDeleteHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPRESOURCE", handler_classes=GroupResourceSaveHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPRESOURCE", handler_classes=GroupResourceListHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_GROUPRESOURCE", handler_classes=GroupResourceDeleteHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_CONTACTLEAVE", handler_classes=ContactLeaveSaveHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="SETTINGS_CONTACTLEAVE", handler_classes=ContactLeaveDeleteHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="TASK_TASKCOMMENTDELETE", handler_classes=TaskCommentDeleteHandler.get_qualified_name(), resource_oql=None))
        return operations
    
    def _get_roleoperations(self):
        roleoperations = []
        ordinary_role = user.get_role(role_name="Ordinary User")
        roleoperations.append(RoleOperation(role_id=ordinary_role.uid, operation_key="SETTINGS_GROUPVERSION"))
        roleoperations.append(RoleOperation(role_id=ordinary_role.uid, operation_key="SETTINGS_GROUPCOMPONENT"))
        roleoperations.append(RoleOperation(role_id=ordinary_role.uid, operation_key="SETTINGS_GROUPEXCEPTION"))
        roleoperations.append(RoleOperation(role_id=ordinary_role.uid, operation_key="SETTINGS_GROUPRESOURCE"))
        roleoperations.append(RoleOperation(role_id=ordinary_role.uid, operation_key="SETTINGS_CONTACTLEAVE"))
        roleoperations.append(RoleOperation(role_id=ordinary_role.uid, operation_key="TASK_TASKCOMMENTDELETE"))
        return roleoperations    

    def _get_i18ns(self):
        i18ns = []
                

        i18ns.append(I18n(i1_key="cont_label_leavefinishdate", i1_locale=conf.LANG_EN, i1_message=u"End Date"))        
        i18ns.append(I18n(i1_key="cont_label_leavefinishdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"结束日期"))
        i18ns.append(I18n(i1_key="cont_label_leavetypecode", i1_locale=conf.LANG_EN, i1_message=u"Vacation Type"))        
        i18ns.append(I18n(i1_key="cont_label_leavetypecode", i1_locale=conf.LANG_ZH_CN, i1_message=u"休假类型"))
        i18ns.append(I18n(i1_key="cont_label_leaveperiod", i1_locale=conf.LANG_EN, i1_message=u"Leave Period"))        
        i18ns.append(I18n(i1_key="cont_label_leaveperiod", i1_locale=conf.LANG_ZH_CN, i1_message=u"休假日期"))
        
        i18ns.append(I18n(i1_key="cont_label_workdaymonday", i1_locale=conf.LANG_EN, i1_message=u"Monday"))        
        i18ns.append(I18n(i1_key="cont_label_workdaymonday", i1_locale=conf.LANG_ZH_CN, i1_message=u"星期一"))
        i18ns.append(I18n(i1_key="cont_label_workdaytuesday", i1_locale=conf.LANG_EN, i1_message=u"Tuesday"))        
        i18ns.append(I18n(i1_key="cont_label_workdaytuesday", i1_locale=conf.LANG_ZH_CN, i1_message=u"星期二"))
        i18ns.append(I18n(i1_key="cont_label_workdaywednesday", i1_locale=conf.LANG_EN, i1_message=u"Wednesday"))        
        i18ns.append(I18n(i1_key="cont_label_workdaywednesday", i1_locale=conf.LANG_ZH_CN, i1_message=u"星期三"))
        i18ns.append(I18n(i1_key="cont_label_workdaythursday", i1_locale=conf.LANG_EN, i1_message=u"Thursday"))        
        i18ns.append(I18n(i1_key="cont_label_workdaythursday", i1_locale=conf.LANG_ZH_CN, i1_message=u"星期四"))
        i18ns.append(I18n(i1_key="cont_label_workdayfriday", i1_locale=conf.LANG_EN, i1_message=u"Friday"))        
        i18ns.append(I18n(i1_key="cont_label_workdayfriday", i1_locale=conf.LANG_ZH_CN, i1_message=u"星期五"))
        i18ns.append(I18n(i1_key="cont_label_workdaysaturday", i1_locale=conf.LANG_EN, i1_message=u"Saturday"))        
        i18ns.append(I18n(i1_key="cont_label_workdaysaturday", i1_locale=conf.LANG_ZH_CN, i1_message=u"星期六"))
        i18ns.append(I18n(i1_key="cont_label_workdaysunday", i1_locale=conf.LANG_EN, i1_message=u"Sunday"))        
        i18ns.append(I18n(i1_key="cont_label_workdaysunday", i1_locale=conf.LANG_ZH_CN, i1_message=u"星期日"))
        
        i18ns.append(I18n(i1_key="cont_label_groupstartdate", i1_locale=conf.LANG_EN, i1_message=u"Start Date"))        
        i18ns.append(I18n(i1_key="cont_label_groupstartdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"开始日期"))
        i18ns.append(I18n(i1_key="cont_label_groupfinishdate", i1_locale=conf.LANG_EN, i1_message=u"Finish Date"))        
        i18ns.append(I18n(i1_key="cont_label_groupfinishdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"结束日期"))
        i18ns.append(I18n(i1_key="cont_label_groupperiod", i1_locale=conf.LANG_EN, i1_message=u"Group Peroid"))        
        i18ns.append(I18n(i1_key="cont_label_groupperiod", i1_locale=conf.LANG_ZH_CN, i1_message=u"分组周期"))
        
        i18ns.append(I18n(i1_key="cont_label_joindate", i1_locale=conf.LANG_EN, i1_message=u"Join Date"))        
        i18ns.append(I18n(i1_key="cont_label_joindate", i1_locale=conf.LANG_ZH_CN, i1_message=u"加入日期"))
        i18ns.append(I18n(i1_key="cont_label_quitdate", i1_locale=conf.LANG_EN, i1_message=u"Quit Date"))        
        i18ns.append(I18n(i1_key="cont_label_quitdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"退出日期"))
        i18ns.append(I18n(i1_key="cont_label_versionname", i1_locale=conf.LANG_EN, i1_message=u"Version Name"))        
        i18ns.append(I18n(i1_key="cont_label_versionname", i1_locale=conf.LANG_ZH_CN, i1_message=u"版本名称"))
        i18ns.append(I18n(i1_key="cont_label_verstartdate", i1_locale=conf.LANG_EN, i1_message=u"Start Date"))        
        i18ns.append(I18n(i1_key="cont_label_verstartdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"开始日期"))
        i18ns.append(I18n(i1_key="cont_label_verfinishdate", i1_locale=conf.LANG_EN, i1_message=u"Finish Date"))        
        i18ns.append(I18n(i1_key="cont_label_verfinishdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"结束日期"))
        i18ns.append(I18n(i1_key="cont_label_verdescription", i1_locale=conf.LANG_EN, i1_message=u"Description"))        
        i18ns.append(I18n(i1_key="cont_label_verdescription", i1_locale=conf.LANG_ZH_CN, i1_message=u"版本描述"))
        i18ns.append(I18n(i1_key="cont_label_componentname", i1_locale=conf.LANG_EN, i1_message=u"Component Name"))        
        i18ns.append(I18n(i1_key="cont_label_componentname", i1_locale=conf.LANG_ZH_CN, i1_message=u"组件名称"))
        i18ns.append(I18n(i1_key="cont_label_compodescription", i1_locale=conf.LANG_EN, i1_message=u"Description"))        
        i18ns.append(I18n(i1_key="cont_label_compodescription", i1_locale=conf.LANG_ZH_CN, i1_message=u"组件描述"))
        i18ns.append(I18n(i1_key="cont_label_expstartdate", i1_locale=conf.LANG_EN, i1_message=u"Exception Start Date"))        
        i18ns.append(I18n(i1_key="cont_label_expstartdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"开始日期"))
        i18ns.append(I18n(i1_key="cont_label_expfinishdate", i1_locale=conf.LANG_EN, i1_message=u"Exception Finish Date"))        
        i18ns.append(I18n(i1_key="cont_label_expfinishdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"结束日期"))
        i18ns.append(I18n(i1_key="cont_label_iswork", i1_locale=conf.LANG_EN, i1_message=u"Is Work"))        
        i18ns.append(I18n(i1_key="cont_label_iswork", i1_locale=conf.LANG_ZH_CN, i1_message=u"是否工作"))
        i18ns.append(I18n(i1_key="cont_label_exceptionname", i1_locale=conf.LANG_EN, i1_message=u"Excpetion Name"))        
        i18ns.append(I18n(i1_key="cont_label_exceptionname", i1_locale=conf.LANG_ZH_CN, i1_message=u"例外名称"))
        i18ns.append(I18n(i1_key="cont_label_workday", i1_locale=conf.LANG_EN, i1_message=u"Work Day"))        
        i18ns.append(I18n(i1_key="cont_label_workday", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作日"))
        
        i18ns.append(I18n(i1_key="cont_label_exceptionwork", i1_locale=conf.LANG_EN, i1_message=u"Exception"))        
        i18ns.append(I18n(i1_key="cont_label_exceptionwork", i1_locale=conf.LANG_ZH_CN, i1_message=u"例外"))
        
        i18ns.append(I18n(i1_key="cont_label_isbillable", i1_locale=conf.LANG_EN, i1_message=u"Is Billable"))        
        i18ns.append(I18n(i1_key="cont_label_isbillable", i1_locale=conf.LANG_ZH_CN, i1_message=u"是否收取费用"))
        i18ns.append(I18n(i1_key="cont_label_contactlevel", i1_locale=conf.LANG_EN, i1_message=u"Level"))        
        i18ns.append(I18n(i1_key="cont_label_contactlevel", i1_locale=conf.LANG_ZH_CN, i1_message=u"联系人等级"))
        i18ns.append(I18n(i1_key="cont_label_isreleased", i1_locale=conf.LANG_EN, i1_message=u"Is Released"))        
        i18ns.append(I18n(i1_key="cont_label_isreleased", i1_locale=conf.LANG_ZH_CN, i1_message=u"是否已发布"))
        i18ns.append(I18n(i1_key="cont_label_releasedate", i1_locale=conf.LANG_EN, i1_message=u"Release Date"))        
        i18ns.append(I18n(i1_key="cont_label_releasedate", i1_locale=conf.LANG_ZH_CN, i1_message=u"发布日期"))
        i18ns.append(I18n(i1_key="cont_error_choosegroup", i1_locale=conf.LANG_EN, i1_message=u"Please Choose Contact Group."))        
        i18ns.append(I18n(i1_key="cont_error_choosegroup", i1_locale=conf.LANG_ZH_CN, i1_message=u"请选择联系人分组。"))
        
        i18ns.append(I18n(i1_key="task_label_assigneetip", i1_locale=conf.LANG_EN, i1_message=u"Assignee will be set oneself by default. The suishouguan account = own account will express oneself."))        
        i18ns.append(I18n(i1_key="task_label_assigneetip", i1_locale=conf.LANG_ZH_CN, i1_message=u"责任人会默认选中自己。联系人的属性‘随手管账号’如果等于自己的登录账号，则表示自己。"))
        
        i18ns.append(I18n(i1_key="task_code_story", i1_locale=conf.LANG_EN, i1_message=u"Story", i1_type="task_type_code"))
        i18ns.append(I18n(i1_key="task_code_story", i1_locale=conf.LANG_ZH_CN, i1_message=u"故事", i1_type="task_type_code"))
 
        i18ns.append(I18n(i1_key="task_label_storypoints", i1_locale=conf.LANG_EN, i1_message=u"Story Points"))        
        i18ns.append(I18n(i1_key="task_label_storypoints", i1_locale=conf.LANG_ZH_CN, i1_message=u"点数"))
        i18ns.append(I18n(i1_key="task_label_components", i1_locale=conf.LANG_EN, i1_message=u"Component(s)"))        
        i18ns.append(I18n(i1_key="task_label_components", i1_locale=conf.LANG_ZH_CN, i1_message=u"组件"))
        i18ns.append(I18n(i1_key="task_label_affectedversions", i1_locale=conf.LANG_EN, i1_message=u"Affected Version(s)"))        
        i18ns.append(I18n(i1_key="task_label_affectedversions", i1_locale=conf.LANG_ZH_CN, i1_message=u"影响版本"))
        i18ns.append(I18n(i1_key="task_label_fixedversions", i1_locale=conf.LANG_EN, i1_message=u"Fixed Version(s)"))        
        i18ns.append(I18n(i1_key="task_label_fixedversions", i1_locale=conf.LANG_ZH_CN, i1_message=u"修复版本"))
        
        i18ns.append(I18n(i1_key="user_label_securitysettings", i1_locale=conf.LANG_EN, i1_message=u"Security Settings"))        
        i18ns.append(I18n(i1_key="user_label_securitysettings", i1_locale=conf.LANG_ZH_CN, i1_message=u"安全设置"))
        i18ns.append(I18n(i1_key="cont_label_addgroupversion", i1_locale=conf.LANG_EN, i1_message=u"Add Task Version"))        
        i18ns.append(I18n(i1_key="cont_label_addgroupversion", i1_locale=conf.LANG_ZH_CN, i1_message=u"新增工作事项版本"))
        i18ns.append(I18n(i1_key="cont_label_addgroupcomponent", i1_locale=conf.LANG_EN, i1_message=u"Add Task Component"))        
        i18ns.append(I18n(i1_key="cont_label_addgroupcomponent", i1_locale=conf.LANG_ZH_CN, i1_message=u"新增工作事项组件"))
        i18ns.append(I18n(i1_key="cont_label_addgroupexcpetion", i1_locale=conf.LANG_EN, i1_message=u"Add Exception"))        
        i18ns.append(I18n(i1_key="cont_label_addgroupexcpetion", i1_locale=conf.LANG_ZH_CN, i1_message=u"新增例外日期"))
        i18ns.append(I18n(i1_key="cont_label_addresource", i1_locale=conf.LANG_EN, i1_message=u"Add Group Resource"))        
        i18ns.append(I18n(i1_key="cont_label_addresource", i1_locale=conf.LANG_ZH_CN, i1_message=u"新增分组成员"))
        i18ns.append(I18n(i1_key="cont_label_contactleave", i1_locale=conf.LANG_EN, i1_message=u"Contact Leave"))        
        i18ns.append(I18n(i1_key="cont_label_contactleave", i1_locale=conf.LANG_ZH_CN, i1_message=u"联系人请假"))
        i18ns.append(I18n(i1_key="cont_action_addcotactleave", i1_locale=conf.LANG_EN, i1_message=u"Add Contact Leave"))        
        i18ns.append(I18n(i1_key="cont_action_addcotactleave", i1_locale=conf.LANG_ZH_CN, i1_message=u"新增联系人请假"))
        i18ns.append(I18n(i1_key="cont_label_companywebsite", i1_locale=conf.LANG_EN, i1_message=u"Website"))        
        i18ns.append(I18n(i1_key="cont_label_companywebsite", i1_locale=conf.LANG_ZH_CN, i1_message=u"官方网址"))
        
        i18ns.append(I18n(i1_key="cont_label_groupcalendar", i1_locale=conf.LANG_EN, i1_message=u"Work Calendar"))        
        i18ns.append(I18n(i1_key="cont_label_groupcalendar", i1_locale=conf.LANG_ZH_CN, i1_message=u"分组工作日历"))
        i18ns.append(I18n(i1_key="cont_label_groupresource", i1_locale=conf.LANG_EN, i1_message=u"Work Resource"))        
        i18ns.append(I18n(i1_key="cont_label_groupresource", i1_locale=conf.LANG_ZH_CN, i1_message=u"分组工作成员"))
        i18ns.append(I18n(i1_key="cont_label_groupcomponent", i1_locale=conf.LANG_EN, i1_message=u"Task Component"))        
        i18ns.append(I18n(i1_key="cont_label_groupcomponent", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作事项组件"))
        i18ns.append(I18n(i1_key="cont_label_groupversion", i1_locale=conf.LANG_EN, i1_message=u"Task Component"))        
        i18ns.append(I18n(i1_key="cont_label_groupversion", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作事项版本"))
        
        i18ns.append(I18n(i1_key="cont_status_nowork", i1_locale=conf.LANG_EN, i1_message=u"No Work", i1_type="cont_workday_code"))     
        i18ns.append(I18n(i1_key="cont_status_nowork", i1_locale=conf.LANG_ZH_CN, i1_message=u"不工作", i1_type="cont_workday_code"))
        i18ns.append(I18n(i1_key="cont_status_workallday", i1_locale=conf.LANG_EN, i1_message=u"Work one day", i1_type="cont_workday_code"))
        i18ns.append(I18n(i1_key="cont_status_workallday", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作一天", i1_type="cont_workday_code"))
        i18ns.append(I18n(i1_key="cont_status_workhalfday", i1_locale=conf.LANG_EN, i1_message=u"Work half day", i1_type="cont_workday_code"))        
        i18ns.append(I18n(i1_key="cont_status_workhalfday", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作半天", i1_type="cont_workday_code"))
        
        i18ns.append(I18n(i1_key="core_label_id", i1_locale=conf.LANG_EN, i1_message=u"Id"))        
        i18ns.append(I18n(i1_key="core_label_id", i1_locale=conf.LANG_ZH_CN, i1_message=u"Id"))
        i18ns.append(I18n(i1_key="core_label_set", i1_locale=conf.LANG_EN, i1_message=u"set"))        
        i18ns.append(I18n(i1_key="core_label_set", i1_locale=conf.LANG_ZH_CN, i1_message=u"设置"))
        i18ns.append(I18n(i1_key="core_label_refresh", i1_locale=conf.LANG_EN, i1_message=u"Refresh"))        
        i18ns.append(I18n(i1_key="core_label_refresh", i1_locale=conf.LANG_ZH_CN, i1_message=u"刷新"))
        i18ns.append(I18n(i1_key="core_label_norecords", i1_locale=conf.LANG_EN, i1_message=u"No Records."))        
        i18ns.append(I18n(i1_key="core_label_norecords", i1_locale=conf.LANG_ZH_CN, i1_message=u"没有记录。"))
        i18ns.append(I18n(i1_key="core_action_action", i1_locale=conf.LANG_EN, i1_message=u"Action"))        
        i18ns.append(I18n(i1_key="core_action_action", i1_locale=conf.LANG_ZH_CN, i1_message=u"操作"))
        i18ns.append(I18n(i1_key="user_label_creatorkey", i1_locale=conf.LANG_EN, i1_message=u"Creator"))        
        i18ns.append(I18n(i1_key="user_label_creatorkey", i1_locale=conf.LANG_ZH_CN, i1_message=u"创建人"))
        i18ns.append(I18n(i1_key="user_label_modifierkey", i1_locale=conf.LANG_EN, i1_message=u"Modifier"))        
        i18ns.append(I18n(i1_key="user_label_modifierkey", i1_locale=conf.LANG_ZH_CN, i1_message=u"修改人"))
        i18ns.append(I18n(i1_key="task_label_creatorkey", i1_locale=conf.LANG_EN, i1_message=u"Creator"))        
        i18ns.append(I18n(i1_key="task_label_creatorkey", i1_locale=conf.LANG_ZH_CN, i1_message=u"创建人"))
        i18ns.append(I18n(i1_key="task_label_modifierkey", i1_locale=conf.LANG_EN, i1_message=u"Modifier"))        
        i18ns.append(I18n(i1_key="task_label_modifierkey", i1_locale=conf.LANG_ZH_CN, i1_message=u"修改人"))
        
        i18ns.append(I18n(i1_key="core_label_type", i1_locale=conf.LANG_EN, i1_message=u"Type"))        
        i18ns.append(I18n(i1_key="core_label_type", i1_locale=conf.LANG_ZH_CN, i1_message=u"类型"))
        i18ns.append(I18n(i1_key="core_label_days", i1_locale=conf.LANG_EN, i1_message=u"Days"))        
        i18ns.append(I18n(i1_key="core_label_days", i1_locale=conf.LANG_ZH_CN, i1_message=u"天数"))
        
        i18ns.append(I18n(i1_key="rept_label_progressdeviationtip", i1_locale=conf.LANG_EN, i1_message=u"Delay Plan=Task Actual Progress < Task Plan Progress; Advance Plan= 'Task Actual Progress > Task Plan Progress';"))
        i18ns.append(I18n(i1_key="rept_label_progressdeviationtip", i1_locale=conf.LANG_ZH_CN, i1_message=u"迟于计划= '工作事项实际完成进度<工作事项计划进度'; 超出计划='工作事项实际完成进度>工作事项计划进度';"))
        
        i18ns.append(I18n(i1_key="cont_error_pendingsaveversion", i1_locale=conf.LANG_EN, i1_message=u"Version is not saved, please save first then go to another version."))
        i18ns.append(I18n(i1_key="cont_error_pendingsaveversion", i1_locale=conf.LANG_ZH_CN, i1_message=u"版本还没有保存，请先保存版本，再切换到其它版本！"))
        i18ns.append(I18n(i1_key="cont_confirm_version_delete", i1_locale=conf.LANG_EN, i1_message=u"If deleting this version, the tasks under this version will not be related to this version, do you confirm to delete this version?"))
        i18ns.append(I18n(i1_key="cont_confirm_version_delete", i1_locale=conf.LANG_ZH_CN, i1_message=u"如果删除这个版本，这个版本下的工作事项将不能和这个版本关联，你确认要删除这个版本吗？"))
        i18ns.append(I18n(i1_key="cont_error_pendingsavecomponent", i1_locale=conf.LANG_EN, i1_message=u"Comonent is not saved, please save first then go to another component."))
        i18ns.append(I18n(i1_key="cont_error_pendingsavecomponent", i1_locale=conf.LANG_ZH_CN, i1_message=u"组件还没有保存，请先保存组件，再切换到其它组件！"))
        i18ns.append(I18n(i1_key="cont_confirm_component_delete", i1_locale=conf.LANG_EN, i1_message=u"If deleting this component, the tasks under this component will not be related to this component, do you confirm to delete this component?"))
        i18ns.append(I18n(i1_key="cont_confirm_component_delete", i1_locale=conf.LANG_ZH_CN, i1_message=u"如果删除这个组件，这个组件下的工作事项将不能和这个组件关联，你确认要删除这个组件吗？"))
        i18ns.append(I18n(i1_key="cont_error_pendingsaveexception", i1_locale=conf.LANG_EN, i1_message=u"Exception is not saved, please save first then go to another exception."))
        i18ns.append(I18n(i1_key="cont_error_pendingsaveexception", i1_locale=conf.LANG_ZH_CN, i1_message=u"例外还没有保存，请先保存组件，再切换到其它例外！"))

        i18ns.append(I18n(i1_key="cont_confirm_deletegroup", i1_locale=conf.LANG_EN, i1_message=u"The components, versions and calendar under this group will be deleted also, Do you confirm to delete this contact group ?"))
        i18ns.append(I18n(i1_key="cont_confirm_deletegroup", i1_locale=conf.LANG_ZH_CN, i1_message=u"这个联系人分组下的组件，版本和日历将一起被删除，你确定要删除这个联系人分组吗？"))
        i18ns.append(I18n(i1_key="cont_confirm_exception_delete", i1_locale=conf.LANG_EN, i1_message=u"Do you confirm to delete this exception?"))
        i18ns.append(I18n(i1_key="cont_confirm_exception_delete", i1_locale=conf.LANG_ZH_CN, i1_message=u"你确认要删除这个例外吗？"))
        i18ns.append(I18n(i1_key="cont_label_leavecomment", i1_locale=conf.LANG_EN, i1_message=u"Leave Comment"))        
        i18ns.append(I18n(i1_key="cont_label_leavecomment", i1_locale=conf.LANG_ZH_CN, i1_message=u"休假备注"))
        
        i18ns.append(I18n(i1_key="cont_label_groupkey", i1_locale=conf.LANG_EN, i1_message=u"Contact Group"))
        i18ns.append(I18n(i1_key="cont_label_groupkey", i1_locale=conf.LANG_ZH_CN, i1_message=u"联系人分组"))
        i18ns.append(I18n(i1_key="cont_label_contactkey", i1_locale=conf.LANG_EN, i1_message="Contact"))
        i18ns.append(I18n(i1_key="cont_label_contactkey", i1_locale=conf.LANG_ZH_CN, i1_message=u"联系人"))
        
        i18ns.append(I18n(i1_key="cont_error_pendingsaveresource", i1_locale=conf.LANG_EN, i1_message=u"Resource is not saved, please save first then go to another resource."))
        i18ns.append(I18n(i1_key="cont_error_pendingsaveresource", i1_locale=conf.LANG_ZH_CN, i1_message=u"人员还没有保存，请先保存人员，再切换到其它人员！"))
        i18ns.append(I18n(i1_key="cont_confirm_resource_delete", i1_locale=conf.LANG_EN, i1_message=u"Do you confirm to delete this resource?"))
        i18ns.append(I18n(i1_key="cont_confirm_resource_delete", i1_locale=conf.LANG_ZH_CN, i1_message=u"你确认要删除这个人员吗？"))
        i18ns.append(I18n(i1_key="cont_confirm_contactleave_delete", i1_locale=conf.LANG_EN, i1_message=u"Do you confirm to delete this contact leave?"))
        i18ns.append(I18n(i1_key="cont_confirm_contactleave_delete", i1_locale=conf.LANG_ZH_CN, i1_message=u"你确认要删除这个联系人请假吗？"))
        
        i18ns.append(I18n(i1_key="task_error_udpateotherstaskcomment", i1_locale=conf.LANG_EN, i1_message=u"You only can edit your created comments."))
        i18ns.append(I18n(i1_key="task_error_udpateotherstaskcomment", i1_locale=conf.LANG_ZH_CN, i1_message=u"你只能编辑你自己创建的工作事项日志！"))
        i18ns.append(I18n(i1_key="task_error_deleteotherstaskcomment", i1_locale=conf.LANG_EN, i1_message=u"You only can delete your created comments."))
        i18ns.append(I18n(i1_key="task_error_deleteotherstaskcomment", i1_locale=conf.LANG_ZH_CN, i1_message=u"你只能删除你自己创建的工作事项日志！"))
        i18ns.append(I18n(i1_key="task_confirm_taskcomment_delete", i1_locale=conf.LANG_EN, i1_message=u"Do you confirm to delete this comment?"))
        i18ns.append(I18n(i1_key="task_confirm_taskcomment_delete", i1_locale=conf.LANG_ZH_CN, i1_message=u"你确认要删除这个工作事项日志吗？"))

        return i18ns
    
