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

from ssguan import config
from ssguan.commons import  dao
from ssguan.commons.dao import Model
from ssguan.modules import auth
from ssguan.modules.auth import RoleOperation, UnauthorizedError


class Label(Model):
    @classmethod
    def meta_domain(cls):
        return config.MODULE_LABELL
    modelname = dao.StringProperty("modelName", required=True, length=80)
    modelkey = dao.StringProperty("modelKey", required=True)
    label_name = dao.StringProperty("labelName", required=True, validator=[dao.IllegalValidator()])
    
def create_label(model_class, model_key, label_name, created_by):
    if not auth.has_permission(created_by, model_class, RoleOperation.OPERATION_UPDATE, model_key):
        raise UnauthorizedError(RoleOperation.OPERATION_UPDATE, model_class.get_modelname(), model_key)
    query = Label.all()
    query.filter("modelkey =", model_key)
    query.filter("modelname =", model_class.get_modelname())
    query.filter("label_name =", label_name)
    if query.count() == 0:
        molabel = Label()
        molabel.modelname = model_class.get_modelname()
        molabel.modelkey = str(model_key)
        molabel.label_name = label_name
        molabel.create(created_by)
    else:
        molabel = query.get()
    return molabel

def delete_labels(model_class, model_key, deleted_by, label_name=None):
    if not auth.has_permission(deleted_by, model_class, RoleOperation.OPERATION_UPDATE, model_key):
        raise UnauthorizedError(RoleOperation.OPERATION_UPDATE, model_class.get_modelname(), model_key)
    query = Label.all()
    query.filter("modelname =", model_class.get_modelname())
    query.filter("modelkey =", model_key)
    if label_name != None:
        query.filter("label_name =", label_name)
    return query.delete(deleted_by)

def fetch_labels(model_class, model_key, read_by):
    if not auth.has_permission(read_by, model_class, RoleOperation.OPERATION_UPDATE, model_key):
        raise UnauthorizedError(RoleOperation.OPERATION_UPDATE, model_class.get_modelname(), model_key)
    query = Label.all()
    query.filter("modelname =", model_class.get_modelname())
    query.filter("modelkey =", model_key)
    return query.fetch()

def install_module():
    Label.create_schema()
    config.dbCFG.add_model_dbkey("%s_*" % config.MODULE_LABELL, config.dbCFG.ROOT_DBKEY)
    return True

def uninstall_module():
    Label.delete_schema()
    return True
