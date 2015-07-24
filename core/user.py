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

import md5
import base64

import conf
from core import  cache, model, cryptoutil
from core import strutil, dtutil,session
from core.error import Error, CoreError, LoginFailedError, UnauthorizedError, \
    LengthError
from core.model import stdModel
from core.session import Token
from model import User, UserProp, Role, Operation, RoleOperation, UserRole


ANONYMOUS_ACCOUNT_NAME = User.ANONYMOUS_ACCOUNT_NAME

CACHESPACE_USERNAME = "username"
CACHESPACE_PERMISSION = "permission"

def decrypt_password(password):
    password = base64.b64decode(password)
    return cryptoutil.rsa_decrypt(password, session.get_token().rsa_key)

def encrypt_password(password):
    if strutil.is_empty(password):
        return password
    pwd = md5.new()
    pwd.update(password)
    password = pwd.hexdigest()
    return password

def create_user(u_name, u_email, u_account, u_password, is_disabled, modifier_id):
    length = conf.get_useraccount_length()
    length = map(int, length)
    if (len(u_account) < length[0] or len(u_account) > length[1]):
        raise LengthError("core_label_accountname", length[0], length[1])
    length = conf.get_userpassword_length()
    length = map(int, length)
    if (len(u_password) < length[0] or len(u_password) > length[1]):
        raise LengthError("core_label_userpassword", length[0], length[1])
    user = User()
    user.u_name = u_name
    user.u_email = u_email
    user.u_account = u_account
    user.u_password = encrypt_password(u_password)
    user.is_disabled = is_disabled
    user.put(modifier_id)
    return user

def update_user(user_id, u_name, u_email, u_account, is_disabled, modifier_id):
    user = User()
    user.u_name = u_name
    user.u_email = u_email
    user.u_account = u_account
    user.modified_time = dtutil.utcnow()
    user.is_disabled = is_disabled
    user.put(modifier_id)
    return user

def update_user_password(user_id, old_password, new_password, modifier_id, verified=True):
    user = User.get_by_key(user_id)
    if verified and user.u_password != encrypt_password(old_password):
        raise Error("core_error_oldpassword_incorrect")
    else:
        length = conf.get_userpassword_length()
        if (len(new_password) < length[0] or len(new_password) > length[1]):
            raise LengthError("core_label_userpassword", length[0], length[1])
        
        user.u_password = encrypt_password(new_password)
    
    user.put(modifier_id)
    return user

def update_user_logined_info(user_id, modifier_id):
    user = User.get_by_key(user_id)
    user.last_logined_time = dtutil.utcnow()
    user.logined_times += 1
    user.modified_time = dtutil.utcnow()
    user.put(modifier_id)

def get_user_display_name(user_id):
    user_name = cache.get(CACHESPACE_USERNAME, user_id)
    if user_name != None:
        return user_name
    else:
        user = get_user(user_id=user_id)
        user_name = ""
        if user != None:
            user_name = user.u_account if strutil.is_empty(user.u_name) else user.u_name
        cache.put(CACHESPACE_USERNAME, user_id, user_name)
        return user_name

def get_user(user_id=None, u_account=None):
    user = None
    if user_id != None and user_id != model.EMPTY_UID and user_id != model.SYSTEM_UID:
        user = User.get_by_key(int(user_id))
    elif u_account != None:
        query = User.all()
        query.filter("u_account =", u_account)
        if query.count() > 0:
            user = query.get()
    if user != None:
        _attach_userprops(user)
    return user
    
def login(login_name, login_password):
    if login_name == ANONYMOUS_ACCOUNT_NAME:
        usermodel = get_user(u_account=login_name)
    else:
        try:
            login_name = decrypt_password(login_name)
            login_password = decrypt_password(login_password)
        except:
            raise LoginFailedError()
        query = User.all()
        query.filter("u_account =", login_name, parenthesis="(")
        query.filter("u_email =", login_name, logic="or", parenthesis=")")
        password = encrypt_password(login_password)
        query.filter("u_password =", password)
        if query.count() > 0:
            usermodel = query.fetch(1)[0]
            _attach_userprops(usermodel)
        else:
            raise LoginFailedError()
    usermodel.logined_times += 1
    update_user_logined_info(usermodel.key(), usermodel.key())
    token = Token(usermodel.uid, anonymous=usermodel.u_account == ANONYMOUS_ACCOUNT_NAME)
    token.userName = usermodel.u_name
    token.accountName = usermodel.u_account
    return token

def signup(u_name, u_email, u_account, u_password, is_disabled, modifier_id):
    
    
    usermodel = create_user(u_name, u_email, u_account, u_password, is_disabled, modifier_id)
    role = get_role(role_name="Anonymous")
    create_userrole(usermodel.key(), role.key(), modifier_id)
    role = get_role(role_name="Ordinary User")
    create_userrole(usermodel.key(), role.key(), modifier_id)
    return usermodel
    

