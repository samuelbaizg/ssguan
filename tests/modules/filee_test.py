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

import os
import shutil
import unittest

from ssguan import config
from ssguan.commons import  database, loggingg, security
from ssguan.commons.error import NoFoundError
from ssguan.modules import sysprop, auth, filee
from ssguan.modules.auth import RoleOperation, Resource, UnauthorizedError, User
from ssguan.modules.filee import Filex, FileExistsError, FileSizeError


class FileeTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        auth.install_module()
        filee.install_module()
        config.fileeCFG.delete_fsinfo(config.fileeCFG.DEFAULT_FSKEY)
        cls.testrootdir = "c:/aattffaaa"
        config.fileeCFG.add_fsinfo(config.fileeCFG.DEFAULT_FSKEY, "c:/aattffaaa")
        if not os.path.exists(cls.testrootdir):
            os.makedirs(cls.testrootdir)
        cls.localfs = filee.get_default_fs()
        cls.testuser = auth.create_user("testmoado", "testmoado@e.m", "testmoado", "testmoado", False, User.ID_ROOT)
        cls.testuser_noperm = auth.create_user("testmoadonoperm", "testmoadonoperm@e.m", "testmoadonoperm", "testmoado", False, User.ID_ROOT)
        cls.role = auth.create_role("rol1", User.ID_ROOT)
        cls.role.create_roleoperation(Filex, RoleOperation.OPERATION_READ, User.ID_ROOT)
        cls.role.create_roleoperation(Filex, RoleOperation.OPERATION_UPDATE, User.ID_ROOT)
        cls.role.create_roleoperation(Filex, RoleOperation.OPERATION_DELETE, User.ID_ROOT)
        cls.role.create_roleoperation(Filex, RoleOperation.OPERATION_CREATE, User.ID_ROOT)
        cls.role.create_roleoperation(sysprop.SysProp, RoleOperation.OPERATION_CREATE, User.ID_ROOT)
        cls.role.create_roleoperation(sysprop.SysProp, RoleOperation.OPERATION_UPDATE, User.ID_ROOT)
        cls.role.create_roleoperation(sysprop.SysProp, RoleOperation.OPERATION_DELETE, User.ID_ROOT)
        cls.role.create_roleoperation(sysprop.SysProp, RoleOperation.OPERATION_READ, User.ID_ROOT)
        auth.create_userpermission(cls.testuser.key(), cls.role.key(), Resource.ID_ALL, User.ID_ROOT)
        
    def test_create_file(self):
        filex = filee.create_file("eedfas.txt", "eeeee", self.testuser.key())
        filex_1 = Filex.get_by_key(filex.key())
        self.assertEqual(filex_1.filename, "eedfas.txt")
        self.assertEqual(filex_1.filesize, 5)
        self.assertEqual(filex_1.filehash, security.str_to_md5_hex("eeeee"))
        (fskey, path) = filex_1.extract_fspath()
        fs = filee.get_fs(fskey)
        b = fs.has_file(path)
        self.assertTrue(b)
        try:
            filex = filee.create_file(self.testuser_noperm.key(), "eedfas.txt", "eeeee")
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
    
    def test_delete_file(self):
        filex = filee.create_file("Ff.txt", "FFADFASDF", self.testuser.key())
        filex_1 = Filex.get_by_key(filex.key())
        (fskey, path) = filex_1.extract_fspath()
        fs = filee.get_fs(fskey)
        b = fs.has_file(path)
        self.assertTrue(b)
        try:
            filee.delete_file(filex_1.key(), self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
        filee.delete_file(filex_1.key(), self.testuser.key())
        f = Filex.get_by_key(filex_1.key())
        self.assertIsNone(f)
        (fskey, path) = filex_1.extract_fspath()
        fs = filee.get_fs(fskey)
        b = fs.has_file(fskey)
        self.assertFalse(b)
    
    def test_get_file(self):
        filex = filee.create_file("aaaa.txt", "aaaaaaaa", self.testuser.key())
        filex_1 = filee.get_file(filex.key(), self.testuser.key(), self.testuser.key())
        self.assertEqual(filex_1.filename, "aaaa.txt")
        try:
            filee.get_file(filex.key(), self.testuser_noperm.key())
            self.assertTrue(False)
        except BaseException, e:
            self.assertIsInstance(e, UnauthorizedError)
        filex_1 = filee.get_file(filex.key(), self.testuser.key(), content=True)
        self.assertEqual(filex_1.file_content, "aaaaaaaa")
        
    def test_fetch_files(self):
        query = Filex.all()
        query.delete(None)
        filee.create_file("ce.txt", "aaaaaaaa", self.testuser.key())
        filee.create_file("edf.txt", "aaaabaaaa", self.testuser.key())
        filee.create_file("aaec.txt", "aaabcaaaaa", self.testuser.key())
        filee.create_file("aabb.ee", "aaaacaaaa", self.testuser.key())
        l = filee.fetch_files(self.testuser.key())
        self.assertEqual(len(l), 4)
        l = filee.fetch_files(self.testuser.key(), "aa")
        self.assertEqual(len(l), 2)
        l = filee.fetch_files(self.testuser.key(), ".txt")
        self.assertEqual(len(l), 3)
        l = filee.fetch_files(self.testuser_noperm.key())
        self.assertEqual(len(l), 0)    
    @classmethod
    def tearDownClass(cls):
        filee.uninstall_module()        
        auth.uninstall_module()
        sysprop.uninstall_module()
        if os.path.exists(cls.testrootdir):
            shutil.rmtree(cls.testrootdir, ignore_errors=True)
        database.drop_db(config.dbCFG.get_root_dbinfo())

class LocalFSTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        loggingg.install_module()
        cls.testrootdir = "c:/mmtestsstt"
        if not os.path.exists(cls.testrootdir):
            os.makedirs(cls.testrootdir)
        config.fileeCFG.add_fsinfo("localfsoverwrite", "c:/mmtestsstt/extfa", maxsize=0.05, overwrite=True)
        config.fileeCFG.add_fsinfo("localfsoverwritefalse", "c:/mmtestsstt/extfalse", overwrite=False)
        cls.localfsoverwrite = filee.get_fs("localfsoverwrite")
        cls.localfsoverfalse = filee.get_fs("localfsoverwritefalse")
        
    def test_notfound(self):
        try:
            b = self.localfsoverwrite.save_file("ttt/tttt1.txt", "eadfadfadfasdfasdf")
            self.assertTrue(b)
            self.localfsoverwrite.get_file("ttt/tttt1.txt")
            self.assertTrue(True)
        except NoFoundError:
            self.assertTrue(False)
        
        try:
            self.localfsoverwrite.get_file("ttt/tttffcccfft1.txt")
            self.assertTrue(False)
        except NoFoundError:
            self.assertTrue(True)
            
        try:
            b = self.localfsoverwrite.save_file("ttt/tttt2.txt", "eadfadfadfasdfasdf")
            self.assertTrue(b)
            self.localfsoverwrite.get_file("ttt/tttt2.txt")
            self.assertTrue(True)
        except NoFoundError:
            self.assertTrue(False)
        
        try:
            self.localfsoverwrite.get_file("ttt/aaa.txt")
            self.assertTrue(False)
        except NoFoundError:
            self.assertTrue(True)
            
    def test_fileexists(self):
        try:
            b = self.localfsoverwrite.save_file("ttt/111.txt", "eadfadfadfasdfasdf")
            self.assertTrue(b)
            b = self.localfsoverwrite.save_file("ttt/111.txt", "ffdafasdf")
            self.assertTrue(b)
            b = self.localfsoverwrite.get_file("ttt/111.txt")
            self.assertTrue(b)
        except FileExistsError:
            self.assertTrue(False)    
        
        try:
            b = self.localfsoverfalse.save_file("ttt/bbb.txt", "eadfadfadfasdfasdf")
            self.assertTrue(b)
            b = self.localfsoverfalse.save_file("ttt/bbb.txt", "eadfadfadfasdfasdf")            
            self.assertFalse(True)
        except FileExistsError:
            self.assertTrue(True)  
    
    def test_filesize(self):
        str1 = ""
        i = 1
        while (i < 0.05 * 1024 * 1024 / 200):
            str1 += "strstrstrsstrstrstrsstrstrstrsstrstrstrsstrstrstrs"
            str1 += "strstrstrsstrstrstrsstrstrstrsstrstrstrsstrstrstrs"
            str1 += "strstrstrsstrstrstrsstrstrstrsstrstrstrsstrstrstrs"
            str1 += "strstrstrsstrstrstrsstrstrstrsstrstrstrsstrstrstrs"
            str1 += "strstrstrsstrstrstrsstrstrstrsstrstrstrsstrstrstrs"
            i += 1
        try:
            self.localfsoverwrite.save_file("ttt/bbb.txt", str1)
            self.assertTrue(False)
        except FileSizeError:
            self.assertTrue(True)
    
    def test_has_file(self):
        b = self.localfsoverwrite.save_file("t/t1.txt", "eadfadfadfasdfasdf")
        self.assertTrue(b)
        b = self.localfsoverwrite.has_file("t/t1.txt")
        self.assertTrue(b)
        b = self.localfsoverwrite.has_file("t/t33.33txt")
        self.assertFalse(b)
    
    def test_save_file(self):
        b = self.localfsoverwrite.save_file("t/t.txt", "eadfadfadfasdfasdf")
        self.assertTrue(b)
        
    def test_delete_file(self):
        b = self.localfsoverwrite.save_file("t/t111sf.txt", "eadfadfadfasdfasdf")
        self.assertTrue(b)
        b = self.localfsoverwrite.delete_file("t/t111sf.txt")
        self.assertTrue(b)
        
    def test_get_file(self):
        b = self.localfsoverwrite.save_file("t/t2.txt", "eadfffffadfadfasdfasdf")
        self.assertTrue(b)
        c = self.localfsoverwrite.get_file("t/t2.txt")
        self.assertEqual(c, "eadfffffadfadfasdfasdf")
    
    @classmethod
    def tearDownClass(cls):
        config.fileeCFG.delete_fsinfo("localfsoverwrite")
        config.fileeCFG.delete_fsinfo("localfsoverwritefalse")
        loggingg.uninstall_module()
        sysprop.uninstall_module()
        if os.path.exists(cls.testrootdir):
            shutil.rmtree(cls.testrootdir, ignore_errors=True)
        database.drop_db(config.dbCFG.get_root_dbinfo())
        
