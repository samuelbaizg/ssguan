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
import traceback
import user
import base64

import conf
from core import filex, session, strutil
from core.error import UnauthorizedError, SessionExpiredError
from error import Error, CoreError
import i18n
import jsonutil
import log
import model
from model import Filex
import sysprop
import web


DEFAULT_INDEX_PATH = "static/index.html"

  
class Rtn(object):
    def __init__(self, handler, data=None, e=None):
        self.__handler = handler
        self.__data = data
        self.__e = e
    
    def set_exception(self, e):
        self.__e = e
    
    def set_data(self, data):
        self.__data = data
        
    def to_dict(self):
        code = "core_status_success" 
        message = ""
        arguments = None
        data = self.__data
        if self.__e != None:
            try:
                e = self.__e
                if not isinstance(e, Error):
                    e = CoreError(traceback.format_exc())
                code = e.get_code()
                arguments = e.get_arguments()
                message = self._get_i18n_message(code, arguments)
                message = str(e) if message is None else message
                data = e.get_data()
            except BaseException, e:
                log.get_logger().error(traceback.format_exc())
                message = str(e)
                code = CoreError(message).get_code()
                arguments = {}
                data = ""
                
        codedt = {}
        codedt['status'] = code
        codedt['message'] = message
        codedt['arguments'] = arguments if arguments is not None else {}
        codedt['data'] = "" if data is None else data
        return codedt
            
    def to_json(self, wrapper=True):
        jsonstr = jsonutil.to_json(self.to_dict(), wrapper)
        jsonstr = base64.b64encode(jsonstr)
        return jsonstr
    
    def _get_i18n_message(self, code, arguments):
        language = conf.get_preferred_language()
        if arguments is not None:
            for key, value in arguments.items():
                if key == 'label' or 'label' in key:
                    i1key = value
                    value = i18n.get_i18n_message(language, i1key)
                    value = i1key if value is None else value
                    arguments[key] = value
        return i18n.get_i18n_message(language, code, arguments)

class BaseHandler(object):
    
    CONTENT_TYPE_FORM = "application/x-www-form-urlencoded"
    CONTENT_TYPE_PAYLOAD = "application/json"
    
    def GET(self):
        """To be implemented by sub-class"""
        raise NotImplementedError()
    
    def POST(self):
        """To be implemented by sub-class"""
        raise NotImplementedError()
    
    def _is_form_request(self):
        ct = self._get_content_type()
        return self.CONTENT_TYPE_FORM in ct
    
    def _is_payload_request(self):
        ct = self._get_content_type()
        return self.CONTENT_TYPE_PAYLOAD in ct
    
    def _get_content_type(self):
        return web.ctx.env.get("CONTENT_TYPE")
    
    def _get_form_data(self):
        return web.input()
    
    def _get_json_data(self):
        data = web.data()
        data = base64.b64decode(data)
        data = jsonutil.to_dict(data)
        return data
    
    def _has_parameter(self, name):
        data = self._get_data()
        return data.has_key(name)
       
    def _get_parameter(self, name):
        data = self._get_data()
        try:
            data = data[name]
        except:
            data = None
        return data
    
    def _get_str_parameter(self, name, default=None):
        value = self._get_parameter(name)
        return default if strutil.is_empty(value) else str(value)
    
    def _get_int_parameter(self, name, default=None):
        value = self._get_str_parameter(name)
        return strutil.to_int(value, default=default)
    
    def _get_float_parameter(self, name, default=None):
        value = self._get_str_parameter(name)
        return strutil.to_float(value, default=default)
    
    def _get_bool_parameter(self, name, default=False):
        value = self._get_str_parameter(name)
        return strutil.to_bool(value, default=default)
    
    def _get_date_parameter(self, name, fmt, default=None):
        value = self._get_str_parameter(name)
        return strutil.to_date(value, fmt=fmt, default=default)
    
    def _get_datetime_parameter(self, name, fmt, default=None):
        value = self._get_str_parameter(name)
        return strutil.to_datetime(value, fmt=fmt, default=default)
    
    def _get_model_parameter(self, model_class):
        keylabel = model_class.get_property(model_class.KEYMETA[0]).get_label()
        key = self._get_str_parameter(keylabel, default=None)
        if key != None:
            model_instance = model_class.get_by_key(key)
        else:
            model_instance = model_class()
        properties = model_instance.get_properties(labelkey=True)
        for label, value in self._get_data().items():
            if properties.has_key(label):
                prop = properties[label]
                value = prop.normalize_value(value)     
                setattr(model_instance, prop.name, value)
                    
        return model_instance
    
    def _get_data(self):
        return self._get_json_data()
    
    def _new_rtn(self, data=None, e=None):
        return Rtn(self, data=data, e=e)

class BaseDispatcher(BaseHandler):
    
    def GET(self):
        return self.POST()
    
    def POST(self):
        try:
            h = self._get_str_parameter(self._get_handler_name())
            handler = self._get_handler(h)
            if handler is None:
                raise CoreError("The responding handler to %s is not defined", h)
            return handler.POST()
        except BaseException, e:
            msg = str(e)
            msg += traceback.format_exc()
            log.get_logger().error(msg)
            rtn = self._new_rtn(e=e).to_json()
            return rtn
                    
    def _get_handler(self):
        """To be override by sub-class"""
        raise NotImplementedError
    
    def _get_handler_name(self):
        return "ha"
    
class Dispatcher(BaseDispatcher):
    
    def _get_handler(self, h):
        handlers = conf.HANDLERs
        for i in range(0, len(handlers) - 1):
            if i % 2 == 0:
                key = handlers[i]
                if (h == key):
                    handler = handlers[i + 1]
                    mod, hcls = handler.rsplit('.', 1)
                    mod = __import__(mod, None, None, [''])
                    handler = getattr(mod, hcls)()
                    return handler
        return None

