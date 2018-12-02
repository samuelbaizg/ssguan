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


class V3(Version):
    
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
        i18ns.append(I18n(i1_key="task_label_highprioritytasks", i1_locale=conf.LANG_EN, i1_message=u"High Priority Tasks"))
        i18ns.append(I18n(i1_key="task_label_highprioritytasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"高优先级的工作"))
        i18ns.append(I18n(i1_key="task_label_completetasks", i1_locale=conf.LANG_EN, i1_message=u"Complete Tasks"))
        i18ns.append(I18n(i1_key="task_label_completetasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"已完成的工作"))
        i18ns.append(I18n(i1_key="task_label_activetasks", i1_locale=conf.LANG_EN, i1_message=u"Active Tasks"))
        i18ns.append(I18n(i1_key="task_label_activetasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"未完成的工作"))
        i18ns.append(I18n(i1_key="task_label_assignedtasks", i1_locale=conf.LANG_EN, i1_message=u"Assigned Tasks"))
        i18ns.append(I18n(i1_key="task_label_assignedtasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"委派他人的工作"))
        i18ns.append(I18n(i1_key="task_label_asaptasks", i1_locale=conf.LANG_EN, i1_message=u"Next Action Tasks"))
        i18ns.append(I18n(i1_key="task_label_asaptasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"尽快完成的工作"))
        i18ns.append(I18n(i1_key="task_label_pipelinetasks", i1_locale=conf.LANG_EN, i1_message=u"Next {{days}} Days Tasks"))
        i18ns.append(I18n(i1_key="task_label_pipelinetasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"{{days}}天内的工作"))
        i18ns.append(I18n(i1_key="task_label_overduetasks", i1_locale=conf.LANG_EN, i1_message=u"Overdue Tasks"))
        i18ns.append(I18n(i1_key="task_label_overduetasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"过期的工作"))
        i18ns.append(I18n(i1_key="task_label_notimelimittasks", i1_locale=conf.LANG_EN, i1_message=u"No Time Constraints Tasks"))
        i18ns.append(I18n(i1_key="task_label_notimelimittasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"没有时间限制的工作"))
        i18ns.append(I18n(i1_key="task_confirm_recovertask", i1_locale=conf.LANG_EN, i1_message=u"Do you confirm to recover this task to {{worksheet}}?"))
        i18ns.append(I18n(i1_key="task_confirm_recovertask", i1_locale=conf.LANG_ZH_CN, i1_message=u"你确定要恢复这个工作事项到{{worksheet}}吗？"))
        
        i18ns.append(I18n(i1_key="cont_error_assignedtasks", i1_locale=conf.LANG_EN, i1_message=u"This contact can't be deleted because he/she is assigned tasks."))
        i18ns.append(I18n(i1_key="cont_error_assignedtasks", i1_locale=conf.LANG_ZH_CN, i1_message=u"不能删除这个联系人，因为他/她被安排了工作！"))
        return i18ns
