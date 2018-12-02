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
from core import properti, user
from core.model import Model
from core.properti import UniqueValidator


NOTE_MODULE_NAME = "note"

class Notebook(Model):
    MODULE = NOTE_MODULE_NAME
    nb_name = properti.StringProperty("notebookName", required=True, length=80, validator=[properti.IllegalValidator(), UniqueValidator("nb_name", scope="creator_id")])
    nb_order = properti.IntegerProperty("notebookOrder", required=False, default=0)
    group_id = properti.IntegerProperty("groupKey", required=False)
    
    def to_dict(self):
        self.creatorDisplayName = user.get_user_display_name(self.creator_id)
        from contact.contactservice import ContactService
        self.groupName = ContactService.get_instance().get_group_name(self.group_id)
        return Model.to_dict(self)

class Note(Model):
    MODULE = NOTE_MODULE_NAME
    n_subject = properti.StringProperty("noteSubject", required=False, length=255, validator=properti.IllegalValidator())
    n_content = properti.StringProperty("noteContent", required=False, length=4294967295, validator=properti.IllegalValidator())
    notebook_id = properti.IntegerProperty("notebookKey", required=True)
    is_trashed = properti.BooleanProperty("isTrashed", default=False)
    n_author = properti.StringProperty("noteAuthor", required=False, length=80, validator=properti.IllegalValidator())
    n_original = properti.StringProperty("noteOriginal", required=False, length=80, validator=properti.IllegalValidator())
    
    def to_dict(self):
        self.creatorDisplayName = user.get_user_display_name(self.creator_id)
        return Model.to_dict(self)

