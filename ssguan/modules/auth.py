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
from ssguan.commons import funcutils, loggingg, dao, security, typeutils
from ssguan.commons.dao import Model, UniqueError, BaseModel, RequiredError, \
    LinkedError, LengthValidator
from ssguan.commons.error import Error, ProgramError
from ssguan.commons.webb import BaseReqHandler, dec_rtn, SessionExpiredError


_logger = loggingg.get_logger(config.MODULE_AUTH)


class User(Model):

    @classmethod
    def meta_domain(cls):
        return config.MODULE_AUTH

    ID_ANONYMOUS = "anonymous"
    ID_ROOT = "root"
    ID_SYSTEM = config.ID_SYSTEM
    ANONYMOUS_ACCOUNT_NAME = "anonymous"
    SYSTEM_ACCOUNT_NAME = "system"
    ROOT_ACCOUNT_NAME = "root"
    u_name = dao.StringProperty("userName", required=False, validator=[
                                dao.IllegalValidator()])
    u_email = dao.StringProperty("userEmail", required=False, validator=[
                                 dao.IllegalValidator()])
    u_account = dao.StringProperty("accountName", required=True, validator=[dao.LengthValidator(
        minlength=3, maxlength=20), dao.UniqueValidator("u_account"), dao.IllegalValidator()])
    u_password = dao.StringProperty(
        "password", required=True, validator=dao.IllegalValidator())
    u_preferences = dao.DictProperty("userPreferences", required=False)
    disabled = dao.BooleanProperty("disabled", default=False)

    logined_times = dao.IntegerProperty(
        "loginedTime", required=True, default=0)
    last_logined_time = dao.DateTimeProperty(
        "lastLoginedTime", required=False, auto_utcnow=False)

    def is_anonymous(self):
        return self.ID_ANONYMOUS == self.key()

    def is_superadmin(self):
        return self.ID_ROOT == self.key()

    @classmethod
    def create_schema(cls, dbconn=None):
        schema = super(User, cls).create_schema(dbconn=dbconn)
        try:
            user1 = User(u_name=cls.ANONYMOUS_ACCOUNT_NAME, u_account=cls.ANONYMOUS_ACCOUNT_NAME,
                         u_password=encrypt_password(cls.ANONYMOUS_ACCOUNT_NAME))
            user1.create(None, key=cls.ID_ANONYMOUS)
            user1 = User(u_name=cls.ROOT_ACCOUNT_NAME, u_account=cls.ROOT_ACCOUNT_NAME,
                         u_password=encrypt_password(cls.ROOT_ACCOUNT_NAME))
            user1.create(None, key=cls.ID_ROOT)
            user1 = User(u_name=cls.SYSTEM_ACCOUNT_NAME, u_account=cls.SYSTEM_ACCOUNT_NAME,
                         u_password=encrypt_password(cls.SYSTEM_ACCOUNT_NAME))
            user1.create(None, key=cls.ID_SYSTEM)
        except UniqueError, e:
            _logger.info(e.message)
            assert e.get_argument("label") == "accountName"
        return schema

    def get_user_display_name(self):
        user_name = self.u_account if typeutils.str_is_empty(
            self.u_name) else self.u_name
        return user_name

    def fetch_userroles():
        query = User


class RoleOperation(Model):

    OPERATION_CREATE = "create"
    OPERATION_UPDATE = "update"
    OPERATION_DELETE = "delete"
    OPERATION_READ = "read"

    ALL_MODEL = "*"

    @classmethod
    def meta_domain(cls):
        return config.MODULE_AUTH

    role_id = dao.StringProperty("roleKey", required=True)
    operation_model = dao.StringProperty(
        "operationModel", length=200, required=True)
    operation_key = dao.StringProperty("operationKey", length=200, required=True, validator=[
                                       dao.UniqueValidator("operation_key", scope=["role_id", "operation_model"])])


