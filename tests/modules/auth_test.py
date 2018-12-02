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

from ssguan import config
from ssguan.commons import database, dao, webb, error, security, \
    typeutils
from ssguan.commons.dao import Model, LengthError, UniqueError, LinkedError, \
    ChoiceError
from ssguan.modules import sysprop, auth
from ssguan.modules.auth import LoginFailedError, UserPermission, ResourceItem, Resource, Role, \
    OldPasswordError, User
from tests.common.webb_test import WebTestCase


class AuthReqHandlerTestCase(WebTestCase):

    @classmethod
    def setUpClass(cls):
        WebTestCase.setUpClass()
        auth.install_module()
        cls.ctx = config.webbCFG.get_settings()["route_context"]

    def get_handlers(self):
        class PrepareReqHandler(auth.AuthReqHandler):
            @webb.dec_rtn
            def get(self):
                token = self.get_current_user()
                return token

        handlers = config.webbCFG.get_handlers()
        handlers.append(("/prepare", PrepareReqHandler))
        return handlers

    def login(self, loginName, password, lopuKey, headers):
        loginName = security.rsa_encrypt(loginName, lopuKey).encode("hex")
        password = security.rsa_encrypt(password, lopuKey).encode("hex")
        args = {"loginName": loginName, "loginPassword": password}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch("%s/auth/login" % self.ctx, method="POST",
                              body=args, headers=headers)
        return response

    def get_lopukey_and_headers(self, headers=None):
        response = self.fetch("/prepare", headers=headers)
        body = self.get_response_body(response).data
        headers = response.headers.get_list("Set-Cookie")
        headers = {"Cookie": headers[0]}
        return (body['lopuKey'], headers)

    def login_superadmin(self):
        (lopuKey, headers) = self.get_lopukey_and_headers()
        self.login(User.ROOT_ACCOUNT_NAME,
                   User.ROOT_ACCOUNT_NAME, lopuKey, headers)
        headers = self.get_lopukey_and_headers(headers=headers)[1]
        return headers

    @classmethod
    def tearDownClass(cls):
        auth.uninstall_module()
        WebTestCase.tearDownClass()


