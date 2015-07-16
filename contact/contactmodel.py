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
from core import properti, user, model
from core.model import Model
from core.properti import UniqueValidator


CONTACT_MODULE_NAME = "cont"

class Group(Model):
    MODULE = CONTACT_MODULE_NAME
    group_name = properti.StringProperty("groupName", required=True, length=80, validator=[properti.IllegalValidator(), UniqueValidator("group_name", scope="creator_id")])
    group_order = properti.IntegerProperty("groupOrder", required=False, default=0)
    is_shared = properti.BooleanProperty("isShared", default=False)
    group_startdate = properti.DateProperty("groupStartdate", required=False, fmt=conf.get_date_py_format())
    group_finishdate = properti.DateProperty("groupFinishdate", required=False, fmt=conf.get_date_py_format(), validator=[properti.CompareValidator(">=", property_name="group_startdate")])
    workday_monday = properti.FloatProperty("workdayMonday", required=True, default=0.0, choices=[0.0, 0.5, 1.0])
    workday_tuesday = properti.FloatProperty("workdayTuesday", required=True, default=0.0, choices=[0.0, 0.5, 1.0])
    workday_wednesday = properti.FloatProperty("workdayWednesday", required=True, default=0.0, choices=[0.0, 0.5, 1.0])
    workday_thursday = properti.FloatProperty("workdayThursday", required=True, default=0.0, choices=[0.0, 0.5, 1.0])
    workday_friday = properti.FloatProperty("workdayFriday", required=True, default=0.0, choices=[0.0, 0.5, 1.0])
    workday_saturday = properti.FloatProperty("workdaySaturday", required=True, default=0.0, choices=[0.0, 0.5, 1.0])
    workday_sunday = properti.FloatProperty("workdaySunday", required=True, default=0.0, choices=[0.0, 0.5, 1.0])
    
    def to_dict(self):
        self.creatorDisplayName = user.get_user_display_name(self.creator_id)
        return Model.to_dict(self)
    
class GroupException(Model):
    MODULE = CONTACT_MODULE_NAME
    group_id = properti.IntegerProperty("groupKey", required=True)
    exp_name = properti.StringProperty("exceptionName", required=True, length=80, validator=[properti.IllegalValidator(), UniqueValidator("exp_name", scope="creator_id")])
    exp_startdate = properti.DateProperty("expStartDate", required=True, fmt=conf.get_date_py_format())
    exp_finishdate = properti.DateProperty("expFinishDate", required=True, fmt=conf.get_date_py_format(), validator=[properti.CompareValidator(">=", property_name="exp_startdate")])
    is_work = properti.BooleanProperty("isWork", required=True, default=False)
    
class GroupVersion(Model):
    MODULE = CONTACT_MODULE_NAME
    group_id = properti.IntegerProperty("groupKey", required=True)
    ver_name = properti.StringProperty("versionName", required=True, length=80, validator=[properti.IllegalValidator(), UniqueValidator("ver_name", scope="creator_id")])
    ver_start_date = properti.DateProperty("verStartDate", required=True, fmt=conf.get_date_py_format())
    ver_finish_date = properti.DateProperty("verFinishDate", required=True, fmt=conf.get_date_py_format(), validator=[properti.CompareValidator(">=", property_name="ver_start_date")])
    is_released = properti.BooleanProperty("isReleased", required=True, default=False)
    release_date = properti.DateProperty("releaseDate", required=False, fmt=conf.get_date_py_format())
    ver_desc = properti.StringProperty("verDescription", required=False, length=1024, validator=[properti.IllegalValidator()])
    
class GroupComponent(Model):
    MODULE = CONTACT_MODULE_NAME
    group_id = properti.IntegerProperty("groupKey", required=True)
    compo_name = properti.StringProperty("componentName", required=True, length=80, validator=[properti.IllegalValidator(), UniqueValidator("compo_name", scope="creator_id")])
    compo_desc = properti.StringProperty("compoDescription", required=False, length=1024, validator=[properti.IllegalValidator()])

