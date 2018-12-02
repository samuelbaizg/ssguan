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



from ssguan.ignitor.audit.model import MCLog
from ssguan.ignitor.base import struct

def add_mclog(last_model, model, modified_by, dbconn=None):
    changedprops = []
    for key, prop in model.get_properties(persistent=True).items():
        value1 = getattr(last_model, key)
        value2 = getattr(model, key)
        if prop.logged is True and value1 != value2:
            changedprops.append((key, prop.get_label(), value1, value2))
    if len(changedprops) > 0:
        changelog = MCLog()
        changelog.modelname = model.get_modelname()
        changelog.modelkey = str(model.get_keyvalue())
        changelog.user_id = modified_by
        changelog.change_props = []
        for cp in changedprops:
            cldetail = struct.Storage()            
            cldetail.field_name = cp[0]
            cldetail.field_label = cp[1]
            cldetail.fvalue_last = str(cp[2])
            cldetail.fvalue_present = str(cp[3])
            changelog.change_props.append(cldetail)
        changelog.create(dbconn=dbconn)

def fetch_mclogs(model_name, model_key, **kwds):
    query = MCLog.all()
    query.filter("modelname =", model_name)
    query.filter("modelkey =", str(model_key))
    mclogs = query.fetch()
    return mclogs
        
def delete_mclogs(model_name, model_key, modified_by, dbconn=None):
    query = MCLog.all()
    query.filter("modelname =", model_name)
    query.filter("modelkey =", str(model_key))
    query.delete(dbconn=dbconn)
        