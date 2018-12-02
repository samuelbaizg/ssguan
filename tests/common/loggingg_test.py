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

import logging
import unittest

from ssguan import config
from ssguan.commons import loggingg, database, dao
from ssguan.commons.dao import Model
from ssguan.modules import sysprop


class LogTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        loggingg.install_module()
    
    def test_dbhandler(self):
        query = loggingg.Log.all()
        query.delete()
        logger = logging.getLogger("todb")
        msg = "test db logger 1"
        logger.debug(msg)
        pager = loggingg.fetch_logs(level=logging.DEBUG, keywords=msg)
        self.assertEqual(pager.count, 1)
        msg = "test db logger 2"
        logger.info(msg)
        pager = loggingg.fetch_logs(level=logging.INFO, keywords=msg)
        self.assertEqual(pager.count, 1)
        msg = "test db logger 3"
        logger.warn(msg)
        pager = loggingg.fetch_logs(level=logging.WARN, keywords=msg)
        self.assertEqual(pager.count, 1)
        msg = "test db logger 4"
        logger.error(msg)
        pager = loggingg.fetch_logs(level=logging.ERROR, keywords=msg)
        self.assertEqual(pager.count, 1)
        msg = "test db logger 5"
        logger.fatal(msg)
        pager = loggingg.fetch_logs(level=logging.FATAL, keywords=msg)
        self.assertEqual(pager.count, 1)
        msg = "test db logger 7"
        logger.info(msg)
        pager = loggingg.fetch_logs(level=logging.INFO)
        self.assertEqual(pager.count, 2)
        logger.info("333")
        pager = loggingg.fetch_logs(keywords="test db logger")
        self.assertEqual(pager.count, 6)
        
    @classmethod
    def tearDownClass(cls):
        loggingg.uninstall_module()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())

class McLogTest(unittest.TestCase):
    
    class MCModel(Model):
        @classmethod
        def meta_domain(cls):
            return "test"
        f_str = dao.StringProperty("fStr")
        f_int = dao.IntegerProperty("fInt")
        f_bool = dao.BooleanProperty("fBool")
        f_float = dao.FloatProperty("fFloat")
        f_date = dao.DateProperty("fDate")
        f_datetime = dao.DateTimeProperty("fDatetime")
        f_v = dao.StringProperty("fV", length=8)
        f_str1 = dao.StringProperty("fStr1", persistent=False)
        f_str_logged = dao.StringProperty("fStrLogged", logged=True)
        f_float_logged = dao.FloatProperty("fFloatLogged", logged=True)
        f_json = dao.DictProperty("fJson")
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)
        sysprop.install_module()
        loggingg.install_module()
        cls.MCModel.create_schema()
        
    def test_add_mclog(self):
        tmodel = self.MCModel()
        tmodel.f_str = "abcd"
        tmodel.f_int = 100
        tmodel.f_float = 1000.0
        tmodel.f_bool = False
        tmodel.f_float_logged = 1.0
        tmodel.f_str_logged = "1234"
        tmodel.create(2)
        tmodel.f_str = 'abcd1'
        tmodel.f_float = 1001.0
        tmodel.f_float_logged = 2.0
        tmodel.f_str_logged = "123456"
        tmodel.update(2)
        query = loggingg.MCLog.all()
        self.assertEqual(query.count(), 1)
        mclog = query.get()
        self.assertEqual(len(mclog.changed_props), 2)
        
    @classmethod
    def tearDownClass(cls):
        loggingg.uninstall_module()                
        cls.MCModel.delete_schema()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())