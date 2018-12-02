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
import unittest

from ssguan.ignitor.auth import service as auth_service
from ssguan.ignitor.auth.error import OldPasswordError, LoginFailedError
from ssguan.ignitor.auth.model import Role, User
from ssguan.ignitor.base import context
from ssguan.ignitor.base.error import LengthError
from ssguan.ignitor.orm import dbpool, config as orm_config, update
from ssguan.ignitor.orm.error import  UniqueError, LinkedError
from ssguan.ignitor.utility import crypt


class AuthServiceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dbpool.create_db(orm_config.get_default_dbinfo(), dropped=True)
        update.install()
        update.upgrade('ignitor.auth')
        
    def set_token(self):
        token = auth_service.login(None, None, True)
        context.set_token(token)
        return token

    def test_create_user(self):
        self.set_token()
        try:
            auth_service.create_user("ma", "123", False)
            self.assertTrue(False)
        except LengthError as e:
            self.assertEqual(e.arguments["label"], "password")

        try:
            auth_service.create_user("ma", "1233333", False)
            self.assertTrue(False)
        except LengthError as e:
            self.assertEqual(e.arguments['label'], "u_account")

        user1 = auth_service.create_user(
                                 "maa", "123456", False, u_attributes={'email':'hua@a.com', 'mobile':'1202'})
        self.assertIsNotNone(user1.key())
        user2 = auth_service.get_user(user1.key())
        self.assertEqual(user1.u_account, user2.u_account)
        self.assertEqual(user1.u_password, user2.u_password)
        self.assertEqual(user1.disable_flag, user2.disable_flag)
        self.assertEqual(user1.u_attributes, user2.u_attributes)
        self.assertFalse(user1.disable_flag)
        try:
            auth_service.create_user("maa", "123444", False)
            self.assertTrue(False)
        except UniqueError as e:
            self.assertEqual(e.arguments['label'], "u_account")

    def test_get_user(self):
        self.set_token()
        auth_service.create_user("ma1", "123456", False, u_attributes={'email':'hua@a.com', 'mobile':'1202'}, u_preferences={"lang":'cc'})
        user1 = auth_service.get_user(u_account="ma1")
        self.assertEqual(user1.u_password,
                         crypt.str_to_sha256_hex("123456"))
        self.assertEqual(user1.u_attributes['email'], "hua@a.com")
        self.assertEqual(user1.u_attributes['mobile'], "1202")
        self.assertEqual(user1.u_preferences['lang'], "cc")
        user1 = auth_service.get_user(user_id=user1.key())
        self.assertEqual(user1.u_password,
                         crypt.str_to_sha256_hex("123456"))
        


    def test_update_user_password(self):
        token1 = self.set_token()
        auth_service.create_user("mffdaacc", "123456", False)
        token = self.login('mffdaacc', '123456', token1)
        context.set_token(token)
        user1 = auth_service.get_user(u_account="mffdaacc")
        oldpwd = crypt.rsa_encrypt("123456", token.to_dict()['lopuKey'])
        newpwd = crypt.rsa_encrypt("12345678", token.to_dict()['lopuKey'])
        auth_service.update_user_password(oldpwd, newpwd)
        user1 = auth_service.get_user(user_id=user1.key())
        self.assertEqual(user1.u_password,
                         crypt.str_to_sha256_hex("12345678"))
        try:
            oldpwd = crypt.rsa_encrypt("1234561", token.to_dict()['lopuKey'])
            newpwd = crypt.rsa_encrypt("12345678", token.to_dict()['lopuKey'])
            auth_service.update_user_password(oldpwd, newpwd)
            self.assertTrue(False)
        except OldPasswordError:
            self.assertTrue(True)

        user1 = auth_service.get_user(user_id=user1.key())
        self.assertEqual(user1.u_password,
                         crypt.str_to_sha256_hex("12345678"))

    def test_disable_user(self):
        self.set_token()
        u1 = auth_service.create_user("maaccad", "123456", False)
        u2 = auth_service.disable_user(u1.key(), True)
        self.assertTrue(u2.disable_flag)
        u2 = auth_service.disable_user(u1.key(), False)
        self.assertFalse(u2.disable_flag)

    def login(self, name, pwd, token):
        name = crypt.rsa_encrypt(name, token.to_dict()['lopuKey'])
        pwd = crypt.rsa_encrypt(pwd, token.to_dict()['lopuKey'])
        return auth_service.login(name, pwd)
    
    def test_login(self):       
        token1 = self.set_token()
        user1 = auth_service.create_user("tuser" , "123456", False, u_preferences={"prefL": "zh"})
        token = self.login("tuser", "123456", token1)
        self.assertEqual(token.user_id, user1.key())
        token = self.login("tuser", "123456", token1)
        self.assertEqual(token.account, "tuser")
        self.assertEqual(token.prefL, "zh")
        self.assertEqual(token.to_dict()['prefL'], "zh")
        try:
            token = self.login("tuser", "1234567", token1)
            self.assertTrue(False)
        except LoginFailedError:
            self.assertTrue(True)
        try:
            token = self.login("tuser33", "1234567", token1)
            self.assertTrue(False)
        except LoginFailedError:
            self.assertTrue(True)

    def test_create_role(self):
        self.set_token()
        role = auth_service.create_role("eeeeee", "eeeeee")
        role1 = auth_service.get_role(role.key())
        self.assertEqual(role.role_name, role1.role_name)
        try:
            role = auth_service.create_role("eeeeee", "eeeeee")
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)
        role = auth_service.create_role("zzzzz", "zzzzz", reserve_flag=True)
        role = auth_service.get_role(role_name="zzzzz")
        self.assertEqual(role.reserve_flag, True)

    def test_get_role(self):
        self.set_token()
        role = auth_service.create_role("fff", "fff")
        role1 = auth_service.get_role(role.key())
        self.assertEqual(role.role_name, role1.role_name)
        role1 = auth_service.get_role(role_name="fff")
        self.assertEqual(role.key(), role1.key())

    def test_fetch_roleoperations(self):
        self.set_token()
        role = auth_service.create_role("a33", "a33")
        role2 = auth_service.get_role(role.key())
        role2.create_roleoperation("111")
        role2.create_roleoperation("222")
        ops = role2.fetch_roleoperations()
        self.assertEqual(len(ops), 2)

    def test_delete_role(self):
        self.set_token()
        role = auth_service.create_role("rrrr", "rrrr")
        auth_service.create_userrole(User.ID_ROOT, role.key())        
        role1 = auth_service.get_role(role.key())
        try:
            auth_service.delete_role(role1.key())
            self.assertTrue(False)
        except LinkedError as e:
            self.assertEqual(e.arguments['linklabel'], 'user')

        role = auth_service.create_role("rrrr3zz3", "rrrr3zz3")
        role2 = auth_service.get_role(role.key())
        role2.create_roleoperation("111")
        role2.create_roleoperation("222")
        auth_service.delete_role(role2.key())
        role = auth_service.get_role(role2.key())
        self.assertIsNone(role)
        ops = role2.fetch_roleoperations()
        self.assertEqual(len(ops), 0)

    def test_create_roleoperation(self):
        self.set_token()
        role = auth_service.create_role("ro33", "ro33")
        role2 = auth_service.get_role(role.key())
        role2.create_roleoperation("111")
        try:
            role2.create_roleoperation("111")
            self.assertTrue(False)
        except UniqueError as e:
            self.assertEqual(e.arguments["label"], "operation_code")

    def test_delete_roleoperations(self):
        self.set_token()
        role = auth_service.create_role("roaa33", "roaa33")
        role2 = auth_service.get_role(role.key())
        role2.create_roleoperation("111")
        role2.delete_roleoperations(None)
        ros = role2.fetch_roleoperations()
        self.assertEqual(len(ros), 0)
        role2.create_roleoperation("222")
        role2.delete_roleoperations("222")
        ros = role2.fetch_roleoperations()
        self.assertEqual(len(ros), 0)
    
    def test_fetch_roles(self):
        self.set_token()
        query = Role.all()
        query.delete(None)
        auth_service.create_role("aaaa2", "aaaa2", enable_flag=True, reserve_flag=False)
        auth_service.create_role("aaaa1", "aaaa1", enable_flag=False, reserve_flag=False)
        auth_service.create_role("aaaa3", "aaaa3", enable_flag=True, reserve_flag=True)
        roles = auth_service.fetch_roles()
        self.assertEqual(len(roles), 3)
        roles = auth_service.fetch_roles(reserve_flag=True)
        self.assertEqual(len(roles), 1)
        roles = auth_service.fetch_roles(enable_flag=True)
        self.assertEqual(len(roles), 2)
        roles = auth_service.fetch_roles(enable_flag=False, reserve_flag=False)
        self.assertEqual(len(roles), 1)

    def test_fetch_useroperations(self):
        self.set_token()
        user1 = auth_service.create_user("upp1", "123456", False)
        token = auth_service.login("upp1", "123456", 123456)
        context.set_token(token)
        role1 = auth_service.create_role("ddddcc2d22", "ddddcc2d22")
        role1.create_roleoperation("create")
        role1.create_roleoperation("update")
        role2 = auth_service.create_role("ddddcc333", "ddddcc333")
        role2.create_roleoperation("delete")
        role2.create_roleoperation("view")
        role2.create_roleoperation("update")
        auth_service.create_userrole(user1.key(), role1.key())
        useroperations = auth_service.fetch_useroperations(user1.key())
        self.assertEqual(len(useroperations), 2)
        self.assertIn('update', useroperations)
        auth_service.create_userrole(user1.key(), role2.key())
        useroperations = auth_service.fetch_useroperations(user1.key())
        self.assertEqual(len(useroperations), 4)
        self.assertIn('view', useroperations)        
        
    @classmethod
    def tearDownClass(cls):        
        dbpool.drop_db(orm_config.get_default_dbinfo())
