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

import os

from ssguan.ignitor.base.error import NoFoundError, NoSupportError, InvalidError
from ssguan.ignitor.base.struct import Storage
from ssguan.ignitor.utility import io, kind, reflect


__web_setting = Storage()
__sessionConfig = None
__handlers = []
__restSetting = None
__func_apis = Storage()

__SECTION_SESSION = "session"
__SECTION_SETTING = "setting"
__SECTION_HANDLER = "handler"
__SECTION_RESTAPI = "restapi"

__OPTION_DEFAULT_HANDLER_CLASS = "default_handler_class"
__OPTION_STATIC_HANDLER_CLASS = "static_handler_class"
__OPTION_STATIC_PATH = "static_path"

VALID_API_FUNCTYPES = ('create', 'update', 'get', 'fetch', 'delete', 'generic')

API_FUNCTYPE_GENERIC = 'generic'

class SessionConfig:
    
    SC_COOKIE_NAME = 'cookie_name'
    SC_COOKIE_DOMAIN = 'cookie_domain'
    SC_COOKIE_PATH = 'cookie_path'
    SC_COOKIE_EXPIRES_DAYS = 'cookie_expires_days' 
    SC_TIMEOUT = 'timeout'
    SC_IGNORE_CHANGE_IP = 'ignore_change_ip' 
    SC_SECRET_KEY = 'secret_key'
    
    def __init__(self, **kwargs):
        self.__cookie_name = kwargs[self.SC_COOKIE_NAME]
        self.__cookie_domain = kwargs[self.SC_COOKIE_DOMAIN]
        self.__cookie_path = kwargs[self.SC_COOKIE_PATH]
        self.__cookie_expires_days = kind.str_to_int(kwargs[self.SC_COOKIE_EXPIRES_DAYS])
        self.__timeout = kind.str_to_int(kwargs[self.SC_TIMEOUT])
        self.__ignore_change_ip = kwargs[self.SC_IGNORE_CHANGE_IP]
        self.__secret_key = kwargs[self.SC_SECRET_KEY]
    
    @property
    def cookie_name(self):
        return self.__cookie_name
    
    @property
    def cookie_domain(self):
        return self.__cookie_domain
    
    @property
    def cookie_path(self):
        return self.__cookie_path
    
    @property
    def cookie_expires_days(self):
        return self.__cookie_expires_days
    
    @property
    def timeout(self):
        return self.__timeout
    
    @property
    def ignore_change_ip(self):
        return self.__ignore_change_ip
    
    @property
    def secret_key(self):
        return self.__secret_key

class RestSetting:
    
    RAC_WEB_CTX = 'web_ctx'
    RAC_FUNC_API_ROUTE = 'func_api_route'
    RAC_SCAN_DIR = 'scan_dir'
    RAC_SCAN_FILENAME = 'scan_filename'
    
    def __init__(self, **kwargs):
        self.__web_ctx = kwargs[self.RAC_WEB_CTX]
        self.__func_api_route = kwargs[self.RAC_FUNC_API_ROUTE]
        self.__scan_dir = kwargs[self.RAC_SCAN_DIR]
        self.__scan_filename = kwargs[self.RAC_SCAN_FILENAME]
        if not os.path.isabs(self.__scan_dir):
            self.__scan_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', self.__scan_dir)
        else:    
            if not os.path.exists(self.__scan_dir):
                self.__scan_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..')
            
    
    @property
    def web_ctx(self):
        return self.__web_ctx
    
    @property
    def func_api_route(self):
        return self.__func_api_route
    
    @property
    def scan_dir(self):
        return self.__scan_dir
    
    @property
    def scan_filename(self):
        return self.__scan_filename
    
