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
import traceback

from core import log
import web    


try:
    import sae
    DB_MASTER = {
                  "host": sae.const.MYSQL_HOST,
                  "port": sae.const.MYSQL_PORT,
                  "username" : sae.const.MYSQL_USER,
                  "password" : sae.const.MYSQL_PASS,
                  "dbname": sae.const.MYSQL_DB
                  }
except:
    DB_MASTER = {
                  "host": "127.0.0.1",
                  "port": 3306,
                  "username" : "root",
                  "password" : "1234",
                  "dbname":"guan"
                  }
    
try:
    from sae.ext.storage import monkey
    monkey.patch_all()
    DEFAULT_UPLOADFILE_ROOTPATH = "/s/"
except:
    import os
    DEFAULT_UPLOADFILE_ROOTPATH = os.path.join(os.path.dirname(__file__), "..") + os.sep + "/work/data/uploadfiles/"

URLs = (
        '/', 'core.handler.IndexHandler',
        '/dynamic.js', 'core.handler.DynamicJsHandler',
        '/sysman', 'core.sysman.SysManDispatcher',
        '/d', 'core.handler.Dispatcher',
        '/__setup__', 'core.handler.SetupHandler'
        )

HANDLERs = (
            'login', 'core.handler.LoginHandler',
            'logout', 'core.handler.LogoutHandler',
            'changepwd', 'core.handler.ChangePasswordHandler',
            'signup', 'core.handler.SignupHandler',
            'notebooklist', 'note.notehandler.NotebookListHandler',
            'savenotebook', 'note.notehandler.NotebookSaveHandler',
            'movenotebook', 'note.notehandler.NotebookMoveHandler',
            'deletenotebook', 'note.notehandler.NotebookDeleteHandler',
            'notelist', 'note.notehandler.NoteListHandler',
            'savenote', 'note.notehandler.NoteSaveHandler',
            'deletenote', 'note.notehandler.NoteDeleteHandler',
            'recovernote', 'note.notehandler.NoteRecoverHandler',
            'emptynotetrash', 'note.notehandler.NoteEmptyTrashHandler',
            
            'contactlist', 'contact.contacthandler.ContactListHandler',
            'savecontact', 'contact.contacthandler.ContactSaveHandler',
            'deletecontact', 'contact.contacthandler.ContactDeleteHandler',
            'recovercontact', 'contact.contacthandler.ContactRecoverHandler',
            'emptycontacttrash', 'contact.contacthandler.ContactEmptyTrashHandler',
            'grouplist', 'contact.contacthandler.GroupListHandler',
            'savegroup', 'contact.contacthandler.GroupSaveHandler',
            'deletegroup', 'contact.contacthandler.GroupDeleteHandler',
            'savecontactleave', 'contact.contacthandler.ContactLeaveSaveHandler',
            'deletecontactleave', 'contact.contacthandler.ContactLeaveDeleteHandler',
            
            'tasklist', 'task.taskhandler.TaskListHandler',
            'savetask', 'task.taskhandler.TaskSaveHandler',
            'deletetask', 'task.taskhandler.TaskDeleteHandler',
            'recovertask', 'task.taskhandler.TaskRecoverHandler',
            'emptytasktrash', 'task.taskhandler.TaskEmptyTrashHandler',
            'worksheetlist', 'task.taskhandler.WorksheetListHandler',
            'saveworksheet', 'task.taskhandler.WorksheetSaveHandler',
            'deleteworksheet', 'task.taskhandler.WorksheetDeleteHandler',
            'savetaskcomment', 'task.taskhandler.TaskCommentSaveHandler',
            'deletetaskcomment', 'task.taskhandler.TaskCommentDeleteHandler',
            
            'rptbasedata', 'report.reporthandler.ReportBaseDataHandler',
            'rptallocationdata', 'report.reporthandler.RptAllocationChartHandler',
            'rptprogressdata', 'report.reporthandler.RptProgressChartHandler',
            
            'savegroupexception', 'contact.contacthandler.GroupExceptionSaveHandler',
            'deletegroupexception', 'contact.contacthandler.GroupExceptionDeleteHandler',
            'groupexceptionlist', 'contact.contacthandler.GroupExceptionListHandler',
            'savegroupversion', 'contact.contacthandler.GroupVersionSaveHandler',
            'deletegroupversion', 'contact.contacthandler.GroupVersionDeleteHandler',
            'groupversionlist', 'contact.contacthandler.GroupVersionListHandler',
            'savegroupcomponent', 'contact.contacthandler.GroupComponentSaveHandler',
            'deletegroupcomponent', 'contact.contacthandler.GroupComponentDeleteHandler',
            'groupcomponentlist', 'contact.contacthandler.GroupComponentListHandler',
            'savegroupresource', 'contact.contacthandler.GroupResourceSaveHandler',
            'deletegroupresource', 'contact.contacthandler.GroupResourceDeleteHandler',
            'groupresourcelist', 'contact.contacthandler.GroupResourceListHandler'
            
            )



LANG_EN = "en"
LANG_ZH_CN = "zh_CN"

G_VERSION = "%s.%d.%d" % ("1.12", 8, 1)  # (app version, db version)

def get_web_config_debug():
    return False

def get_config_debug_sql():
    return False

def get_session_timeout():
    return 30 * 60

def get_log_root_level():
    from core import sysprop
    return sysprop.get_sysprop_value("LOG_ROOT_LEVEL", default="INFO")
    
def get_log_console_format():
    from core import sysprop
    return sysprop.get_sysprop_value("LOG_CONSOLE_FORMAT", default="%(levelname)s : %(asctime)s : %(message)s")

def get_log_console_level():
    from core import sysprop
    return sysprop.get_sysprop_value("LOG_CONSOLE_LEVEL", default="INFO")

