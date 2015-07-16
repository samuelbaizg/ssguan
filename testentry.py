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
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'contrib'))

import traceback
import unittest

from core import migration, model
from core.db import dbutil
import test.testsuits



reload(sys)
sys.setdefaultencoding('utf-8')



def gettestsuits():
    alltestsuits = unittest.TestSuite()
    for ts in test.testsuits.TESTSUITS:
        i = ts.rfind('.')
        module = ts[0:i]
        name = ts[i + 1:]
        m = __import__(module, globals(), locals(), name)
        clazz = getattr(m, name)
        alltestsuits.addTest(clazz())
    return alltestsuits

def runtests(quiet=False):
    try:
        if quiet is True:
            out = StringIO()
            runner = unittest.TextTestRunner(stream=out)
            results = runner.run(gettestsuits())
            for failure in results.failures:
                print "FAIL:", failure[0]
            for error in results.errors:
                print "ERROR:", error[0]
        else:
            runner = unittest.TextTestRunner()
            results = runner.run(gettestsuits())
        if not results.wasSuccessful():
            return False
        else:
            return True
    except BaseException, e:
        print str(e)
        traceback.print_exc()

def main():
    test_dbinfo = dbutil.get_master_dbinfo()
    test_dbinfo = test_dbinfo.copy(dbname='%s_test' % test_dbinfo.get_dbname())
    dbutil.change_master_dbinfo(test_dbinfo)
    migration.setup_db()
    migration.setup_core_tables()
    b = runtests(quiet=False)
    dbutil.drop_db(dbutil.get_master_dbinfo())
    return b
if __name__ == '__main__':
    main()