class Role(Model):

    @classmethod
    def meta_domain(cls):
        return config.MODULE_AUTH

    ID_ANONYMOUS = "role_anonymous_0"

    ANONYMOUS_ROLE_NAME = "anonymous"

    role_name = dao.StringProperty("roleName", required=True, validator=[
                                   dao.UniqueValidator("role_name")])
    reserved = dao.BooleanProperty("reserved", default=False)
    enabled = dao.BooleanProperty("enabled", default=True)

    def fetch_roleoperations(self):
        query = RoleOperation.all()
        query.filter("role_id =", self.key())
        return query.fetch()

    def delete_roleoperations(self, deleted_by, model_class=None, operation_key=None):
        query = RoleOperation.all()
        query.filter("role_id =", self.key())
        if model_class is not None:
            query.filter("operation_model =",
                         self.get_operation_model(model_class))
        if operation_key is not None:
            query.filter("operation_key =", operation_key)
        query.delete(deleted_by)

    def create_roleoperation(self, model_class, operation_key, created_by):
        operation_model = self.get_operation_model(model_class)
        roleoperation = RoleOperation(role_id=self.key(
        ), operation_model=operation_model, operation_key=operation_key)
        roleoperation.create(created_by)
        return roleoperation

    def delete(self, deleted_by):
        self.delete_roleoperations(deleted_by)
        return Model.delete(self, deleted_by)

    @classmethod
    def create_schema(cls, dbconn=None):
        schema = super(Role, cls).create_schema(dbconn=dbconn)
        try:
            role = Role(role_name=cls.ANONYMOUS_ROLE_NAME, reserved=True)
            role.create(None, key=cls.ID_ANONYMOUS)
        except UniqueError, e:
            _logger.info(e.message)
            assert e.get_argument("label") == "roleName"
        return schema

    @classmethod
    def get_operation_model(cls, model_class):
        model_name = model_class if type(
            model_class) == str else model_class.get_modelname()
        return model_name


class Resource(Model):

    @classmethod
    def meta_domain(cls):
        return config.MODULE_AUTH

    ID_ALL = "resource_0"
    resource_name = dao.StringProperty("resourceName", required=True, validator=[
                                       dao.UniqueValidator('resource_name')])
    reserved = dao.BooleanProperty("reserved", default=False)
    enabled = dao.BooleanProperty("enabled", default=True)

    @classmethod
    def create_schema(cls, dbconn=None):
        schema = super(Resource, cls).create_schema(dbconn=dbconn)
        try:
            resource = Resource(resource_name=cls.ID_ALL,
                                reserved=True, enabled=True)
            resource.create(None, key=cls.ID_ALL)
        except UniqueError, e:
            _logger.info(e.message)
            assert e.get_argument("label") == "resourceName"
        return schema

    def delete(self, deleted_by):
        self.delete_resourceitems(deleted_by)
        return Model.delete(self, deleted_by)

    def create_resourceitem(self, resitem_model, resitem_format, resitem_value, created_by):
        """
            resitem_format must be the value of either ResourceItem.FORMAT_VALUE or ResourceItem.FORMAT_QFILTER.
            if resitem_format == ResourceItem.FORMAT_QFILTER:
                resitem_value must be a filter dict like {"property_op": "f_str", "value":"111"} 
                    or a list like 
                    [
                        {'property_op':'f_int =', 'value':1},
                         {'property_op':'f_str =', 'value':'abced', 'parenthesis':'('}, 
                         {'property_op':'f_str =', 'value':'xfg', 'parenthesis':')', 'logic':'or'}
                     ]
            if resitem_format == ResourceItem.FORMAT_VALUE:
                resitem_value could by any str. 
            if resitem_value == ResourceItem.VALUE_ALL, means all records in resitem_model.
        """
        if not issubclass(resitem_model, BaseModel):
            raise ProgramError("resitem_model must be sub-class of BaseModel.")
        if resitem_format == ResourceItem.FORMAT_QFILTER and type(resitem_value) != dict and type(resitem_value) != list:
            raise ProgramError(
                "resitem_value must be the type of dict if resitem_format == QFILTER.")
        resouceitem_value = typeutils.obj_to_str(resitem_value)
        resitem = ResourceItem(resource_id=self.key(), resitem_model=resitem_model.get_modelname(
        ), resitem_format=resitem_format, resitem_value=resouceitem_value)
        return resitem.create(created_by)

    def update_resourceitem(self, resitem_id, resitem_model, resitem_format, resitem_value, modified_by):
        if not issubclass(resitem_model, BaseModel):
            raise ProgramError("resitem_model must be sub-class of BaseModel.")
        resitem = ResourceItem.get_by_key(resitem_id)
        resitem.resitem_model = resitem_model.get_modelname()
        resitem.resitem_format = resitem_format
        resitem.resitem_value = resitem_value
        return resitem.update(modified_by)

    def get_resourceitem(self, resitem_id):
        return ResourceItem.get_by_key(resitem_id)

    def delete_resourceitems(self, deleted_by):
        query = ResourceItem.all()
        query.filter("resource_id =", self.key())
        return query.delete(deleted_by)

    def fetch_resourceitems(self):
        query = ResourceItem.all()
        query.filter("resource_id =", self.key())
        return query.fetch()


