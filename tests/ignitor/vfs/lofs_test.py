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

import shutil
import unittest

from ssguan.ignitor.base.error import NoFoundError
from ssguan.ignitor.utility import kind
from ssguan.ignitor.vfs import service as fs_service
from ssguan.ignitor.vfs.error import FileExistingError, FileSizeError


class LocalFSTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.fs = fs_service.get_fs("lotest") 
        cls.localfsoverfalse = fs_service.get_fs("localfsoverfalse")
        if len(cls.fs.rootpath) <= 3 or len(cls.localfsoverfalse.rootpath) <=3:
            raise Exception("the rootpath can't be root dir.")
        pass
        
    def test_notfound(self):
        try:
            b = self.fs.save_file("ttt/tttt1.txt", "eadfadfadfasdfasdf")
            self.assertTrue(b)
            self.fs.get_file("ttt/tttt1.txt")
            self.assertTrue(True)
        except NoFoundError:
            self.assertTrue(False)
        
        try:
            self.fs.get_file("ttt/tttffcccfft1.txt")
            self.assertTrue(False)
        except NoFoundError:
            self.assertTrue(True)
            
        try:
            b = self.fs.save_file("ttt/tttt2.txt", "eadfadfadfasdfasdf")
            self.assertTrue(b)
            self.fs.get_file("ttt/tttt2.txt")
            self.assertTrue(True)
        except NoFoundError:
            self.assertTrue(False)
        
        try:
            self.fs.get_file("ttt/aaa.txt")
            self.assertTrue(False)
        except NoFoundError:
            self.assertTrue(True)
            
    def test_fileexists(self):
        try:
            b = self.fs.save_file("ttt/111.txt", "eadfadfadfasdfasdf")
            self.assertTrue(b)
            b = self.fs.save_file("ttt/111.txt", "ffdafasdf")
            self.assertTrue(b)
            b = self.fs.get_file("ttt/111.txt")
            self.assertTrue(b)
        except FileExistingError:
            self.assertTrue(False)    
        
        try:
            b = self.localfsoverfalse.save_file("ttt/bbb.txt", "eadfadfadfasdfasdf")
            self.assertTrue(b)
            b = self.localfsoverfalse.save_file("ttt/bbb.txt", "eadfadfadfasdfasdf")            
            self.assertFalse(True)
        except FileExistingError:
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
            self.fs.save_file("ttt/bbb.txt", str1)
            self.assertTrue(False)
        except FileSizeError:
            self.assertTrue(True)
    
    def test_has_file(self):
        b = self.fs.save_file("t/t1.txt", "eadfadfadfasdfasdf")
        self.assertTrue(b)
        b = self.fs.has_file("t/t1.txt")
        self.assertTrue(b)
        b = self.fs.has_file("t/t33.33txt")
        self.assertFalse(b)
    
    def test_save_file(self):
        b = self.fs.save_file("t/t.txt", "eadfadfadfasdfasdf")
        self.assertTrue(b)
        
    def test_delete_file(self):
        b = self.fs.save_file("t/t111sf.txt", "eadfadfadfasdfasdf")
        self.assertTrue(b)
        b = self.fs.delete_file("t/t111sf.txt")
        self.assertTrue(b)
        
    def test_get_file(self):
        b = self.fs.save_file("t/t2.txt", "eadfffffadfadfasdfasdf")
        self.assertTrue(b)
        c = self.fs.get_file("t/t2.txt")
        c = kind.safestr(c)
        self.assertEqual(c, "eadfffffadfadfasdfasdf")
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.fs.rootpath)
        shutil.rmtree(cls.localfsoverfalse.rootpath)
        pass
        
