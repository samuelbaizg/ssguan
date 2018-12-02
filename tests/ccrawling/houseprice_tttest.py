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

from ssguan import common, config
from ssguan.commons import schedule, database, sysprop, loggingg


class HousePrice163Test(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        database.create_db(config.dbCFG.get_root_dbinfo(), dropped=True)       
        sysprop.install_module()
        loggingg.install_module()
        schedule.install_module()
        
    def test_run(self):
        cj1 = schedule.create_cronjob("runonce1", "runonce1", "ssguan.ccrawling.houseprice.HousePrice163", "runallnode222", common.ID_SYSTEM)
        scher = schedule.Scheduler("runallnode222")
        scher.run_once(cj1.key(), None)

    @classmethod
    def tearDownClass(cls):        
        schedule.uninstall_module()
        loggingg.uninstall_module()
        sysprop.uninstall_module()
        database.drop_db(config.dbCFG.get_root_dbinfo())