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
""" moado: model access data object """

import os

from ssguan import config
from ssguan.commons import loggingg, dao, typeutils
from ssguan.commons.dao import RequiredError, Query
from ssguan.commons.error import NoFoundError
from ssguan.commons.webb import dec_rtn, WrongParamError
from ssguan.modules import auth
from ssguan.modules.auth import RoleOperation, UnauthorizedError, AuthReqHandler


_logger = loggingg.get_logger(config.MODULE_ENTITY)

def create_model(model, created_by, mocallback=None):
        if not auth.has_permission(created_by, model , RoleOperation.OPERATION_CREATE):
            raise UnauthorizedError(RoleOperation.OPERATION_CREATE, model.get_modelname(), "")
        model = model.create(created_by, key=model.key())
        if mocallback is not None:
            mocallback(model)
        return model
        
def update_model(model, modified_by, mocallback=None):
    if typeutils.str_is_empty(model.key()):
        raise RequiredError("model key is required. - %s" % model.get_modelname())
    if not auth.has_permission(modified_by, model , RoleOperation.OPERATION_UPDATE, model_id=model.key()):
        raise UnauthorizedError(RoleOperation.OPERATION_UPDATE, model.get_modelname(), model.key())
    model = model.update(modified_by)
    if model is None:
        raise NoFoundError(model, model.key())
    if mocallback is not None:
        mocallback(model)
    return model

def delete_model(model_class, model_key, deleted_by, mocallback=None):
    if typeutils.str_is_empty(model_key):
        raise RequiredError("model key is required.%s" % model_class.get_modelname())
    if not auth.has_permission(deleted_by, model_class , RoleOperation.OPERATION_DELETE, model_id=model_key):
        raise UnauthorizedError(RoleOperation.OPERATION_DELETE, model_class.get_modelname(), model_key)
    model = model_class.get_by_key(model_key)
    if model is None:
        raise NoFoundError(model_class, model_key)
    model.delete(deleted_by)
    if mocallback is not None:
        mocallback(model)
    return True

def get_model_by_key(model_class, model_key, read_by, mocallback=None):
    if typeutils.str_is_empty(model_key):
        raise RequiredError("model key is required.%s" % model_class.get_modelname())
    if not auth.has_permission(read_by, model_class , RoleOperation.OPERATION_READ, model_id=model_key):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, model_class.get_modelname(), model_key)
    model = model_class.get_by_key(model_key)
    if model is None:
        raise NoFoundError(model_class, model_key)
    if mocallback != None:
        mocallback(model)
    return model

def has_model_by_key(model_class, model_key, read_by):
    if typeutils.str_is_empty(model_key):
        raise RequiredError("model key is required.%s" % model_class.get_modelname())
    if not auth.has_permission(read_by, model_class , RoleOperation.OPERATION_READ, model_id=model_key):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, model_class.get_modelname(), model_key)
    query = model_class.all()
    query.filter("_id =", model_key)
    return query.count() > 0


def fetch_models(model_class, filters, read_by, whats=[], orders=[], rivars={}, limit=Query.DEFAULT_FETCH_LIMIT, offset=0, paging=False, mocallback=None, parenthesis_left=None, parenthesis_right=None):
    """
        user_id, model_class, rivars are the arguments of method gen_queryfilters_of_allowed_resources
        filters, parenthesis_left,parenthesis_right and logic  are the arguments of Query.filter_x
        limit, offset, paging and mocallback are the arguments of Query.fetch
        whats is the list with tuple lick (name, alias)
        rivars is the arguments for ResourceItem.eval_resitem_value
    """
    
    query = auth.gen_query_of_allowed_resources(read_by, model_class, RoleOperation.OPERATION_READ, **rivars)
    if query is None:
        return [] if paging is False else typeutils.gen_empty_pager()
    else:       
        query.filter_x(filters, parenthesis_left=parenthesis_left, parenthesis_right=parenthesis_right, logic="and")
        for (name, alias) in whats:
            query.what(name, alias)
        for order in orders:
            query.order(order)
        return query.fetch(limit=limit, offset=offset, paging=paging, mocallback=mocallback)

