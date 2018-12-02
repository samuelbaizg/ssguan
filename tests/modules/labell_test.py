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
from ssguan.commons import  database, dao
from ssguan.commons.dao import Model
from ssguan.modules import sysprop, auth, labell
from ssguan.modules.auth import  Resource, UnauthorizedError, RoleOperation, User
from ssguan.modules.labell import Label


class LModel1(Model):
    @classmethod
    def meta_domain(cls):
        return "test"
    f_str = dao.StringProperty("fStr")
    f_int = dao.IntegerProperty("fInt")

class LabelTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        auth.install_module()
        LModel1.create_schema()
        labell.install_module()
        cls.testuser = auth.create_user("testmoado", "testmoado@e.m", "testmoado", "testmoado", False, User.ID_ROOT)
        cls.testuser_noperm = auth.create_user("testmoadonoperm", "testmoadonoperm@e.m", "testmoadonoperm", "testmoado", False, User.ID_ROOT)
        cls.role = auth.create_role("rol1", User.ID_ROOT)
        auth.create_userpermission(cls.testuser.key(), cls.role.key(), Resource.ID_ALL, User.ID_ROOT)
        cls.role.create_roleoperation(LModel1, RoleOperation.OPERATION_READ, User.ID_ROOT)
        cls.role.create_roleoperation(LModel1, RoleOperation.OPERATION_UPDATE, User.ID_ROOT)
        cls.role.create_roleoperation(LModel1, RoleOperation.OPERATION_DELETE, User.ID_ROOT)
        cls.role.create_roleoperation(LModel1, RoleOperation.OPERATION_CREATE, User.ID_ROOT)
        
    
    def test_create_label(self):
        model = LModel1(f_str="fstr", f_int=100)
        model = model.create(self.testuser.key())
        labell.create_label(LModel1, model.key(), "aaaa", self.testuser.key())
        query = Label.all()
        query.filter("modelname", LModel1.get_modelname())
        query.filter("modelkey", model.key())
        label = query.get()
        self.assertEqual(label.label_name, "aaaa")
        labell.create_label(LModel1, model.key(), "aaaa", self.testuser.key())
        query = Label.all()
        query.filter("modelname", LModel1.get_modelname())
        query.filter("modelkey", model.key())
        self.assertEqual(query.count(), 1)
        la = query.get()
        self.assertEqual(la.label_name, "aaaa")
        try:
            labell.create_label(LModel1, model.key(), "aaaa", self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
    
    def test_fetch_labels(self):
        model = LModel1(f_str="fffstr", f_int=100)
        model = model.create(self.testuser.key())
        labell.create_label(LModel1, model.key(), "aaaa", self.testuser.key())
        labell.create_label(LModel1, model.key(), "bbbb", self.testuser.key())    
        l = labell.fetch_labels(LModel1, model.key(), self.testuser.key())
        self.assertEqual(len(l), 2)
        try:
            labell.fetch_labels(LModel1, model.key(), self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
    
    def test_delete_labels(self):
        model = LModel1(f_str="fffstr", f_int=100)
        model = model.create(self.testuser.key())
        labell.create_label(LModel1, model.key(), "aaaffa", self.testuser.key())
        labell.create_label(LModel1, model.key(), "bbbffb", self.testuser.key())
        labell.delete_labels(LModel1, model.key(), self.testuser.key(), label_name="aaaffa")
        l = labell.fetch_labels(LModel1, model.key(), self.testuser.key())
        self.assertEqual(len(l), 1)
        labell.create_label(LModel1, model.key(), "zz", self.testuser.key())
        labell.create_label(LModel1, model.key(), "ff", self.testuser.key())
        l = labell.fetch_labels(LModel1, model.key(), self.testuser.key())
        self.assertEqual(len(l), 3)
        labell.delete_labels(LModel1, model.key(), self.testuser.key())
        l = labell.fetch_labels(LModel1, model.key(), self.testuser.key())
        self.assertEqual(len(l), 0)
        try:
            labell.delete_labels(LModel1, model.key(), self.testuser_noperm.key(), label_name="aaaffa")
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)

    
    @classmethod
    def tearDownClass(cls):
        LModel1.delete_schema()
        labell.uninstall_module()
        auth.uninstall_module()
        sysprop.uninstall_module()

