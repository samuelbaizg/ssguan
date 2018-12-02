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
from cStringIO import StringIO
import datetime
import os
import sys
import unittest

reload(sys)
sys.setdefaultencoding('utf-8')


from ssguan import config
from ssguan.commons import database
from ssguan.commons import loggingg
from ssguan.commons import webb

path = "conf%sconfig_test.properties" % os.sep
path = os.path.dirname(__file__) + os.sep + path
config.fileConfig(path)



path = "conf%sloggingg_test.properties" % os.sep
path = os.path.dirname(__file__) + os.sep + path
loggingg.fileConfig(path)

all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "*_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "filee_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "labell_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "auth_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "entity_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "sysprop_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "fetch_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "dao_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "mqueue_test.py")
all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "schedule_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "utility_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "mcloggingg_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "webb_test.py")
# all_suite = unittest.TestLoader().discover(os.path.dirname(__file__), "houseprice_test.py")
