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
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'contrib'))
reload(sys)
sys.setdefaultencoding('utf-8')

import conf
from core import migration
import web


web.config.debug = conf.get_web_config_debug()
web.config.debug_sql = conf.get_config_debug_sql()

migration.setup_db()

webapp = web.application(conf.URLs, globals())

if web.config.get('_session') is None:
    from core.db import dbutil
    from core.model import Session
    session = web.session.Session(webapp, web.session.DBStore(dbutil.get_dbconn(), Session.get_modelname()), initializer={})
    web.config._session = session
    web.config.session_parameters['timeout'] = conf.get_session_timeout()
else:
    session = web.config._session
    
def session_hook():  
    web.ctx.session = session
      
webapp.add_processor(web.loadhook(session_hook))

def notfound():
    return "Not Found"

def main():
    webapp.run()
    

if __name__ == "__main__":
    main()
