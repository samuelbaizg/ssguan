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

from ssguan.ignitor import IGNITOR_DOMAIN
from ssguan.ignitor.auth import logger
from ssguan.ignitor.base import context
from ssguan.ignitor.orm import properti
from ssguan.ignitor.orm.error import UniqueError
from ssguan.ignitor.orm.model import Model
from ssguan.ignitor.orm.validator import UniqueValidator, IllegalValidator, \
    LengthValidator
from ssguan.ignitor.utility import crypt, kind
from ssguan.ignitor.base.struct import JsonMixin


def encrypt_password(password):
    return password if kind.str_is_empty(password) else crypt.str_to_sha256_hex(password)

class User(Model):

    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN

    ID_ANONYMOUS = "anonymous"
    ID_ROOT = "root"
    ID_SYSTEM = "system"
    ACCOUNT_NAME_ANONYMOUS = "anonymous"
    ACCOUNT_NAME_ROOT = "root"
    ACCOUNT_NAME_SYSTEM = "system"

    u_account = properti.StringProperty(required=True, validator=[LengthValidator(minlength=3, maxlength=20), UniqueValidator("u_account"), IllegalValidator()])    
    u_password = properti.StringProperty(required=True, validator=IllegalValidator())
    u_attributes = properti.DictProperty(required=False)
    u_preferences = properti.DictProperty(required=False)
    disable_flag = properti.BooleanProperty(default=False)

    def is_anonymous(self):
        return self.ID_ANONYMOUS == self.key()

    def is_superadmin(self):
        return self.ID_ROOT == self.key()

    @classmethod
    def create_schema(cls, dbconn=None):
        schema = super(User, cls).create_schema(dbconn=dbconn)
        try:
            user1 = User(u_account=cls.ACCOUNT_NAME_ANONYMOUS,
                         u_password=encrypt_password(cls.ACCOUNT_NAME_ANONYMOUS))
            user1.create(None, key=cls.ID_ANONYMOUS)
            user1 = User(u_account=cls.ACCOUNT_NAME_ROOT,
                         u_password=encrypt_password(cls.ACCOUNT_NAME_ROOT))
            user1.create(None, key=cls.ID_ROOT)
            user1 = User(u_account=cls.ACCOUNT_NAME_SYSTEM,
                         u_password=encrypt_password(cls.ACCOUNT_NAME_SYSTEM))
            user1.create(None, key=cls.ID_SYSTEM)
        except UniqueError as e:
            logger.info(e.message)
            assert e.get_argument("label") == "u_account"
        return schema


class Role(Model):

    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN

    ID_ANONYMOUS = "role_anonymous_0"
    ANONYMOUS_ROLE_CODE = "anonymous"
    ANONYMOUS_ROLE_NAME = "anonymous"

    role_code = properti.StringProperty(required=True, validator=[UniqueValidator("role_code")])
    role_name = properti.StringProperty(required=True, validator=[UniqueValidator("role_name")])
    reserve_flag = properti.BooleanProperty(default=False)
    enable_flag = properti.BooleanProperty(default=True)

    def fetch_roleoperations(self):
        """
            :rtype list: return the operation codes of this role
        """
        query = RoleOperation.all()
        query.filter("role_id =", self.key())
        roleopeations = query.fetch()
        codes = []
        for ro in roleopeations:
            codes.append(ro.operation_code)
        return codes
    
    def delete_roleoperations(self, operation_code=None):
        query = RoleOperation.all()
        query.filter("role_id =", self.key())
        if operation_code is not None:
            query.filter("operation_code =", operation_code)
        return query.delete(context.get_user_id())

    def create_roleoperation(self, operation_code):
        roleoperation = RoleOperation(role_id=self.key(
        ), operation_code=operation_code)
        roleoperation.create(context.get_user_id())
        return roleoperation

    @classmethod
    def create_schema(cls, dbconn=None):
        schema = super(Role, cls).create_schema(dbconn=dbconn)
        try:
            role = Role(role_code=cls.ANONYMOUS_ROLE_CODE, role_name=cls.ANONYMOUS_ROLE_NAME, reserve_flag=True)
            role.create(None, key=cls.ID_ANONYMOUS)            
        except UniqueError as e:
            logger.info(e.message)
            assert e.get_argument("label") == "roleName"
        return schema

class RoleOperation(Model):

    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN

    role_id = properti.StringProperty(required=True)
    operation_code = properti.StringProperty(length=200, required=True, validator=[
                                       UniqueValidator("operation_code", scope=["role_id"])])
    
class UserRole(Model):

    @classmethod
    def meta_domain(cls):
        return IGNITOR_DOMAIN

    user_id = properti.StringProperty(required=True)
    role_id = properti.StringProperty(required=True)
    
    @classmethod
    def create_schema(cls, dbconn=None):
        schema = super(UserRole, cls).create_schema(dbconn=dbconn)
        try:
            userrole = UserRole(user_id=User.ID_ANONYMOUS, role_id=Role.ID_ANONYMOUS)
            userrole.create(None)
        except UniqueError as e:
            logger.info(e.message)
            assert e.get_argument("label") == "roleName"
        return schema
    

class Token(JsonMixin):

    def __init__(self, user_id, u_account, role_codes, operation_codes, anonymous=False):
        self.__user_id = user_id
        self.__account = u_account
        self.__anonymous = anonymous
        self.__role_codes = list(role_codes)
        self.__operation_codes = list(operation_codes)
        self.__rsa_key = crypt.rsa_gen_key_hex(256)

    @property
    def user_id(self):
        return self.__user_id
    
    @property
    def account(self):
        return self.__account
    
    @property
    def rsa_key(self):
        return self.__rsa_key

    @property
    def role_codes(self):
        return self.__role_codes
    
    @property
    def operation_codes(self):
        return self.__operation_codes

    def is_anonymous(self):
        return self.__anonymous is True

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        
    def to_dict(self):
        dic = {}
        dic['lopuKey'] = {'e': self.__rsa_key['e'], 'n': self.__rsa_key['n']}
        dic['anonymous'] = self.__anonymous
        dic['account'] = self.__account
        dic['operation_codes'] = self.__operation_codes
        for key, value in self.__dict__.items():
            if not key.startswith("__"):
                dic[key] = value
        return dic