class ResourceItem(Model):

    FORMAT_VALUE = "VALUE"
    FORMAT_QFILTER = "QFILTER"

    VALUE_ALL = "*"

    ID_ALL = "resourceitem_0"

    @classmethod
    def meta_domain(cls):
        return config.MODULE_AUTH

    resource_id = dao.StringProperty("resourceKey", required=True)
    resitem_model = dao.StringProperty("resItemModel", required=True)
    resitem_format = dao.StringProperty("resItemFormat", required=True, choices=[
                                        FORMAT_VALUE, FORMAT_QFILTER])
    resitem_value = dao.StringProperty("resItemValue", required=True, length=200, validator=[
                                       dao.UniqueValidator('resitem_value', ['resource_id', 'resitem_model', 'resitem_format'])])

    @classmethod
    def create_schema(cls, dbconn=None):
        schema = super(ResourceItem, cls).create_schema(dbconn=dbconn)
        try:
            resourceitem = ResourceItem(resource_id=Resource.ID_ALL, resitem_model=cls.VALUE_ALL,
                                        resitem_format=cls.FORMAT_VALUE, resitem_value=cls.VALUE_ALL)
            resourceitem.create(None, key=cls.ID_ALL)
        except UniqueError, e:
            _logger.info(e.message)
            assert e.get_argument("label") == "resItemValue"
        return schema

    def eval_resitem_value(self, **kwargs):
        """
            if resitem_value == {"property_op": "action", "value":'#action'} and kwargs ==  {"action": "add"}:
                resitem_value will be replaced to {"property_op": "action", "value":'add'}
            if resitem_value == '#action' and kwargs ==  {"action": "add"}:
                resitem_value will be replaced to 'add'
        """
        value = self.resitem_value
        if self.resitem_format == self.FORMAT_VALUE:
            value = self.resitem_value
        elif self.resitem_format == self.FORMAT_QFILTER:
            for key, val in kwargs.items():
                value = value.replace("#%s" % key, val)
        return value


class UserPermission(Model):

    @classmethod
    def meta_domain(cls):
        return config.MODULE_AUTH

    user_id = dao.StringProperty("userKey", required=True)
    role_id = dao.StringProperty("roleKey", required=True)
    resource_id = dao.StringProperty("resourceKey", required=True, validator=[
                                     dao.UniqueValidator("resource_id", scope=["user_id", "role_id"])])


class Token(typeutils.JsonMixin):

    def __init__(self, user_id, operations, anonymous=False):
        self.__user_id = user_id
        self.__anonymous = anonymous
        self.__operations = operations
        self.__rsa_key = security.rsa_gen_key_hex(256)

    @property
    def user_id(self):
        return self.__user_id

    @property
    def rsa_key(self):
        return self.__rsa_key

    @property
    def operations(self):
        return self.__operations

    def is_anonymous(self):
        return self.__anonymous is True

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def to_dict(self):
        dic = {}
        dic['lopuKey'] = {'e': self.__rsa_key['e'], 'n': self.__rsa_key['n']}
        dic['anonymous'] = self.__anonymous
        dic['operations'] = self.__operations
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                dic[key] = value
        return dic


