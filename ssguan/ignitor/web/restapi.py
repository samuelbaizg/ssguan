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

import copy
import os

from ssguan.ignitor.auth import service  as auth_service
from ssguan.ignitor.auth.error import UnauthorizedError
from ssguan.ignitor.auth.model import User
from ssguan.ignitor.base import context
from ssguan.ignitor.base.error import NoFoundError
from ssguan.ignitor.orm import properti
from ssguan.ignitor.base.error import RequiredError
from ssguan.ignitor.orm.model import Query
from ssguan.ignitor.utility import kind, reflect
from ssguan.ignitor.web import config as web_config
from ssguan.ignitor.web.error import WrongParamError
from ssguan.ignitor.web.handler import BaseReqHandler, Rtn


class AuthReqHandler(BaseReqHandler):
    
    SESSION_TOKEN = "SESSION_TOKEN"

    def set_current_user(self, token):
        self.session[self.SESSION_TOKEN] = token

    def get_current_user(self):
        return self.session[self.SESSION_TOKEN] if self.SESSION_TOKEN in self.session else None

    def delete_current_user(self):
        del self.session[self.SESSION_TOKEN]

    def prepare(self):
        BaseReqHandler.prepare(self)
        if self.get_current_user() is None:
            anonymous_token = auth_service.login(
                User.ACCOUNT_NAME_ANONYMOUS, None, is_anonymous=True)
            self.set_current_user(anonymous_token)
        context.set_token(self.get_current_user())
    
    def _assert_permission(self, operation_code):
        has = operation_code in self.get_current_user().operation_codes
        if not has:
            raise UnauthorizedError(operation_code)

