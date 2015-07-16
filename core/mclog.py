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
from core.model import MCLog, MCLogDetail
from core import user

def fetch_mclogs(model_name, model_key, **kwds):
    query = MCLog.all()
    query.filter("model_name =", model_name)
    query.filter("model_key =", str(model_key))
    mclogs = query.fetch()
    for mclog in mclogs:
        query = MCLogDetail.all()
        query.filter("changelog_id =", mclog.key())
        mclog.logDetails = query.fetch()
        for logdetail in mclog.logDetails:
            if kwds.has_key(logdetail.field_name):
                logdetail.fvalue_last = kwds[logdetail.field_name](logdetail.fvalue_last)
                logdetail.fvalue_present = kwds[logdetail.field_name](logdetail.fvalue_present)
        mclog.userDisplayName = user.get_user_display_name(mclog.user_id)
    return mclogs
        
def delete_mclogs(model_name, model_key, modifier_id):
    query = MCLog.all()
    query.filter("model_name =", model_name)
    query.filter("model_key =", str(model_key))
    mclogs = query.fetch()
    for mclog in mclogs:
        query2 = MCLogDetail.all()
        query2.filter("changelog_id =", mclog.key())
        query2.delete()
        mclog.delete()
