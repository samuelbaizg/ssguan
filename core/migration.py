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
from datetime import datetime
import traceback
import user

import conf
from core import model
from core import strutil, cache
from core.error import CoreError
from core.model import Filex, TagModel
from db import dbutil
import i18n
import log
from model import I18n
from model import Log, Tag
from model import MCLog, MCLogDetail
from model import Migration, SysProp
from model import Uid
from model import User, UserProp, Role, Operation, RoleOperation, UserRole
import versions


# Setup the core database when the app starts first time
def setup_db():
    if not dbutil.has_db(dbutil.get_master_dbinfo()):
        try:
            dbutil.create_db(dbutil.get_master_dbinfo())
        except:
            #dbutil.drop_db(dbutil.get_master_dbinfo())
            raise
    from core.model import Session
    try:
        Session.create_table()
    except:
        Session.delete_table()

# Setup core tables
def setup_core_tables():
    conn = dbutil.get_dbconn()
    sql = "SHOW TABLES LIKE '%s'" % 'core_sysprop'    
    result = conn.query(sql)
    sql = "SHOW TABLES LIKE '%s'" % 'core_uid'
    result2 = conn.query(sql)
    if len(result) == 0 and len(result2) == 0:
        try:
            SysProp.create_table()
            Log.create_table()
            Uid.create_table()
            Migration.create_table()
            I18n.create_table()
            MCLog.create_table()
            MCLogDetail.create_table()
            User.create_table()
            Role.create_table()
            Operation.create_table()
            RoleOperation.create_table()
            UserRole.create_table()
            UserProp.create_table()
            Filex.create_table()
            Tag.create_table()
            TagModel.create_table()
            
            for i1 in __get_default_i18ns():
                i18n.create_i18n(i1.i1_key, i1.i1_message, i1.i1_locale, i1.i1_type, model.SYSTEM_UID)
            
            initialize_userandacs(model.SYSTEM_UID)
        except:
            traceback.print_exc()
            SysProp.delete_table()
            Log.delete_table()
            Migration.delete_table()
            I18n.delete_table()
            MCLog.delete_table()
            MCLogDetail.delete_table()
            
            User.delete_table()
            Role.delete_table()
            Operation.delete_table()
            RoleOperation.delete_table()
            UserRole.delete_table()
            UserProp.delete_table()
            Filex.delete_table()
            Tag.delete_table()
            TagModel.delete_table()
            Uid.delete_table()
            
