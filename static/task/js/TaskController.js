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

var TaskController = function($scope, $rootScope, $timeout, $filter,
		$translate, taskService, contactService) {

	$scope.TRASH_WORKSHEET_ID = -100;
	$scope.DEFAULT_WORKSHEET_ID = EMPTY_UID;
	$scope.worksheetEditable = false;
	$scope.worksheets = null;
	$scope.activeWorksheet = null;
	$scope.taskEditable = false;
	$scope.taskPager = null;
	$scope.activeTask = null;
	$scope.taskSearchResultsShown = false;
	$scope.baseData = {};

	$scope.contacts = null;

	var taskPendingSave = false;

	$scope.$on('EVENT_SHORTCUT_WORKSHEET', function() {
		$rootScope.showSidebar(false);
	});

	$scope.$on('EVENT_CLOSE_WSRIGHTCOL', function() {
		if (taskPendingSave == true) {
			var message = $filter('translate')('task_error_pendingsave');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(true);
		}
	});

	function loadTaskModule() {

		function _loadOptions(data) {
			$scope.contactGroups = data.contactGroups;
			$scope.baseData.worksheetContacts = data.worksheetContacts;
			$scope.baseData.worksheetComponents = data.worksheetComponents;
			$scope.baseData.worksheetVersions = data.worksheetVersions;
		}

		$scope.fetchWorksheets().then(function(data) {
			_loadOptions(data);
		});
	}

	function getTaskFilterMap() {
		var taskKeywordsMap = {};
		function _worksheetFilter() {
			if ($scope.worksheets != null) {
				$.each($scope.worksheets, function(i, worksheet) {
					taskKeywordsMap["ws=" + worksheet.worksheetName] = {
						ws : worksheet.key
					};
				});
			}
		}
		function _taskStatusFilter() {
			taskKeywordsMap['st='
					+ $filter('translate')('task_label_completetasks')] = {
				st : 'task_code_closed'
			};
			taskKeywordsMap['st='
					+ $filter('translate')('task_label_activetasks')] = {
				st : 'active'
			};

			$.each($rootScope.envVar.TASKSTATUS_OPTIONS, function(name, value) {
				taskKeywordsMap['st=' + value] = {
					st : name
				};
			});
		}

		function _taskPriorityFilter() {
			taskKeywordsMap['pr='
					+ $filter('translate')('task_label_highprioritytasks')] = {
				pr : 'high'
			};

			$.each($rootScope.envVar.TASKPRIORITY_OPTIONS,
					function(name, value) {
						taskKeywordsMap['pr=' + value] = {
							pr : name
						};
					});
		}

		function _taskTypeFilter() {
			$.each($rootScope.envVar.TASKTYPE_OPTIONS, function(name, value) {
				taskKeywordsMap['tt=' + value] = {
					tt : name
				};
			});
		}

		function _daysFilter() {
			taskKeywordsMap['dt='
					+ $filter('translate')('task_label_asaptasks')] = {
				dt : 1
			};
			taskKeywordsMap['dt='
					+ $filter('translate')('task_label_overduetasks')] = {
				dt : -101
			};
			taskKeywordsMap['dt='
					+ $filter('translate')('task_label_notimelimittasks')] = {
				dt : -102
			};

			var days = [ 7, 15 ];
			for ( var i in days) {
				taskKeywordsMap['dt='
						+ $filter('translate')('task_label_pipelinetasks', {
							days : days[i]
						})] = {
					dt : days[i]
				};
			}
		}

		function _assigneeFilter() {
			taskKeywordsMap['as='
					+ $filter('translate')('task_label_assignedtasks')] = {
				as : EMPTY_UID
			};
			taskKeywordsMap['as='
					+ $filter('translate')('task_label_assignedtometasks')] = {
				as : -201
			};
			if ($scope.baseData.worksheetContacts != null) {
				$.each($scope.baseData.worksheetContacts, function(
						worksheetKey, contacts) {
					$.each(contacts, function(i, contact) {
						taskKeywordsMap['as=' + contact.contactName] = {
							as : contact.key
						};
					});
				});
			}
		}

		function _componentFilter() {
			if ($scope.baseData.worksheetComponents != null) {
				$.each($scope.baseData.worksheetComponents, function(
						worksheetKey, components) {
					$.each(components, function(i, component) {
						taskKeywordsMap['co=' + component.componentName] = {
							co : component.key
						};
					});
				});
			}
		}

		function _versionFilter() {
			if ($scope.baseData.worksheetVersions != null) {
				$.each($scope.baseData.worksheetVersions, function(
						worksheetKey, versions) {
					$.each(versions, function(i, version) {
						taskKeywordsMap['fv=' + version.versionName] = {
							fv : version.key
						};
						taskKeywordsMap['av=' + version.versionName] = {
							av : version.key
						};
					});
				});
			}
		}

		_worksheetFilter();
		_taskStatusFilter();
		_taskPriorityFilter();
		_taskTypeFilter();
		_daysFilter();
		_assigneeFilter();
		_componentFilter();
		_versionFilter();
		return taskKeywordsMap;
	}

	function updateTaskCount(worksheetKey, count) {
		$.each($scope.worksheets, function(i, worksheet) {
			if (worksheet.key == worksheetKey) {
				worksheet.taskcount += count;
				return false;
			}
		});
	}

	$scope.editWorksheet = function(editable) {
		if (editable) {
			$scope.worksheetEditable = true;
		} else {
			$scope.worksheetEditable = false;
		}
	}

	$scope.updateWorksheet = function(worksheet) {
		if (worksheet != undefined) {
			$scope.updatedWorksheet = {};
			angular.copy(worksheet, $scope.updatedWorksheet);
		} else {
			$scope.updatedWorksheet = {
				worksheetName : "",
				groupKey : EMPTY_UID
			};
		}
		$("#worksheetDialog").modal('show');

	};

	$scope.saveWorksheet = function() {
		taskService.saveWorksheet($scope.updatedWorksheet).then(function(data) {
			$("#worksheetDialog").modal('hide');
			$("#worksheetDialog").on('hidden.bs.modal', function() {
				$scope.fetchWorksheets();
			});
		});
	};

	$scope.deleteWorksheet = function(worksheet) {
		var message = $filter('translate')('task_confirm_worksheet_delete');
		infobox.confirm(message, function(result) {
			if (result == true) {
				taskService.deleteWorksheet(worksheet).then(function(data) {
					$scope.fetchWorksheets();
				});
			}
		});
	};

	$scope.emptyTaskTrash = function(worksheet) {
		var message = $filter('translate')('task_confirm_emptytrash');
		infobox.confirm(message, function(result) {
			if (result == true) {
				taskService.emptyTaskTrash().then(function(data) {
					$scope.fetchWorksheets();
				});
			}
		});
	};

	$scope.viewWorksheet = function(worksheet) {
		if ($scope.worksheetEditable == false) {
			$rootScope.showSidebar(true);
			$rootScope.showWsRightCol(true);
			$scope.activeTask = null;
			$scope.activeWorksheet = worksheet;
			$scope.taskSearchLabel = worksheet.worksheetName;
			$scope.taskSearchKeywords = [ "ws=" + worksheet.worksheetName ];
			$scope.fetchTasks();
		}
	};

	$scope.worksheetClick = function(worksheet, $event) {
		if (taskPendingSave == true) {
			var message = $filter('translate')('task_error_pendingsave');
			infobox.alert(message);
		} else {
			var srcElmt = $($event.target);
			if (srcElmt.hasClass("fa-remove")) {
				if (worksheet.key == $scope.TRASH_WORKSHEET_ID) {
					$scope.emptyTaskTrash(worksheet);
				} else {
					$scope.deleteWorksheet(worksheet);
				}
			} else if (srcElmt.hasClass("fa-edit")) {
				$scope.updateWorksheet(worksheet);
			} else {
				$scope.viewWorksheet(worksheet);
			}
		}
	};

	$scope.fetchWorksheets = function() {
		return taskService.fetchWorksheetList().then(function(data) {
			$scope.worksheets = data.worksheets;
			if (!$scope.worksheetEditable) {
				$scope.activeWorksheet = data.worksheets[0];
				$scope.viewWorksheet($scope.worksheets[0]);
			}
			return data;
		});
	};

	$scope.getTaskSearchKeywordHints = function() {
		var taskSearchKeywordHints = [];

		var map = getTaskFilterMap();

		$.each(map, function(name, value) {
			taskSearchKeywordHints.push(name);
		});

		return taskSearchKeywordHints;
	};

	$scope.worksheetChange = function(pendingSave) {
		if (pendingSave) {
			taskPendingSave = true;
		}
		var components = $scope.baseData.worksheetComponents[$scope.activeTask.worksheetKey];
		components = (components != null) ? components : [];
		delete $scope.components;
		$scope.components = [];
		angular.copy(components, $scope.components);
		var versions = $scope.baseData.worksheetVersions[$scope.activeTask.worksheetKey];
		versions = (versions != null) ? versions : [];
		delete $scope.versions;
		$scope.versions = [];
		angular.copy(versions, $scope.versions);
		var contacts = $scope.baseData.worksheetContacts[$scope.activeTask.worksheetKey];
		contacts = (contacts != null) ? contacts : [];
		delete $scope.contacts;
		$scope.contacts = [];
		angular.copy(contacts, $scope.contacts);
	};

	$scope.newTask = function() {
		var task = {
			key : "",
			planProgress : "NA",
			taskPriorityCode : 'task_code_p3',
			taskStatusCode : 'task_code_open',
			taskTypeCode : 'task_code_task',
			dueStartdate : $filter('date')(new Date(),
					$rootScope.loginUser.dateFormat),
			dueFinishdate : null,
			actualProgress : 0,
			storyPoints : $rootScope.envVar.DEFAULT_STORY_POINTS,
			taskAssigneeKey : $rootScope.loginUser.contactKey,
			worksheetKey : $scope.activeWorksheet.key,
			taskComments : []
		};
		task.dueFinishdate = task.dueStartdate;
		$scope.updateTask(task, true);
	};

	$scope.editTask = function(editable) {
		if (editable) {
			$scope.taskEditable = true;
		} else {
			$scope.taskEditable = false;
		}
	};

	$scope.updateTask = function(task, editable) {
		if (taskPendingSave == true) {
			var message = $filter('translate')('task_error_pendingsave');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(false);
			$("#taskSaveStatusDiv").html("");
			$scope.activeTask = {};
			angular.copy(task, $scope.activeTask);
			$scope.activeTask.original = task;
			$scope.worksheetChange();
			if (editable == true) {
				$('#taskSubjectTxt').focus();
				$scope.taskEditable = true;
			} else {
				$scope.taskEditable = false;
			}
		}
	};

	$scope.saveTask = function(auto) {
		taskPendingSave = true;
		var oldtaskKey = $scope.activeTask.key;
		var oldtaskStatusCode = $scope.activeTask.original.taskStatusCode;
		var oldtaskAssigneeKey = $scope.activeTask.original.taskAssigneeKey;
		$scope.activeTask.taskAssigneeKey = $("#assigneeSelt").val();
		$scope.activeTask.componentKeys = $("#componentSelt").val();
		$scope.activeTask.affectedVersionKeys = $("#affectedVersionSelt").val();
		$scope.activeTask.fixedVersionKeys = $("#fixedVersionSelt").val();

		function _addTask(task) {
			$scope.taskPager.records.unshift(task);
			$scope.taskPager.count += 1;
			if ($scope.taskPager.count == 1) {
				$scope.taskPager.page = 1;
				$scope.taskPager.pageNumbers = [ 1 ];
				$scope.taskPager.total = 1;
			}
			$scope.activeTask.creatorDisplayName = task.creatorDisplayName;
			$scope.activeTask.createdTime = task.createdTime;
			updateTaskCount(task.worksheetKey, 1);
		}

		return taskService.saveTask($scope.activeTask).then(function(task) {
			var oldNbId = $scope.activeTask.original.worksheetKey;
			angular.copy(task, $scope.activeTask.original);
			$scope.activeTask.planProgress = task.planProgress;
			$scope.activeTask.original = task;
			$scope.activeTask.key = task.key;
			$scope.activeTask.modifiedTime = task.modifiedTime;
			$scope.activeTask.rowVersion = task.rowVersion;
			$scope.activeTask.actualStartdate = task.actualStartdate;
			$scope.activeTask.actualFinishdate = task.actualFinishdate;
			$scope.activeTask.mclogs = task.mclogs;
			if (oldtaskKey == null || oldtaskKey == '') {
				_addTask(task);
			} else {
				updateTaskCount($scope.activeTask.worksheetKey, 1);
				updateTaskCount(oldNbId, -1);
			}
			taskPendingSave = false;
			if (!auto) {
				$scope.taskEditable = false;
			}
			return task;
		}, function(data) {
			taskPendingSave = false;
		});
	};

	$scope.autoSaveTask = function($event) {
		if ($scope.taskEditable) {
			taskPendingSave = true;
		}
		if ($event != null) {
			var srcElmt = $($event.target);
			if (srcElmt.prop("id") === "actualProgressTxt") {
				if (srcElmt.val() === "100") {
					$scope.activeTask.taskStatusCode = 'task_code_closed';
				} else {
					$scope.activeTask.taskStatusCode = 'task_code_inprogress';
				}
			}
		}
	};

	$scope.cancelSaveTask = function() {
		var bak = $scope.activeTask.original;
		angular.copy($scope.activeTask.original, $scope.activeTask);
		$scope.activeTask.original = bak;
		taskPendingSave = false;
		$scope.taskEditable = false;
		$scope.worksheetChange();
	};

	$scope.taskStatusChange = function($event) {
		taskPendingSave = true;
		if ($scope.activeTask.taskStatusCode == 'task_code_closed') {
			$scope.activeTask.actualProgress = 100;
		}
	};

	$scope.deleteTask = function() {

		function _deleteTask(result) {
			if (result == true) {
				taskService.deleteTask($scope.activeTask).then(function(data) {
					updateTaskCount($scope.activeTask.worksheetKey, -1);
					updateTaskCount($scope.TRASH_WORKSHEET_ID, 1);
					$scope.activeTask = null;
					$scope.fetchTasks().then(function(data) {
						$rootScope.showWsRightCol(true);
					});
				});
			}
		}
		var message = $filter('translate')('task_confirm_deletetask');
		infobox.confirm(message, function(result) {
			_deleteTask(result);
		});
	};

	$scope.permanentDeleteTask = function() {
		function _permanentDeleteTask(result) {
			if (result == true) {
				taskService.deleteTask($scope.activeTask).then(function(data) {
					updateTaskCount($scope.TRASH_WORKSHEET_ID, -1);
					$scope.activeTask = null;
					$scope.fetchTasks(function(data) {
						$rootScope.showWsRightCol(true);
					});
				});
			}
		}
		var message = $filter('translate')('task_confirm_permanentdeletetask');
		infobox.confirm(message, function(result) {
			_permanentDeleteTask(result);
		});
	};

	$scope.recoverTask = function(worksheet) {

		function _recoverTask(result) {
			if (result == true) {
				taskService.recoverTask($scope.activeTask,
						$scope.DEFAULT_WORKSHEET_ID).then(function(data) {
					updateTaskCount($scope.DEFAULT_WORKSHEET_ID, 1);
					updateTaskCount($scope.TRASH_WORKSHEET_ID, -1);
					$scope.fetchTasks();
				});
			}
		}
		var message = $filter('translate')('task_confirm_recovertask', {
			worksheet : $scope.worksheets[0].worksheetName
		});
		infobox.confirm(message, function(result) {
			_recoverTask(result);
		});
	};

	$scope.searchTask = function() {
		$("#taskSearchDialog").modal('show');
	};

	$scope.shortcutClick = function(shortcutKey, shortcutLbl, lblArgs) {
		$scope.taskSearchKeywords = [];
		var message = $filter('translate')(shortcutLbl, lblArgs);
		$scope.taskSearchKeywords.push(shortcutKey + message);
		$scope.taskSearchLabel = message;
		$("#taskSearchDialog").modal('hide');
		$scope.fetchTasks();
	}

	$scope.submitTaskSearch = function() {
		$("#taskSearchDialog").modal('hide');
		$scope.taskSearchLabel = $filter('translate')
				('core_label_searchresult');
		$scope.fetchTasks();
	};

	$scope.fetchTasks = function(page, addMore) {

		function _getFilters() {
			var keywordsArr = $scope.taskSearchKeywords;
			var taskKeywordsMap = getTaskFilterMap();
			var arr = [];
			for ( var i in keywordsArr) {
				var kw = taskKeywordsMap[keywordsArr[i]];
				arr.push(kw ? kw : {
					kw : keywordsArr[i]
				});
			}
			return arr;
		}

		page = page == undefined ? 1 : page;
		addMore = addMore == undefined ? false : addMore;
		if (addMore == false || $scope.taskPager.total >= page) {
			return taskService.fetchTaskList(_getFilters(), page).then(
					function(data) {
						if (addMore == true) {
							var records = $scope.taskPager.records
									.concat(data.records);
							$scope.taskPager = data;
							$scope.taskPager.records = records;
						} else {
							$scope.taskPager = data;
						}
						$scope.activeTask = null;
						$rootScope.showWsRightCol(true);
						return data;
					});
		}
	};

	loadTaskModule();

	var taskCommentPendingSave = false;

	$scope.newTaskComment = function() {
		var taskcomment = {
			key : "",
			tcContent : "",
			taskKey : $scope.activeTask.key
		};
		$scope.updateTaskComment(taskcomment, true);
	};

	$scope.updateTaskComment = function(taskComment, editable) {
		$scope.activeTaskComment = {};
		angular.copy(taskComment, $scope.activeTaskComment);
		$scope.activeTaskComment.original = taskComment;
		$("#taskCommentEditDialog").modal('show');
		$('#taskCommentEditDialog').on('shown.bs.modal', function() {
			$("#taskCommentSaveStatusDiv").html("");
		});
		$('#taskCommentEditDialog').on('hide.bs.modal', function() {
			taskCommentPendingSave = false;
		});
	}

	$scope.saveTaskComment = function(auto) {
		taskCommentPendingSave = true;
		$scope
		var oldTaskCommentId = $scope.activeTaskComment.key;
		function _addTaskComment(taskComment) {
			$scope.activeTask.taskComments.unshift(taskComment);
			$scope.activeTask.original.taskComments.unshift(taskComment);
			$scope.activeTaskComment.original = taskComment;
			$scope.activeTaskComment.key = taskComment.key;
			$scope.activeTaskComment.creatorKey = taskComment.creatorKey;
		}
		return taskService
				.saveTaskComment($scope.activeTaskComment)
				.then(
						function(data) {
							var taskComment = data;
							angular.copy(taskComment,
									$scope.activeTaskComment.original);
							$scope.activeTaskComment.rowVersion = taskComment.rowVersion;
							if (oldTaskCommentId == null
									|| oldTaskCommentId == '') {
								_addTaskComment(taskComment);
							}
							taskCommentPendingSave = false;
							if (!auto) {
								$("#taskCommentEditDialog").modal('hide');
							}
							return taskComment;
						}, function(data) {
							taskCommentPendingSave = false;
						});
	};

	$scope.deleteTaskComment = function(taskComment) {
		function _deleteTaskComment() {
			taskService.deleteTaskComment(taskComment).then(function(data) {
				$.each($scope.activeTask.taskComments, function(i, tc) {
					if (taskComment.key == tc.key) {
						$scope.activeTask.taskComments.splice(i, 1);
						return false;
					}
				});
			});
		}
		var message = $filter('translate')('task_confirm_taskcomment_delete');
		infobox.confirm(message, function(result) {
			if (result == true) {
				_deleteTaskComment();
			}
		});
	};

};

TaskController.$inject = [ '$scope', '$rootScope', '$timeout', '$filter',
		'$filter', 'taskService', 'contactService' ];