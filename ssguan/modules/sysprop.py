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
from ssguan import config
from ssguan.commons import dao, typeutils
from ssguan.commons.cache import dec_cached
from ssguan.commons.dao import Model, UniqueValidator
from ssguan.commons.error import ProgramError


class SysProp(Model):
    
    @classmethod
    def meta_domain(cls):
        return config.MODULE_CONFIG
    
    p_key = dao.StringProperty("propKey", required=True, validator=[UniqueValidator("p_key")])
    p_value = dao.ObjectProperty("propValue", required=True, length=255)
    p_module = dao.StringProperty("propModule", required=True, length=20)
    p_group = dao.StringProperty("propGroup", required=False, length=20)
    removed = dao.BooleanProperty("removed", required=True, default=False) 

@dec_cached()
def get_sysprop(p_key, read_by):
    from ssguan.modules import auth
    if not auth.has_permission(read_by, SysProp, auth.RoleOperation.OPERATION_READ):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_READ, SysProp.get_modelname(), p_key)
    if typeutils.str_is_empty(p_key):
        raise ProgramError("p_key can't be empty.")
    query = SysProp.all()
    query.filter("p_key =", p_key)
    return query.get()

@dec_cached()
def get_sysprop_value(p_key, read_by):
    """
        :param default|touple: the touple with two elements like (value, group)
    """
    from ssguan.modules import auth
    if not auth.has_permission(read_by, SysProp, auth.RoleOperation.OPERATION_READ):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_READ, SysProp.get_modelname(), p_key)
    if typeutils.str_is_empty(p_key):
        raise ProgramError("p_key can't be empty.")
    query = SysProp.all()
    query.filter("p_key =", p_key)
    sysprop1 = query.get()   
    value = sysprop1.p_value if sysprop1 != None else None        
    return value

@dec_cached()
def has_sysprop(p_key, read_by, removed=False):
    from ssguan.modules import auth
    if not auth.has_permission(read_by, SysProp, auth.RoleOperation.OPERATION_READ):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_READ, SysProp.get_modelname(), p_key)
    query = SysProp.all()
    query.filter("p_key =", p_key)
    if removed is not None:
        query.filter("removed =", removed)
    return query.count() > 0

def fetch_sysprops(p_module, p_group, read_by, removed=False, value_dict=False):
    from ssguan.modules import auth
    if not auth.has_permission(read_by, SysProp, auth.RoleOperation.OPERATION_READ):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_READ, SysProp.get_modelname(), "%s-%s-%s" % (p_module, p_group,str(removed)))
    query = SysProp.all()
    if p_module != None:
        query.filter("p_module =", p_module)
    if p_group != None:
        query.filter("p_group =", p_group)
    if removed is not None:
        query.filter("removed =", removed)
    query.order("p_module")
    query.order("p_group")
    sysprops = query.fetch()
    vd = {}
    for sp in sysprops:
        vd[sp.p_key] = sp.p_value
    return vd

def add_sysprop(p_key, p_value, p_module, p_group, created_by, removed=False):
    from ssguan.modules import auth
    if not auth.has_permission(created_by, SysProp, auth.RoleOperation.OPERATION_CREATE):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_CREATE, SysProp.get_modelname(), p_key)
    if typeutils.str_is_empty(p_key):
        raise ProgramError("p_key can't be empty.")
    if p_value is None:
        raise ProgramError("value can't be None.")
    sysprop = SysProp(p_key=p_key, p_value=p_value, p_module=p_module, p_group=p_group, removed=removed)
    sysprop.create(created_by)
    return sysprop

def update_sysprop(p_key, p_value, p_module, p_group, modified_by):
    from ssguan.modules import auth
    if not auth.has_permission(modified_by, SysProp, auth.RoleOperation.OPERATION_UPDATE):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_UPDATE, SysProp.get_modelname(), p_key)

    if typeutils.str_is_empty(p_key):
        raise ProgramError("p_key can't be empty.")
    if p_value is None:
        raise ProgramError("p_value can't be None.")
    query = SysProp.all()
    query.filter("p_key =", p_key)    
    query.filter("removed =", False)
    if query.count() == 0:
        raise ProgramError("the key %s of sysprop does not existed.", p_key)
    query = SysProp.all()
    query.filter("p_key =", p_key)
    query.set("p_value", p_value)
    query.set("p_module", p_module)
    query.set("p_group", p_group)
    return query.update(modified_by=modified_by)

def remove_sysprop(p_key, removed, modified_by):
    from ssguan.modules import auth
    if not auth.has_permission(modified_by, SysProp, auth.RoleOperation.OPERATION_UPDATE):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_UPDATE, SysProp.get_modelname(), p_key)
    if typeutils.str_is_empty(p_key):
        raise ProgramError("key can't be empty.")
    query = SysProp.all()
    query.filter("p_key =", p_key)
    query.set("removed", removed)
    return query.update(modified_by=modified_by)

def delete_sysprop(p_key, deleted_by):
    from ssguan.modules import auth
    if not auth.has_permission(deleted_by, SysProp, auth.RoleOperation.OPERATION_DELETE):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_DELETE, SysProp.get_modelname(), p_key)
    query = SysProp.all()
    query.filter("p_key =", p_key)
    return query.delete(deleted_by)

def remove_sysprops(p_module, p_group, removed, modified_by):
    from ssguan.modules import auth
    if not auth.has_permission(modified_by, SysProp, auth.RoleOperation.OPERATION_UPDATE):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_UPDATE, SysProp.get_modelname(), "%s-%s" % (p_module, p_group))
    if typeutils.str_is_empty(p_module):
        raise ProgramError("p_module can't be empty.")
    query = SysProp.all()
    query.filter("p_module =", p_module)
    if p_group != None:
        query.filter("p_group", p_group)
    query.set("removed", removed)
    return query.update(modified_by=modified_by)

def delete_sysprops(p_module, p_group, deleted_by):
    from ssguan.modules import auth
    if not auth.has_permission(deleted_by, SysProp, auth.RoleOperation.OPERATION_DELETE):
        raise auth.UnauthorizedError(auth.RoleOperation.OPERATION_DELETE, SysProp.get_modelname(), "%s-%s" % (p_module, p_group))
    query = SysProp.all()
    if p_module is not None:
        query.filter("p_module =", p_module)
    if p_group is not None:
        query.filter("p_group =", p_group)
    return query.delete(deleted_by)

def install_module():
    SysProp.create_schema()
    return True
    
def uninstall_module():
    SysProp.delete_schema()
    return True
