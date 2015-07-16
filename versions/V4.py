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


class V4(Version):
    
    def _upgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        b = self._exist_column('cont_contact', 'ct_company_address')
        if b is False:
            sql = "ALTER TABLE cont_contact ADD ct_company_address VARCHAR(200) NULL DEFAULT NULL AFTER ct_company;"
            conn.query(sql)
        b = self._exist_column('cont_contact', 'bind_user_id')
        if b is False:
            sql = "ALTER TABLE cont_contact ADD bind_user_id INT(11) NULL DEFAULT NULL;"
            conn.query(sql)
        b = self._exist_column('cont_group', 'is_project')
        if b is False:
            sql = "ALTER TABLE cont_group ADD is_project TINYINT(1) NOT NULL DEFAULT 0 AFTER uid;"
            conn.query(sql)
        b = self._exist_column('cont_group', 'proj_startdate')
        if b is False:
            sql = "ALTER TABLE cont_group ADD proj_startdate DATE NULL DEFAULT NULL;"
            conn.query(sql)
        b = self._exist_column('cont_group', 'proj_finishdate')
        if b is False:
            sql = "ALTER TABLE cont_group ADD proj_finishdate DATE NULL DEFAULT NULL;"
            conn.query(sql)        
        b = self._exist_column('task_worksheet', 'group_id')
        if b is False:
            sql = "ALTER TABLE task_worksheet ADD group_id INT(11) NULL DEFAULT NULL;"
            conn.query(sql)
        sql = "UPDATE task_worksheet SET group_id = -1;"
        conn.query(sql)
        
        b = self._exist_column('note_notebook', 'group_id')
        if b is False:
            sql = "ALTER TABLE note_notebook ADD group_id INT(11) NULL DEFAULT NULL;"
            conn.query(sql)
        sql = "UPDATE note_notebook SET group_id = -1;"
        conn.query(sql)
        self._change_user_id_to_creator_id(conn)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'task_confirm_movetask'"
        conn.query(sql)
        sql = "DELETE FROM core_i18n WHERE i1_key = 'note_confirm_movenote'"
        conn.query(sql)
            
    def _downgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        b = self._exist_column('cont_contact', 'ct_company_address')
        if b is True:
            sql = "ALTER TABLE cont_contact DROP ct_company_address;"
            conn.query(sql)
        b = self._exist_column('cont_contact', 'bind_user_id')
        if b is True:
            sql = "ALTER TABLE cont_contact DROP bind_user_id;"
            conn.query(sql)
        b = self._exist_column('cont_group', 'is_project')
        if b is True:
            sql = "ALTER TABLE cont_group DROP is_project;"
            conn.query(sql)
        b = self._exist_column('cont_group', 'is_shared')
        if b is True:
            sql = "ALTER TABLE cont_group DROP is_shared;"
            conn.query(sql)
        b = self._exist_column('cont_group', 'proj_startdate')
        if b is True:
            sql = "ALTER TABLE cont_group DROP proj_startdate;"
            conn.query(sql)
        b = self._exist_column('cont_group', 'proj_finishdate')
        if b is True:
            sql = "ALTER TABLE cont_group DROP proj_finishdate;"
            conn.query(sql)
        
        b = self._exist_column('task_worksheet', 'group_id')
        if b is True:
            sql = "ALTER TABLE task_worksheet DROP group_id;"
            conn.query(sql)
        
        b = self._exist_column('note_notebook', 'group_id')
        if b is True:
            sql = "ALTER TABLE note_notebook DROP group_id;"
            conn.query(sql)
            
        self._change_creator_id_to_user_id(conn)
            
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
        i18ns.append(I18n(i1_key="cont_label_companyaddress", i1_locale=conf.LANG_EN, i1_message=u"Company Address"))
        i18ns.append(I18n(i1_key="cont_label_companyaddress", i1_locale=conf.LANG_ZH_CN, i1_message=u"单位地址"))
        i18ns.append(I18n(i1_key="cont_label_linkuserid", i1_locale=conf.LANG_EN, i1_message=u"Suishouguan Account"))
        i18ns.append(I18n(i1_key="cont_label_linkuserid", i1_locale=conf.LANG_ZH_CN, i1_message=u"随手管账号"))
        i18ns.append(I18n(i1_key="cont_label_isproject", i1_locale=conf.LANG_EN, i1_message=u"Is Project Group"))
        i18ns.append(I18n(i1_key="cont_label_isproject", i1_locale=conf.LANG_ZH_CN, i1_message=u"是否是项目组"))
        i18ns.append(I18n(i1_key="cont_label_projectgroup", i1_locale=conf.LANG_EN, i1_message=u"Project Group"))
        i18ns.append(I18n(i1_key="cont_label_projectgroup", i1_locale=conf.LANG_ZH_CN, i1_message=u"项目组"))
        i18ns.append(I18n(i1_key="cont_label_projecttip", i1_locale=conf.LANG_EN, i1_message=u"If set to Project Group, the notes, tasks and contacts related to this project group will be shared to the contacts of groups"))
        i18ns.append(I18n(i1_key="cont_label_projecttip", i1_locale=conf.LANG_ZH_CN, i1_message=u"如果设置成项目组，那么此项目组关联的笔记本，联系人，工作清单会被分享给项目组内的所有联系人。"))
        i18ns.append(I18n(i1_key="cont_label_projstartdate", i1_locale=conf.LANG_EN, i1_message=u"Project Start Date"))
        i18ns.append(I18n(i1_key="cont_label_projstartdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"项目开始日期"))
        i18ns.append(I18n(i1_key="cont_label_projfinishdate", i1_locale=conf.LANG_EN, i1_message=u"Project Finish Date"))
        i18ns.append(I18n(i1_key="cont_label_projfinishdate", i1_locale=conf.LANG_ZH_CN, i1_message=u"项目结束日期"))
        i18ns.append(I18n(i1_key="cont_label_sharedgroups", i1_locale=conf.LANG_EN, i1_message=u"Friends Sharing Groups"))
        i18ns.append(I18n(i1_key="cont_label_sharedgroups", i1_locale=conf.LANG_ZH_CN, i1_message=u"朋友分享的联系人分组"))
        i18ns.append(I18n(i1_key="cont_error_linkusernotfound", i1_locale=conf.LANG_EN, i1_message=u"Account {{account}} is not found."))
        i18ns.append(I18n(i1_key="cont_error_linkusernotfound", i1_locale=conf.LANG_ZH_CN, i1_message=u"账号 {{account}}不存在！"))
        i18ns.append(I18n(i1_key="cont_error_linkuserexisted", i1_locale=conf.LANG_EN, i1_message=u"Account {{account}} is already link to contact {{contactName}}，不能再链接."))
        i18ns.append(I18n(i1_key="cont_error_linkuserexisted", i1_locale=conf.LANG_ZH_CN, i1_message=u"账号 {{account}}已经链接到联系人{{contactName}}, 不能再链接！"))
        i18ns.append(I18n(i1_key="cont_error_updatesharedcontact", i1_locale=conf.LANG_EN, i1_message=u"You can't edit the contacts of friends sharing."))
        i18ns.append(I18n(i1_key="cont_error_updatesharedcontact", i1_locale=conf.LANG_ZH_CN, i1_message=u"你不能编辑朋友分享的联系人！"))
        i18ns.append(I18n(i1_key="cont_error_deletesharedcontact", i1_locale=conf.LANG_EN, i1_message=u"You can't delete the contacts of friends sharing."))
        i18ns.append(I18n(i1_key="cont_error_deletesharedcontact", i1_locale=conf.LANG_ZH_CN, i1_message=u"你不能删除朋友分享的联系人！"))
        i18ns.append(I18n(i1_key="cont_label_ownself", i1_locale=conf.LANG_EN, i1_message=u"Ownself"))
        i18ns.append(I18n(i1_key="cont_label_ownself", i1_locale=conf.LANG_ZH_CN, i1_message=u"自己"))
        i18ns.append(I18n(i1_key="task_label_project", i1_locale=conf.LANG_EN, i1_message=u"Project Group"))
        i18ns.append(I18n(i1_key="task_label_project", i1_locale=conf.LANG_ZH_CN, i1_message=u"项目组"))
        i18ns.append(I18n(i1_key="task_label_sharedgroups", i1_locale=conf.LANG_EN, i1_message=u"Friends Sharing Worksheet"))
        i18ns.append(I18n(i1_key="task_label_sharedgroups", i1_locale=conf.LANG_ZH_CN, i1_message=u"朋友分享的工作清单"))
        i18ns.append(I18n(i1_key="task_error_deletesharedtask", i1_locale=conf.LANG_EN, i1_message=u"You can't delete the tasks of friends sharing."))
        i18ns.append(I18n(i1_key="task_error_deletesharedtask", i1_locale=conf.LANG_ZH_CN, i1_message=u"你不能删除朋友分享的工作事项！"))
        i18ns.append(I18n(i1_key="task_error_movesharedtask", i1_locale=conf.LANG_EN, i1_message=u"You can't move the tasks of friends sharing to others' worksheets."))
        i18ns.append(I18n(i1_key="task_error_movesharedtask", i1_locale=conf.LANG_ZH_CN, i1_message=u"你不能移动朋友分享的工作事项到其它的工作清单中！"))
        i18ns.append(I18n(i1_key="core_label_yes", i1_locale=conf.LANG_EN, i1_message=u"Yes"))
        i18ns.append(I18n(i1_key="core_label_yes", i1_locale=conf.LANG_ZH_CN, i1_message=u"是"))
        i18ns.append(I18n(i1_key="core_label_no", i1_locale=conf.LANG_EN, i1_message=u"No"))
        i18ns.append(I18n(i1_key="core_label_no", i1_locale=conf.LANG_ZH_CN, i1_message=u"否"))
        i18ns.append(I18n(i1_key="core_label_share", i1_locale=conf.LANG_EN, i1_message=u"Share"))
        i18ns.append(I18n(i1_key="core_label_share", i1_locale=conf.LANG_ZH_CN, i1_message=u"分享"))
        i18ns.append(I18n(i1_key="core_label_notselected", i1_locale=conf.LANG_EN, i1_message=u"Not selected"))
        i18ns.append(I18n(i1_key="core_label_notselected", i1_locale=conf.LANG_ZH_CN, i1_message=u"没有选择"))
        i18ns.append(I18n(i1_key="note_label_project", i1_locale=conf.LANG_EN, i1_message=u"Project Group"))
        i18ns.append(I18n(i1_key="note_label_project", i1_locale=conf.LANG_ZH_CN, i1_message=u"项目组"))
        i18ns.append(I18n(i1_key="note_label_sharednotebooks", i1_locale=conf.LANG_EN, i1_message=u"Friends Sharing Notebooks"))
        i18ns.append(I18n(i1_key="note_label_sharednotebooks", i1_locale=conf.LANG_ZH_CN, i1_message=u"朋友分享的笔记本"))
        i18ns.append(I18n(i1_key="note_error_deletesharednote", i1_locale=conf.LANG_EN, i1_message=u"You can't delete the notes of friends sharing."))
        i18ns.append(I18n(i1_key="note_error_deletesharednote", i1_locale=conf.LANG_ZH_CN, i1_message=u"你不能删除朋友分享的笔记！"))
        i18ns.append(I18n(i1_key="note_error_movesharednote", i1_locale=conf.LANG_EN, i1_message=u"You can't move the notes of friends sharing to others' notebooks."))
        i18ns.append(I18n(i1_key="note_error_movesharednote", i1_locale=conf.LANG_ZH_CN, i1_message=u"你不能移动朋友分享的笔记到其它的笔记本中！"))
        i18ns.append(I18n(i1_key="core_error_updateexpireddata", i1_locale=conf.LANG_EN, i1_message=u"The local data is expired, please refresh data or UI after reloading latest data from server."))
        i18ns.append(I18n(i1_key="core_error_updateexpireddata", i1_locale=conf.LANG_ZH_CN, i1_message=u"本地数据已经过期，请刷新数据或界面后再编辑提交."))
    
        return i18ns
    
    def _change_user_id_to_creator_id(self, conn):
        
        table_names1 = ['cont_contact', 'cont_group', 'core_filex', 'core_tag', 'note_note', 'note_notebook', 'task_task', 'task_taskcomment', 'task_worksheet']
        
        for tn in table_names1:
            b = self._exist_column(tn, 'user_id')
            if b is True:
                sql = "ALTER TABLE %s CHANGE user_id creator_id INT(11);" % tn
                conn.query(sql)
                
        table_names2 = ['cont_contactgroup', 'core_migration', 'core_operation', 'core_operation', 'core_role', 'core_roleoperation', 'core_sysprop', 'core_tagmodel', 'core_user', 'core_userprop', 'core_userrole', 'core_i18n']
        for tn in table_names2:
            b = self._exist_column(tn, 'creator_id')
            if b is False:
                sql = "ALTER TABLE %s ADD creator_id INT(11);" % tn
                conn.query(sql)
            sql = "UPDATE %s SET creator_id = modifier_id;" % tn
            
        
        table_names1.extend(table_names2)
        for tn in table_names1:
            b = self._exist_column(tn, 'row_version')
            if b is False:
                sql = "ALTER TABLE %s ADD row_version INT(11);" % tn
                conn.query(sql)
            sql = "UPDATE %s set row_version = 1;" % tn
            conn.query(sql)
                
    def _change_creator_id_to_user_id(self, conn):
        
        table_names1 = ['cont_contact', 'cont_group', 'core_filex', 'core_tag', 'note_note', 'note_notebook', 'task_task', 'task_taskcomment', 'task_worksheet']
        
        for tn in table_names1:
            b = self._exist_column(tn, 'creator_id')
            if b is True:
                sql = "ALTER TABLE %s CHANGE creator_id user_id INT(11);" % tn
                conn.query(sql)
        
        table_names2 = ['cont_contactgroup', 'core_migration', 'core_operation', 'core_operation', 'core_role', 'core_roleoperation', 'core_sysprop', 'core_tagmodel', 'core_user', 'core_userprop', 'core_userrole', 'core_i18n']
        for tn in table_names2:
            b = self._exist_column(tn, 'creator_id')
            if b is True:
                sql = "ALTER TABLE %s DROP creator_id;" % tn
                conn.query(sql)
                
        table_names1.extend(table_names2)
        for tn in table_names1:
            b = self._exist_column(tn, 'row_version')
            if b is True:
                sql = "ALTER TABLE %s DROP row_version;" % tn
                conn.query(sql)
"""
run below SQLs in MySQL Client before running migration over UI if upgrading V3 to V4

ALTER TABLE core_operation ADD creator_id INT(11);
ALTER TABLE core_operation ADD row_version INT(11);
UPDATE core_operation SET row_version = 1;
UPDATE core_operation SET creator_id = modifier_id;
ALTER TABLE core_user ADD creator_id INT(11);
ALTER TABLE core_user ADD row_version INT(11);
UPDATE core_user SET row_version = 1;
UPDATE core_user SET creator_id = modifier_id;
ALTER TABLE core_userprop ADD creator_id INT(11);
ALTER TABLE core_userprop ADD row_version INT(11);
UPDATE core_userprop SET row_version = 1;
UPDATE core_userprop SET creator_id = modifier_id;

ALTER TABLE core_migration ADD creator_id INT(11);
ALTER TABLE core_migration ADD row_version INT(11);
UPDATE core_migration SET row_version = 1;
UPDATE core_migration SET creator_id = modifier_id;

ALTER TABLE core_i18n ADD creator_id INT(11);
ALTER TABLE core_i18n ADD row_version INT(11);
UPDATE core_i18n SET row_version = 1;
UPDATE core_i18n SET creator_id = modifier_id;

"""