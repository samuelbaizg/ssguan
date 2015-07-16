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
import conf
from core.db import dbutil
from core.migration import Version
from core.model import I18n


class V8(Version):
    
    def _upgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        b = self._exist_column('cont_contactgroup', 'remark')
        if b is False:
            sql = "ALTER TABLE cont_contactgroup ADD remark VARCHAR(255) NULL"
            conn.query(sql)
            
    def _downgrade(self, modifier_id):
        conn = dbutil.get_dbconn()
        b = self._exist_column('cont_contactgroup', 'remark')
        if b is True:
            sql = "ALTER TABLE cont_contactgroup DROP remark"
            conn.query(sql)
        
            
    def _get_roles(self):
        return []

    def _get_operations(self):
        operations = []
        return operations
    
    def _get_roleoperations(self):
        roleoperations = []
        return roleoperations    

    def _get_i18ns(self):
        i18ns = []
                
        i18ns.append(I18n(i1_key="cont_label_cgremark", i1_locale=conf.LANG_EN, i1_message=u"Remark"))        
        i18ns.append(I18n(i1_key="cont_label_cgremark", i1_locale=conf.LANG_ZH_CN, i1_message=u"备注"))
        return i18ns
    
