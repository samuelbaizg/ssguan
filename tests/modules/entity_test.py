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
from ssguan.commons import database, dao, webb, security, typeutils
from ssguan.commons.dao import Model, RequiredError
from ssguan.modules import sysprop, auth, entity
from ssguan.modules.auth import RoleOperation, Resource, UnauthorizedError, \
    ResourceItem, User
from tests.modules.auth_test import AuthReqHandlerTestCase


class MoadoModel(Model):
    @classmethod
    def meta_domain(cls):
        return "test"
    f_str = dao.StringProperty("fStr")
    f_int = dao.IntegerProperty("fInt")


class MoadoModel2(Model):
    @classmethod
    def meta_domain(cls):
        return "test"
    f_str = dao.StringProperty("fStr")
    f_int = dao.IntegerProperty("fInt")

    def mcb2(self):
        self.fff = "ffss"


class MoadoModel3(Model):
    @classmethod
    def meta_domain(cls):
        return "test"
    f_str = dao.StringProperty("fStr")
    f_int = dao.IntegerProperty("fInt")

    def mcb(self):
        self.eee = "eee111"


class EntityTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        auth.install_module()
        MoadoModel.create_schema()
        MoadoModel2.create_schema()
        MoadoModel3.create_schema()
        cls.testuser = auth.create_user(
            "testmoado", "testmoado@e.m", "testmoado", "testmoado", False, User.ID_ROOT)
        cls.testuser_noperm = auth.create_user(
            "testmoadonoperm", "testmoadonoperm@e.m", "testmoadonoperm", "testmoado", False, User.ID_ROOT)
        cls.role = auth.create_role("rol1", User.ID_ROOT)
        cls.role.create_roleoperation(
            MoadoModel, RoleOperation.OPERATION_READ, User.ID_ROOT)
        cls.role.create_roleoperation(
            MoadoModel, RoleOperation.OPERATION_UPDATE, User.ID_ROOT)
        cls.role.create_roleoperation(
            MoadoModel, RoleOperation.OPERATION_DELETE, User.ID_ROOT)
        cls.role.create_roleoperation(
            MoadoModel, RoleOperation.OPERATION_CREATE, User.ID_ROOT)
        auth.create_userpermission(
            cls.testuser.key(), cls.role.key(), Resource.ID_ALL, User.ID_ROOT)

        cls.role2 = auth.create_role("rol2", User.ID_ROOT)
        cls.role2.create_roleoperation(
            MoadoModel2, RoleOperation.OPERATION_READ, User.ID_ROOT)
        cls.role2.create_roleoperation(
            MoadoModel2, RoleOperation.OPERATION_CREATE, User.ID_ROOT)
        cls.role2.create_roleoperation(
            MoadoModel2, RoleOperation.OPERATION_UPDATE, User.ID_ROOT)
        cls.resource = auth.create_resource("model_1,2,3", User.ID_ROOT)
        auth.create_userpermission(
            cls.testuser.key(), cls.role2.key(), cls.resource.key(), User.ID_ROOT)

        cls.role3 = auth.create_role("rol3", User.ID_ROOT)
        cls.role3.create_roleoperation(
            MoadoModel3, RoleOperation.OPERATION_READ, User.ID_ROOT)
        cls.role3.create_roleoperation(
            MoadoModel3, RoleOperation.OPERATION_CREATE, User.ID_ROOT)
        auth.create_userpermission(
            cls.testuser.key(), cls.role3.key(), Resource.ID_ALL, User.ID_ROOT)

        cls.testuser4 = auth.create_user(
            "testmoadonope444rm", "testmoadon44perm@e.m", "testmo44operm", "testmo44", False, User.ID_ROOT)
        cls.resource4 = auth.create_resource("model_33333", User.ID_ROOT)
        cls.role4 = auth.create_role("rol4", User.ID_ROOT)
        cls.role4.create_roleoperation(
            MoadoModel3, RoleOperation.OPERATION_READ, User.ID_ROOT)
        auth.create_userpermission(
            cls.testuser4.key(), cls.role4.key(), cls.resource4.key(), User.ID_ROOT)

        cls.testuser5 = auth.create_user(
            "testmoadonope55rm", "testmoadono55perm@e.m", "testmoa55donoperm", "testmoado55", False, User.ID_ROOT)
        cls.role5 = auth.create_role("rol5", User.ID_ROOT)
        cls.role5.create_roleoperation(
            MoadoModel3, RoleOperation.OPERATION_READ, User.ID_ROOT)
        cls.resource5 = auth.create_resource("model_5555", User.ID_ROOT)
        auth.create_userpermission(
            cls.testuser5.key(), cls.role5.key(), cls.resource5.key(), User.ID_ROOT)

    def test_create_model(self):
        model = MoadoModel(f_str="fstr", f_int=100)
        try:
            entity.create_model(model, self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)

        model = entity.create_model(model, self.testuser.key())
        model2 = entity.get_model_by_key(
            model, model.key(), self.testuser.key())
        self.assertEqual(model.f_str, model2.f_str)

        model = MoadoModel2(f_str="fstr", f_int=100)
        try:
            entity.create_model(model, self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)

        model = entity.create_model(model, self.testuser.key())
        self.resource.create_resourceitem(
            MoadoModel2, ResourceItem.FORMAT_VALUE, model.key(), None)
        model2 = entity.get_model_by_key(
            model, model.key(), self.testuser.key())
        self.assertEqual(model.f_str, model2.f_str)

    def test_update_model(self):
        model = MoadoModel(f_str="fstr", f_int=100)
        model = model.create(None)
        try:
            entity.update_model(model, self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
        model.f_str = "fstrstr"
        model_1 = entity.update_model(model, self.testuser.key())
        self.assertEqual("fstrstr", model_1.f_str)

        model2 = MoadoModel2(f_str="fstrrr")
        model2.create(None, "22222")
        try:
            model2 = entity.update_model(model2, self.testuser.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)

        self.resource.create_resourceitem(
            MoadoModel2, ResourceItem.FORMAT_VALUE, "22222", None)
        model2.f_str = "fstrrr2222"
        model2 = entity.update_model(model2, self.testuser.key())
        model2_1 = entity.get_model_by_key(
            model2, model2.key(), self.testuser.key())
        self.assertEqual("fstrrr2222", model2_1.f_str)

        model = MoadoModel(f_str="fstr", f_int=100)
        try:
            entity.update_model(model, self.testuser.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, RequiredError)

    def test_delete_model(self):
        model = MoadoModel(f_str="fstr", f_int=100)
        try:
            entity.delete_model(model, model.key(), self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, RequiredError)
        model.create(None, "55555")
        try:
            entity.delete_model(model, model.key(), self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)

        entity.delete_model(model, model.key(), self.testuser.key())
        model = MoadoModel.get_by_key(model.key())
        self.assertIsNone(model)

        model2 = MoadoModel2(f_str="fstr", f_int=100)
        model2.create(None)
        try:
            entity.delete_model(model2, model2.key(), self.testuser.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
        model2 = MoadoModel2(f_str="fstrfstr", f_int=100)
        model2.create(None, "333")
        self.resource.create_resourceitem(
            MoadoModel2, ResourceItem.FORMAT_VALUE, "333", None)
        try:
            entity.delete_model(model2, model2.key(), self.testuser.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
        self.role2.create_roleoperation(
            MoadoModel2, RoleOperation.OPERATION_DELETE, None)
        entity.delete_model(model2, model2.key(), self.testuser.key())
        model2 = MoadoModel2.get_by_key(model2.key())
        self.assertIsNone(model2)

    def test_get_model(self):
        model = MoadoModel(f_str="fstr", f_int=100)
        model.create(None, "11")
        try:
            entity.get_model_by_key(
                MoadoModel, model.key(), self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
        model2 = entity.get_model_by_key(
            MoadoModel, model.key(), self.testuser.key())
        self.assertEqual(model.f_str, model2.f_str)
        model2 = MoadoModel2(f_str="fst33rfstr", f_int=100)
        model2.create(None, "eee")
        self.resource.create_resourceitem(
            MoadoModel2, ResourceItem.FORMAT_VALUE, "eee", None)
        model2_1 = entity.get_model_by_key(
            MoadoModel2, model2.key(), self.testuser.key())
        self.assertEqual(model2_1.f_str, model2.f_str)
        mo = entity.get_model_by_key(
            MoadoModel2, model2.key(), self.testuser.key(), MoadoModel2.mcb2)
        self.assertEqual(mo.fff, "ffss")

    def test_has_model(self):
        model = MoadoModel(f_str="fstr", f_int=100)
        model.create(None, "33333")
        try:
            entity.get_model_by_key(
                MoadoModel, model.key(), self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
        b = entity.has_model_by_key(
            MoadoModel, model.key(), self.testuser.key())
        self.assertTrue(b)
        b = entity.has_model_by_key(MoadoModel, "1111", self.testuser.key())
        self.assertFalse(b)

    def test_fetch_models(self):
        MoadoModel3(f_str="fstr0", f_int=100).create(
            self.testuser5.key(), "000")
        MoadoModel3(f_str="fstr1", f_int=110).create(
            self.testuser5.key(), "111")
        MoadoModel3(f_str="fstr2", f_int=101).create(
            self.testuser4.key(), "222")
        MoadoModel3(f_str="fstr3", f_int=130).create(
            self.testuser4.key(), "333")
        l = entity.fetch_models(MoadoModel3, [], self.testuser_noperm.key())
        self.assertEqual(len(l), 0)
        l = entity.fetch_models(MoadoModel3, [], self.testuser.key())
        self.assertEqual(len(l), 4)
        self.resource4.create_resourceitem(MoadoModel3, ResourceItem.FORMAT_QFILTER, {
                                           "property_op": "f_str =", "value": "#value"}, None)
        l = entity.fetch_models(
            MoadoModel3, [], self.testuser4.key(), rivars={"value": "fstr2"})
        self.assertEqual(len(l), 1)
        l = entity.fetch_models(MoadoModel3, [], self.testuser5.key())
        self.assertEqual(len(l), 0)
        self.resource5.create_resourceitem(
            MoadoModel3, ResourceItem.FORMAT_VALUE, "111", None)
        self.resource5.create_resourceitem(
            MoadoModel3, ResourceItem.FORMAT_VALUE, "222", None)
        l = entity.fetch_models(MoadoModel3, [], self.testuser5.key())
        self.assertEqual(len(l), 2)
        self.resource5.create_resourceitem(MoadoModel3, ResourceItem.FORMAT_QFILTER, {
                                           "property_op": "created_by =", "value": self.testuser5.key()}, None)
        l = entity.fetch_models(MoadoModel3, [], self.testuser5.key())
        self.assertEqual(len(l), 3)
        l = entity.fetch_models(
            MoadoModel3, [{"property_op": "f_str =", "value": "fstr0"}], self.testuser5.key())
        self.assertEqual(len(l), 1)
        l = entity.fetch_models(MoadoModel3, [
                                {"property_op": "f_str =", "value": "fstr0"}], self.testuser5.key(), mocallback=MoadoModel3.mcb)
        mo = l[0]
        self.assertEqual(mo.eee, "eee111")
        l = entity.fetch_models(MoadoModel3, [{"property_op": "f_str =", "value": "fstr0"}], self.testuser5.key(
        ), whats=[("_id", None)], mocallback=MoadoModel3.mcb)
        mo = l[0]
        self.assertEqual(mo.f_str, None)
        l = entity.fetch_models(
            MoadoModel3, [], self.testuser5.key(), orders=["-f_int"])
        mo = l[0]
        self.assertEqual(mo.f_str, "fstr1")

    @classmethod
    def tearDownClass(cls):
        MoadoModel.delete_schema()
        MoadoModel2.delete_schema()
        MoadoModel3.delete_schema()
        auth.uninstall_module()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())


class TModelWeb(Model):
    @classmethod
    def meta_domain(cls):
        return "test"
    f_str = dao.StringProperty("fStr", length=40)
    f_int = dao.IntegerProperty("fInt")
    f_date = dao.DateProperty("fDate")
    f_datetime = dao.DateTimeProperty("fDatetime")
    f_float = dao.FloatProperty("fFloat")


class ModelHandlerTest(AuthReqHandlerTestCase):

    @classmethod
    def setUpClass(cls):
        super(ModelHandlerTest, cls).setUpClass()
        config.webbCFG.add_model(
            "tmodel", "tests.modules.entity_test.TModelWeb")
        TModelWeb.create_schema()
        entity.install_module()
        cls.ctx = config.webbCFG.get_settings()["route_context"]

    def test_notfound_model(self):
        headers = self.login_superadmin()
        response = self.fetch("%s/mod/tmodel11" % self.ctx, headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(1004, body.status)
        self.assertIn("not found", body.message)
        response = self.fetch("%s/mod/tmodel/tt11" % self.ctx, headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(1004, body.status)
        self.assertIn("not found", body.message)

    def test_get_model(self):
        key = TModelWeb(f_str="fstr0").create(1).key()
        headers = self.login_superadmin()
        response = self.fetch("%s/mod/tmodel" % self.ctx, headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        headers = self.login_superadmin()
        response = self.fetch("%s/mod/tmodel?%s" % (self.ctx,
                                                    self.to_args({"key": key})), headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        self.assertEqual(body.data['key'], key)
        response = self.fetch("%s/mod/tmodel?%s" % (self.ctx, self.to_args(
            {"filters": {"propertyOp": "fStr =", "value": "fstr0"}})), headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        self.assertEqual(body.data['fStr'], "fstr0")
        headers = self.login_superadmin()
        response = self.fetch("%s/mod/tmodel?%s" % (self.ctx, self.to_args({"filters": {
                              "propertyOp": "fStr =", "value": "fstr0", "xcca": "yqq3"}})), headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        response = self.fetch("%s/mod/tmodel?%s" % (self.ctx, self.to_args(
            {"filters": {"cae": "fStr =", "value": "fstr0"}})), headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        response = self.fetch("%s/mod/tmodel?%s" % (self.ctx, self.to_args(
            {"filters": {"propertyOp": "fStr =", "value1": "fstr0"}})), headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        response = self.fetch("%s/mod/tmodel?%s" % (self.ctx, self.to_args({"filters": {
            "propertyOp": "fStr =", "value": "fstr0", "xcca": "yqq3"}, "whats": ["fInt"]})), headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        response = self.fetch("%s/mod/tmodel?%s" % (self.ctx, self.to_args({"filters": {
            "propertyOp": "fStr =", "value": "fstr0", "xcca": "yqq3"}, "whats": ["fInt1"]})), headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        response = self.fetch("%s/mod/tmodel?%s" % (self.ctx, self.to_args({"filters": {
            "propertyOp": "fStr =", "value": "fstr0", "xcca": "yqq3"}, "whats": ["fInt"], "orders": "-fStr"})), headers=headers)
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)

    def test_create_model(self):
        headers = self.login_superadmin()
        args = {'fStr': 'fstr111', 'fInt': 101, 'fFloat': 1.2,
                'fDate': "2015-03-03", 'fDatetime': '2015-02-04 02:03'}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/mod/tmodel" % self.ctx, headers=headers, body=args, method="POST")
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['fDatetime'], '2015-02-04 02:03:00')
        self.assertEqual(body['fDate'], '2015-03-03')
        self.assertEqual(body['fFloat'], 1.2)
        self.assertEqual(body['fInt'], 101)
        self.assertEqual(body['fStr'], 'fstr111')
        headers = self.login_superadmin()
        args = {'fStr': 'fstr111fstr111fstr111fstr111fstr111fstrfstr111fstfstr111fstr111fstr111fstr111fstr111fstrr111fstr111fstr111fstr111fstr',
                'fInt': 23232323, 'fFloat': 232323233.2, 'fDate': "2015/06/03", 'fDateFMT': '%Y/%m/%d', 'fDatetime': '201508-04 02', 'fDatetimeFMT': '%Y%m-%d %H'}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/mod/tmodel" % self.ctx, headers=headers, body=args, method="POST")
        body = self.get_response_body(response)
        self.assertEqual(1023, body.status)
        args = {'fStr': 'fffadfdasfsdaf', 'fInt': 11111123, 'fFloat': 232323233.2, 'fDate': "2015/06/03",
                'fDateFMT': '%Y/%m/%d', 'fDatetime': '201508-04 02', 'fDatetimeFMT': '%Y%m-%d %H'}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/mod/tmodel" % self.ctx, headers=headers, body=args, method="POST")
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['fDatetime'], '2015-08-04 02:00:00')
        self.assertEqual(body['fDate'], '2015-06-03')
        self.assertEqual(body['fFloat'], 232323233.2)
        self.assertEqual(body['fInt'], 11111123)
        self.assertEqual(body['fStr'], 'fffadfdasfsdaf')
        args = {'fStr': 'fstr111', 'fInt': 101,
                'fFloat': 1.2, 'key': '33323222'}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/mod/tmodel" % self.ctx, headers=headers, body=args, method="POST")
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['key'], '33323222')

    def test_update_model(self):
        headers = self.login_superadmin()
        args = {'fStr': 'fstr111', 'fInt': 101, 'fFloat': 1.2,
                'fDate': "2015-03-03", 'fDatetime': '2015-02-04 02:03'}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/mod/tmodel" % self.ctx, headers=headers, body=args, method="PUT")
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        args = {'key': '2233', 'fStr': 'fstr111', 'fInt': 101, 'fFloat': 1.2,
                'fDate': "2015-03-03", 'fDatetime': '2015-02-04 02:03'}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/mod/tmodel" % self.ctx, headers=headers, body=args, method="PUT")
        body = self.get_response_body(response)
        self.assertEqual(1004, body.status)
        tmodel = TModelWeb(f_str="aa", f_int=12, f_float=3223.0)
        tmodel.create("222")
        args = {'key': tmodel.key(), 'fStr': 'fstr111', 'fInt': 223, 'fFloat': 122.2,
                'fDate': "2015-03-23", 'fDatetime': '2015-03-22 12:03'}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/mod/tmodel" % self.ctx, headers=headers, body=args, method="PUT")
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['fDatetime'], '2015-03-22 12:03:00')
        self.assertEqual(body['fDate'], '2015-03-23')
        self.assertEqual(body['fFloat'], 122.2)
        self.assertEqual(body['fInt'], 223)
        self.assertEqual(body['fStr'], 'fstr111')
        args = {'key': tmodel.key(), 'fStr': 'adeddadsfasdfadfsasdfasdf', 'fInt': 222333, 'fFloat': 13322.2,
                'fDate': "2012-1123", 'fDateFMT': '%Y-%m%d', 'fDatetime': '20160322 11:03:55', 'fDatetimeFMT': '%Y%m%d %H:%M:%S'}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch(
            "%s/mod/tmodel" % self.ctx, headers=headers, body=args, method="PUT")
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        body = body.data
        self.assertEqual(body['fDatetime'], '2016-03-22 11:03:55')
        self.assertEqual(body['fDate'], '2012-11-23')
        self.assertEqual(body['fFloat'], 13322.2)
        self.assertEqual(body['fInt'], 222333)
        self.assertEqual(body['fStr'], 'adeddadsfasdfadfsasdfasdf')

    def test_delete_model(self):
        tmodel = TModelWeb(f_str="a222a", f_int=12, f_float=3223.0)
        tmodel.create("222")
        headers = self.login_superadmin()
        args = {'key1': tmodel.key()}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch("%s/mod/tmodel?%s" % (self.ctx,
                                                    args), headers=headers, method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(1054, body.status)
        args = {'key': tmodel.key()}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch("%s/mod/tmodel?%s" %
                              (self.ctx, args), headers=headers, method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)
        tmodel = TModelWeb(f_str="a2cc22a", f_int=12, f_float=3223.0)
        key1 = tmodel.create("222").key()
        tmodel = TModelWeb(f_str="accc2cc22a", f_int=12, f_float=3223.0)
        key2 = tmodel.create("222").key()
        args = {'keys': [key1, key2]}
        args = security.str_to_base64(
            typeutils.obj_to_json(args), remove_cr=True)
        response = self.fetch("%s/mod/tmodel?%s" %
                              (self.ctx, args), headers=headers, method="DELETE")
        body = self.get_response_body(response)
        self.assertEqual(webb.Rtn.STATUS_SUCCESS, body.status)

    @classmethod
    def tearDownClass(cls):
        TModelWeb.delete_schema()
        entity.uninstall_module()
        super(ModelHandlerTest, cls).tearDownClass()