class ModelHandler(AuthReqHandler):
    
    def prepare(self):
        AuthReqHandler.prepare(self)
        modelname, get_args = self.decode_arguments_uri()
        self._model_class = self._get_model_class(modelname)        
        body_args = self.decode_arguments_body()
        self._body_args = body_args
        self._get_args = get_args
        
    @dec_rtn
    def get(self, *args, **kwargs):
        """
            Get or Fetch models by criteria and criteria parameters are as below,
                key: the argument of entity.get_model_by_key
                filters: the argument of entity.fetch_models
                parenthesisLeft: the argument of entity.fetch_models
                parenthesisRight: the argument of entity.fetch_models
                whats: the argument of entity.fetch_models
                orders: the argument of entity.fetch_models
                rivars: the argument of entity.fetch_models
                limit: the argument of entity.fetch_models
                offset: the argument of entity.fetch_models
                paging: the argument of entity.fetch_models
            if both key and filters are in parameters, filters and other parameters will be ignored.
        """
        
        def _parse_filters(model_class, filters):
            """
                filters is the arguments of Query.filter_x but propertyOp is label name instead of property name 
            """
            properties = model_class.get_properties(persistent=True, labelkey=True)
            filters_p = []
            invalid_filters = []
            invalid_props = []
            if type(filters) == dict:
                filters = [filters]
            for filter_dic in filters:
                if  filter_dic.has_key("propertyOp") and filter_dic.has_key("value"):
                    pop = filter_dic["propertyOp"]
                    poplist = pop.split(" ")
                    if len(poplist) == 0:
                        invalid_props.append(pop)
                    else:
                        plabel = poplist[0]
                        poperator = poplist[1]
                        if not properties.has_key(plabel):
                            invalid_props.append(pop)
                        else:
                            pname = properties[plabel].name
                            del filter_dic["propertyOp"]
                            filter_dic[u"property_op"] = "%s %s" % (pname, poperator)
                            filters_p.append(filter_dic)
                else:
                    invalid_filters.append(filter_dic)
            if len(invalid_filters) > 0 or len(invalid_props) > 0:
                raise WrongParamError(self.request.uri, "get")
            return filters_p
        
        def _parse_whats(model_class, whats):
            whats_p = []
            invalid_props = []
            properties = model_class.get_properties(persistent=True, labelkey=True)
            if type(whats) in (str, unicode):
                whats = []
            for what in whats:
                if not properties.has_key(what):
                    invalid_props.append(what)
                else:
                    pname = properties[what].name
                    whats_p.append((pname, pname))
            if len(invalid_props) > 0:
                raise WrongParamError(self.request.uri, 'get')
            return whats_p
        
        def _parse_orders(model_class, orders):
            orders_p = []
            invalid_props = []
            properties = model_class.get_properties(persistent=True, labelkey=True)
            if type(orders) in (str, unicode):
                orders = [orders]
            for order in orders:
                if order[0:1] == '-':                
                    prefix = "-"
                    order = order[1:]
                else:
                    prefix = ""
                if not properties.has_key(order):
                    invalid_props.append(order)
                else:
                    pname = properties[order].name
                    orders_p.append(prefix + pname)
            if len(invalid_props) > 0:
                raise WrongParamError(self.request.uri, 'get')
            return orders_p
        
        model_class = self._model_class
        body = self._get_args
        if "key" in body:
            model = get_model_by_key(model_class, body['key'], self.get_current_user().user_id, mocallback=None)
            return model
        elif "filters" in body:
            filters = _parse_filters(model_class, body['filters'])
            parenthesis_left = body['parenthesisLeft'] if "parenthesisLeft" in body else None
            parenthesis_right = body['parenthesisRight'] if "parenthesisRight" in body else None
            whats = _parse_whats(model_class, body['whats']) if "whats" in body else []
            orders = _parse_orders(model_class, body["orders"]) if "orders" in body else []
            rivars = typeutils.json_to_object(body['rivars']) if "rivars" in body else {}
            limit = typeutils.str_to_int(body['limit']) if "limit" in body else Query.DEFAULT_FETCH_LIMIT
            offset = typeutils.str_to_int(body['offset']) if "offset" in body else 0
            paging = typeutils.str_to_bool(body['paging'], False) if "paging" in body else False
            models = fetch_models(model_class, filters, self.get_current_user().user_id, whats=whats, orders=orders, rivars=rivars, limit=limit, offset=offset, paging=paging, mocallback=None, parenthesis_left=parenthesis_left, parenthesis_right=parenthesis_right)
            return models
        else:
            raise WrongParamError(self.request.uri, "get")
            
    @dec_rtn
    def post(self, *args, **kwargs):
        """
            Create a new Model and the parameters are value of each property in Model but the parameter key is property label instead of property name.
        """
        
        model_class = self._model_class
        body = self._body_args
        model = model_class()
        properties = model_class.get_properties(persistent=True, labelkey=True, excluded=True)
        wrong = True
        for (key, prop) in properties.items():
            if key in body and key != 'key':
                if isinstance(prop, dao.DateTimeProperty):
                    fmt = body[key + "FMT"] if key + "FMT" in body else "%Y-%m-%d %H:%M"
                    value = typeutils.str_to_datetime(body[key], fmt , None)
                elif isinstance(prop, dao.DateProperty):
                    fmt = body[key + "FMT"] if key + "FMT" in body else "%Y-%m-%d"
                    value = typeutils.str_to_datetime(body[key], fmt , None)
                else:
                    value = prop.normalize_value(body[key])                
                setattr(model, prop.name, value)
                wrong = False
        if wrong is False:
            if "key" in body:
                setattr(model, model.DEFAULT_KEYNAME, body['key'])
            model = create_model(model, self.get_current_user().user_id, mocallback=None)
        else:
            raise WrongParamError(self.request.uri, "post")
        return model
        
    @dec_rtn
    def put(self, *args, **kwargs):
        """
            update a  Model with key.
            The parameters are value of each property in Model but the parameter key is property label instead of property name.
        """
        
        model_class = self._model_class
        body = self._body_args
        if "key" in body:
            model = get_model_by_key(model_class, body["key"], self.get_current_user().user_id)
            if model is not None:
                properties = model_class.get_properties(persistent=True, labelkey=True, excluded=True)
                for (key, prop) in properties.items():
                    if key in body and key != 'key':
                        if isinstance(prop, dao.DateTimeProperty):
                            fmt = body[key + "FMT"] if key + "FMT" in body else "%Y-%m-%d %H:%M"
                            value = typeutils.str_to_datetime(body[key], fmt , None)
                        elif isinstance(prop, dao.DateProperty):
                            fmt = body[key + "FMT"] if key + "FMT" in body else "%Y-%m-%d"
                            value = typeutils.str_to_datetime(body[key], fmt , None)
                        else:
                            value = prop.normalize_value(body[key])                
                        setattr(model, prop.name, value)
                return update_model(model, self.get_current_user().user_id, mocallback=None)
            else:
                raise NoFoundError(model_class, body["key"])            
        else:
            raise WrongParamError(self.request.uri, "put")
    
    @dec_rtn
    def delete(self, *args, **kwargs):
        """
            Delete a Model by key or multiple keys and criteria parameters are as below,
            key: the argument of entity.delete_model_by_key
            keys: [] with key and key is the argument of entity.delete_model_by_key
            if both key and keys are in parameters, keys will be ignored.
            
        """
        model_class = self._model_class
        body = self._get_args
        if "key" in body:
            return delete_model(model_class, body['key'], self.get_current_user().user_id, mocallback=None)
        elif "keys" in body:
            keys = body["keys"]
            for key in keys:
                delete_model(model_class, key, self.get_current_user().user_id, mocallback=None)
            return True
        else:
            raise WrongParamError(self.request.uri, "delete")
    
    def _get_model_class(self, modelname):
        model = os.path.basename(modelname)
        model_class = config.webbCFG.get_model(model)
        if model_class is None:
            raise NoFoundError("Web Alias Model", modelname)
        else:
            return model_class
        
def uninstall_module():
    config.webbCFG.delete_handler("/mod/[^/]+")
    return True

def install_module():
    config.webbCFG.add_handler("/mod/[^/]+", "ssguan.modules.entity.ModelHandler")
    return True