def encrypt_password(password):
    return password if typeutils.str_is_empty(password) else security.str_to_sha256_hex(password)


class AuthInteceptor(object):

    def login_prepare(self, login_name, login_password, is_anonymous=False):
        """do nothing by default and override by subclass"""

    def login_finish(self, token):
        """do nothing by default and override by subclass"""

    def logout_prepare(self, token):
        """do nothing by default and override by subclass"""

    def logout_finish(self, token):
        """do nothing by default and override by subclass"""

    def create_user_finish(self, usermodel):
        """do nothing by default and override by subclass"""


def signup(u_name, u_email, u_account, u_password):
    usermodel = create_user(u_name, u_email, u_account,
                            u_password, False, User.ID_ANONYMOUS)
    return usermodel


def create_user(u_name, u_email, u_account, u_password, disabled, created_by, u_preferences=None):
    if not has_permission(created_by, User, RoleOperation.OPERATION_CREATE):
        raise UnauthorizedError(
            RoleOperation.OPERATION_CREATE, User.get_modelname(), u_name)
    if _validate_password(u_password):
        user1 = User()
        user1.u_name = u_name
        user1.u_email = u_email
        user1.u_account = u_account
        user1.u_password = encrypt_password(u_password)
        user1.disabled = disabled
        user1.u_preferences = u_preferences
        user1.create(created_by)
        aui = get_authinteceptor()
        aui.create_user_finish(user1)
        return user1


def update_user_password(user_id, old_password, new_password, verified, modified_by):
    if user_id != modified_by:
        if not has_permission(modified_by, User, RoleOperation.OPERATION_UPDATE):
            raise UnauthorizedError(
                RoleOperation.OPERATION_UPDATE, User.get_modelname(), user_id)
    user = User.get_by_key(user_id)
    if verified and user.u_password != encrypt_password(old_password):
        raise OldPasswordError()
    else:
        if _validate_password(new_password):
            user.u_password = encrypt_password(new_password)
            user.update(modified_by)
    return user


def disable_user(user_id, disabled, modified_by):
    if not has_permission(modified_by, User, RoleOperation.OPERATION_UPDATE):
        raise UnauthorizedError(
            RoleOperation.OPERATION_CREATE, User.get_modelname(), modified_by)
    user = User.get_by_key(user_id)
    user.disabled = disabled
    return user.update(modified_by)