def create_userprop(p_key, p_value, user_id, modifier_id):
    
    if strutil.is_empty(p_key):
        raise CoreError("user prop key can't be empty.")
    query = UserProp.all()
    query.filter("p_key =", p_key)
    query.filter("user_id =", user_id)
    if query.count() > 0:
        raise CoreError("the prop key %s of the user %d has existed." % (p_key, user_id))
    userprop = UserProp()
    userprop.p_key = p_key
    p_value = strutil.to_str(p_value)
    userprop.p_value = p_value
    userprop.user_id = user_id
    userprop.create(modifier_id)
    return userprop

def update_userprop(p_key, p_value, user_id, modifier_id):
    if strutil.is_empty(p_key):
        raise CoreError("the prop key can't be empty.")
    query = UserProp.all()
    query.filter("p_key =", p_key)
    query.filter("user_id =", user_id)
    if get_userprop(p_key, user_id) == None:
        raise CoreError("the prop key %s of user %d doesn't exist." % (p_key, user_id))
    else:
        userprop = query.get()
        userprop.p_key = p_key
        p_value = strutil.to_str(p_value)
        userprop.p_value = p_value
        userprop.update(modifier_id)

def get_userprop(p_key, user_id):
    if strutil.is_empty(p_key):
        raise CoreError("prop key %s of user %d can't be empty." % (p_key, user_id))
    query = UserProp.all()
    query.filter("p_key =", p_key)
    query.filter("user_id =", user_id)
    if query.count() == 0:
        userprop = None
    elif query.count() > 1:
        raise CoreError("prop key %s of user %d has multiple values." % (p_key, user_id))
    else:
        userprop = query.get()
    return userprop

def has_userprop(p_key, user_id):
    return get_userprop(p_key, user_id) != None

def get_userprop_value(p_key, user_id, strict=True, fmt=None):
    if strutil.is_empty(p_key):
        raise CoreError("key can't be empty.")
    userprop = get_userprop(p_key, user_id)
    if userprop == None:
        raise CoreError("key %s of user %d doesn't exist." % (p_key, user_id))
    else:
        return strutil.to_object(userprop.p_value, default=None, strict=strict, fmt=fmt)

def replace_userprop(p_key, p_value, user_id, modifier_id):
    if not has_userprop(p_key, user_id):
        userprop = create_userprop(p_key, p_value, user_id, modifier_id)
    else:
        userprop = update_userprop(p_key, p_value, user_id, modifier_id)
    return userprop

def fetch_userprops(user_id):
    query = UserProp.all()
    query.filter("user_id =", int(user_id))
    return query.fetch()

def save_userprops(user_id, props, modifier_id):
    for (key, value) in props.items():
        replace_userprop(key, value, user_id, modifier_id)
    return True

def get_role(role_id=None, role_name=None):
    if role_id != None:
        role = Role.get_by_key(role_id)
    else:
        query = Role.all()
        query.filter("role_name =", role_name)
        role = query.get()
    return role

def fetch_operations(role_id):
    query = Operation.all("a")
    query.model(RoleOperation.get_modelname(), "b", join="inner", on="a.operation_key = b.operation_key")
    query.filter("b.role_id =", role_id)
    return query.fetch()

def get_operation(operation_key=None, handler_class=None):
    if operation_key is None and handler_class is None:
        raise CoreError("operation_key and handler_class can't be empty meantime.")
    
    query = Operation.all()
    if operation_key is not None:
        query.filter("operation_key =", operation_key)
    if handler_class is not None:
        query.filter("handler_classes like ", "%%%s%%" % handler_class)
    operation = query.get()
    return operation

def fetch_roles(operation_key):
    query = Role.all("a")
    query.model(RoleOperation.get_modelname(), "b", join="inner", on="a.role_id = b.role_id")
    query.filter("b.operation_key =", operation_key)
    return query.fetch()

def create_role(role_name, modifier_id):
    role = Role(role_name=role_name)
    role.create(modifier_id)
    return role

def delete_role(role_id, modifier_id):
    query = UserRole.all()
    query.filter("role_id =", role_id)
    if query.count() > 0 :
        raise CoreError("The role %s is set to user, can not be deleted." % role_id)
    role = Role.get_by_key(int(role_id))
    delete_roleoperations(role_id=role_id)
    role.delete(modifier_id)
    
def delete_roleoperations(role_id=None, operation_key=None, modifier_id=None):
    query = RoleOperation.all()
    if role_id is not None:
        query.filter("role_id =", role_id)
    if operation_key is not None:
        query.filter("operation_key =", operation_key)
    query.delete(modifier_id)
    
def create_roleoperation(role_id, operation_key, modifier_id):
    roleoperation = RoleOperation(role_id=role_id, operation_key=operation_key)
    roleoperation.create(modifier_id)
    return roleoperation

