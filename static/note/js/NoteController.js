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

var NoteController = function($scope, $rootScope, $timeout, $filter,
		noteService) {

	$scope.TRASH_NOTEBOOK_ID = -100;
	$scope.DEFAULT_NOTEBOOK_ID = EMPTY_UID;
	$scope.notebookEditable = false;
	$scope.notebooks = null;
	$scope.activeNotebook = null;
	$scope.noteEditable = false;
	$scope.notePager = null;
	$scope.activeNote = null;

	$scope.contactGroups = null;

	var notePendingSave = false;

	$scope.$on('EVENT_SHORTCUT_NOTEBOOK', function() {
		$rootScope.showSidebar(false);
	});

	$scope.$on('EVENT_CLOSE_WSRIGHTCOL', function() {
		if (notePendingSave == true) {
			var message = $filter('translate')('note_error_pendingsave');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(true);
		}
	});

	function loadNoteModule() {
		function _loadOptions(data) {
			$scope.contactGroups = data.contactGroups;
		}

		$rootScope.$on("EVENT_RESIZE_WSRIGHTCOL", function() {
			$scope.$broadcast("EVENT_RESIZE_WYSIWYG", "noteEditor");
		});

		$scope.fetchNotebooks().then(function(data) {
			_loadOptions(data);
		});
	}

	function getNoteFilterMap() {
		var noteKeywordsMap = {};
		if ($scope.notebooks != null) {
			$.each($scope.notebooks, function(i, notebook) {
				noteKeywordsMap["nb=" + notebook.notebookName] = {
					nb : notebook.key
				};
			});
		}
		return noteKeywordsMap;
	}

	function updateNoteCount(notebookKey, count) {
		$.each($scope.notebooks, function(i, notebook) {
			if (notebook.key == notebookKey) {
				notebook.notecount += count;
				return false;
			}
		});
	}

	$scope.editNotebook = function(editable) {
		if (editable) {
			$scope.notebookEditable = true;
		} else {
			$scope.notebookEditable = false;
		}
	}

	$scope.updateNotebook = function(notebook) {
		if (notebook != undefined) {
			$scope.updatedNotebook = {};
			angular.copy(notebook, $scope.updatedNotebook);
		} else {
			$scope.updatedNotebook = {
				notebookName : "",
				groupKey : EMPTY_UID
			};
		}
		$("#notebookDialog").modal('show');
	};

	$scope.saveNotebook = function() {
		noteService.saveNotebook($scope.updatedNotebook).then(function(data) {
			$("#notebookDialog").modal('hide');
			$("#notebookDialog").on('hidden.bs.modal', function() {
				$scope.fetchNotebooks();
			});
		});
	};

	$scope.deleteNotebook = function(notebook) {
		var message = $filter('translate')('note_confirm_notebook_delete');
		infobox.confirm(message, function(result) {
			if (result == true) {
				noteService.deleteNotebook(notebook).then(function(data) {
					$scope.fetchNotebooks();
				});
			}
		});
	};

	$scope.emptyNoteTrash = function(notebook) {
		var message = $filter('translate')('note_confirm_emptytrash');
		infobox.confirm(message, function(result) {
			if (result == true) {
				noteService.emptyNoteTrash().then(function(data) {
					$scope.fetchNotebooks();
				});
			}
		});
	};

	$scope.viewNotebook = function(notebook) {
		if ($scope.notebookEditable == false) {
			$rootScope.showSidebar(true);
			$rootScope.showWsRightCol(true);
			$scope.activeNote = null;
			$scope.activeNotebook = notebook;
			$scope.noteSearchLabel = notebook.notebookName;
			$scope.noteSearchKeywords = [ "nb=" + notebook.notebookName ];
			$scope.fetchNotes();
		}
	};

	$scope.notebookClick = function(notebook, $event) {
		if (notePendingSave == true) {
			var message = $filter('translate')('note_error_pendingsave');
			infobox.alert(message);
		} else {
			var srcElmt = $($event.target);
			if (srcElmt.hasClass("fa-remove")) {
				if (notebook.key == $scope.TRASH_NOTEBOOK_ID) {
					$scope.emptyNoteTrash(notebook);
				} else {
					$scope.deleteNotebook(notebook);
				}
			} else if (srcElmt.hasClass("fa-edit")) {
				$scope.updateNotebook(notebook);
			} else {
				$scope.viewNotebook(notebook);
			}
		}
	};

	$scope.fetchNotebooks = function() {
		return noteService.fetchNotebookList().then(function(data) {
			$scope.notebooks = data.notebooks;
			if (!$scope.notebookEditable) {
				$scope.activeNotebook = $scope.notebooks[0];
				$scope.viewNotebook(data.notebooks[0]);
			}
			return data;
		});
	};

	$scope.getNoteSearchKeywordHints = function() {
		var noteSearchKeywordHints = [];
		var map = getNoteFilterMap();

		$.each(map, function(name, value) {
			noteSearchKeywordHints.push(name);
		});
		return noteSearchKeywordHints;
	};

	$scope.newNote = function() {
		var note = {
			key : "",
			noteSubject : "",
			noteContent : "",
			notebookKey : $scope.activeNotebook.key
		};
		$scope.updateNote(note, true);
	};

	$scope.editNote = function(editable) {
		if (editable) {
			$scope.noteEditable = true;
		} else {
			$scope.noteEditable = false;
		}
	};

	$scope.updateNote = function(note, editable) {
		if (notePendingSave == true) {
			var message = $filter('translate')('note_error_pendingsave');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(false);
			$("#noteSaveStatusDiv").html("");
			$scope.activeNote = {};
			angular.copy(note, $scope.activeNote);
			$.each($scope.notebooks, function(i, notebook) {
				if ($scope.activeNote.notebookKey == notebook.key) {
					$scope.activeNote.notebookName = notebook.notebookName;
					return false;
				}
			});
			$scope.activeNote.original = note;
			if (editable == true) {
				$('#subjectTxt').focus();
				$scope.noteEditable = true;
			} else {
				$scope.noteEditable = false;
			}
		}
	};

	$scope.saveNote = function(auto) {
		notePendingSave = true;
		var oldnoteKey = $scope.activeNote.key;

		function _addNote(note) {
			$scope.notePager.records.unshift(note);
			$scope.notePager.count += 1;
			if ($scope.notePager.count == 1) {
				$scope.notePager.page = 1;
				$scope.notePager.pageNumbers = [ 1 ];
				$scope.notePager.total = 1;
			}
			updateNoteCount(note.notebookKey, 1);
			$scope.activeNote.original = note;
			$scope.activeNote.key = note.key;
		}

		return noteService.saveNote($scope.activeNote).then(function(note) {
			var oldNbId = $scope.activeNote.original.notebookKey;
			angular.copy(note, $scope.activeNote.original);
			$scope.activeNote.rowVersion = note.rowVersion;
			if (oldnoteKey == null || oldnoteKey == '') {
				_addNote(note);
			} else {
				updateNoteCount($scope.activeNote.notebookKey, 1);
				updateNoteCount(oldNbId, -1);
			}
			notePendingSave = false;
			if (!auto) {
				$scope.noteEditable = false;
			}
			return note;
		}, function(data) {
			notePendingSave = false;
		});
	};
	
	$scope.cancelSaveNote = function() {
		var bak = $scope.activeNote.original;
		angular.copy($scope.activeNote.original, $scope.activeNote);
		$scope.activeNote.original = bak;
		notePendingSave = false;
		$scope.noteEditable = false;
	};

	$scope.deleteNote = function() {
		function _deleteNote(result) {
			if (result == true) {
				noteService.deleteNote($scope.activeNote).then(function(data) {
					updateNoteCount($scope.activeNote.notebookKey, -1);
					updateNoteCount($scope.TRASH_NOTEBOOK_ID, 1);
					$scope.activeNote = null;
					$scope.fetchNotes().then(function(data) {
						$rootScope.showWsRightCol(true);
					});
				});
			}
		}
		var message = $filter('translate')('note_confirm_deletenote');
		infobox.confirm(message, function(result) {
			_deleteNote(result);
		});
	};

	$scope.permanentDeleteNote = function() {
		function _permanentDeleteNote(result) {
			if (result == true) {
				noteService.deleteNote($scope.activeNote).then(function(data) {
					updateNoteCount($scope.TRASH_NOTEBOOK_ID, -1);
					$scope.activeNote = null;
					$scope.fetchNotes().then(function(data) {
						$rootScope.showWsRightCol(true);
					});
				});
			}
		}
		var message = $filter('translate')('note_confirm_permanentdeletenote');
		infobox.confirm(message, function(result) {
			_permanentDeleteNote(result);
		});
	};

	$scope.recoverNote = function(notebook) {
		function _recoverNote(result) {
			if (result == false) {
				return true;
			}
			noteService.recoverNote($scope.activeNote, notebook).then(
					function(data) {
						updateNoteCount(notebook.key, 1);
						updateNoteCount($scope.TRASH_NOTEBOOK_ID, -1);
						$scope.fetchNotes();
					});
		}
		var message = $filter('translate')('note_confirm_recovernote', {
			notebook : notebook.notebookName
		});
		infobox.confirm(message, function(result) {
			_recoverNote(result);
		});
	};

	$scope.searchNote = function() {
		$("#noteSearchDialog").modal('show');
	};

	$scope.submitNoteSearch = function() {
		$("#noteSearchDialog").modal('hide');
		$scope.noteSearchLabel = $filter("translate")
				("core_label_searchresult");
		$scope.fetchNotes();
	};

	$scope.fetchNotes = function(page, addMore) {

		function _getFilters() {
			var keywordsArr = $scope.noteSearchKeywords;
			var noteKeywordsMap = getNoteFilterMap();
			var arr = [];
			for ( var i in keywordsArr) {
				var kw = noteKeywordsMap[keywordsArr[i]];
				arr.push(kw ? kw : {
					kw : keywordsArr[i]
				});
			}
			return arr;
		}

		page = page == undefined ? 1 : page;
		addMore = addMore == undefined ? false : addMore;
		if (addMore == false || $scope.notePager.total >= page) {

			return noteService.fetchNoteList(_getFilters(), page).then(
					function(data) {
						if (addMore == true) {
							var records = $scope.notePager.records
									.concat(data.records);
							$scope.notePager = data;
							$scope.notePager.records = records;
						} else {
							$scope.notePager = data;
						}
						
						$scope.activeNote = null;
						$rootScope.showWsRightCol(true);
						
						return data;
					});
		}
	};

	loadNoteModule();

};

NoteController.$inject = [ '$scope', '$rootScope', '$timeout', '$filter',
		'noteService' ];