class Handler(BaseHandler):
    
    @classmethod
    def get_qualified_name(cls):
        return cls.__module__ + "." + cls.__name__
    
    def GET(self):
        return self.POST()
    
    def POST(self):
        rtn = None
        try:
            if session.has_token() is False:
                anonymous_user = user.login(user.ANONYMOUS_ACCOUNT_NAME, None)
                session.set_token(anonymous_user)
                
            operation = user.get_operation(handler_class=self.get_qualified_name())
            if operation is not None:
                paramnames = operation.get_resource_oql_paramnames()
                oqlparams = self._get_resource_oql_params(paramnames)
                if user.has_permission(self._get_user_id(), operation.operation_key, oqlparams=oqlparams):
                    rtn = self.execute()
                else:
                    if session.get_token().is_anonymous():
                        raise SessionExpiredError(session.get_token())
                    else:
                        raise UnauthorizedError()
            else:
                raise CoreError("%s is not related to operation." , self.get_qualified_name())
        
        except BaseException, e:
            msg = str(e)
            msg += traceback.format_exc()
            log.get_logger().error(msg)
            rtn = self._new_rtn(e=e).to_json()
        return rtn
    
    def execute(self):
        """To be override in sub class"""
        raise NotImplementedError
    
    def _get_user_id(self):
        return session.get_token().user_id
    
    def _get_resource_oql_params(self, paramnames):
        oqlparams = {}
        if len(paramnames) > 0:
            data = self._get_data()
            for paramname in paramnames:
                if hasattr(session.get_token(), paramname):
                    oqlparams[paramname] = getattr(session.get_token(), paramname)
                elif data.has_key(paramname):
                    oqlparams[paramname] = data[paramname]
                else:
                    raise UnauthorizedError()
        return oqlparams
        

class IndexHandler(Handler):
    
    def execute(self):
        path = sysprop.get_sysprop_value("INDEX_PATH", DEFAULT_INDEX_PATH)
        return web.seeother(path)

class DynamicJsHandler(Handler):
    
    def execute(self):
        web.header('Content-Type', 'application/x-javascript')
        translations = {}
        langs = conf.get_supported_languages()
        for lang in langs : 
            results = i18n.fetch_i18ns(locale=lang, return_dic=True)
            translations[lang] = results
        js = "var I18N = {"
        js += "translations : %s," % jsonutil.to_json(translations)
        js += "defaultLanguage : '%s'" % conf.get_preferred_language()
        js += "};" 
        js += "var G_VERSION='%s';" % conf.G_VERSION
        js += "var EMPTY_UID=%d;" % model.EMPTY_UID
        js += "var LOGIN_USER=%s;" % jsonutil.to_json(session.get_token().to_dict())
        
        js += conf.dynamicjs_hook()
        return js

class PreferredLanguageHandler(Handler):
    
    def execute(self):
        preferred_language = self._get_str_parameter('preferredLanguage')
        rtn = self._new_rtn()
        rtn.set_data(preferred_language)
        return rtn
        

class LoginHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        login_name = self._get_str_parameter('loginName')
        login_pwd = self._get_str_parameter('loginPwd')
        token = user.login(login_name, login_pwd)
        token = session.set_token(token)
        rtn.set_data(token.to_dict())
        return rtn.to_json()
    
class LogoutHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        session.drop_token()
        token = user.login(user.ANONYMOUS_ACCOUNT_NAME, None)
        token = session.set_token(token)
        rtn.set_data(token)
        return rtn.to_json()
    
class ChangePasswordHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        old_password = self._get_str_parameter('oldPassword')
        new_password = self._get_str_parameter('newPassword')
        dup_password = self._get_str_parameter('dupPassword')
        if new_password != dup_password:
            raise Error('core_error_password_notmatch')
        user.update_user_password(self._get_user_id(), old_password, new_password, self._get_user_id())
        rtn.set_data(True)
        return rtn.to_json()
    
class SignupHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        accountName = self._get_str_parameter('accountName')
        password = self._get_str_parameter('password')
        userEmail = self._get_str_parameter('userEmail')
        userName = self._get_str_parameter('userName')
        data = user.signup(userName, userEmail, accountName, password, False, self._get_user_id())
        rtn.set_data(data)
        return rtn.to_json()
        
        
class FileUploadHandler(Handler):
    def execute(self):
        file1 = self._get_parameter("file")
        filex = Filex()
        filex.file_name = file1.filename
        filex.file_bytes = file1.value
        filex.creator_id = self._get_user_id()
        model_name = self._get_str_parameter("modelName")
        model_key = self._get_str_parameter("modelKey")
        filex.create_file(file1.filename, file1.value, self._get_user_id(), self._get_user_id(), model_name=model_name, model_key=model_key)
        rtn = self._new_rtn()
        rtn.set_data(True)
        return rtn.to_json()
    
    def _get_data(self):
        return self._get_form_data()
    
    
class FileDeleteHandler(Handler):
    def execute(self):
        rtn = self._new_rtn()
        file_id = self._get_int_parameter('fileId')
        filex.delete_file(file_id, self._get_user_id())
        rtn.set_data(True)
        return rtn

class FileDownloadHandler(Handler):
    def execute(self):
        file_id = self._get_int_parameter('fileId')
        file1 = filex.get_file(file_id)
        web.header('Content-Type', 'application/octet-stream')
        web.header('Content-disposition', 'attachment; filename=%s' % file1.file_name)
        return file1.file_bytes

class SetupHandler(object):
    def GET(self):
        return self.POST()
    def POST(self):
        from core import migration
        migration.setup_core_tables()
        return "done"