def __get_default_i18ns():
    i18ns = []
    i18ns.append(I18n(i1_key="core_error_core", i1_locale=conf.LANG_EN, i1_message=u"System error. please contact help desk."))
    i18ns.append(I18n(i1_key="core_error_core", i1_locale=conf.LANG_ZH_CN, i1_message=u"系统发生错误。"))
    i18ns.append(I18n(i1_key="core_error_illegalword", i1_locale=conf.LANG_EN, i1_message=u"{{label}} includes the illegal word {{illegalword}}"))
    i18ns.append(I18n(i1_key="core_error_illegalword", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}} 包含非法字符 {{illegalword}}。"))
    
    i18ns.append(I18n(i1_key="core_error_unique", i1_locale=conf.LANG_EN, i1_message=u"The value {{value}} of {{label}} has existed."))
    i18ns.append(I18n(i1_key="core_error_unique", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}} {{value}} 已经存在，请重新输入。"))
    i18ns.append(I18n(i1_key="core_error_required", i1_locale=conf.LANG_EN, i1_message=u"Please input {{label}}."))
    i18ns.append(I18n(i1_key="core_error_required", i1_locale=conf.LANG_ZH_CN, i1_message=u"请输入{{label}}。"))
    i18ns.append(I18n(i1_key="core_error_choices", i1_locale=conf.LANG_EN, i1_message=u"The value of {{label}} must be one of {{choices}}."))
    i18ns.append(I18n(i1_key="core_error_choices", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}}的值必须是{{choices}}其中的一个。"))
    i18ns.append(I18n(i1_key="core_error_length", i1_locale=conf.LANG_EN, i1_message=u"The length of {{label}} must between {{minlength}} and {{maxlength}}."))
    i18ns.append(I18n(i1_key="core_error_length", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}}的长度必须在 {{minlength}}和{{maxlength}}之间."))
    i18ns.append(I18n(i1_key="core_error_range", i1_locale=conf.LANG_EN, i1_message=u"The value of {{label}} must between {{mininum}} and {{maximum}}."))
    i18ns.append(I18n(i1_key="core_error_range", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}}必须在{{mininum}}和{{maximum}}之间。"))
    i18ns.append(I18n(i1_key="core_error_typeint", i1_locale=conf.LANG_EN, i1_message=u"The value of {{label}} must be an integer."))
    i18ns.append(I18n(i1_key="core_error_typeint", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}}是整数类型，只能输入数字和-。"))
    i18ns.append(I18n(i1_key="core_error_typefloat", i1_locale=conf.LANG_EN, i1_message=u"The value of {{label}} must be an integer."))
    i18ns.append(I18n(i1_key="core_error_typefloat", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}}是浮点类型，只能输入数字,'-'和'.'。"))
    i18ns.append(I18n(i1_key="core_error_typedate", i1_locale=conf.LANG_EN, i1_message=u"The value of {{label}} must be the format {{fmt}}."))
    i18ns.append(I18n(i1_key="core_error_typedate", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}}是日期类型，只能按格式{{fmt}}输入。"))
    i18ns.append(I18n(i1_key="core_error_typedatetime", i1_locale=conf.LANG_EN, i1_message=u"The value of {{label}} must be the format {{fmt}}."))
    i18ns.append(I18n(i1_key="core_error_typedatetime", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}}是日期时间类型，只能按格式{{fmt}}输入。"))
    i18ns.append(I18n(i1_key="core_error_typewrong", i1_locale=conf.LANG_EN, i1_message=u"The format of {{label}} is not correct, please follow the format {{fmt}} to input."))
    i18ns.append(I18n(i1_key="core_error_typewrong", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{label}}格式不正确，请按格式{{fmt}}输入。"))
    i18ns.append(I18n(i1_key="core_status_success", i1_locale=conf.LANG_EN, i1_message=u"Succeeded."))
    i18ns.append(I18n(i1_key="core_status_success", i1_locale=conf.LANG_ZH_CN, i1_message=u"成功。"))
    i18ns.append(I18n(i1_key="core_label_day", i1_locale=conf.LANG_EN, i1_message=u"Day"))
    i18ns.append(I18n(i1_key="core_label_day", i1_locale=conf.LANG_ZH_CN, i1_message=u"日"))
    i18ns.append(I18n(i1_key="core_label_month", i1_locale=conf.LANG_EN, i1_message=u"Month"))
    i18ns.append(I18n(i1_key="core_label_month", i1_locale=conf.LANG_ZH_CN, i1_message=u"月"))
    i18ns.append(I18n(i1_key="core_label_year", i1_locale=conf.LANG_EN, i1_message=u"Year"))
    i18ns.append(I18n(i1_key="core_label_year", i1_locale=conf.LANG_ZH_CN, i1_message=u"年"))
    i18ns.append(I18n(i1_key="core_label_hour", i1_locale=conf.LANG_EN, i1_message=u"Hour"))
    i18ns.append(I18n(i1_key="core_label_hour", i1_locale=conf.LANG_ZH_CN, i1_message=u"时"))
    i18ns.append(I18n(i1_key="core_label_minute", i1_locale=conf.LANG_EN, i1_message=u"Minute"))
    i18ns.append(I18n(i1_key="core_label_minute", i1_locale=conf.LANG_ZH_CN, i1_message=u"分"))
    i18ns.append(I18n(i1_key="core_label_second", i1_locale=conf.LANG_EN, i1_message=u"Second"))
    i18ns.append(I18n(i1_key="core_label_second", i1_locale=conf.LANG_ZH_CN, i1_message=u"秒"))
    i18ns.append(I18n(i1_key="core_label_millisecond", i1_locale=conf.LANG_EN, i1_message=u"Millisecond"))
    i18ns.append(I18n(i1_key="core_label_millisecond", i1_locale=conf.LANG_ZH_CN, i1_message=u"毫秒"))
    
    
    i18ns.append(I18n(i1_key="core_label_previouspage", i1_locale=conf.LANG_EN, i1_message=u"Previous Page"))
    i18ns.append(I18n(i1_key="core_label_previouspage", i1_locale=conf.LANG_ZH_CN, i1_message=u"上一页"))
    i18ns.append(I18n(i1_key="core_label_nextpage", i1_locale=conf.LANG_EN, i1_message=u"Next Page"))
    i18ns.append(I18n(i1_key="core_label_nextpage", i1_locale=conf.LANG_ZH_CN, i1_message=u"下一页"))
    i18ns.append(I18n(i1_key="core_label_page", i1_locale=conf.LANG_EN, i1_message=u"Page"))
    i18ns.append(I18n(i1_key="core_label_page", i1_locale=conf.LANG_ZH_CN, i1_message=u"页"))
    i18ns.append(I18n(i1_key="core_label_pageorder", i1_locale=conf.LANG_EN, i1_message=u"Page {{page}}"))
    i18ns.append(I18n(i1_key="core_label_pageorder", i1_locale=conf.LANG_ZH_CN, i1_message=u"第{{page}}页"))
    i18ns.append(I18n(i1_key="core_label_firstpage", i1_locale=conf.LANG_EN, i1_message=u"First Page"))
    i18ns.append(I18n(i1_key="core_label_firstpage", i1_locale=conf.LANG_ZH_CN, i1_message=u"首页"))
    i18ns.append(I18n(i1_key="core_label_lastpage", i1_locale=conf.LANG_EN, i1_message=u"Last Page"))
    i18ns.append(I18n(i1_key="core_label_lastpage", i1_locale=conf.LANG_ZH_CN, i1_message=u"末页"))
    i18ns.append(I18n(i1_key="core_label_operationkey", i1_locale=conf.LANG_EN, i1_message=u"Operation Key"))
    i18ns.append(I18n(i1_key="core_label_operationkey", i1_locale=conf.LANG_ZH_CN, i1_message=u"操作"))
    i18ns.append(I18n(i1_key="core_label_modifiedtime", i1_locale=conf.LANG_EN, i1_message=u"Modified time"))
    i18ns.append(I18n(i1_key="core_label_modifiedtime", i1_locale=conf.LANG_ZH_CN, i1_message=u"修改时间"))
    i18ns.append(I18n(i1_key="core_label_createdtime", i1_locale=conf.LANG_EN, i1_message=u"Created time"))
    i18ns.append(I18n(i1_key="core_label_createdtime", i1_locale=conf.LANG_ZH_CN, i1_message=u"创建时间"))
    i18ns.append(I18n(i1_key="core_label_modifierid", i1_locale=conf.LANG_EN, i1_message=u"Modifier"))
    i18ns.append(I18n(i1_key="core_label_modifierid", i1_locale=conf.LANG_ZH_CN, i1_message=u"修改人"))
    i18ns.append(I18n(i1_key="core_label_modifier", i1_locale=conf.LANG_EN, i1_message=u"Modifier"))
    i18ns.append(I18n(i1_key="core_label_modifier", i1_locale=conf.LANG_ZH_CN, i1_message=u"修改人"))
    i18ns.append(I18n(i1_key="core_label_warn", i1_locale=conf.LANG_EN, i1_message=u"Warning"))
    i18ns.append(I18n(i1_key="core_label_warn", i1_locale=conf.LANG_ZH_CN, i1_message=u"警告"))
    i18ns.append(I18n(i1_key="core_label_info", i1_locale=conf.LANG_EN, i1_message=u"Information"))
    i18ns.append(I18n(i1_key="core_label_info", i1_locale=conf.LANG_ZH_CN, i1_message=u"信息"))
    i18ns.append(I18n(i1_key="core_label_ok", i1_locale=conf.LANG_EN, i1_message=u"OK"))
    i18ns.append(I18n(i1_key="core_label_ok", i1_locale=conf.LANG_ZH_CN, i1_message=u"OK"))
    i18ns.append(I18n(i1_key="core_label_confirm", i1_locale=conf.LANG_EN, i1_message=u"Confirm"))
    i18ns.append(I18n(i1_key="core_label_confirm", i1_locale=conf.LANG_ZH_CN, i1_message=u"确认"))
    i18ns.append(I18n(i1_key="core_label_prompt", i1_locale=conf.LANG_EN, i1_message=u"Prompt"))
    i18ns.append(I18n(i1_key="core_label_prompt", i1_locale=conf.LANG_ZH_CN, i1_message=u"提示"))
    i18ns.append(I18n(i1_key="core_label_required", i1_locale=conf.LANG_EN, i1_message=u"Required"))
    i18ns.append(I18n(i1_key="core_label_required", i1_locale=conf.LANG_ZH_CN, i1_message=u"必填项"))
    i18ns.append(I18n(i1_key="core_label_optional", i1_locale=conf.LANG_EN, i1_message=u"Optional"))
    i18ns.append(I18n(i1_key="core_label_optional", i1_locale=conf.LANG_ZH_CN, i1_message=u"选填项"))
    i18ns.append(I18n(i1_key="core_action_cancel", i1_locale=conf.LANG_EN, i1_message=u"Cancel"))
    i18ns.append(I18n(i1_key="core_action_cancel", i1_locale=conf.LANG_ZH_CN, i1_message=u"取消"))
    i18ns.append(I18n(i1_key="core_action_close", i1_locale=conf.LANG_EN, i1_message=u"Close"))
    i18ns.append(I18n(i1_key="core_action_close", i1_locale=conf.LANG_ZH_CN, i1_message=u"关闭"))
    i18ns.append(I18n(i1_key="core_action_save", i1_locale=conf.LANG_EN, i1_message=u"Save"))
    i18ns.append(I18n(i1_key="core_action_save", i1_locale=conf.LANG_ZH_CN, i1_message=u"保存"))
    i18ns.append(I18n(i1_key="core_action_view", i1_locale=conf.LANG_EN, i1_message=u"View"))
    i18ns.append(I18n(i1_key="core_action_view", i1_locale=conf.LANG_ZH_CN, i1_message=u"查看"))
    i18ns.append(I18n(i1_key="core_action_create", i1_locale=conf.LANG_EN, i1_message=u"Create"))
    i18ns.append(I18n(i1_key="core_action_create", i1_locale=conf.LANG_ZH_CN, i1_message=u"新增"))
    i18ns.append(I18n(i1_key="core_action_update", i1_locale=conf.LANG_EN, i1_message=u"Edit"))
    i18ns.append(I18n(i1_key="core_action_update", i1_locale=conf.LANG_ZH_CN, i1_message=u"编辑"))
    i18ns.append(I18n(i1_key="core_action_delete", i1_locale=conf.LANG_EN, i1_message=u"Delete"))
    i18ns.append(I18n(i1_key="core_action_delete", i1_locale=conf.LANG_ZH_CN, i1_message=u"删除"))
    i18ns.append(I18n(i1_key="core_action_done", i1_locale=conf.LANG_EN, i1_message=u"Done"))
    i18ns.append(I18n(i1_key="core_action_done", i1_locale=conf.LANG_ZH_CN, i1_message=u"完成"))
    i18ns.append(I18n(i1_key="core_action_back", i1_locale=conf.LANG_EN, i1_message=u"Back"))
    i18ns.append(I18n(i1_key="core_action_back", i1_locale=conf.LANG_ZH_CN, i1_message=u"返回"))
    i18ns.append(I18n(i1_key="core_action_forward", i1_locale=conf.LANG_EN, i1_message=u"Forward"))
    i18ns.append(I18n(i1_key="core_action_forward", i1_locale=conf.LANG_ZH_CN, i1_message=u"前进"))
    i18ns.append(I18n(i1_key="core_action_backward", i1_locale=conf.LANG_EN, i1_message=u"Back"))
    i18ns.append(I18n(i1_key="core_action_backward", i1_locale=conf.LANG_ZH_CN, i1_message=u"后退"))
    
    i18ns.append(I18n(i1_key="core_status_http0_networkrefused", i1_locale=conf.LANG_EN, i1_message=u"Server is not available,please try again."))
    i18ns.append(I18n(i1_key="core_status_http0_networkrefused", i1_locale=conf.LANG_ZH_CN, i1_message=u"连接被服务器拒绝，请稍后重试。"))
    
    i18ns.append(I18n(i1_key="core_status_http500_internalservererror", i1_locale=conf.LANG_EN, i1_message=u"Internal Server Error."))
    i18ns.append(I18n(i1_key="core_status_http500_internalservererror", i1_locale=conf.LANG_ZH_CN, i1_message=u"服务器发生错误，请稍后重试。"))
    
    i18ns.append(I18n(i1_key="core_error_login_failed", i1_locale=conf.LANG_EN, i1_message=u"Your email or account is not matched your password, please enter again"))
    i18ns.append(I18n(i1_key="core_error_login_failed", i1_locale=conf.LANG_ZH_CN, i1_message=u"邮件或账号与密码不匹配，请重新输入。"))
    i18ns.append(I18n(i1_key="core_error_session_expired", i1_locale=conf.LANG_EN, i1_message=u"Your session is expired, please login again"))
    i18ns.append(I18n(i1_key="core_error_session_expired", i1_locale=conf.LANG_ZH_CN, i1_message=u"登录会话已经过期，请重新登录。"))
    i18ns.append(I18n(i1_key="core_error_unauthorized", i1_locale=conf.LANG_EN, i1_message=u"You don't have permission to access it."))
    i18ns.append(I18n(i1_key="core_error_unauthorized", i1_locale=conf.LANG_ZH_CN, i1_message=u"你没有操作权限。"))
    i18ns.append(I18n(i1_key="core_error_oldpassword_incorrect", i1_locale=conf.LANG_EN, i1_message=u"Old password is not correct, please input again."))
    i18ns.append(I18n(i1_key="core_error_oldpassword_incorrect", i1_locale=conf.LANG_ZH_CN, i1_message=u"现在的密码不正确，不能修改密码。"))
    i18ns.append(I18n(i1_key="core_error_password_notmatch", i1_locale=conf.LANG_EN, i1_message=u"Those two new passwords are not identical."))
    i18ns.append(I18n(i1_key="core_error_password_notmatch", i1_locale=conf.LANG_ZH_CN, i1_message=u"两次输入的新密码不一致，请重新输入。"))
    i18ns.append(I18n(i1_key="core_error_filesize_exceeded", i1_locale=conf.LANG_EN, i1_message=u"The filesize exceed {{filesize}}, can't upload."))
    i18ns.append(I18n(i1_key="core_error_filesize_exceeded", i1_locale=conf.LANG_ZH_CN, i1_message=u"文件超过了{{filesize}} M，不能上传！"))
    i18ns.append(I18n(i1_key="core_error_duplicatesubmit", i1_locale=conf.LANG_EN, i1_message=u"Last request is handling, please don't submit duplicate."))
    i18ns.append(I18n(i1_key="core_error_duplicatesubmit", i1_locale=conf.LANG_ZH_CN, i1_message=u"上一个请求正在处理，请不要重复提交."))
    i18ns.append(I18n(i1_key="core_error_notagreeslaprivacy", i1_locale=conf.LANG_EN, i1_message=u"You can't signup and use if you don't agree the sla and privacy policy"))
    i18ns.append(I18n(i1_key="core_error_notagreeslaprivacy", i1_locale=conf.LANG_ZH_CN, i1_message=u"请同意服务条款和隐私政策，否则您不能注册和使用."))
    
    i18ns.append(I18n(i1_key="core_status_savesuccess", i1_locale=conf.LANG_EN, i1_message=u"Save Successfully."))
    i18ns.append(I18n(i1_key="core_status_savesuccess", i1_locale=conf.LANG_ZH_CN, i1_message=u"保存成功。"))
    i18ns.append(I18n(i1_key="core_status_deletesuccess", i1_locale=conf.LANG_EN, i1_message=u"Delete Successfully."))
    i18ns.append(I18n(i1_key="core_status_deletesuccess", i1_locale=conf.LANG_ZH_CN, i1_message=u"已成功删除。"))
    i18ns.append(I18n(i1_key="core_action_login", i1_locale=conf.LANG_EN, i1_message=u"Login"))
    i18ns.append(I18n(i1_key="core_action_login", i1_locale=conf.LANG_ZH_CN, i1_message=u"登录"))
    i18ns.append(I18n(i1_key="core_action_userexit", i1_locale=conf.LANG_EN, i1_message=u"Secure Exit"))
    i18ns.append(I18n(i1_key="core_action_userexit", i1_locale=conf.LANG_ZH_CN, i1_message=u"安全退出"))
    i18ns.append(I18n(i1_key="core_action_changepwd", i1_locale=conf.LANG_EN, i1_message=u"Change Password"))
    i18ns.append(I18n(i1_key="core_action_changepwd", i1_locale=conf.LANG_ZH_CN, i1_message=u"修改密码"))
    i18ns.append(I18n(i1_key="core_action_forgotpwd", i1_locale=conf.LANG_EN, i1_message=u"Forgot Password"))
    i18ns.append(I18n(i1_key="core_action_forgotpwd", i1_locale=conf.LANG_ZH_CN, i1_message=u"忘记密码"))
    i18ns.append(I18n(i1_key="core_action_signup", i1_locale=conf.LANG_EN, i1_message=u"Signup"))
    i18ns.append(I18n(i1_key="core_action_signup", i1_locale=conf.LANG_ZH_CN, i1_message=u"注册"))
    i18ns.append(I18n(i1_key="core_action_search", i1_locale=conf.LANG_EN, i1_message=u"Search"))
    i18ns.append(I18n(i1_key="core_action_search", i1_locale=conf.LANG_ZH_CN, i1_message=u"搜索"))
    i18ns.append(I18n(i1_key="core_action_ok", i1_locale=conf.LANG_EN, i1_message=u"OK"))
    i18ns.append(I18n(i1_key="core_action_ok", i1_locale=conf.LANG_ZH_CN, i1_message=u"确定"))
    i18ns.append(I18n(i1_key="core_action_cancel", i1_locale=conf.LANG_EN, i1_message=u"Cancel"))
    i18ns.append(I18n(i1_key="core_action_cancel", i1_locale=conf.LANG_ZH_CN, i1_message=u"取消"))
    i18ns.append(I18n(i1_key="core_action_cancelsearch", i1_locale=conf.LANG_EN, i1_message=u"Cancel Search"))
    i18ns.append(I18n(i1_key="core_action_cancelsearch", i1_locale=conf.LANG_ZH_CN, i1_message=u"取消搜索"))
    i18ns.append(I18n(i1_key="core_action_usersettings", i1_locale=conf.LANG_EN, i1_message=u"Settings"))
    i18ns.append(I18n(i1_key="core_action_usersettings", i1_locale=conf.LANG_ZH_CN, i1_message=u"设置"))
    
    
    i18ns.append(I18n(i1_key="core_label_searchresult", i1_locale=conf.LANG_EN, i1_message=u"Search Results"))
    i18ns.append(I18n(i1_key="core_label_searchresult", i1_locale=conf.LANG_ZH_CN, i1_message=u"搜索结果"))
    i18ns.append(I18n(i1_key="core_label_savedin", i1_locale=conf.LANG_EN, i1_message=u"Saved in {{datetime}}."))
    i18ns.append(I18n(i1_key="core_label_savedin", i1_locale=conf.LANG_ZH_CN, i1_message=u"已存于{{datetime}}."))
    i18ns.append(I18n(i1_key="core_label_saving", i1_locale=conf.LANG_EN, i1_message=u"Saving..."))
    i18ns.append(I18n(i1_key="core_label_saving", i1_locale=conf.LANG_ZH_CN, i1_message=u"正在保存..."))
    i18ns.append(I18n(i1_key="core_label_submitedin", i1_locale=conf.LANG_EN, i1_message=u"Submitted in{{datetime}}"))
    i18ns.append(I18n(i1_key="core_label_submitedin", i1_locale=conf.LANG_ZH_CN, i1_message=u"已于{{datetime}}提交."))
    i18ns.append(I18n(i1_key="core_label_submiting", i1_locale=conf.LANG_EN, i1_message=u"Submiting..."))
    i18ns.append(I18n(i1_key="core_label_submiting", i1_locale=conf.LANG_ZH_CN, i1_message=u"正在提交..."))
    i18ns.append(I18n(i1_key="core_label_deletedin", i1_locale=conf.LANG_EN, i1_message=u"Deleted in{{datetime}}"))
    i18ns.append(I18n(i1_key="core_label_deletedin", i1_locale=conf.LANG_ZH_CN, i1_message=u"已于{{datetime}}刪除."))
    i18ns.append(I18n(i1_key="core_label_deleting", i1_locale=conf.LANG_EN, i1_message=u"Deleting..."))
    i18ns.append(I18n(i1_key="core_label_deleting", i1_locale=conf.LANG_ZH_CN, i1_message=u"正在刪除..."))    
    i18ns.append(I18n(i1_key="core_label_loadedin", i1_locale=conf.LANG_EN, i1_message=u"Loaded in{{datetime}}"))
    i18ns.append(I18n(i1_key="core_label_loadedin", i1_locale=conf.LANG_ZH_CN, i1_message=u"已于{{datetime}}加载."))
    i18ns.append(I18n(i1_key="core_label_loading", i1_locale=conf.LANG_EN, i1_message=u"Loading..."))
    i18ns.append(I18n(i1_key="core_label_loading", i1_locale=conf.LANG_ZH_CN, i1_message=u"正在加载...")) 
    
    i18ns.append(I18n(i1_key="core_label_user", i1_locale=conf.LANG_EN, i1_message=u"User"))
    i18ns.append(I18n(i1_key="core_label_user", i1_locale=conf.LANG_ZH_CN, i1_message=u"用户"))
    i18ns.append(I18n(i1_key="core_label_keyword", i1_locale=conf.LANG_EN, i1_message=u"Keywords"))
    i18ns.append(I18n(i1_key="core_label_keyword", i1_locale=conf.LANG_ZH_CN, i1_message=u"关键字"))
    i18ns.append(I18n(i1_key="core_label_accountname", i1_locale=conf.LANG_EN, i1_message=u"Account"))
    i18ns.append(I18n(i1_key="core_label_accountname", i1_locale=conf.LANG_ZH_CN, i1_message=u"账号"))
    i18ns.append(I18n(i1_key="core_label_useremail", i1_locale=conf.LANG_EN, i1_message=u"Email"))
    i18ns.append(I18n(i1_key="core_label_useremail", i1_locale=conf.LANG_ZH_CN, i1_message=u"电子邮件"))
    i18ns.append(I18n(i1_key="core_label_userpassword", i1_locale=conf.LANG_EN, i1_message=u"Password"))
    i18ns.append(I18n(i1_key="core_label_userpassword", i1_locale=conf.LANG_ZH_CN, i1_message=u"密码"))
    i18ns.append(I18n(i1_key="core_label_loginedtimes", i1_locale=conf.LANG_EN, i1_message=u"Login Times"))
    i18ns.append(I18n(i1_key="core_label_loginedtimes", i1_locale=conf.LANG_ZH_CN, i1_message=u"登录次数"))
    i18ns.append(I18n(i1_key="core_label_lastloginedtimes", i1_locale=conf.LANG_EN, i1_message=u"Last Login Time"))
    i18ns.append(I18n(i1_key="core_label_lastloginedtimes", i1_locale=conf.LANG_ZH_CN, i1_message=u"上次登录时间"))
    i18ns.append(I18n(i1_key="core_label_isdisabled", i1_locale=conf.LANG_EN, i1_message=u"Disabled"))
    i18ns.append(I18n(i1_key="core_label_isdisabled", i1_locale=conf.LANG_ZH_CN, i1_message=u"禁用"))
    i18ns.append(I18n(i1_key="core_label_sla", i1_locale=conf.LANG_EN, i1_message=u"'Service Agreement'"))
    i18ns.append(I18n(i1_key="core_label_sla", i1_locale=conf.LANG_ZH_CN, i1_message=u'“服务条款”'))
    i18ns.append(I18n(i1_key="core_label_privacypolicy", i1_locale=conf.LANG_EN, i1_message=u"'Privacy Policy'"))
    i18ns.append(I18n(i1_key="core_label_privacypolicy", i1_locale=conf.LANG_ZH_CN, i1_message=u'“隐私条款”'))
    i18ns.append(I18n(i1_key="core_label_agree", i1_locale=conf.LANG_EN, i1_message=u"Agree"))
    i18ns.append(I18n(i1_key="core_label_agree", i1_locale=conf.LANG_ZH_CN, i1_message=u'我同意'))
    i18ns.append(I18n(i1_key="core_label_and", i1_locale=conf.LANG_EN, i1_message=u"and"))
    i18ns.append(I18n(i1_key="core_label_and", i1_locale=conf.LANG_ZH_CN, i1_message=u'和'))
    i18ns.append(I18n(i1_key="core_label_useroldpassword", i1_locale=conf.LANG_EN, i1_message=u"Old Password",))
    i18ns.append(I18n(i1_key="core_label_useroldpassword", i1_locale=conf.LANG_ZH_CN, i1_message=u"现在的密码"))
    i18ns.append(I18n(i1_key="core_label_usernewpassword", i1_locale=conf.LANG_EN, i1_message=u"New Password"))
    i18ns.append(I18n(i1_key="core_label_usernewpassword", i1_locale=conf.LANG_ZH_CN, i1_message=u"设置新的密码"))
    i18ns.append(I18n(i1_key="core_label_userdupnewpassword", i1_locale=conf.LANG_EN, i1_message=u"Duplicate New Password"))
    i18ns.append(I18n(i1_key="core_label_userdupnewpassword", i1_locale=conf.LANG_ZH_CN, i1_message=u"重复新的密码"))
    i18ns.append(I18n(i1_key="core_label_username", i1_locale=conf.LANG_EN, i1_message=u"Username"))
    i18ns.append(I18n(i1_key="core_label_username", i1_locale=conf.LANG_ZH_CN, i1_message=u"姓名"))
    i18ns.append(I18n(i1_key="core_label_usermodule", i1_locale=conf.LANG_EN, i1_message=u"User"))
    i18ns.append(I18n(i1_key="core_label_usermodule", i1_locale=conf.LANG_ZH_CN, i1_message=u"用户"))
    i18ns.append(I18n(i1_key="core_label_signupsuccess", i1_locale=conf.LANG_EN, i1_message=u"You have already signed up successfully, please login in to use."))
    i18ns.append(I18n(i1_key="core_label_signupsuccess", i1_locale=conf.LANG_ZH_CN, i1_message=u"您已经注册成功，登录后即可使用。"))
        
    return i18ns

def initialize_userandacs(modifier_id):
    from core.handler import ChangePasswordHandler, PreferredLanguageHandler, DynamicJsHandler
    from core.handler import IndexHandler, LoginHandler, LogoutHandler, SignupHandler
    from core.sysman import CacheSmHandler, MigrationSmHandler, LogSmHandler, SysPropSmHandler, I18nSmHandler
    anonymous_role = user.create_role("Anonymous", modifier_id)
    user.create_operation("SYSTEM_INDEX", [IndexHandler.get_qualified_name(), DynamicJsHandler.get_qualified_name(), PreferredLanguageHandler.get_qualified_name()], None, modifier_id)
    user.create_operation("SYSTEM_SIGNUP", [SignupHandler.get_qualified_name()], None, modifier_id)
    user.create_operation("SYSTEM_LOGIN", [LoginHandler.get_qualified_name()], None, modifier_id)
    user.create_roleoperation(anonymous_role.uid, "SYSTEM_LOGIN", modifier_id)
    user.create_roleoperation(anonymous_role.uid, "SYSTEM_INDEX", modifier_id)
    user.create_roleoperation(anonymous_role.uid, "SYSTEM_SIGNUP", modifier_id)
    
    user.create_operation("SYSTEM_LOGOUT", [LogoutHandler.get_qualified_name()], None, modifier_id)
    user.create_operation("CHANGE_PASSWORD", [ChangePasswordHandler.get_qualified_name()], None, modifier_id)
    ordinary_role = user.create_role("Ordinary User", modifier_id)
    user.create_roleoperation(ordinary_role.uid, "SYSTEM_LOGOUT", modifier_id)
    user.create_roleoperation(ordinary_role.uid, "CHANGE_PASSWORD", modifier_id)
    
    user.create_operation("SYSTEM_MANAGEMENT", [LogSmHandler.get_qualified_name(), CacheSmHandler.get_qualified_name(), I18nSmHandler.get_qualified_name(), SysPropSmHandler.get_qualified_name(), MigrationSmHandler.get_qualified_name()], None, modifier_id)
    sysadmin_role = user.create_role("System Administrator", modifier_id)
    user.create_roleoperation(sysadmin_role.uid, "SYSTEM_MANAGEMENT", modifier_id)
    
    anonymous = user.create_user("Anonymous User", "anonymous@localhost.com", "anonymous", "anonymous", False, modifier_id)
    sysadmin = user.create_user("System Administrator", "sysadmin@localhost.com", "sysadmin", "sysadmin", False, modifier_id)
    
    user.create_userrole(anonymous.uid, anonymous_role.uid, modifier_id)
    
    user.create_userrole(sysadmin.uid, anonymous_role.uid, modifier_id)
    user.create_userrole(sysadmin.uid, ordinary_role.uid, modifier_id)
    user.create_userrole(sysadmin.uid, sysadmin_role.uid, modifier_id)

def fetch_migrations(modifier_id):
    migrations = []
    vers = versions.__all__
    for version in vers:
        cls = version.rsplit('.', 1)[1]
        ver_id = int(cls[1:])
        migration = _get_migration(ver_id, modifier_id)
        migrations.append(migration)
    return migrations

def downgrade(ver_id, modifier_id):
    d = strutil.to_bool(conf.get_migration_downgrade())
    if d is not True:
        raise CoreError("Downgrade is not allowed.")
    
    ver_id = int(ver_id)
    vers = _fetch_versions()
    instance = None
    migration = None
    for verid, version in vers.items():
        if verid > ver_id:
            migration = _get_migration(verid, modifier_id)
            if migration.is_upgraded:
                raise CoreError("The higher version %d is migrated, please downgrade the higher version first." % verid)
        elif verid == ver_id:
            migration = _get_migration(verid, modifier_id)
            if migration.is_upgraded is False:
                raise CoreError("This version %d is not migrated, please upgraded it first." % verid)
            else:
                instance = version()
    if instance is not None:
        migration.is_upgraded = False
        migration.update(modifier_id)
        instance.downgrade(modifier_id)
        cache.empty()

def migrate(modifier_id):
    vers = _fetch_versions()
    for ver_id, version in vers.items():
        migration = _get_migration(ver_id, modifier_id)
        if not migration.is_upgraded:
            version = version()
            try:
                version.upgrade(modifier_id)
                migration.is_upgraded = True
                migration.migration_time = datetime.utcnow()
                migration.update(modifier_id)
                cache.empty()
            except BaseException, e:
                msg = str(e)
                msg += traceback.format_exc()
                log.get_logger().fatal(msg)
                version.downgrade(modifier_id)
                raise e

def _fetch_versions():
    vers = versions.__all__
    vs = {}
    for version in vers:
        mod, cls = version.rsplit('.', 1)
        ver_id = int(cls[1:])
        mod = __import__(mod, None, None, [''])
        cls = getattr(mod, cls)
        vs[ver_id] = cls
    return vs

def _get_migration(ver_id, modifier_id):
    query = Migration.all()
    query = query.filter("ver_id =", int(ver_id))
    if query.count() == 0:
        mig = Migration()
        mig.ver_id = int(ver_id)
        mig.is_upgraded = False
        mig.create(modifier_id)
    else:
        mig = query.get()
    return mig

class Version:
    
    def __init__(self):
        self.__updated_operations = {}
    
    def upgrade(self, modifier_id):
        self.__upgrade_i18ns(modifier_id)
        self.__upgrade_useracs(modifier_id)
        self._upgrade(modifier_id)
        
    def downgrade(self, modifier_id):
        self.__downgrade_i18ns(modifier_id)
        self.__downgrade_useracs(modifier_id)
        self._downgrade(modifier_id)
    
    def _exist_column(self, table, column, conn=None):
        sql = "SHOW COLUMNS FROM %s LIKE '%s'" % (table, column)
        conn = conn if conn is not None else dbutil.get_dbconn()
        result = conn.query(sql)
        return len(result) > 0
    
    def __upgrade_i18ns(self, modifier_id):
        i18ns = self._get_i18ns()
        for i1 in i18ns:
            if hasattr(i1, "updade") and i1.update == True:
                i18n.update_i18n(i1.i1_key, i1.i1_message, i1.i1_locale, i1.i1_type, modifier_id)
            else:
                i18n.create_i18n(i1.i1_key, i1.i1_message, i1.i1_locale, i1.i1_type, modifier_id)
        
    def __downgrade_i18ns(self, modifier_id):
        i18ns = self._get_i18ns()
        for i1 in i18ns:
            i18n.delete_i18n(i1.i1_key, i1.i1_locale, modifier_id)
    
    def __upgrade_useracs(self, modifier_id):
        roles = self._get_roles()
        if roles != None:
            for role in roles:
                user.create_role(role.role_name, modifier_id)
        operations = self._get_operations()
        
        if operations != None:
            for operation in operations:
                oper1 = user.get_operation(operation_key=operation.operation_key)
                if oper1 is None:
                    user.create_operation(operation.operation_key, operation.handler_classes, operation.resource_oql, modifier_id)
                else:
                    self.__updated_operations[operation.operation_key] = operation
                    user.update_operation_handlers(operation.operation_key, operation.handler_classes, modifier_id, replace=False)
                    
        roleoperations = self._get_roleoperations()
        if roleoperations != None:
            for roleoperation in roleoperations:
                user.create_roleoperation(roleoperation.role_id, roleoperation.operation_key, modifier_id)
    
    def __downgrade_useracs(self, modifier_id):
        roles = self._get_roles()
        if roles != None:
            for role in roles:
                user.delete_role(role.role_id, modifier_id)
        operations = self._get_operations()
        if operations != None:
            for operation in operations:
                if self.__updated_operations.has_key(operation.operation_key):
                    user.remove_operation_handlers(operation.operation_key, self.__updated_operations[operation.operation_key].handler_classes.split(","), modifier_id)
                else:
                    user.delete_operation(operation.operation_key, modifier_id)
        roleoperations = self._get_roleoperations()
        if roleoperations != None:
            for roleoperation in roleoperations:
                user.delete_roleoperations(role_id=roleoperation.role_id, operation_key=roleoperation.operation_key, modifier_id=modifier_id)
                
    def _get_i18ns(self):
        """To be override in sub class"""
        raise NotImplementedError
    
    def _get_roles(self):
        """To be override in sub class"""
        raise NotImplementedError
    
    def _get_operations(self):
        """To be override in sub class"""
        raise NotImplementedError
    
    def _get_roleoperations(self):
        """To be override in sub class"""
        raise NotImplementedError
    
    def _upgrade(self, modifier_id):
        """To be override in sub class"""
        raise NotImplementedError
    
    def _downgrade(self, modifier_id):
        """To be override in sub class"""
        raise NotImplementedError
