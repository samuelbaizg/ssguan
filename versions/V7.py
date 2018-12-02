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
from core.migration import Version
from core.model import I18n


class V7(Version):
    
    def _upgrade(self, modifier_id):
        """"""
        
            
    def _downgrade(self, modifier_id):
        """"""
        
            
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
                
        i18ns.append(I18n(i1_key="cont_label_groupsettings", i1_locale=conf.LANG_EN, i1_message=u"Contact Group Settings"))        
        i18ns.append(I18n(i1_key="cont_label_groupsettings", i1_locale=conf.LANG_ZH_CN, i1_message=u"联系人分组设置"))
        i18ns.append(I18n(i1_key="task_label_changelog", i1_locale=conf.LANG_EN, i1_message=u"Task Change Log"))        
        i18ns.append(I18n(i1_key="task_label_changelog", i1_locale=conf.LANG_ZH_CN, i1_message=u"修改历史"))
        i18ns.append(I18n(i1_key="task_label_changetask", i1_locale=conf.LANG_EN, i1_message=u"Change Task"))        
        i18ns.append(I18n(i1_key="task_label_changetask", i1_locale=conf.LANG_ZH_CN, i1_message=u"修改工作事项"))
        i18ns.append(I18n(i1_key="task_label_taskcomment", i1_locale=conf.LANG_EN, i1_message=u"Task Comment"))
        i18ns.append(I18n(i1_key="task_label_taskcomment", i1_locale=conf.LANG_ZH_CN, i1_message=u"工作日志"))
        i18ns.append(I18n(i1_key="core_label_fieldname", i1_locale=conf.LANG_EN, i1_message=u"Field Name"))
        i18ns.append(I18n(i1_key="core_label_fieldname", i1_locale=conf.LANG_ZH_CN, i1_message=u"属性名称"))
        i18ns.append(I18n(i1_key="core_label_lastvalue", i1_locale=conf.LANG_EN, i1_message=u"Last Value"))
        i18ns.append(I18n(i1_key="core_label_lastvalue", i1_locale=conf.LANG_ZH_CN, i1_message=u"值（修改前）"))
        i18ns.append(I18n(i1_key="core_label_presentvalue", i1_locale=conf.LANG_EN, i1_message=u"Present Value"))
        i18ns.append(I18n(i1_key="core_label_presentvalue", i1_locale=conf.LANG_ZH_CN, i1_message=u"值（修改后）"))
        
        return i18ns
    