class Contact(Model):
    MODULE = CONTACT_MODULE_NAME
    contact_name = properti.StringProperty("contactName", required=True, length=80, validator=properti.IllegalValidator())
    ct_email_work = properti.StringProperty("emailWork", required=False, length=80, validator=properti.IllegalValidator())
    ct_email_home = properti.StringProperty("emailHome", required=False, length=80, validator=properti.IllegalValidator())
    
    ct_birthday = properti.DateProperty("birthday", required=False, fmt=conf.get_date_py_format())
    
    ct_phone_mobile_business = properti.StringProperty("mobileBusiness", required=False, length=80, validator=properti.IllegalValidator())
    ct_phone_mobile_private = properti.StringProperty("mobilePrivate", required=False, length=80, validator=properti.IllegalValidator())
    ct_phone_phone_office = properti.StringProperty("phoneOffice", required=False, length=80, validator=properti.IllegalValidator())
    ct_phone_phone_home = properti.StringProperty("phoneHome", required=False, length=80, validator=properti.IllegalValidator())
    ct_phone_fax_office = properti.StringProperty("faxOffice", required=False, length=80, validator=properti.IllegalValidator())
    ct_company_address = properti.StringProperty("companyAddress", required=False, length=200, validator=properti.IllegalValidator())
    ct_company = properti.StringProperty("company", required=False, length=80, validator=properti.IllegalValidator())
    ct_company_website = properti.StringProperty("companyWebsite", required=False, length=80, validator=properti.IllegalValidator())
    ct_department = properti.StringProperty("department", required=False, length=80, validator=properti.IllegalValidator())
    ct_position = properti.StringProperty("position", required=False, length=80, validator=properti.IllegalValidator())
    
    ct_im_qq = properti.StringProperty("imQQ", required=False, length=80, validator=properti.IllegalValidator())
    ct_im_skype = properti.StringProperty("imSkype", required=False, length=80, validator=properti.IllegalValidator())
    ct_so_weixin = properti.StringProperty("soWeixin", required=False, length=80, validator=properti.IllegalValidator())
    ct_so_weibo = properti.StringProperty("soWeibo", required=False, length=80, validator=properti.IllegalValidator())

    ct_remark = properti.StringProperty("remark", required=False, length=255, validator=properti.IllegalValidator())
    bind_user_id = properti.IntegerProperty("bindUserKey", required=False)
    bind_user_account = properti.StringProperty("bindUserAccount", required=False, persistent=False)
    is_trashed = properti.BooleanProperty("isTrashed", default=False)
    
    def to_dict(self):
        self.bind_user_account = user.get_user(user_id=self.bind_user_id).u_account if self.bind_user_id != None and self.bind_user_id != model.EMPTY_UID else ""
        self.creatorDisplayName = user.get_user_display_name(self.creator_id)
        from contact.contactservice import ContactService
        self.groupKeys = list(set(map(lambda x: x.group_id, ContactService.get_instance().fetch_contactgroups(contact_id=self.key()))))
        return Model.to_dict(self)

class ContactGroup(Model):
    MODULE = CONTACT_MODULE_NAME
    
    contact_id = properti.IntegerProperty("contactKey", required=True)
    group_id = properti.IntegerProperty("groupKey", required=True)
    join_date = properti.DateProperty("joinDate", required=False, fmt=conf.get_date_py_format())
    quit_date = properti.DateProperty("quitDate", required=False, fmt=conf.get_date_py_format())
    is_billable = properti.BooleanProperty("isBillable", required=True, default=False)
    contact_level = properti.IntegerProperty("contactLevel", required=True, default=1)
    remark = properti.StringProperty("cgRemark", required=False, length=255, validator=properti.IllegalValidator())
    
    def to_dict(self):
        from contact.contactservice import ContactService
        self.contactName = ContactService.get_instance().get_contact_name(self.contact_id)
        return Model.to_dict(self)

class ContactLeave(Model):
    MODULE = CONTACT_MODULE_NAME
    
    contact_id = properti.IntegerProperty("contactKey", required=True)
    leave_startdate = properti.DateProperty("leaveStartdate", required=True, fmt=conf.get_date_py_format())
    leave_finishdate = properti.DateProperty("leaveFinishdate", required=True, fmt=conf.get_date_py_format(), validator=[properti.CompareValidator(">=", property_name="leave_startdate")])
    leave_days = properti.FloatProperty("leaveDays", required=True)
    leave_type_code = properti.StringProperty("leaveTypeCode", length=30, required=True)
    leave_comment = properti.StringProperty("leaveComment", length=200)


    