def get_user(read_by, user_id=None, u_account=None):
    if not has_permission(read_by, User, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(
            RoleOperation.OPERATION_READ, User.get_modelname(), read_by)
    user = None
    if user_id != None and user_id != User.NULL_USER_ID:
        user = User.get_by_key(user_id)
    elif u_account != None:
        query = User.all()
        query.filter("u_account =", u_account)
        if query.count() > 0:
            user = query.get()
    return user


def get_authinteceptor():
    aic = config.authCFG.get_authinteceptor()
    ai = None
    if aic is not None:
        ai = funcutils.import_module(aic)
        if ai is None:
            from ssguan.commons.error import NoFoundError
            raise NoFoundError("AuthInteceptor", aic)
        ai = ai()
    return ai


def login(login_name, login_password, is_anonymous=False):
    """
    Return Token
    """
    authinteceptor = get_authinteceptor()
    authinteceptor.login_prepare(
        login_name, login_password, is_anonymous=is_anonymous)
    if is_anonymous:
        usermodel = get_user(User.ID_ROOT, User.ID_ANONYMOUS)
    else:
        if typeutils.str_is_empty(login_name):
            raise RequiredError("loginName")
        query = User.all()
        query.filter("u_account =", login_name, parenthesis="(")
        query.filter("u_email =", login_name, logic="or", parenthesis=")")
        password = encrypt_password(login_password)
        query.filter("u_password =", password)
        if query.count() > 0:
            usermodel = query.fetch(1)[0]
        else:
            raise LoginFailedError()
    usermodel.logined_times += 1
    _update_user_logined_info(usermodel.key(), usermodel.key())
    useroperations = fetch_useroperations(usermodel.key())
    token = Token(usermodel.key(), useroperations,
                  anonymous=usermodel.is_anonymous())
    token.userName = usermodel.u_name
    token.accountName = usermodel.u_account
    token.displayName = usermodel.get_user_display_name()
    if usermodel.u_preferences is not None:
        for (key, value) in usermodel.u_preferences.items():
            setattr(token, key, value)
    authinteceptor.login_finish(token)
    return token


def logout(token):
    authinteceptor = get_authinteceptor()
    authinteceptor.logout_prepare(token)
    authinteceptor.logout_finish(token)
    token = login(None, None, is_anonymous=True)
    return token


def get_role(read_by, role_id=None, role_name=None):
    if not has_permission(read_by, Role, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(RoleOperation.OPERATION_READ,
                                Role.get_modelname(), "%s%s" % (role_id, role_name))
    if role_id != None:
        role = Role.get_by_key(role_id)
    else:
        query = Role.all()
        query.filter("role_name =", role_name)
        role = query.get()
    return role


def create_role(role_name, created_by, enabled=True, reserved=False):
    if not has_permission(created_by, Role, RoleOperation.OPERATION_CREATE):
        raise UnauthorizedError(
            RoleOperation.OPERATION_UPDATE, Role.get_modelname(), role_name)
    role = Role(role_name=role_name, enabled=enabled, reserved=reserved)
    role.create(created_by)
    return role


def delete_role(role_id, deleted_by):
    if not has_permission(deleted_by, Role, RoleOperation.OPERATION_DELETE):
        raise UnauthorizedError(
            RoleOperation.OPERATION_DELETE, Role.get_modelname(), role_id)
    query = UserPermission.all()
    query.filter("role_id =", role_id)
    if query.count() > 0:
        raise LinkedError("role", "user")
    role = Role.get_by_key(role_id)
    return role.delete(deleted_by)


def fetch_roles(read_by, enabled=None, reserved=None):
    if not has_permission(read_by, Role, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, Role.get_modelname(
        ), "enabled=%s,reserved=%s" % (str(enabled), str(reserved)))
    query = Role.all()
    if enabled != None:
        query.filter("enabled =", enabled)
    if reserved != None:
        query.filter("reserved =", reserved)
    return query.fetch()


def create_resource(resource_name, created_by, enabled=True, reserved=False):
    if not has_permission(created_by, Resource, RoleOperation.OPERATION_CREATE):
        raise UnauthorizedError(
            RoleOperation.OPERATION_CREATE, Resource.get_modelname(), resource_name)
    resource = Resource(resource_name=resource_name,
                        enabled=enabled, reserved=reserved)
    return resource.create(created_by)


def get_resource(resource_id, read_by):
    if not has_permission(read_by, Resource, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(
            RoleOperation.OPERATION_READ, Resource.get_modelname(), resource_id)
    return Resource.get_by_key(resource_id)


def delete_resource(resource_id, deleted_by):
    if not has_permission(deleted_by, Resource, RoleOperation.OPERATION_DELETE):
        raise UnauthorizedError(
            RoleOperation.OPERATION_DELETE, Resource.get_modelname(), resource_id)
    query = UserPermission.all()
    query.filter("resource_id =", resource_id)
    if query.count() > 0:
        raise LinkedError("resource", "user")
    resource = Resource.get_by_key(resource_id)
    return resource.delete(deleted_by)


def fetch_resources(read_by, enabled=None, reserved=None):
    if not has_permission(read_by, Resource, RoleOperation.OPERATION_READ):
        raise UnauthorizedError(RoleOperation.OPERATION_READ, Resource.get_modelname(
        ), "enabled=%s,reserved=%s" % (str(enabled), str(reserved)))
    query = Resource.all()
    if enabled != None:
        query.filter("enabled =", enabled)
    if reserved != None:
        query.filter("reserved =", reserved)
    return query.fetch()


def create_userpermission(user_id, role_id, resource_id, created_by):
    if not has_permission(created_by, UserPermission, RoleOperation.OPERATION_DELETE):
        raise UnauthorizedError(RoleOperation.OPERATION_DELETE, UserPermission.get_modelname(
        ), "%s-%s-%s" % (user_id, role_id, resource_id))
    userpermission = UserPermission(
        user_id=user_id, role_id=role_id, resource_id=resource_id)
    return userpermission.create(created_by)


def delete_userpermissions(deleted_by, userpermission_id=None, user_id=None, role_id=None, resource_id=None):
    if not has_permission(deleted_by, UserPermission, RoleOperation.OPERATION_DELETE):
        raise UnauthorizedError(RoleOperation.OPERATION_DELETE, UserPermission.get_modelname(
        ), "%s-%s-%s" % (user_id, role_id, resource_id))
    if userpermission_id is None and user_id is None and role_id is None and resource_id is None:
        raise ProgramError(
            "one of userpermission_id, user_id, role_id, resource_id can't be None at least")
    if userpermission_id is not None:
        userpermission = UserPermission.get_by_key(userpermission_id)
        return userpermission.delete(deleted_by)
    query = UserPermission.all()
    if user_id is not None:
        query.filter("user_id =", user_id)
    if role_id is not None:
        query.filter("role_id =", role_id)
    if resource_id is not None:
        query.filter("resource_id =", resource_id)
    return query.delete(deleted_by)


def fetch_userpermissions(user_id, model_class=None, operation_key=None):
    query = Role.all()
    query.filter("enabled =", True)
    roles = query.fetch()
    if len(roles) == 0:
        return []
    query = RoleOperation.all()
    query.filter("role_id in", [role.key() for role in roles])
    if model_class is not None:
        operation_model = Role.get_operation_model(model_class)
        query.filter("operation_model =", operation_model)
    if operation_key is not None:
        query.filter("operation_key =", operation_key)
    roleoperations = query.fetch()
    query = UserPermission.all()
    query.filter("user_id =", user_id)
    userpermissions = []
    if len(roleoperations) > 0:
        query.filter("role_id in", [
                     roleoperation.role_id for roleoperation in roleoperations])
        userpermissions = query.fetch()
    return userpermissions


def fetch_useroperations(user_id, role_id=None):
    if user_id == User.ID_SYSTEM:
        return '*'
    query = UserPermission.all()
    query.filter("user_id =", user_id)
    userpermissions = query.fetch()
    query = RoleOperation.all()
    useroperations = []    
    if role_id is None:
        if len(useroperations) == 0:
            return useroperations
        else:
            query.filter("role_id in", [
                userpermission.role_id for userpermission in userpermissions])
    else:
        query.filter("role_id =", role_id)
    roleoperations = query.fetch()
    for roleoperation in roleoperations:
        useroperations.append("%s_%s" % (
            roleoperation.operation_key, roleoperation.operation_model))
    return set(useroperations)


def has_permission(user_id, model_class, operation_key, model_id=None, **kwargs):
    """
        Return True or False.  
        True means user_id has the permission. 
        False means user_id doesn't have the permission.
        Also return False if model_id can't be found in model_class table. 

        **kwargs is the arguments for ResourceItem.eval_resitem_value.
    """
    if user_id is None:
        return False
    if user_id == User.ID_ROOT or user_id == User.ID_SYSTEM:
        return True
    if typeutils.str_is_empty(model_id):
        userpermissions = fetch_userpermissions(
            user_id, model_class, operation_key)
        b = True if len(userpermissions) > 0 else False
    else:
        query = gen_query_of_allowed_resources(
            user_id, model_class, operation_key, **kwargs)
        if query is None:
            b = False
        elif len(query.get_query_sets()) == 0:
            b = True
        else:
            query.filter("_id =", model_id)
            b = query.count() > 0
    return b


def gen_query_of_allowed_resources(user_id, model_class, operation_key, **kwargs):
    """
        Returns model.Query. 
        None means user_id doesn't have permission to fetch models from model_class.
        0 elements in Query.get_query_sets() means user_id has permission to fetch ALL models from model_class.
        more than 0 elements in Query.get_query_sets() means user_id has permission to fetch partial models from model_class.
        **kwargs is the arguments for ResourceItem.eval_resitem_value.

    """
    if model_class is None:
        raise ProgramError("model_class can't be None")
    rtn_query = model_class.all()

    if user_id == User.ID_ROOT:
        return rtn_query

    userpermissions = fetch_userpermissions(
        user_id, model_class, operation_key)
    if len(userpermissions) == 0:
        return None

    query = ResourceItem.all()
    query.filter("resource_id in", [
                 userpermission.resource_id for userpermission in userpermissions])
    query.filter("resitem_model in ", [
                 ResourceItem.VALUE_ALL, model_class.get_modelname()])
    resourceitems = query.fetch()

    if len(resourceitems) == 0:
        return None

    values = []
    first = None
    last = None
    for i in xrange(0, len(resourceitems)):
        resourceitem = resourceitems[i]
        if resourceitem.key() == ResourceItem.ID_ALL:
            return rtn_query
        value = resourceitem.eval_resitem_value(**kwargs)
        if resourceitem.resitem_format == ResourceItem.FORMAT_VALUE:
            values.append(value)
        elif resourceitem.resitem_format == ResourceItem.FORMAT_QFILTER:
            obj = typeutils.str_to_object(value)
            obj = obj if type(obj) == list else [obj]
            if first is None:
                first = obj
            else:
                rtn_query.filter_x(obj, logic="or")
            if last is None and i == len(resourceitems) - 1:
                last = obj

    if first is None and last is None:
        rtn_query.filter_x([{'property_op': "_id in", 'value': values}])
    elif (first is not None and last is None) or (first == last):
        if len(values) > 0:
            rtn_query.filter_x(
                [{'property_op': "_id in", 'value': values}], parenthesis_left="(")
            rtn_query.filter_x(first, logic="or", parenthesis_right=")")
        else:
            rtn_query.filter_x(first)
    else:
        if len(values) > 0:
            rtn_query.filter_x(
                [{'property_op': "_id in", 'value': values}], logic="or", parenthesis_left="(")
            rtn_query.filter_x(first, logic="or")
            rtn_query.filter_x(last, logic="or", parenthesis_right=")")
        else:
            rtn_query.filter_x(first, parenthesis_left="(")
            rtn_query.filter_x(last, logic="or", parenthesis_right=")")

    return rtn_query


def _validate_password(password):
    validator = LengthValidator(minlength=6, maxlength=20)
    return validator.validate(password, "password")


def _update_user_logined_info(user_id, modified_by):
    user = User.get_by_key(user_id)
    user.last_logined_time = typeutils.utcnow()
    user.logined_times += 1
    user.modified_time = typeutils.utcnow()
    user.update(modified_by)


class LoginFailedError(Error):
    def __init__(self):
        super(LoginFailedError, self).__init__(
            "Your email or account is not matched your password, please enter again")

    @property
    def code(self):
        return 1100


class UnauthorizedError(Error):
    def __init__(self, action, model, value):
        super(UnauthorizedError, self).__init__(
            "You don't have permission to {{actionlabel}} {{modellabel}} -- {{value}}.", actionlabel=action, modellabel=model, value=value)

    @property
    def code(self):
        return 1101


class OldPasswordError(Error):
    def __init__(self):
        super(OldPasswordError, self).__init__(
            "You old password is not correct.")

    @property
    def code(self):
        return 1102


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
            anonymous_token = login(
                User.ANONYMOUS_ACCOUNT_NAME, None, is_anonymous=True)
            self.set_current_user(anonymous_token)


class LoginHandler(AuthReqHandler):

    @dec_rtn
    def post(self, *args, **kwargs):
        body = self.decode_arguments_body()
        login_name = body['loginName']
        if login_name == User.ANONYMOUS_ACCOUNT_NAME:
            token = self.get_current_user()
            if token is None:
                token = login(None, None, is_anonymous=True)            
        else:
            if typeutils.str_is_empty(login_name):
                raise RequiredError("loginName")
            if typeutils.str_is_empty(login_name):
                raise RequiredError("loginPassword")            
            login_name = login_name.decode('hex')
            login_name = security.rsa_decrypt(
                login_name, self.get_current_user().rsa_key)
            login_password = body['loginPassword']
            login_password = login_password.decode('hex')
            login_password = security.rsa_decrypt(
                login_password, self.get_current_user().rsa_key)
            token = login(login_name, login_password)
        self.set_current_user(token)
        return token


class LogoutHandler(AuthReqHandler):

    @dec_rtn
    def post(self, *args, **kwargs):
        token = logout(self.get_current_user())        
        self.set_current_user(token)
        return token


class SignupHandler(AuthReqHandler):

    @dec_rtn
    def post(self, *args, **kwargs):
        body = self.decode_arguments_body()
        u_account = body['accountName']
        u_account = u_account.decode('hex')
        u_account = security.rsa_decrypt(
            u_account, self.get_current_user().rsa_key)
        u_email = body['userEmail']
        u_email = u_email.decode('hex')
        u_email = security.rsa_decrypt(
            u_email, self.get_current_user().rsa_key)
        u_password = body['loginPassword']
        u_password = u_password.decode('hex')
        u_password = security.rsa_decrypt(
            u_password, self.get_current_user().rsa_key)
        signup(u_account, u_email, u_account, u_password)
        return True


class UpdateUserPwdHandler(AuthReqHandler):

    @dec_rtn
    def post(self, *args, **kwargs):
        body = self.decode_arguments_body()
        old_password = body['oldPassword']
        old_password = old_password.decode('hex')
        old_password = security.rsa_decrypt(
            old_password, self.get_current_user().rsa_key)
        new_password = body['newPassword']
        new_password = new_password.decode('hex')
        new_password = security.rsa_decrypt(
            new_password, self.get_current_user().rsa_key)
        if self.get_current_user().is_anonymous():
            raise SessionExpiredError()
        else:
            update_user_password(self.get_current_user(
            ).user_id, old_password, new_password, True, self.get_current_user().user_id)
            return True


def install_module():
    Role.create_schema()
    RoleOperation.create_schema()
    User.create_schema()
    UserPermission.create_schema()
    Resource.create_schema()
    ResourceItem.create_schema()
    config.dbCFG.add_model_dbkey(
        "%s_*" % config.MODULE_AUTH, config.dbCFG.ROOT_DBKEY)
    config.authCFG.add_authinteceptor("ssguan.modules.auth.AuthInteceptor")
    role = get_role(User.ID_ROOT, role_id=Role.ID_ANONYMOUS)
    role.create_roleoperation(
        User, RoleOperation.OPERATION_CREATE, config.ID_SYSTEM)
    create_userpermission(User.ID_ANONYMOUS, Role.ID_ANONYMOUS,
                          Resource.ID_ALL, config.ID_SYSTEM)
    config.webbCFG.add_handler(
        "/auth/login", "ssguan.modules.auth.LoginHandler")
    config.webbCFG.add_handler(
        "/auth/logout", "ssguan.modules.auth.LogoutHandler")
    config.webbCFG.add_handler(
        "/auth/signup", "ssguan.modules.auth.SignupHandler")
    config.webbCFG.add_handler(
        "/auth/updatepwd", "ssguan.modules.auth.UpdateUserPwdHandler")
    return True


def uninstall_module():
    Role.delete_schema()
    RoleOperation.delete_schema()
    User.delete_schema()
    UserPermission.delete_schema()
    Resource.delete_schema()
    ResourceItem.delete_schema()
    config.authCFG.delete_authinteceptor()
    config.dbCFG.delete_model_dbkey("%s_*" % config.MODULE_AUTH)
    config.webbCFG.delete_handler("/auth/login")
    config.webbCFG.delete_handler("/auth/logout")
    config.webbCFG.delete_handler("/auth/signup")
    config.webbCFG.delete_handler("/auth/updatepwd")
    return True