class UserTest(unittest.TestCase):

    class TModel(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        a = dao.StringProperty("a")

    class TModel2(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        a = dao.StringProperty("a")

    class TModel3(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        a = dao.StringProperty("a")

    class TModel4(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        a = dao.StringProperty("a")

    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        auth.install_module()
        cls.TModel.create_schema()
        cls.TModel2.create_schema()
        cls.TModel3.create_schema()
        cls.TModel4.create_schema()

    def test_create_user(self):
        try:
            auth.create_user("marry", "m_a@a.com", "ma",
                             "123", False, User.ID_ROOT)
            self.assertTrue(False)
        except LengthError, e:
            self.assertEqual(e.arguments["label"], "password")

        try:
            auth.create_user("marry", "m_a@a.com", "ma",
                             "1233333", False, User.ID_ROOT)
            self.assertTrue(False)
        except LengthError, e:
            self.assertEqual(e.arguments['label'], "accountName")

        user1 = auth.create_user("marry", "m_a@a.com",
                                 "maa", "123456", False, User.ID_ROOT)
        self.assertIsNotNone(user1.key())
        user2 = auth.get_user(User.ID_ROOT, user1.key())
        self.assertEqual(user1.u_name, user2.u_name)
        self.assertEqual(user1.u_email, user2.u_email)
        self.assertEqual(user1.u_account, user2.u_account)
        self.assertEqual(user1.u_password, user2.u_password)
        self.assertEqual(user1.disabled, user2.disabled)
        self.assertFalse(user1.disabled)
        self.assertEqual(user2.logined_times, 0)
        self.assertIsNone(user2.last_logined_time)
        try:
            auth.create_user("marry", "m_a@a.com", "maa",
                             "123444", False, User.ID_ROOT)
            self.assertTrue(False)
        except UniqueError, e:
            self.assertEqual(e.arguments['label'], "accountName")

    def test_get_user(self):
        auth.create_user("marry", "m_a1@a.com", "ma1",
                         "123456", False, User.ID_ROOT)
        user1 = auth.get_user(User.ID_ROOT, u_account="ma1")
        self.assertEqual(user1.u_password,
                         security.str_to_sha256_hex("123456"))
        self.assertEqual(user1.u_email, "m_a1@a.com")
        user1 = auth.get_user(User.ID_ROOT, user_id=user1.key())
        self.assertEqual(user1.u_password,
                         security.str_to_sha256_hex("123456"))
        self.assertEqual(user1.u_email, "m_a1@a.com")

    def test_get_user_display_name(self):
        auth.create_user("marry1111", "m_a1@a.com", "ma112",
                         "123456", False, User.ID_ROOT)
        user1 = auth.get_user(User.ID_ROOT, u_account="ma112")
        display_name = user1.get_user_display_name()
        self.assertEqual(display_name, "marry1111")
        user2 = auth.create_user(
            "", "m_a@a.com", "maa2", "123456", False, User.ID_ROOT)
        display_name = display_name = user2.get_user_display_name()
        self.assertEqual(display_name, "maa2")

    def test_update_user_password(self):
        auth.create_user("", "m_a11@a.com", "mffdaacc",
                         "123456", False, User.ID_ROOT)
        user1 = auth.get_user(User.ID_ROOT, u_account="mffdaacc")
        auth.update_user_password(
            user1.key(), "123456", "12345678", True, User.ID_ROOT)
        user1 = auth.get_user(User.ID_ROOT, user_id=user1.key())
        self.assertEqual(user1.u_password,
                         security.str_to_sha256_hex("12345678"))
        try:
            auth.update_user_password(
                user1.key(), "1234561", "12345678", True, User.ID_ROOT)
            self.assertTrue(False)
        except OldPasswordError:
            self.assertTrue(True)

        user1 = auth.get_user(User.ID_ROOT, user_id=user1.key())
        self.assertEqual(user1.u_password,
                         security.str_to_sha256_hex("12345678"))

    def test_disable_user(self):
        u1 = auth.create_user("adfasdf", "m_asdfa11@a.com",
                              "maaccad", "123456", False, User.ID_ROOT)
        u2 = auth.disable_user(u1.key(), True, User.ID_ROOT)
        self.assertTrue(u2.disabled)
        u2 = auth.disable_user(u1.key(), False, User.ID_ROOT)
        self.assertFalse(u2.disabled)

    def test_login(self):
        token = auth.login("", "", is_anonymous=True)
        self.assertTrue(token.is_anonymous())
        user1 = auth.create_user("tuserjack", "", "tuser", "123456",
                                 False, User.ID_ROOT, u_preferences={"prefL": "zh"})
        token = auth.login("tuser", "123456")
        self.assertEqual(token.user_id, user1.key())
        token = auth.login("tuser", "123456")
        self.assertEqual(token.userName, "tuserjack")
        self.assertEqual(token.accountName, "tuser")
        self.assertEqual(token.prefL, "zh")
        self.assertEqual(token.to_dict()['prefL'], "zh")
        user2 = auth.get_user(User.ID_ROOT, token.user_id)
        self.assertEqual(user2.logined_times, 2)
        try:
            token = auth.login("tuser", "1234567")
            self.assertTrue(False)
        except LoginFailedError:
            self.assertTrue(True)
        try:
            token = auth.login("tuser33", "1234567")
            self.assertTrue(False)
        except LoginFailedError:
            self.assertTrue(True)

    def test_create_role(self):
        role = auth.create_role("eeeeee", User.ID_ROOT)
        role1 = auth.get_role(User.ID_ROOT, role.key())
        self.assertEqual(role.role_name, role1.role_name)
        try:
            role = auth.create_role("eeeeee", User.ID_ROOT)
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)
        role = auth.create_role("zzzzz", User.ID_ROOT, reserved=True)
        role = auth.get_role(User.ID_ROOT, role_name="zzzzz")
        self.assertEqual(role.reserved, True)

    def test_get_role(self):
        role = auth.create_role("fff", User.ID_ROOT)
        role1 = auth.get_role(User.ID_ROOT, role.key())
        self.assertEqual(role.role_name, role1.role_name)
        role1 = auth.get_role(User.ID_ROOT, role_name="fff")
        self.assertEqual(role.key(), role1.key())

    def test_fetch_roleoperations(self):
        role = auth.create_role("a33", User.ID_ROOT)
        role2 = auth.get_role(User.ID_ROOT, role.key())
        role2.create_roleoperation("111", "tm", User.ID_ROOT)
        role2.create_roleoperation("222", "tm", User.ID_ROOT)
        ops = role2.fetch_roleoperations()
        self.assertEqual(len(ops), 2)

    def test_delete_role(self):
        role = auth.create_role("rrrr", User.ID_ROOT)
        role1 = auth.get_role(User.ID_ROOT, role.key())
        user1 = auth.create_user(
            "tuserrole", "", "turols", "123456", False, User.ID_ROOT)
        auth.create_userpermission(
            user1.key(), role1.key(), Resource.ID_ALL, User.ID_ROOT)
        try:
            auth.delete_role(role1.key(), User.ID_ROOT)
            self.assertTrue(False)
        except LinkedError, e:
            self.assertEqual(e.arguments['linklabel'], 'user')

        role = auth.create_role("rrrr3zz3", User.ID_ROOT)
        role2 = auth.get_role(User.ID_ROOT, role.key())
        role2.create_roleoperation("111", "tm", User.ID_ROOT)
        role2.create_roleoperation("222", "tm", User.ID_ROOT)
        auth.delete_role(role2.key(), User.ID_ROOT)
        role = auth.get_role(User.ID_ROOT, role2.key())
        self.assertIsNone(role)
        ops = role2.fetch_roleoperations()
        self.assertEqual(len(ops), 0)

    def test_create_roleoperation(self):
        role = auth.create_role("ro33", User.ID_ROOT)
        role2 = auth.get_role(User.ID_ROOT, role.key())
        role2.create_roleoperation("111", "tm", User.ID_ROOT)
        try:
            role2.create_roleoperation("111", "tm", User.ID_ROOT)
            self.assertTrue(False)
        except UniqueError, e:
            self.assertEqual(e.arguments["label"], "operationKey")

    def test_delete_roleoperations(self):
        role = auth.create_role("roaa33", User.ID_ROOT)
        role2 = auth.get_role(User.ID_ROOT, role.key())
        role2.create_roleoperation("tm", "111", User.ID_ROOT)
        role2.delete_roleoperations(None)
        ros = role2.fetch_roleoperations()
        self.assertEqual(len(ros), 0)
        role2.create_roleoperation("tm", "222", User.ID_ROOT)
        role2.delete_roleoperations(
            None, model_class="tm", operation_key="222")
        ros = role2.fetch_roleoperations()
        self.assertEqual(len(ros), 0)

    def test_create_resource(self):
        res = auth.create_resource(
            "rrr", User.ID_ROOT, enabled=True, reserved=False)
        res1 = auth.get_resource(res.key(), User.ID_ROOT)
        self.assertEqual(res1.resource_name, "rrr")
        self.assertEqual(res1.reserved, False)
        self.assertEqual(res1.enabled, True)
        try:
            res = auth.create_resource(
                "rrr", User.ID_ROOT, enabled=True, reserved=False)
            self.assertTrue(False)
        except UniqueError:
            self.assertTrue(True)

    def test_get_resource(self):
        res = auth.create_resource(
            "cccc33cc", User.ID_ROOT, enabled=True, reserved=False)
        res1 = auth.get_resource(res.key(), User.ID_ROOT)
        self.assertEqual(res1.resource_name, "cccc33cc")

    def test_create_resourceitem(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            a = dao.StringProperty("a")
        res = auth.create_resource(
            "res1", User.ID_ROOT, enabled=True, reserved=False)
        res.create_resourceitem(TModel, ResourceItem.FORMAT_VALUE, "11", None)
        res.create_resourceitem(TModel, ResourceItem.FORMAT_VALUE, "22", None)
        query = ResourceItem.all()
        query.filter("resitem_value =", "11")
        query.filter("resource_id =", res.key())
        self.assertEqual(query.count(), 1)
        try:
            res.create_resourceitem(TModel, "fffff", "11", None)
            self.assertTrue(False)
        except ChoiceError:
            self.assertTrue(True)

    def test_update_resourceitem(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            a = dao.StringProperty("a")
        res = auth.create_resource(
            "res2", User.ID_ROOT, enabled=True, reserved=False)
        res.create_resourceitem(TModel, ResourceItem.FORMAT_VALUE, "22", None)
        query = ResourceItem.all()
        query.filter("resitem_value =", "22")
        query.filter("resource_id =", res.key())
        self.assertEqual(query.count(), 1)
        resitem = query.get()
        res.update_resourceitem(resitem.key(), TModel,
                                ResourceItem.FORMAT_VALUE, "33", None)
        res.update_resourceitem(resitem.key(), TModel,
                                ResourceItem.FORMAT_VALUE, "33", None)
        query = ResourceItem.all()
        query.filter("resitem_value =", "33")
        query.filter("resource_id =", res.key())
        resitem = query.get()
        try:
            res.update_resourceitem(resitem.key(), TModel, "fffff", "11", None)
            self.assertTrue(False)
        except ChoiceError:
            self.assertTrue(True)

    def test_delete_resourceitems(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            a = dao.StringProperty("a")
        res = auth.create_resource(
            "res3", User.ID_ROOT, enabled=True, reserved=False)
        res.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "22", User.ID_ROOT)
        res.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "44", User.ID_ROOT)
        res.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "55", User.ID_ROOT)
        query = ResourceItem.all()
        query.filter("resource_id =", res.key())
        self.assertEqual(query.count(), 3)
        res.delete_resourceitems(None)
        query = ResourceItem.all()
        query.filter("resource_id =", res.key())
        self.assertEqual(query.count(), 0)

    def test_fetch_resourceitems(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            a = dao.StringProperty("a")
        res = auth.create_resource(
            "res4", User.ID_ROOT, enabled=True, reserved=False)
        res.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "22", User.ID_ROOT)
        res.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "44", User.ID_ROOT)
        res.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "55", User.ID_ROOT)
        ris = res.fetch_resourceitems()
        self.assertEqual(len(ris), 3)

    def test_delete_resource(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            a = dao.StringProperty("a")
        role = auth.create_role("rrrr33", User.ID_ROOT)
        resource = auth.create_resource("res55", User.ID_ROOT)
        user1 = auth.create_user(
            "tuserrole11", "", "turol11s", "123456", False, User.ID_ROOT)
        auth.create_userpermission(
            user1.key(), role.key(), resource.key(), User.ID_ROOT)
        try:
            auth.delete_resource(resource.key(), User.ID_ROOT)
            self.assertTrue(False)
        except LinkedError, e:
            self.assertEqual(e.arguments['linklabel'], 'user')

        resource = auth.create_resource("res56", User.ID_ROOT)
        resource.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "55", User.ID_ROOT)
        resource.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "66", User.ID_ROOT)
        auth.delete_resource(resource.key(), User.ID_ROOT)
        resource1 = auth.get_resource(resource.key(), User.ID_ROOT)
        self.assertIsNone(resource1)
        query = ResourceItem.all()
        query.filter("resource_id =", resource.key())
        self.assertEqual(query.count(), 0)

    def test_create_userpermission(self):
        user1 = auth.create_user(
            "upp1", "", "upp1", "123456", False, User.ID_ROOT)
        role1 = auth.create_role("ddddd", User.ID_ROOT)
        auth.create_userpermission(
            user1.key(), role1.key(), Resource.ID_ALL, User.ID_ROOT)
        query = UserPermission.all()
        query.filter("user_id =", user1.key())
        query.filter("role_id =", role1.key())
        self.assertEqual(query.count(), 1)
        try:
            auth.create_userpermission(
                user1.key(), role1.key(), Resource.ID_ALL, User.ID_ROOT)
            self.assertFalse(True)
        except UniqueError, e:
            self.assertEqual(e.arguments["label"], "resourceKey")

        role2 = auth.create_role("eeee", User.ID_ROOT)
        res2 = auth.create_resource("eeeee", User.ID_ROOT)
        perm = auth.create_userpermission(
            user1.key(), role2.key(), res2.key(), User.ID_ROOT)
        up = UserPermission.get_by_key(perm.key())
        self.assertEqual(up.user_id, user1.key())
        self.assertEqual(up.role_id, role2.key())
        self.assertEqual(up.resource_id, res2.key())

    def test_delete_userpermissions(self):
        user1 = auth.create_user(
            "upp1", "", "uppcc122", "123456", False, User.ID_ROOT)
        role1 = auth.create_role("ddddccd22", User.ID_ROOT)
        up = auth.create_userpermission(
            user1.key(), role1.key(), Resource.ID_ALL, User.ID_ROOT)
        auth.delete_userpermissions(User.ID_ROOT, user_id=user1.key())
        up = UserPermission.get_by_key(up.key())
        self.assertIsNone(up, User.ID_ROOT)
        res1 = auth.create_resource("c1", User.ID_ROOT)
        up = auth.create_userpermission(
            user1.key(), role1.key(), res1.key(), User.ID_ROOT)
        res2 = auth.create_resource("c2", User.ID_ROOT)
        up = auth.create_userpermission(
            user1.key(), role1.key(), res2.key(), User.ID_ROOT)
        auth.delete_userpermissions(User.ID_ROOT, user_id=user1.key(
        ), role_id=role1.key(), resource_id=res2.key())
        up = UserPermission.get_by_key(up.key())
        self.assertIsNone(up, User.ID_ROOT)
        res3 = auth.create_resource("c3", User.ID_ROOT)
        up = auth.create_userpermission(
            user1.key(), role1.key(), res3.key(), User.ID_ROOT)
        auth.delete_userpermissions(
            User.ID_ROOT, user_id=user1.key(), role_id=role1.key())
        query = UserPermission.all()
        query.filter("user_id =", user1.key())
        self.assertEqual(query.count(), 0)

    def test_fetch_roles(self):
        query = Role.all()
        query.delete(None)
        auth.create_role("aaaa2", User.ID_ROOT, enabled=True, reserved=False)
        auth.create_role("aaaa1", User.ID_ROOT, enabled=False, reserved=False)
        auth.create_role("aaaa3", User.ID_ROOT, enabled=True, reserved=True)
        roles = auth.fetch_roles(User.ID_ROOT)
        self.assertEqual(len(roles), 3)
        roles = auth.fetch_roles(User.ID_ROOT, reserved=True)
        self.assertEqual(len(roles), 1)
        roles = auth.fetch_roles(User.ID_ROOT, enabled=True)
        self.assertEqual(len(roles), 2)
        roles = auth.fetch_roles(User.ID_ROOT, enabled=False, reserved=False)
        self.assertEqual(len(roles), 1)

    def test_fetch_resources(self):
        query = Resource.all()
        query.delete(None)
        auth.create_resource("c2", User.ID_ROOT, enabled=True, reserved=False)
        auth.create_resource("c3", User.ID_ROOT, enabled=True, reserved=True)
        auth.create_resource("c1", User.ID_ROOT, enabled=False, reserved=True)
        resources = auth.fetch_resources(User.ID_ROOT)
        self.assertEqual(len(resources), 3)
        resources = auth.fetch_resources(User.ID_ROOT, reserved=False)
        self.assertEqual(len(resources), 1)
        resources = auth.fetch_resources(User.ID_ROOT, enabled=True)
        self.assertEqual(len(resources), 2)
        resources = auth.fetch_resources(
            User.ID_ROOT, enabled=False, reserved=True)
        self.assertEqual(len(resources), 1)

    def test_fetch_user_permissions(self):
        class TModel(Model):
            @classmethod
            def meta_domain(cls):
                return "test"
            a = dao.StringProperty("a")
        user1 = auth.create_user(
            "upp1", "", "uppc2c122", "123456", False, User.ID_ROOT)
        role1 = auth.create_role("ddddcc2d22", User.ID_ROOT)
        role1.create_roleoperation("tm", "create", User.ID_ROOT)
        role1.create_roleoperation("tm", "update", User.ID_ROOT)
        role2 = auth.create_role("ddddcc333", User.ID_ROOT)
        role2.create_roleoperation("ff", "delete", User.ID_ROOT)
        role2.create_roleoperation("ff", "view", User.ID_ROOT)
        res1 = auth.create_resource("cce2", User.ID_ROOT)
        res1.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "11", User.ID_ROOT)
        res1.create_resourceitem(
            TModel, ResourceItem.FORMAT_VALUE, "12", User.ID_ROOT)
        auth.create_userpermission(
            user1.key(), role1.key(), res1.key(), User.ID_ROOT)
        res2 = auth.create_resource("cc3", User.ID_ROOT)
        auth.create_userpermission(
            user1.key(), role1.key(), res2.key(), User.ID_ROOT)
        ups = auth.fetch_userpermissions(user1.key(), "tm", "create")
        self.assertEqual(len(ups), 2)
        ups = auth.fetch_userpermissions(user1.key(), "ff", "delete")
        self.assertEqual(len(ups), 0)

    def test_has_permission(self):
        user1 = auth.create_user(
            "uppcc1", "", "uppc2c12111", "123456", False, User.ID_ROOT)
        role1 = auth.create_role("eee222", User.ID_ROOT)
        role1.create_roleoperation(self.TModel, "create", User.ID_ROOT)
        role1.create_roleoperation(
            self.TModel.get_modelname(), "update", User.ID_ROOT)
        auth.create_userpermission(
            user1.key(), role1.key(), Resource.ID_ALL, User.ID_ROOT)
        b = auth.has_permission(user1.key(), self.TModel, "eee33c222")
        self.assertFalse(b)
        b = auth.has_permission(user1.key(), self.TModel, "create")
        self.assertTrue(b)
        b = auth.has_permission(user1.key(), self.TModel,
                                "update", model_id="11")
        self.assertTrue(b)
        query = self.TModel2.all()
        query.delete(None)
        role2 = auth.create_role("fff222", User.ID_ROOT)
        role2.create_roleoperation(self.TModel2, "create", User.ID_ROOT)
        role2.create_roleoperation("test_tmodel2", "update", User.ID_ROOT)
        role2.create_roleoperation(self.TModel3, "update", User.ID_ROOT)
        role2.create_roleoperation(self.TModel4, "update", User.ID_ROOT)
        res1 = auth.create_resource("ccccc2", User.ID_ROOT)
        res1.create_resourceitem(self.TModel3, ResourceItem.FORMAT_QFILTER, {
                                 "property_op": "created_by =", "value": "#creator"}, User.ID_ROOT)
        res1.create_resourceitem(self.TModel4, ResourceItem.FORMAT_QFILTER, [
                                 {"property_op": "created_by =", "value": "#creator"}, {"property_op": "a =", "value": "#value"}], User.ID_ROOT)
        auth.create_userpermission(
            user1.key(), role2.key(), res1.key(), User.ID_ROOT)
        b = auth.has_permission(user1.key(), self.TModel2, "create")
        self.assertTrue(b)
        self.TModel2(a="eeee").create(User.ID_ROOT, key="11")
        self.TModel2(a="ffff").create(User.ID_ROOT, key="33")
        b = auth.has_permission(user1.key(), self.TModel2, "create")
        self.assertTrue(b)
        b = auth.has_permission(user1.key(), self.TModel2, "update")
        self.assertTrue(b)
        b = auth.has_permission(
            user1.key(), self.TModel2, "update", model_id="11")
        self.assertFalse(b)
        res1.create_resourceitem(
            self.TModel2, ResourceItem.FORMAT_VALUE, "12", User.ID_ROOT)
        b = auth.has_permission(
            user1.key(), self.TModel2, "update", model_id="11")
        self.assertFalse(b)
        res1.create_resourceitem(
            self.TModel2, ResourceItem.FORMAT_VALUE, "11", User.ID_ROOT)
        b = auth.has_permission(
            user1.key(), self.TModel2, "update", model_id="11")
        self.assertTrue(b)
        b = auth.has_permission(
            user1.key(), self.TModel2, "update", model_id="33")
        self.assertFalse(b)
        query = self.TModel3.all()
        query.delete(User.ID_ROOT)
        self.TModel3(a="eeee").create(user1.key(), key="11")
        self.TModel3(a="ffff").create("6", key="33")
        b = auth.has_permission(user1.key(), self.TModel3,
                                "create", model_id="33", creator=user1.key())
        self.assertFalse(b)
        b = auth.has_permission(user1.key(), self.TModel3,
                                "update", model_id="33", creator=user1.key())
        self.assertFalse(b)
        b = auth.has_permission(
            user1.key(), self.TModel3, "update", model_id="11")
        self.assertFalse(b)
        b = auth.has_permission(user1.key(), self.TModel3,
                                "update", model_id="11", creator=user1.key())
        self.assertTrue(b)
        query = self.TModel4.all()
        query.delete(User.ID_ROOT)
        self.TModel4(a="eeee").create(user1.key(), key="tttt111")
        self.TModel4(a="ffff").create("6", key="ttt222")
        b = auth.has_permission(user1.key(), self.TModel4,
                                "update", model_id="tttt111")
        self.assertFalse(b)
        b = auth.has_permission(user1.key(), self.TModel4, "update",
                                model_id="tttt111", creator=user1.key(), value="eeee")
        self.assertTrue(b)
        b = auth.has_permission(user1.key(), self.TModel4,
                                "update", model_id="tttt111", creator=user1.key())
        self.assertFalse(b)

    @classmethod
    def tearDownClass(cls):
        auth.uninstall_module()
        cls.TModel.delete_schema()
        cls.TModel2.delete_schema()
        cls.TModel3.delete_schema()
        cls.TModel4.delete_schema()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())