def copy_roleoperations(role_id_from, role_id_to, modifier_id):
    query = RoleOperation.all()
    query.filter("role_id =", int(role_id_from))
    roleoperations = query.fetch()
    for ro in roleoperations:
        create_roleoperation(ro.role_id, ro.operation_key, modifier_id)
        
def create_operation(operation_key, handler_classes, resource_oql, modifier_id):
    if type(handler_classes) == str:        
        handler_classes = [handler_classes]
        
    query = Operation.all()
    for handler_class in handler_classes:
        query.filter("handler_classes like ", "%%%s%%" % handler_class)
        if query.count() > 0:
            raise CoreError("One handler only can have one corresponding operation. The handler %s is corresponding to multiple operations." % handler_class)
    query = Operation.all()
    query.filter("operation_key =", operation_key)
    operation = Operation(operation_key=operation_key)
    operation.handler_classes = ",".join(handler_classes)
    operation.resource_oql = resource_oql
    operation.create(modifier_id)
    return operation

def update_operation_handlers(operation_key, handler_classes, modifier_id, replace=False):
    operation = get_operation(operation_key=operation_key)
    if type(handler_classes) == str:        
        handler_classes = [handler_classes]
    if replace is False:
        operation.handler_classes += ",%s" % ",".join(handler_classes)
    else:
        operation.handler_classes = ",".join(handler_classes)
    operation.update(modifier_id)
    
    
def remove_operation_handlers(operation_key, handler_classes, modifier_id):
    operation = get_operation(operation_key=operation_key)
    if type(handler_classes) == str:        
        handler_classes = [handler_classes]
    
    handlers = operation.handler_classes.split(",")
    handlers_new = []
    for handler in handler_classes:
        if handler not in handlers:
            handlers_new.append(handler)
    operation.handler_classes = ",".join(handlers_new)
    operation.update(modifier_id)
    
def update_operation_resource_oql(operation_key, resource_oql, modifier_id):
    operation = get_operation(operation_key=operation_key)
    operation.resource_oql = resource_oql
    operation.update(modifier_id)

def delete_operation(operation_key, modifier_id):
    delete_roleoperations(operation_key=operation_key, modifier_id=modifier_id)
    operation = Operation.get_by_key(operation_key)
    if operation is not None:
        operation.delete(modifier_id)
        
    
def create_userrole(user_id, role_id, modifier_id):
    userrole = UserRole(user_id=user_id, role_id=role_id)
    userrole.create(modifier_id)

def delete_userrole(user_id, role_id, modifier_id):
    userrole = UserRole(user_id=user_id, role_id=role_id)
    if userrole is not None:
        userrole.delete(modifier_id)
    
def _attach_userprops(user):
    userprops = fetch_userprops(user.uid)
    props = {}
    for userprop in userprops:
        props[userprop.p_key] = userprop.p_value
    user.props = props
    return user

def has_permission(user_id, operation_key, oqlparams=None):
    b = False
    cachekey = '%d:%s:%r' % (user_id, operation_key, oqlparams)
    perm = cache.get(CACHESPACE_PERMISSION, cachekey)
    if perm != None:
        return perm
    
    query = stdModel.all()
    query.model(UserRole.get_modelname(), "a")
    query.model(Role.get_modelname(), "b", join="inner", on="a.role_id=b.uid")
    query.model(RoleOperation.get_modelname(), "c", join="inner", on="c.role_id=b.uid")
    query.model(Operation.get_modelname(), "d", join="inner", on="c.operation_key=d.operation_key")
    query.what("a.user_id", alias="user_id")
    query.what("b.uid", alias="role_id")
    query.what("d.operation_key", alias="operation_key")
    query.what("d.handler_classes", alias="handler_classes")
    query.what("d.resource_oql", alias="resource_oql")
    query.what("a.user_id", alias="user_id")
    
    query.filter("a.user_id =", user_id)
    if operation_key is not None:
        query.filter("d.operation_key =", operation_key)
    std = query.get()
    
    if std != None:
        if std.resource_oql != None:
            operation = get_operation(operation_key=operation_key)
            params = operation.get_resource_oql_paramnames()
            if len(params) != len(oqlparams):
                raise UnauthorizedError()
            query = stdModel.all()
            if oqlparams != None and len(oqlparams) > 0 :
                query = query.sql(std.resource_oql, sql_vars=oqlparams)
            else:
                query = query.sql(std.resource_oql)
            if query.count() > 0:
                b = True
        else:
            b = True
    cache.put(CACHESPACE_PERMISSION, cachekey, b)
    return b

def execute_oql(user_id, operation_key, oqlparam, limit=10000, offset=0, paging=False, metadata=None):
    operation = get_operation(operation_key=operation_key)
    results = []
    if operation != None:
        oql = operation.resource_oql
        query = stdModel.all()
        query = query.sql(oql, sql_vars=oqlparam.to_dict())
        results = query.fetch(limit, offset, paging, metadata)
    return results

