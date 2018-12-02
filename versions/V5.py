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
from contact.contactmodel import ContactLeave
from core import user
from core.db import dbutil
from core.migration import Version
from core.model import I18n, Operation, RoleOperation
from report.reporthandler import      RptProgressChartHandler, ReportBaseDataHandler, \
    RptAllocationChartHandler


class V5(Version):
    
    def _upgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        b = self._exist_column('task_task', 'actual_startdate')
        if b is False:
            sql = "ALTER TABLE task_task ADD actual_startdate DATE;"
            conn.query(sql)
        b = self._exist_column('task_task', 'actual_finishdate')
        if b is False:
            sql = "ALTER TABLE task_task ADD actual_finishdate DATE;"
            conn.query(sql)
        
        sql = "UPDATE task_task SET actual_startdate = due_startdate WHERE t_status_code != 'task_code_open';"
        conn.query(sql)
        sql = "UPDATE task_task SET actual_finishdate = modified_time WHERE t_status_code = 'task_code_closed';"
        conn.query(sql)
        
        sql = "DELETE FROM core_i18n WHERE i1_key = 'task_label_duestarttime'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'task_label_duefinishtime'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'cont_label_isproject'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'cont_label_projectgroup'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'cont_label_projecttip'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'task_label_project'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'cont_label_projstartdate'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'cont_label_projfinishdate'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'task_code_meeting'"
        conn.query(sql)
        
        b = self._exist_column('task_task', 't_type_code')
        if b is False:
            sql = "ALTER TABLE task_task ADD t_type_code VARCHAR(20) NULL;"
            conn.query(sql)
        sql = "UPDATE task_task SET t_type_code = 'task_code_task';"
        conn.query(sql)
        
        b = self._exist_column("cont_group", "is_project", conn)
        if b is True:
            if not self._exist_column("cont_group", "is_shared", conn):
                sql = "ALTER TABLE cont_group CHANGE is_project is_shared TINYINT(1)"
                conn.query(sql)
            else:
                sql = "ALTER TABLE cont_group DROP is_project"
                conn.query(sql)
            
        b = self._exist_column('cont_group', 'proj_startdate')
        if b is True:
            if not self._exist_column('cont_group', 'group_startdate'):
                sql = "ALTER TABLE cont_group CHANGE proj_startdate group_startdate DATE NULL DEFAULT NULL;"
                conn.query(sql)
            else:
                sql = "ALTER TABLE cont_group DROP proj_startdate"
                conn.query(sql)
                
        b = self._exist_column('cont_group', 'proj_finishdate')
        if b is True:
            if not self._exist_column('cont_group', 'group_finishdate'):
                sql = "ALTER TABLE cont_group CHANGE proj_finishdate group_finishdate DATE NULL DEFAULT NULL;"
                conn.query(sql)
            else:
                sql = "ALTER TABLE cont_group DROP proj_finishdate"
                conn.query(sql)
            
    def _downgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        b = self._exist_column('task_task', 'actual_startdate')
        if b is True:
            sql = "ALTER TABLE task_task DROP actual_startdate;"
            conn.query(sql)
        b = self._exist_column('task_task', 'actual_finishdate')
        if b is True:
            sql = "ALTER TABLE task_task DROP actual_finishdate;"
            conn.query(sql)
        b = self._exist_column('task_task', 't_type_code')
        if b is True:
            sql = "ALTER TABLE task_task DROP t_type_code;"
            conn.query(sql)
        
        b = self._exist_column("cont_group", "is_shared", conn)
        if b is True:
            sql = "ALTER TABLE cont_group CHANGE is_shared is_project TINYINT(1)"
            conn.query(sql)
            
        b = self._exist_column('cont_group', 'group_startdate')
        if b is True:
            sql = "ALTER TABLE cont_group CHANGE group_startdate proj_startdate DATE NULL DEFAULT NULL;"
            conn.query(sql)
        b = self._exist_column('cont_group', 'group_finishdate')
        if b is True:
            sql = "ALTER TABLE cont_group CHANGE group_finishdate proj_finishdate DATE NULL DEFAULT NULL;"
            conn.query(sql)
            
    def _get_roles(self):
        return []
    
    def _get_operations(self):
        operations = []
        operations.append(Operation(operation_key="REPORT_TASK", handler_classes=RptAllocationChartHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="REPORT_TASK", handler_classes=ReportBaseDataHandler.get_qualified_name(), resource_oql=None))
        operations.append(Operation(operation_key="REPORT_TASK", handler_classes=RptProgressChartHandler.get_qualified_name(), resource_oql=None))
        return operations
    
    def _get_roleoperations(self):
        roleoperations = []
        ordinary_role = user.get_role(role_name="Ordinary User")
        roleoperations.append(RoleOperation(role_id=ordinary_role.uid, operation_key="REPORT_TASK"))
        return roleoperations
    
    def _get_i18ns(self):
        i18ns = []
        i18ns.append(I18n(i1_key="task_label_duestartdate", i1_locale=conf.LANG_EN, i1_message=u"Plan Start Date"))
        i18ns.append(I18n(i1_key="task_label_duestartdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"计划开始日期"))
        i18ns.append(I18n(i1_key="task_label_duefinishdate", i1_locale=conf.LANG_EN, i1_message=u"Plan Finish Date"))
        i18ns.append(I18n(i1_key="task_label_duefinishdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"计划完成日期"))
        i18ns.append(I18n(i1_key="task_label_shortduestartdate", i1_locale=conf.LANG_EN, i1_message=u"Plan Start"))
        i18ns.append(I18n(i1_key="task_label_shortduestartdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"计划开始"))
        i18ns.append(I18n(i1_key="task_label_shortduefinishdate", i1_locale=conf.LANG_EN, i1_message=u"Plan Finish"))
        i18ns.append(I18n(i1_key="task_label_shortduefinishdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"计划完成"))
        
        i18ns.append(I18n(i1_key="task_label_actualstartdate", i1_locale=conf.LANG_EN, i1_message=u"Actual Start Date"))
        i18ns.append(I18n(i1_key="task_label_actualstartdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"实际开始日期"))
        i18ns.append(I18n(i1_key="task_label_actualfinishdate", i1_locale=conf.LANG_EN, i1_message=u"Actual Finish Date"))
        i18ns.append(I18n(i1_key="task_label_actualfinishdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"实际完成日期"))
        i18ns.append(I18n(i1_key="task_label_shortactualstartdate", i1_locale=conf.LANG_EN, i1_message=u"Actual Start"))
        i18ns.append(I18n(i1_key="task_label_shortactualstartdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"实际开始"))
        i18ns.append(I18n(i1_key="task_label_shortactualfinishdate", i1_locale=conf.LANG_EN, i1_message=u"Actual Finish"))
        i18ns.append(I18n(i1_key="task_label_shortactualfinishdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"实际完成"))
        
        i18ns.append(I18n(i1_key="task_label_assignedtometasks", i1_locale=conf.LANG_EN, i1_message=u"Assigned to me"))
        i18ns.append(I18n(i1_key="task_label_assignedtometasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"分配给我的工作"))
        
        i18ns.append(I18n(i1_key="rept_label_report", i1_locale=conf.LANG_EN, i1_message=u"Charts"))
        i18ns.append(I18n(i1_key="rept_label_report", i1_locale=conf.LANG_ZH_CN, i1_message=u"图表"))
        i18ns.append(I18n(i1_key="rept_label_progressreport", i1_locale=conf.LANG_EN, i1_message=u"Progress Charts"))
        i18ns.append(I18n(i1_key="rept_label_progressreport", i1_locale=conf.LANG_ZH_CN, i1_message=u"进度图表"))
        
        i18ns.append(I18n(i1_key="rept_label_searchcriteria", i1_locale=conf.LANG_EN, i1_message=u"Search Criteria"))
        i18ns.append(I18n(i1_key="rept_label_searchcriteria", i1_locale=conf.LANG_ZH_CN, i1_message=u"查询条件"))
        i18ns.append(I18n(i1_key="rept_label_startdate", i1_locale=conf.LANG_EN, i1_message=u"Start Date"))
        i18ns.append(I18n(i1_key="rept_label_startdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"开始日期"))
        i18ns.append(I18n(i1_key="rept_label_enddate", i1_locale=conf.LANG_EN, i1_message=u"End Date"))
        i18ns.append(I18n(i1_key="rept_label_enddate", i1_locale=conf.LANG_ZH_CN, i1_message=u"结束日期"))
        
        i18ns.append(I18n(i1_key="rept_label_planfinishquantity", i1_locale=conf.LANG_EN, i1_message=u"Planned Numbers"))
        i18ns.append(I18n(i1_key="rept_label_planfinishquantity", i1_locale=conf.LANG_ZH_CN, i1_message=u"计划完成个数"))
        i18ns.append(I18n(i1_key="rept_label_actualfinishquantity", i1_locale=conf.LANG_EN, i1_message=u"Actual Numbers"))
        i18ns.append(I18n(i1_key="rept_label_actualfinishquantity", i1_locale=conf.LANG_ZH_CN, i1_message=u"实际完成个数"))
        i18ns.append(I18n(i1_key="rept_label_forecastfinishquantity", i1_locale=conf.LANG_EN, i1_message=u"Forecast Numbers"))
        i18ns.append(I18n(i1_key="rept_label_forecastfinishquantity", i1_locale=conf.LANG_ZH_CN, i1_message=u"预测完成个数"))
        i18ns.append(I18n(i1_key="rept_label_cancelquantity", i1_locale=conf.LANG_EN, i1_message=u"Cancel Numbers"))
        i18ns.append(I18n(i1_key="rept_label_cancelquantity", i1_locale=conf.LANG_ZH_CN, i1_message=u"取消个数"))
        
        i18ns.append(I18n(i1_key="rept_label_deviationstatus", i1_locale=conf.LANG_EN, i1_message=u"Deviation Status"))
        i18ns.append(I18n(i1_key="rept_label_deviationstatus", i1_locale=conf.LANG_ZH_CN, i1_message=u"偏差状态"))
        i18ns.append(I18n(i1_key="rept_label_deviationdelay", i1_locale=conf.LANG_EN, i1_message=u"Delay"))
        i18ns.append(I18n(i1_key="rept_label_deviationdelay", i1_locale=conf.LANG_ZH_CN, i1_message=u"迟于计划"))
        i18ns.append(I18n(i1_key="rept_label_deviationadvance", i1_locale=conf.LANG_EN, i1_message=u"Advance"))
        i18ns.append(I18n(i1_key="rept_label_deviationadvance", i1_locale=conf.LANG_ZH_CN, i1_message=u"超出计划"))
        
        i18ns.append(I18n(i1_key="rept_label_plandays", i1_locale=conf.LANG_EN, i1_message=u"Planning Days"))
        i18ns.append(I18n(i1_key="rept_label_plandays", i1_locale=conf.LANG_ZH_CN, i1_message=u"计划天数"))
        i18ns.append(I18n(i1_key="rept_label_remainingdays", i1_locale=conf.LANG_EN, i1_message=u"Remaining Days"))
        i18ns.append(I18n(i1_key="rept_label_remainingdays", i1_locale=conf.LANG_ZH_CN, i1_message=u"剩余天数"))
        i18ns.append(I18n(i1_key="rept_label_numberofdays", i1_locale=conf.LANG_EN, i1_message=u"Number of Days"))
        i18ns.append(I18n(i1_key="rept_label_numberofdays", i1_locale=conf.LANG_ZH_CN, i1_message=u"天数"))
        i18ns.append(I18n(i1_key="rept_label_days", i1_locale=conf.LANG_EN, i1_message=u"Days"))
        i18ns.append(I18n(i1_key="rept_label_days", i1_locale=conf.LANG_ZH_CN, i1_message=u"日"))
        
        i18ns.append(I18n(i1_key="rept_label_progressdeviationdetails", i1_locale=conf.LANG_EN, i1_message=u"Deviation Details"))
        i18ns.append(I18n(i1_key="rept_label_progressdeviationdetails", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作偏差明细"))
        
        i18ns.append(I18n(i1_key="rept_label_days", i1_locale=conf.LANG_EN, i1_message=u"Days"))
        i18ns.append(I18n(i1_key="rept_label_days", i1_locale=conf.LANG_ZH_CN, i1_message=u"日"))
        
        i18ns.append(I18n(i1_key="core_label_testingaccpwd", i1_locale=conf.LANG_EN, i1_message=u"Testing Account/Password"))
        i18ns.append(I18n(i1_key="core_label_testingaccpwd", i1_locale=conf.LANG_ZH_CN, i1_message=u"测试账号/密码"))
        
        i18ns.append(I18n(i1_key="task_label_lastcomment", i1_locale=conf.LANG_EN, i1_message=u"Last Comment"))
        i18ns.append(I18n(i1_key="task_label_lastcomment", i1_locale=conf.LANG_ZH_CN, i1_message=u"最后一条工作日志"))
        
        i18ns.append(I18n(i1_key="rept_label_generate", i1_locale=conf.LANG_EN, i1_message=u"Generate"))
        i18ns.append(I18n(i1_key="rept_label_generate", i1_locale=conf.LANG_ZH_CN, i1_message=u"生成"))
        
        i18ns.append(I18n(i1_key="task_code_task", i1_locale=conf.LANG_EN, i1_message=u"Task", i1_type="task_type_code"))
        i18ns.append(I18n(i1_key="task_code_task", i1_locale=conf.LANG_ZH_CN, i1_message=u"任务", i1_type="task_type_code"))
        i18ns.append(I18n(i1_key="task_code_bug", i1_locale=conf.LANG_EN, i1_message=u"Bug", i1_type="task_type_code"))
        i18ns.append(I18n(i1_key="task_code_bug", i1_locale=conf.LANG_ZH_CN, i1_message=u"缺陷", i1_type="task_type_code"))
        i18ns.append(I18n(i1_key="task_code_risk", i1_locale=conf.LANG_EN, i1_message=u"Risk", i1_type="task_type_code"))
        i18ns.append(I18n(i1_key="task_code_risk", i1_locale=conf.LANG_ZH_CN, i1_message=u"风险", i1_type="task_type_code"))
        i18ns.append(I18n(i1_key="task_code_issue", i1_locale=conf.LANG_EN, i1_message=u"Issue", i1_type="task_type_code"))
        i18ns.append(I18n(i1_key="task_code_issue", i1_locale=conf.LANG_ZH_CN, i1_message=u"问题", i1_type="task_type_code"))
        
        i18ns.append(I18n(i1_key="task_label_tasktypecode", i1_locale=conf.LANG_EN, i1_message=u"Task Type"))        
        i18ns.append(I18n(i1_key="task_label_tasktypecode", i1_locale=conf.LANG_ZH_CN, i1_message=u"分类"))
        
        i18ns.append(I18n(i1_key="cont_label_leavestartdate", i1_locale=conf.LANG_EN, i1_message=u"Start Date"))        
        i18ns.append(I18n(i1_key="cont_label_leavestartdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"开始日期"))
        i18ns.append(I18n(i1_key="cont_label_leaveenddate", i1_locale=conf.LANG_EN, i1_message=u"End Date"))        
        i18ns.append(I18n(i1_key="cont_label_leaveenddate", i1_locale=conf.LANG_ZH_CN, i1_message=u"结束日期"))
        i18ns.append(I18n(i1_key="cont_label_leavedays", i1_locale=conf.LANG_EN, i1_message=u"Vacation Days"))        
        i18ns.append(I18n(i1_key="cont_label_leavedays", i1_locale=conf.LANG_ZH_CN, i1_message=u"请假天数"))
        i18ns.append(I18n(i1_key="cont_label_leavetype", i1_locale=conf.LANG_EN, i1_message=u"Vacation Type"))        
        i18ns.append(I18n(i1_key="cont_label_leavetype", i1_locale=conf.LANG_ZH_CN, i1_message=u"假期类型"))
        i18ns.append(I18n(i1_key="cont_label_leavecomment", i1_locale=conf.LANG_EN, i1_message=u"Leave Comment"))        
        i18ns.append(I18n(i1_key="cont_label_leavecomment", i1_locale=conf.LANG_ZH_CN, i1_message=u"请假备注"))
        
        i18ns.append(I18n(i1_key="cont_code_annualleave", i1_locale=conf.LANG_EN, i1_message=u"Annual Leave", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_annualleave", i1_locale=conf.LANG_ZH_CN, i1_message=u"年假", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_personalleave", i1_locale=conf.LANG_EN, i1_message=u"Personal Leave", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_personalleave", i1_locale=conf.LANG_ZH_CN, i1_message=u"事假", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_sickleave", i1_locale=conf.LANG_EN, i1_message=u"Sick Leave", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_sickleave", i1_locale=conf.LANG_ZH_CN, i1_message=u"病假", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_marriageleave", i1_locale=conf.LANG_EN, i1_message=u"Marriage Leave", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_marriageleave", i1_locale=conf.LANG_ZH_CN, i1_message=u"婚假", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_maternityleave", i1_locale=conf.LANG_EN, i1_message=u"Maternity Leave", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_maternityleave", i1_locale=conf.LANG_ZH_CN, i1_message=u"产假", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_paternityleave", i1_locale=conf.LANG_EN, i1_message=u"Paternity Leave", i1_type="cont_leavetype_code"))
        i18ns.append(I18n(i1_key="cont_code_paternityleave", i1_locale=conf.LANG_ZH_CN, i1_message=u"陪产假", i1_type="cont_leavetype_code"))
        
        i18ns.append(I18n(i1_key="rept_label_peoplereport", i1_locale=conf.LANG_EN, i1_message=u"People Charts"))
        i18ns.append(I18n(i1_key="rept_label_peoplereport", i1_locale=conf.LANG_ZH_CN, i1_message=u"人员图表"))
        
        i18ns.append(I18n(i1_key="core_label_more", i1_locale=conf.LANG_EN, i1_message=u"More"))
        i18ns.append(I18n(i1_key="core_label_more", i1_locale=conf.LANG_ZH_CN, i1_message=u"更多"))
        i18ns.append(I18n(i1_key="rept_label_report", i1_locale=conf.LANG_EN, i1_message=u"Report"))
        i18ns.append(I18n(i1_key="rept_label_report", i1_locale=conf.LANG_ZH_CN, i1_message=u"图表"))
        
        i18ns.append(I18n(i1_key="cont_label_isshared", i1_locale=conf.LANG_EN, i1_message=u"Is Shared"))
        i18ns.append(I18n(i1_key="cont_label_isshared", i1_locale=conf.LANG_ZH_CN, i1_message=u"是否分享"))
        i18ns.append(I18n(i1_key="cont_label_sharetip", i1_locale=conf.LANG_EN, i1_message=u"If Yes, the notes, tasks and contacts related to this group will be shared to the contacts belonging to this group"))
        i18ns.append(I18n(i1_key="cont_label_sharetip", i1_locale=conf.LANG_ZH_CN, i1_message=u"如果选择‘是’，那么此分组关联的笔记本，联系人，工作清单会被分享给该组内的所有联系人。"))
        
        i18ns.append(I18n(i1_key="rept_label_progresschart", i1_locale=conf.LANG_EN, i1_message=u"Progress Chart"))
        i18ns.append(I18n(i1_key="rept_label_progresschart", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作进度图表"))
        i18ns.append(I18n(i1_key="rept_label_progressline", i1_locale=conf.LANG_EN, i1_message=u"Progress Line"))
        i18ns.append(I18n(i1_key="rept_label_progressline", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作进度曲线"))
        i18ns.append(I18n(i1_key="rept_label_allocationchart", i1_locale=conf.LANG_EN, i1_message=u"Allocation Chart"))
        i18ns.append(I18n(i1_key="rept_label_allocationchart", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作分配图表"))
        i18ns.append(I18n(i1_key="rept_label_allocationline", i1_locale=conf.LANG_EN, i1_message=u"Allocation Line"))
        i18ns.append(I18n(i1_key="rept_label_allocationline", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作分配曲线"))
        
        i18ns.append(I18n(i1_key="rept_label_progressoverrall", i1_locale=conf.LANG_EN, i1_message=u"Progress Overall"))
        i18ns.append(I18n(i1_key="rept_label_progressoverrall", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作进度总体情况"))
        i18ns.append(I18n(i1_key="rept_label_progressoverralltip", i1_locale=conf.LANG_EN, i1_message=u"Plan Finish Count=Task Plan Finish Date <= End Date and Task Status != Cancel; Actual Finish Count = Task Status = Closed; Task Cancel Count= Task Status=Cancel"))
        i18ns.append(I18n(i1_key="rept_label_progressoverralltip", i1_locale=conf.LANG_ZH_CN, i1_message=u"计划完成个数 = '工作事项计划完成日期<=统计结束日期'并且 '工作事项状态!= 取消'; 实际完成个数='工作事项状态= 已完成'; 取消个数='工作事项状态= 取消'; "))
        i18ns.append(I18n(i1_key="rept_label_progresslinetip", i1_locale=conf.LANG_EN, i1_message=u"Plan Finish Count=Task Plan Finish Date <= End Date and Task Status != Cancel; Actual Finish Count = 'Task Status = Closed' and 'Task Actual Finish Date <= End Date'; Forecast Finish Count= 'Actual Finish Task Count from start date to today / workdays from start date to today * workdays;"))
        i18ns.append(I18n(i1_key="rept_label_progresslinetip", i1_locale=conf.LANG_ZH_CN, i1_message=u"计划完成个数= '工作事项计划完成日期<=统计结束日期'并且 '工作事项状态!= 取消'; 实际完成个数='工作事项状态= 已完成' 并且 '工作事项实际结束日期<=统计结束日期'; 预测完成个数='统计开始日期到今天内实际完成个数[实际开始日期>=统计开始日期 并且 实际结束日期<=今天 并且 工作事项状态=已完成]/统计开始日期到今天内的工作天数*天数'; "))
        i18ns.append(I18n(i1_key="rept_label_progressdeviationtip", i1_locale=conf.LANG_EN, i1_message=u"Delay Plan=Task Actual Progress < Task Plan Progress; Advance Plan= 'Task Actual Progress > Task Plan Progress';"))
        i18ns.append(I18n(i1_key="rept_label_progressdeviationtip", i1_locale=conf.LANG_ZH_CN, i1_message=u"迟于计划= '工作事项实际完成进度<工作事项计划进度'; 超出计划='工作事项实际完成进度>工作事项计划进度';"))

        i18ns.append(I18n(i1_key="rept_label_allocationoverrall", i1_locale=conf.LANG_EN, i1_message=u"Allocation Overall"))
        i18ns.append(I18n(i1_key="rept_label_allocationoverrall", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作分配总体情况"))
        i18ns.append(I18n(i1_key="rept_label_allocationoverralltip", i1_locale=conf.LANG_EN, i1_message=u"Status Count=Task Plan Finish Date <= End Date and Task Plan Start Date >= Start Date and Task Status= Separate Status"))
        i18ns.append(I18n(i1_key="rept_label_allocationoverralltip", i1_locale=conf.LANG_ZH_CN, i1_message=u"各个状态个数 = '工作事项计划开始日期>=统计开始日期'并且'工作事项计划完成日期<=统计结束日期'并且 '工作事项状态!= 各个状态'; "))
        i18ns.append(I18n(i1_key="rept_label_allocationlinetip", i1_locale=conf.LANG_EN, i1_message=u"Daily Allocation Count=Task Plan Finish Date <= End Date and Task Plan Start Date >= Start Date;"))
        i18ns.append(I18n(i1_key="rept_label_allocationlinetip", i1_locale=conf.LANG_ZH_CN, i1_message=u"每天分配个数= '工作事项计划开始日期>=统计开始日期'并且'工作事项计划完成日期<=统计结束日期'; "))
        i18ns.append(I18n(i1_key="rept_label_allocationdetailstaskcounttip", i1_locale=conf.LANG_EN, i1_message=u"TaskCount= Task Plan Finish Date <= End Date and Task Plan Start Date >= Start Date"))
        i18ns.append(I18n(i1_key="rept_label_allocationdetailstaskcounttip", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作事项个数= '工作事项计划开始日期>=统计开始日期'并且'工作事项计划完成日期<=统计结束日期';"))
        
        i18ns.append(I18n(i1_key="rept_label_quantity", i1_locale=conf.LANG_EN, i1_message=u"Count"))
        i18ns.append(I18n(i1_key="rept_label_quantity", i1_locale=conf.LANG_ZH_CN, i1_message=u"个数"))
        i18ns.append(I18n(i1_key="rept_label_busyperiod", i1_locale=conf.LANG_EN, i1_message=u"Busy Period"))
        i18ns.append(I18n(i1_key="rept_label_busyperiod", i1_locale=conf.LANG_ZH_CN, i1_message=u"繁忙区间段/天数"))
        i18ns.append(I18n(i1_key="rept_label_idleperiod", i1_locale=conf.LANG_EN, i1_message=u"Idle Period"))
        i18ns.append(I18n(i1_key="rept_label_idleperiod", i1_locale=conf.LANG_ZH_CN, i1_message=u"空闲区间段/天数"))
        i18ns.append(I18n(i1_key="rept_label_allocationdetails", i1_locale=conf.LANG_EN, i1_message=u"Allocation Details"))
        i18ns.append(I18n(i1_key="rept_label_allocationdetails", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作分配明细"))
        i18ns.append(I18n(i1_key="rept_label_taskquantity", i1_locale=conf.LANG_EN, i1_message=u"Task(Count)"))
        i18ns.append(I18n(i1_key="rept_label_taskquantity", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作事项(个数)"))
        i18ns.append(I18n(i1_key="rept_label_efforts", i1_locale=conf.LANG_EN, i1_message=u"Task/Work/Idle(days)"))
        i18ns.append(I18n(i1_key="rept_label_efforts", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作量/工作日/空闲日(天数)"))
        i18ns.append(I18n(i1_key="rept_label_assignee", i1_locale=conf.LANG_EN, i1_message=u"Assignee"))
        i18ns.append(I18n(i1_key="rept_label_assignee", i1_locale=conf.LANG_ZH_CN, i1_message=u"责任人"))
        i18ns.append(I18n(i1_key="rept_label_sum", i1_locale=conf.LANG_EN, i1_message=u"Sum"))
        i18ns.append(I18n(i1_key="rept_label_sum", i1_locale=conf.LANG_ZH_CN, i1_message=u"合计"))
        i18ns.append(I18n(i1_key="rept_label_busyperiodtip", i1_locale=conf.LANG_EN, i1_message=u"Busy Period = Task Count >= 2 in a day"))
        i18ns.append(I18n(i1_key="rept_label_busyperiodtip", i1_locale=conf.LANG_ZH_CN, i1_message=u"繁忙时间段指一天有两个及以上任务的时间段"))
        
        return i18ns
    