def get_log_db_format():
    from core import sysprop
    return sysprop.get_sysprop_value("LOG_DB_FORMAT", default="%(levelname)s : %(asctime)s : %(message)s")

def get_log_db_level():
    from core import sysprop
    return sysprop.get_sysprop_value("LOG_DB_LEVEL", default="INFO")

def get_date_py_format():
    from core import sysprop
    return sysprop.get_sysprop_value("DATE_PY_FORMAT", default="%Y-%m-%d")

def get_date_js_format():
    from core import sysprop
    return sysprop.get_sysprop_value("DATE_JS_FORMAT", default="yyyy-MM-dd")

def get_datesecond_py_format():
    from core import sysprop
    return sysprop.get_sysprop_value("DATESECOND_PY_FORMAT", default="%Y-%m-%d %H:%M:%S")

def get_datesecond_js_format():
    from core import sysprop
    return sysprop.get_sysprop_value("DATESECOND_JS_FORMAT", default="yyyy-MM-dd hh:mm:ss")

def get_dateminute_py_format():
    from core import sysprop
    return sysprop.get_sysprop_value("DATEMINUTE_PY_FORMAT", default="%Y-%m-%d %H:%M")

def get_dateminute_js_format():
    from core import sysprop
    return sysprop.get_sysprop_value("DATEMINUTE_JS_FORMAT", default="yyyy-MM-dd hh:mm")

def get_migration_downgrade():
    from core import sysprop
    return sysprop.get_sysprop_value("MIGRATION_DOWNGRADE", False)

def get_upload_file_maximum_size():
    from core import sysprop, user, session
    try:
        return user.get_userprop_value("UPLOADFILE_MAXIMUM_SIZE", session.get_token().user_id)
    except:
        value = sysprop.get_sysprop_value("UPLOADFILE_MAXIMUM_SIZE", 5 * 1024 * 1024)
        user.create_userprop("UPLOADFILE_MAXIMUM_SIZE", value, session.get_token().user_id, session.get_token().user_id)
        return value

def get_useraccount_length():
    from core import sysprop
    return sysprop.get_sysprop_value("USERACCOUNT_LENGTH", [3, 20])

def get_userpassword_length():
    from core import sysprop
    return sysprop.get_sysprop_value("USERPASSWORD_LENGTH", [6, 20])

def get_supported_languages():
    from core import sysprop
    return sysprop.get_sysprop_value("SUPPORTED_LANGUAGES", (LANG_EN, LANG_ZH_CN))

def get_preferred_language():
    from core import sysprop, user, session
    try:
        return user.get_userprop_value("PREFERRED_LANGUAGE", session.get_token().user_id)
    except:
        value = sysprop.get_sysprop_value("PREFERRED_LANGUAGE", LANG_ZH_CN)
        user.create_userprop("PREFERRED_LANGUAGE", value, session.get_token().user_id, session.get_token().user_id)
        return value

def get_story_points_options():
    from core import sysprop
    sps = sysprop.get_sysprop_value("STORY_POINTS", default=[0, 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 100])
    sps = map(float, sps)
    options = {}
    for sp in sps:
        if sp != 0.5:
            options[sp] = int(sp)
        else:
            options[sp] = "1/2"
    return options

def get_default_story_points():
    from core import sysprop
    return float(sysprop.get_sysprop_value("DEFAULT_STORY_POINT", default=1))

def get_preferred_timezone():
    from core import sysprop, user, session
    try:
        return user.get_userprop_value("PREFERRED_TIMEZONE", session.get_token().user_id)
    except:
        value = sysprop.get_sysprop_value("PREFERRED_TIMEZONE", "Asia/Shanghai")
        user.create_userprop("PREFERRED_TIMEZONE", value, session.get_token().user_id, session.get_token().user_id)
        return value

def dynamicjs_hook():
    from core import dtutil, jsonutil, i18n
    from core.model import stdModel
    
    std = stdModel()
    today = dtutil.localtoday(get_preferred_timezone())
    std.RPT_SEARCH_START_DATE = today + datetime.timedelta(days=-30)
    std.RPT_SEARCH_END_DATE = today + datetime.timedelta(days=30)
    std.TASKSTATUS_OPTIONS = i18n.get_i18n_messages(language=get_preferred_language(), i1_type="task_status_code", rtn_dict=True)
    std.TASKPRIORITY_OPTIONS = i18n.get_i18n_messages(language=get_preferred_language(), i1_type="task_priority_code", rtn_dict=True)
    std.TASKTYPE_OPTIONS = i18n.get_i18n_messages(language=get_preferred_language(), i1_type="task_type_code", rtn_dict=True)
    std.STORY_POINTS_OPTIONS = get_story_points_options()
    std.LEAVETYPE_OPTIONS = i18n.get_i18n_messages(language=get_preferred_language(), i1_type="cont_leavetype_code", rtn_dict=True)
    std.DEFAULT_STORY_POINTS = "%0.1f" % get_default_story_points()
    js = "var ENV_VAR = %s;" % jsonutil.to_json(std.to_dict())
    return js
    
def session_hook(token):
    
    token.preferredLanguage = get_preferred_language()
    token.preferredTimezone = get_preferred_timezone()
    token.dateSecondFormat = get_datesecond_js_format()
    token.dateMinuteFormat = get_dateminute_js_format()
    token.dateFormat = get_date_js_format()
    
    
    try:
        from core import model
        from contact.contactservice import ContactService
        contact = ContactService.get_instance().get_myself(token.user_id)
        token.contactKey = contact.key() if contact is not None else model.EMPTY_UID
    except:
        msg = traceback.format_exc()
        log.get_logger().error(msg)
        token.contactKey = model.EMPTY_UID
    return token
         