class FuncReqHandler(AuthReqHandler):   
    
    def get(self, *args, **kwargs):
        """
            handle GET request and parse parameters from query string.
        """
        params = self.decode_arguments_query()
        self._do(**params)
         
 
    def post(self, *args, **kwargs):
        """
            handle POST request and parse parameters from body.
        """
        params = self.decode_arguments_body()
        self._do(**params)
         
     
    def put(self, *args, **kwargs):
        """
            handle PUT request and parse parameters from body.
        """
        params = self.decode_arguments_body()
        self._do(**params)
     
    def delete(self, *args, **kwargs):
        """
            handle DELETE request and parse parameters from query string.
        """
        params = self.decode_arguments_query()
        self._do(**params)

    def _do(self, **params):
        """
            handle the request
        """
        funcapi = self._get_func_api()
        self._assert_permission(funcapi['operation'])
        func = eval("self._do_%s" % funcapi.functype, globals(), locals())
        rtn_value = func(funcapi, **params)
        rtn = Rtn(content_type=funcapi['content-type'], data=rtn_value)
        rtn.write(self)

    def _get_func_api(self):
        """
            find restapi config by self.request.path
        """
        prefix = os.path.join(web_config.get_restSetting().web_ctx, web_config.get_restSetting().func_api_route)
        prefix = '/' + prefix + '/' if not prefix.startswith('/') else prefix + '/'
        route = self.request.path.replace(prefix, '')
        func_apis = web_config.get_func_apis()
        if route in func_apis:
            return func_apis[route]
        else:
            raise NoFoundError("function service", route)
            
    def _do_generic(self, funcapi, **params):
        """
            call the genenic function
            :param restapi|json: one item defined in restapi.json
            :return: return json-friendly object if restapi.content-type is application/json.                    
                    return string if restapi.content-type is text/html,text/plain,text/xml etc.
                    return file absolute path if restapi.content-type is application/octet-stream, application/pdf,application/xml, image/* etc.
        """
        def parse_arg_values(arg_names, defaults, kwargs_copy):
            karg_names = None
            default_values = {}
            # Distinguish the arguments and the arguments with default values 
            if defaults is not None:
                karg_names = []
                i = len(defaults)
                j = len(arg_names)
                while (i > 0):
                    arg_name = arg_names[j - 1]        
                    karg_names.append(arg_name)
                    default_values[arg_name] = defaults[i - 1]
                    arg_names.pop(j - 1)                
                    i -= 1
                    j -= 1
            # set values for arguments without key
            arg_values = None
            if arg_names is not None:
                arg_values = []
                for arg_name in arg_names:
                    if arg_name in kwargs_copy:
                        arg_value = kwargs_copy[arg_name]
                        kwargs_copy.pop(arg_name)                
                    else:
                        arg_value = None
                    arg_values.append(arg_value)
            # set values for arguments with key
            karg_values = None
            if karg_names is not None:
                karg_values = {}
                for arg_name in karg_names:
                    if arg_name in kwargs_copy:
                        karg_values[arg_name] = kwargs_copy[arg_name]
                        kwargs_copy.pop(arg_name)
                    else:
                        karg_values[arg_name] = default_values[arg_name]
            return (arg_values, karg_values)
        
        def call_func(arg_values, karg_values, keywords, kwargs_copy):
            rtn_value = None
            if arg_values is not None:
                if karg_values is not None:
                    if keywords is not None:
                        karg_values.update(**kwargs_copy)
                        rtn_value = funcapi.function(*arg_values, **karg_values)
                    else:
                        rtn_value = funcapi.function(*arg_values, **karg_values)
                else:
                    if keywords is not None:
                        rtn_value = funcapi.function(*arg_values, **kwargs_copy)
                    else:
                        rtn_value = funcapi.function(*arg_values)
            else:
                if karg_values is not None:
                    if keywords is not None:
                        karg_values.update(**kwargs_copy)
                        rtn_value = funcapi.function(**karg_values)
                    else:
                        rtn_value = funcapi.function(**karg_values)
                else:
                    if keywords is not None:
                        rtn_value = funcapi.function(**kwargs_copy)
                    else:
                        rtn_value = funcapi.function()
            return rtn_value
        kwargs_copy = copy.deepcopy(params)
        arg_spec = reflect.get_function_args(funcapi.function)
        (arg_values, karg_values) = parse_arg_values(arg_spec[0], arg_spec[3], kwargs_copy)
        return call_func(arg_values, karg_values, arg_spec[2], kwargs_copy)
            
    def _do_create(self, funcapi, **params):
        """
            call the create model api.
        """
        def create_model(model, creator_id):
            model = model.create(creator_id, key=model.key())            
            return model
        model_class = funcapi.function
        model = model_class()
        settled = self._set_model_props(model, params)
        if settled:
            if "key" in params:
                setattr(model, model.DEFAULT_KEYNAME, params['key'])
            model = create_model(model, self.get_current_user().user_id)
        else:
            raise WrongParamError(self.request.uri, "create:model")
        return model
    
    def _do_update(self, funcapi, **params):
        """
            call the update model api.
        """
        def update_model(model, modifier):
            if kind.str_is_empty(model.key()):
                raise RequiredError("model key is required. - %s" % model.get_modelname())
            model = model.update(modifier)
            if model is None:
                raise NoFoundError(model, model.key())
            return model
        model_class = funcapi.function
        if "key" in params:
            model = self._get_model_by_key(model_class, params['key'])
            settled = self._set_model_props(model, params)
            if settled:
                model = update_model(model, self.get_current_user().user_id)
            else:
                raise WrongParamError(self.request.uri, "put")
            return model
        else:
            raise WrongParamError(self.request.uri, "update:model")
        
    def _do_delete(self, funcapi, **params):
        """
            call the delete model api.
        """
        def delete_model(model_class, model_key, deleted_by):
            if kind.str_is_empty(model_key):
                raise RequiredError("model key is required.%s" % model_class.get_modelname())
            model = model_class.get_by_key(model_key)
            if model is None:
                raise NoFoundError(model_class, model_key)
            model.delete(deleted_by)
            return True
        model_class = funcapi.function
        if "key" in params:
            return delete_model(model_class, params['key'], self.get_current_user().user_id)
        elif "keys" in params:
            keys = params["keys"]
            for key in keys:
                delete_model(model_class, key, self.get_current_user().user_id)
            return True
        else:
            raise WrongParamError(self.request.uri, "delete:model")
        
    def _do_get(self, funcapi, **params):
        """
            call the get model api.
        """
        model_class = funcapi.function
        if 'key' in params:
            model = self._get_model_by_key(model_class, params['key'])
            return model
        else:
            raise WrongParamError(self.request.uri, "get:model")
    
    def _do_fetch(self, funcapi, **params):
        """
            call the fetch model api.
        """
        def parse_filters(model_class, filters):
            """
                filters is the arguments of Query.filter_x but propertyOp is label name instead of property name 
            """
            properties = model_class.get_properties(persistent=True)
            filters_p = []
            invalid_filters = []
            invalid_props = []
            if type(filters) == dict:
                filters = [filters]
            for filter_dic in filters:
                if  "propertyOp" in filter_dic and "value" in filter_dic:
                    pop = filter_dic["propertyOp"]
                    poplist = pop.split(" ")
                    if len(poplist) == 0:
                        invalid_props.append(pop)
                    else:
                        pname = poplist[0]
                        poperator = poplist[1]
                        if not pname in properties:
                            invalid_props.append(pop)
                        else:
                            del filter_dic["propertyOp"]
                            filter_dic[u"property_op"] = "%s %s" % (pname, poperator)
                            filters_p.append(filter_dic)
                else:
                    invalid_filters.append(filter_dic)
            if len(invalid_filters) > 0 or len(invalid_props) > 0:
                raise WrongParamError(self.request.uri, "fetch:models")
            return filters_p
        
        def parse_whats(model_class, whats):
            whats_p = []
            invalid_props = []
            properties = model_class.get_properties(persistent=True)
            if type(whats) == str:
                whats = []
            for what in whats:
                if not what in properties:
                    invalid_props.append(what)
                else:        
                    whats_p.append((what, what))
            if len(invalid_props) > 0:
                raise WrongParamError(self.request.uri, 'fetch:models')
            return whats_p
        
        def parse_orders(model_class, orders):
            orders_p = []
            invalid_props = []
            properties = model_class.get_properties(persistent=True)
            if type(orders) == str:
                orders = [orders]
            for order in orders:
                if order[0:1] == '-':                
                    prefix = "-"
                    order = order[1:]
                else:
                    prefix = ""
                if not order in properties:
                    invalid_props.append(order)
                else:
                    orders_p.append(prefix + order)
            if len(invalid_props) > 0:
                raise WrongParamError(self.request.uri, 'fetch:models')
            return orders_p
        model_class = funcapi.function
            
        if "filters" in params:
            filters = parse_filters(model_class, params['filters'])
            parenthesis_left = params['parenthesisLeft'] if "parenthesisLeft" in params else None
            parenthesis_right = params['parenthesisRight'] if "parenthesisRight" in params else None
            whats = parse_whats(model_class, params['whats']) if "whats" in params else []
            orders = parse_orders(model_class, params["orders"]) if "orders" in params else []
            limit = kind.str_to_int(params['limit']) if "limit" in params else Query.DEFAULT_FETCH_LIMIT
            offset = kind.str_to_int(params['offset']) if "offset" in params else 0
            paging = kind.str_to_bool(params['paging'], False) if "paging" in params else False
            query = model_class.all()
            query.filter_x(filters, parenthesis_left=parenthesis_left, parenthesis_right=parenthesis_right, logic="and")
            for (name, alias) in whats:
                query.what(name, alias)
            for order in orders:
                query.order(order)
            models = query.fetch(limit=limit, offset=offset, paging=paging)
            return models
        else:
            raise WrongParamError(self.request.uri, "fetch:models")
    
    def _get_model_by_key(self, model_class, model_key):
        if kind.str_is_empty(model_key):
            raise RequiredError("model key is required.%s" % model_class.get_modelname())
        model = model_class.get_by_key(model_key)
        if model is None:
            raise NoFoundError(model_class, model_key)
        return model

    def _set_model_props(self, model, kwargs):
        """
            Set property value for model.
            :param kwargs|dict:
            :rtype bool: return True if any property is set or else return False 
        """        
        properties = model.get_properties(persistent=True, excluded=True)
        b = False
        for (key, prop) in properties.items():
            if key in kwargs and key != 'key':
                if isinstance(prop, properti.DateTimeProperty):
                    fmt = kwargs[key + "FMT"] if key + "FMT" in kwargs else "%Y-%m-%d %H:%M"
                    value = kind.str_to_datetime(kwargs[key], fmt , None)
                elif isinstance(prop, properti.DateProperty):
                    fmt = kwargs[key + "FMT"] if key + "FMT" in kwargs else "%Y-%m-%d"
                    value = kind.str_to_datetime(kwargs[key], fmt , None)
                else:
                    value = prop.normalize_value(kwargs[key])                
                setattr(model, prop.name, value)
                b = True
        return b
