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


from ssguan.ignitor.auth.error import OldPasswordError, LoginFailedError, \
    CredentialExpiredError
from ssguan.ignitor.auth.model import User, RoleOperation, Token, Role, \
    UserRole, encrypt_password
from ssguan.ignitor.base import context
from ssguan.ignitor.base.error import  ProgramError, RequiredError
from ssguan.ignitor.orm.error import LinkedError
from ssguan.ignitor.orm.validator import LengthValidator
from ssguan.ignitor.utility import kind, crypt


def signup(u_name, u_email, u_account, u_password):
    u_name = crypt.rsa_decrypt(u_name, context.get_token().rsa_key)
    u_email = crypt.rsa_decrypt(u_email, context.get_token().rsa_key)
    u_account = crypt.rsa_decrypt(u_account, context.get_token().rsa_key)
    u_password = crypt.rsa_decrypt(u_password, context.get_token().rsa_key)
    create_user(u_name, u_email, u_account,
                            u_password, False, User.ID_ANONYMOUS)
    return True

def update_user_password(old_password, new_password):
    if context.get_token().is_anonymous():
            raise CredentialExpiredError()
    old_password = crypt.rsa_decrypt(old_password, context.get_token().rsa_key)
    new_password = crypt.rsa_decrypt(new_password, context.get_token().rsa_key)
    user = User.get_by_key(context.get_user_id())
    if user.u_password != encrypt_password(old_password):
        raise OldPasswordError()
    else:
        if __validate_password(new_password):
            user.u_password = encrypt_password(new_password)
            user.update(context.get_user_id())
    return True

def create_user(u_account, u_password, disable_flag, u_attributes=None, u_preferences=None):
    if __validate_password(u_password):
        user1 = User()        
        user1.u_account = u_account
        user1.u_password = encrypt_password(u_password)        
        user1.disable_flag = disable_flag
        user1.u_attributes = u_attributes
        user1.u_preferences = u_preferences
        user1.create(context.get_user_id())
        return user1

def disable_user(user_id, disable_flag):
    user = User.get_by_key(user_id)
    user.disable_flag = disable_flag
    return user.update(context.get_user_id())

def get_user(user_id=None, u_account=None):
    user = None
    if user_id != None and user_id != User.NULL_USER_ID:
        user = User.get_by_key(user_id)
    elif u_account != None:
        query = User.all()
        query.filter("u_account =", u_account)
        if query.count() > 0:
            user = query.get()
    return user

def login(login_name, login_password, is_anonymous=False):
    """
    Return Token
    """
    if is_anonymous:
        usermodel = get_user(User.ID_ANONYMOUS)
    else:
        if kind.str_is_empty(login_name):
            raise RequiredError("login_name")
        if kind.str_is_empty(login_name):
            raise RequiredError("login_password")            
        login_name = crypt.rsa_decrypt(
            login_name, context.get_token().rsa_key)
        login_password = crypt.rsa_decrypt(
            login_password, context.get_token().rsa_key)
        query = User.all()
        query.filter("u_account =", login_name)
        password = encrypt_password(login_password)
        query.filter("u_password =", password)
        if query.count() > 0:
            usermodel = query.fetch(1)[0]
        else:
            raise LoginFailedError()
    role_codes = fetch_userroles(usermodel.key())
    operation_codes = fetch_useroperations(usermodel.key())
    token = Token(usermodel.key(), usermodel.u_account, role_codes, operation_codes,
                  anonymous=usermodel.is_anonymous())    
    if usermodel.u_preferences is not None:
        for (key, value) in usermodel.u_preferences.items():
            setattr(token, key, value)
    return token

def logout():
    token = login(None, None, is_anonymous=True)
    return token

def get_role(role_id=None, role_name=None):
    if role_id != None:
        role = Role.get_by_key(role_id)
    else:
        query = Role.all()
        query.filter("role_name =", role_name)
        role = query.get()
    return role

def create_role(role_code, role_name, enable_flag=True, reserve_flag=False):
    role = Role(role_code=role_code, role_name=role_name, enable_flag=enable_flag, reserve_flag=reserve_flag)
    role.create(context.get_user_id())
    return role

def delete_role(role_id):
    query = UserRole.all()
    query.filter("role_id =", role_id)
    if query.count() > 0:
        raise LinkedError("role", "user")
    role = Role.get_by_key(role_id)
    role.delete_roleoperations()
    return role.delete(context.get_user_id())

def fetch_roles(enable_flag=None, reserve_flag=None):
    query = Role.all()
    if enable_flag != None:
        query.filter("enable_flag =", enable_flag)
    if reserve_flag != None:
        query.filter("reserve_flag =", reserve_flag)
    return query.fetch()

def create_userrole(user_id, role_id):
    userrole = UserRole(user_id=user_id, role_id=role_id)
    return userrole.create(context.get_user_id())

def delete_userroles(userrole_id=None, user_id=None, role_id=None):
    if userrole_id is None and user_id is None and role_id is None:
        raise ProgramError(
            "one of userrole_id, user_id, role_id  can't be None at least")
    if userrole_id is not None:
        userrole = UserRole.get_by_key(userrole_id)
        return userrole.delete(context.get_user_id())
    query = UserRole.all()
    if user_id is not None:
        query.filter("user_id =", user_id)
    if role_id is not None:
        query.filter("role_id =", role_id)
    return query.delete(context.get_user_id())

def fetch_userroles(user_id):
    """
        Return the set of role_code that the user owns.
    """
    codes = set()
    query = UserRole.all()
    query.filter("user_id =", user_id)
    userroles = query.fetch()
    if len(userroles) > 0:
        query = Role.all()
        query.filter("_id in ", [
                    userrole.role_id for userrole in userroles])
        roles = query.fetch()
        for role in roles:
            codes.add(role.role_code)
    return codes

def fetch_useroperations(user_id, role_id=None):
    """
        Return the set of opeation_code that the user owns in the role.
    """
    operation_codes = []
    if user_id == User.ID_ROOT:
        for role in fetch_roles():
            if role_id is None or role_id == role.key():
                codes = role.fetch_roleoperations()
                operation_codes.extend(codes)
        return set(operation_codes)
    useroperations = []    
    if role_id is None:
        query = UserRole.all()
        query.filter("user_id =", user_id)
        userroles = query.fetch()
        if len(userroles) == 0:
            return set()
        else:
            query = RoleOperation.all()            
            query.filter("role_id in", [
                userrole.role_id for userrole in userroles])
    else:
        query = RoleOperation.all()
        query.filter("role_id =", role_id)
    roleoperations = query.fetch()
    for roleoperation in roleoperations:
        useroperations.append(roleoperation.operation_code)
    return set(useroperations)

def __validate_password(password):
    validator = LengthValidator(minlength=6, maxlength=20)
    return validator.validate(password, "password")
