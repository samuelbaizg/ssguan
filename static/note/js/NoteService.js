'use strict';
//  Copyright 2015 www.suishouguan.com
//
//  Licensed under the Private License (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      https://github.com/samuelbaizg/ssguan/blob/master/LICENSE
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

var NoteService = function(http, $q, $translate) {

	var factory = {};

	factory.fetchNotebookList = function() {
		return http.post('d?ha=notebooklist', {}).then(function(data) {
			return data;
		});
	};

	factory.saveNotebook = function(notebook) {
		return http.post('d?ha=savenotebook', {
			key : notebook.key,
			notebookName : notebook.notebookName,
			groupKey : notebook.groupKey,
			rowVersion : notebook.rowVersion
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteNotebook = function(notebook) {
		return http.post('d?ha=deletenotebook', {
			notebookKey : notebook.key
		}).then(function(data) {
			return data;
		});
	};

	factory.emptyNoteTrash = function() {
		return http.post('d?ha=emptynotetrash', {}).then(function(data) {
			return data;
		});
	};

	factory.fetchNoteList = function(filters, page) {
		var postData = {
			filters : angular.toJson(filters),
			offset : page == undefined ? 1 : page,
			limit : 25
		};
		return http.post('d?ha=notelist', postData).then(function(data) {
			return data;
		});
	};

	factory.saveNote = function(note) {
		return http.post('d?ha=savenote', {
			key : note.key,
			noteSubject : note.noteSubject,
			noteContent : note.noteContent,
			notebookKey : note.notebookKey,
			rowVersion : note.rowVersion
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteNote = function(note) {
		return http.post('d?ha=deletenote', {
			noteKey : note.key
		}).then(function(data) {
			return data;
		});
	};

	factory.recoverNote = function(note, notebook) {
		return http.post('d?ha=recovernote', {
			noteKey : note.key,
			notebookKey : notebook.key
		}).then(function(data) {
			return data;
		});
	};

	return factory;

};

NoteService.$inject = [ 'dsHttp', '$q', '$translate' ];