def file_config(filepath, defaults=None):
    parser = io.get_configparser(filepath, defaults=defaults)
    global __web_setting, __sessionConfig, __handlers, __restSetting, __func_apis
    __web_setting.update(__parse_web_setting(parser))
    __sessionConfig = SessionConfig(**__parse_session_config(parser))
    __handlers.extend(__parse_handlers(parser))
    __restSetting = RestSetting(**__parse_rest_setting(parser))
    func_apis = __parse_restapi_configs(__restSetting)
    __func_apis.update(**func_apis)
    

def get_settings():
    return __web_setting

def get_sessionConfig():
    return __sessionConfig

def get_handlers():
    return __handlers

def get_restSetting():
    return __restSetting

def get_func_apis():
    return __func_apis

def get_model_apis():
    return __func_apis

def __parse_web_setting(parser):
    cfg = {}
    for (key, value) in parser.items(__SECTION_SETTING):
        cfg[key] = value
    notfound_hc = reflect.import_module(cfg[__OPTION_DEFAULT_HANDLER_CLASS])
    if notfound_hc is None:
        raise NoFoundError("NotFoundHandlerClass", cfg[__OPTION_DEFAULT_HANDLER_CLASS])
    static_hc = reflect.import_module(cfg[__OPTION_STATIC_HANDLER_CLASS])
    if static_hc is None:
        raise NoFoundError("StaticHandlerClass", cfg[__OPTION_STATIC_HANDLER_CLASS])
    static_path = os.path.join(os.path.dirname(__file__), "..", "..", cfg[__OPTION_STATIC_PATH])
    if not os.path.exists(static_path):
        raise NoFoundError("StaticPath", static_path)
    cfg[__OPTION_DEFAULT_HANDLER_CLASS] = notfound_hc
    cfg[__OPTION_STATIC_HANDLER_CLASS] = static_hc
    cfg[__OPTION_STATIC_PATH] = static_path
    return cfg

def __parse_session_config(parser):
    cfg = {}
    for (key, value) in parser.items(__SECTION_SESSION):
        cfg[key] = value
    return cfg

def __parse_handlers(parser):
    hcs = []
    for (key, value) in parser.items(__SECTION_HANDLER):
        handlerc = reflect.import_module(value)
        if handlerc is None:
            raise NoFoundError("WebHandlerClass", value)
        else:
            hcs.append((r'' + key, handlerc))
    return hcs

def __parse_rest_setting(parser): 
    cfg = {}
    for (key, value) in parser.items(__SECTION_RESTAPI):
        cfg[key] = value
    return cfg

def __parse_restapi_configs(restSetting):
    func_apis = {}
    def parse_func_apis(funcapicfg):
        for key, value in funcapicfg.items():
            if key in func_apis:
                raise InvalidError("function path %s" % key, " it has been configured.")
            else:
                vo = Storage()
                for k, v in value.items():
                    vo[k] = v
                if ":" not in vo.function:
                    vo.function = '%s:%s' % (API_FUNCTYPE_GENERIC, vo.function)
               
                func = vo.function.split(":")
                if func[0] not in VALID_API_FUNCTYPES:
                    raise NoSupportError('function', func[0])
                vo.functype = func[0]
                vo.function = reflect.import_module(func[1])
                if vo.function is None:
                    raise NoFoundError("service" , func[1])
                if vo.functype == API_FUNCTYPE_GENERIC :
                    if reflect.get_function_args(vo.function)[1] is not None:  # does not support the function with * arguments.
                        raise NoSupportError("service" , value['function'])
                else:
                    from ssguan.ignitor.orm.model import PropertiedClass
                    if type(vo.function) != PropertiedClass:  # only support subclass of orm.model.BaseModel.
                        raise NoSupportError("model" , value['function'])
                func_apis[key] = vo    
    filepaths = io.discover_files(restSetting.scan_dir, restSetting.scan_filename)
    jsons = []
    for fp in filepaths:
        jsonstr = io.read_file(fp) 
        json = kind.json_to_object(jsonstr)
        jsons.append(json)
    for json in jsons:
        funcapicfg = json
        parse_func_apis(funcapicfg)
    return func_apis 
