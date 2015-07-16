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
from contact.contactservice import ContactService
from core import jsonutil, filex, user
from core import model, i18n
from core import strutil
from core.handler import Handler
from core.model import stdModel
from note.notemodel import Note
from note.notemodel import Notebook
from note.noteservice import NoteService
import web


class NotebookSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        notebook = self._get_model_parameter(Notebook)
        if strutil.is_empty(notebook.key()):
            notebook.creator_id = self._get_user_id()
            notebook = NoteService.get_instance().create_notebook(notebook, self._get_user_id())
        else:
            notebook = NoteService.get_instance().update_notebook(notebook, self._get_user_id())
        rtn.set_data(notebook)
        return rtn.to_json()

class NotebookDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        notebook_id = self._get_int_parameter("notebookKey")
        status = NoteService.get_instance().delete_notebook(notebook_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class NotebookMoveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        notebook_id = self._get_int_parameter("notebookKey")
        notebook = NoteService.get_instance().get_notebook(notebook_id)
        notebook = NoteService.get_instance().update_notebook(notebook, self._get_user_id())
        rtn.set_data(notebook)
        return rtn.to_json()

class NoteEmptyTrashHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        status = NoteService.get_instance().empty_trash(self._get_user_id(), self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class NotebookListHandler(Handler):
    
    def execute(self):        
        rtn = self._new_rtn()
        notebooks = NoteService.get_instance().fetch_notebooks(self._get_user_id())
        std = stdModel()
        defaultnotebook = Notebook()
        defaultnotebook.uid = model.EMPTY_UID
        defaultnotebook.nb_name = i18n.get_i18n_message(conf.get_preferred_language(), "note_label_defaultnotebook")
        defaultnotebook.notecount = NoteService.get_instance().get_notecount(False, self._get_user_id(), notebook_id=model.EMPTY_UID)
        defaultnotebook.creator_id = self._get_user_id()
        notebooks.insert(0, defaultnotebook);
        
        trash = Notebook()
        trash.uid = -100
        trash.nb_name = i18n.get_i18n_message(conf.get_preferred_language(), "note_label_recyclebin")
        trash.notecount = NoteService.get_instance().get_notecount(True, self._get_user_id())
        trash.creator_id = self._get_user_id()
        notebooks.append(trash)
        
        std.notebooks = notebooks
        std.notecount = NoteService.get_instance().get_notecount(False, self._get_user_id())
        std.contactGroups = ContactService.get_instance().fetch_my_groups(self._get_user_id())
        
        stmnotebooks = NoteService.get_instance().fetch_notebooks(self._get_user_id(), sharetome=True)
        notebooks.extend(stmnotebooks)
        
        rtn.set_data(std)
        return rtn.to_json()

class NoteListHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        offset = self._get_int_parameter('offset', 1)
        limit = self._get_int_parameter('limit', 20)
        filters = self._get_str_parameter('filters')
        filters = jsonutil.to_dict(filters)
        pager = NoteService.get_instance().fetch_notes(self._get_user_id(), filters=filters, limit=limit, offset=offset)
        for note in pager.records:
            note.files = jsonutil.to_json(filex.fetch_files(self._get_user_id(), (Note.get_modelname(), note.key())))
        rtn.set_data(pager)
        return rtn.to_json()
        
class NoteSaveHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        note = self._get_model_parameter(Note)        
        if strutil.is_empty(note.key()):
            note.creator_id = self._get_user_id()
            note = NoteService.get_instance().create_note(note, self._get_user_id())
        else:
            note = NoteService.get_instance().update_note(note, self._get_user_id())
        rtn.set_data(note)
        return rtn.to_json()

class NoteDeleteHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        note_id = self._get_int_parameter("noteKey")
        status = NoteService.get_instance().delete_note(note_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()

class NoteRecoverHandler(Handler):
    
    def execute(self):
        rtn = self._new_rtn()
        note_id = self._get_int_parameter("noteKey")
        notebook_id = self._get_int_parameter("notebookKey")
        status = NoteService.get_instance().recover_note(note_id, notebook_id, self._get_user_id())
        rtn.set_data(status)
        return rtn.to_json()
    
    