class AuthReqHandlerTest(WebTestCase):

    @classmethod
    def setUpClass(cls):
        WebTestCase.setUpClass()
        auth.install_module()

    def get_handlers(self):

        class CurrentUserHandler(auth.AuthReqHandler):
            @webb.dec_rtn
            def get(self, *args, **kwargs):
                r = {}
                token = self.get_current_user()
                r['token'] = token
                r['pid'] = self.session.sid
                return r

        class DecArgReqHandler(auth.AuthReqHandler):

            @webb.dec_rtn
            def get(self, *args, **kwargs):
                uri, args1 = self.decode_arguments_uri()
                if uri not in ['mm', 'gg']:
                    raise error.Error("uri is not correct.")
                return args1 if len(args1) > 0 else {"zero": True}

            @webb.dec_rtn
            def post(self, *args, **kwargs):
                argsuri = self.decode_arguments_uri()[1]
                argsbody = self.decode_arguments_body()
                if len(argsuri) == 0 and len(argsbody) == 0:
                    return {"zero11": True}
                else:
                    return typeutils.dict_add(argsuri, argsbody)

            @webb.dec_rtn
            def put(self, *args, **kwargs):
                argsuri = self.decode_arguments_uri()[1]
                argsbody = self.decode_arguments_body()
                if len(argsuri) == 0 and len(argsbody) == 0:
                    return {"zero22": True}
                else:
                    return typeutils.dict_add(argsuri, argsbody)

            @webb.dec_rtn
            def delete(self, *args, **kwargs):
                argsuri = self.decode_arguments_uri()[1]
                if len(argsuri) == 0:
                    return {"zero33": True}
                else:
                    return argsuri

        return [
            ("/cur", CurrentUserHandler),
            ("/decarg", DecArgReqHandler),
            ("/decarg/([^/]+)", DecArgReqHandler),
        ]

    def test_prepare(self):
        config.webbCFG.get_session_configs()["timeout"] = 180
        response1 = self.fetch("/cur")
        body1 = self.get_response_body(response1).data
        self.assertEqual(body1['token']['anonymous'], True)
        headers = response1.headers.get_list("Set-Cookie")
        headers = {"Cookie": headers[0]}
        response2 = self.fetch("/cur", headers=headers)
        body2 = self.get_response_body(response2).data
        self.assertEqual(body1['pid'], body2['pid'])
        lopuKey1 = body1['token']['lopuKey']
        lopuKey2 = body2['token']['lopuKey']
        self.assertEqual(lopuKey1, lopuKey2)

    def test_decode_arguments_uri(self):
        args = typeutils.obj_to_json({"a": False, "c": "cstring"})
        args = security.str_to_base64(args, remove_cr=True)
        response = self.fetch("/decarg/mm?%s" % args)
        self.assertEqual(200, response.code)
        body = self.get_response_body(response)
        self.assertEqual(body.data['a'], False)
        self.assertEqual(body.data['c'], "cstring")
        response = self.fetch("/decarg/gg")
        body = self.get_response_body(response)
        self.assertEqual(body.data['zero'], True)

    def test_decode_arguments_body(self):
        argsuri = typeutils.obj_to_json({"a11": True, "c11": "cstring12"})
        argsuri = security.str_to_base64(argsuri, remove_cr=True)
        argsbody = typeutils.obj_to_json({"a1": False, "c1": "cstring"})
        argsbody = security.str_to_base64(argsbody, remove_cr=True)
        response = self.fetch("/decarg?%s" %
                              argsuri, method="POST", body=argsbody)
        body = self.get_response_body(response)
        self.assertEqual(body.data['a1'], False)
        self.assertEqual(body.data['c1'], "cstring")
        self.assertEqual(body.data['a11'], True)
        self.assertEqual(body.data['c11'], "cstring12")
        args = security.str_to_base64("", remove_cr=True)
        response = self.fetch("/decarg?", method="POST", body=args)
        body = self.get_response_body(response)
        self.assertEqual(body.data['zero11'], True)

        argsuri = typeutils.obj_to_json({"a21": True, "c21": "cstring22"})
        argsuri = security.str_to_base64(argsuri, remove_cr=True)
        argsbody = typeutils.obj_to_json({"a2": False, "c2": "cstring"})
        argsbody = security.str_to_base64(argsbody, remove_cr=True)
        response = self.fetch("/decarg?%s" %
                              argsuri, method="PUT", body=argsbody)
        body = self.get_response_body(response)
        self.assertEqual(body.data['a21'], True)
        self.assertEqual(body.data['c21'], "cstring22")
        self.assertEqual(body.data['a2'], False)
        self.assertEqual(body.data['c2'], "cstring")
        args = security.str_to_base64("", remove_cr=True)
        response = self.fetch("/decarg?", method="PUT", body=args)
        body = self.get_response_body(response)
        self.assertEqual(body.data['zero22'], True)

        argsuri = typeutils.obj_to_json({"a3": False, "c3": "cstring"})
        argsuri = security.str_to_base64(argsuri, remove_cr=True)
        response = self.fetch("/decarg?%s" % argsuri, method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(body.data['a3'], False)
        self.assertEqual(body.data['c3'], "cstring")

        args = security.str_to_base64("", remove_cr=True)
        response = self.fetch("/decarg", method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(body.data['zero33'], True)

    @classmethod
    def tearDownClass(cls):
        auth.uninstall_module()
        WebTestCase.tearDownClass()


class UserHandlerTest(AuthReqHandlerTestCase):

    @classmethod
    def setUpClass(cls):
        AuthReqHandlerTestCase.setUpClass()

    def test_login(self):
        auth.create_user("test11", "test1@a.com", "test11",
                         "password11", False, User.ID_ROOT)
        args = {"loginName": "test1", "loginPassword": ""}
        response = self.fetch("%s/auth/login" % self.ctx, method="POST",
                              body=typeutils.obj_to_json(args))
        body = self.get_response_body(response)
        self.assertEqual(error.CODE_UNKNOWN, body['status'])
        self.assertEqual("Incorrect padding", body['message'])
        lopuKey = self.get_lopukey_and_headers()[0]
        response = self.login("test11", "password11", lopuKey, None)
        body = self.get_response_body(response)
        self.assertEqual("Decryption failed", body['message'])
        (lopuKey, headers) = self.get_lopukey_and_headers()
        response = self.login("test11", "password11", lopuKey, headers)
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['anonymous'], False)
        self.assertEqual(body['accountName'], "test11")
        response = self.fetch("/prepare", headers=headers)
        body1 = self.get_response_body(response).data
        self.assertEqual(body1['anonymous'], False)
        self.assertEqual(body1['accountName'], "test11")

    def test_logout(self):
        auth.create_user("test12", "test12@a.com", "test12",
                         "password12", False, User.ID_ROOT)
        (lopuKey, headers) = self.get_lopukey_and_headers()
        response = self.login("test12", "password12", lopuKey, headers)
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['anonymous'], False)
        self.assertEqual(body['accountName'], "test12")
        response = self.fetch("%s/auth/logout" % self.ctx, method="POST",
                              body=security.str_to_base64("{}", True), headers=headers)
        body = self.get_response_body(response).data
        self.assertEqual(body, True)
        response = self.fetch("/prepare", headers=headers)
        body1 = self.get_response_body(response).data
        self.assertEqual(body1['anonymous'], True)

    def test_signup(self):
        (lopuKey, headers) = self.get_lopukey_and_headers()
        loginName = security.rsa_encrypt("test15", lopuKey).encode("hex")
        password = security.rsa_encrypt("password15", lopuKey).encode("hex")
        email = security.rsa_encrypt("aa@email15.com", lopuKey).encode("hex")
        args = {"accountName": loginName,
                "userEmail": email, "loginPassword": password}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch("%s/auth/signup" % self.ctx, method="POST",
                              body=args, headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        self.assertEqual(body.data, True)
        user1 = auth.get_user(User.ID_ROOT, u_account="test15")
        self.assertEqual(user1.u_email, "aa@email15.com")
        (lopuKey, headers) = self.get_lopukey_and_headers()
        response = self.login("test15", "password15", lopuKey, headers)
        body = self.get_response_body(response).data
        self.assertEqual(body['anonymous'], False)
        self.assertEqual(body['accountName'], "test15")

    def test_updateuserpassword(self):
        u1 = auth.create_user("test20", "test12@a.com",
                              "test20", "password20", False, User.ID_ROOT)
        (lopuKey, headers) = self.get_lopukey_and_headers()
        password = security.rsa_encrypt("password20", lopuKey).encode("hex")
        newPassword = security.rsa_encrypt("password50", lopuKey).encode("hex")
        args = {"oldPassword": password, "newPassword": newPassword}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/auth/updatepwd" % self.ctx, method="POST", body=args, headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(1050, body.status)
        self.assertIn("Session expired", body.message)
        (lopuKey, headers) = self.get_lopukey_and_headers()
        response = self.login("test20", "password20", lopuKey, headers)
        body = self.get_response_body(response).data
        self.assertEqual(body['anonymous'], False)
        (lopuKey, headers) = self.get_lopukey_and_headers(headers=headers)
        password = security.rsa_encrypt("password20", lopuKey).encode("hex")
        newPassword = security.rsa_encrypt("password50", lopuKey).encode("hex")
        args = {"oldPassword": password, "newPassword": newPassword}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/auth/updatepwd" % self.ctx, method="POST", body=args, headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        self.assertEqual(body.data, True)
        token = auth.login("test20", "password50", False)
        self.assertEqual(u1.key(), token.user_id)
