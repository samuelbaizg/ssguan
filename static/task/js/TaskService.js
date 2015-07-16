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

var TaskService = function(http, $q, $translate) {

	var factory = {};

	factory.fetchWorksheetList = function() {
		return http.post('d?ha=worksheetlist', {}).then(function(data) {
			return data;
		});
	};

	factory.saveWorksheet = function(worksheet) {
		return http.post('d?ha=saveworksheet', {
			key : worksheet.key,
			worksheetName : worksheet.worksheetName,
			groupKey : worksheet.groupKey,
			rowVersion : worksheet.rowVersion
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteWorksheet = function(worksheet) {
		return http.post('d?ha=deleteworksheet', {
			worksheetKey : worksheet.key
		}).then(function(data) {
			return data;
		});
	};

	factory.emptyTaskTrash = function() {
		return http.post('d?ha=emptytasktrash', {}).then(function(data) {
			return data;
		});
	};

	factory.fetchTaskList = function(filters, page) {
		var postData = {
			filters : angular.toJson(filters),
			offset : page == undefined ? 1 : page,
			limit : 25
		};
		return http.post('d?ha=tasklist', postData).then(function(data) {
			return data;
		});
	};

	factory.saveTask = function(task) {
		return http
				.post(
						'd?ha=savetask',
						{
							key : task.key,
							taskSubject : task.taskSubject,
							taskDescription : task.taskDescription,
							taskStatusCode : task.taskStatusCode,
							taskPriorityCode : task.taskPriorityCode,
							taskTypeCode : task.taskTypeCode,
							taskAssigneeKey : task.taskAssigneeKey,
							worksheetKey : task.worksheetKey,
							dueStartdate : task.dueStartdate,
							dueFinishdate : task.dueFinishdate,
							actualProgress : task.actualProgress,
							storyPoints : task.storyPoints,
							affectedVersionKeys : task.affectedVersionKeys != null ? task.affectedVersionKeys
									.join(",")
									: "",
							fixedVersionKeys : task.fixedVersionKeys != null ? task.fixedVersionKeys
									.join(",")
									: "",
							componentKeys : task.componentKeys != null ? task.componentKeys
									.join(",")
									: "",
							rowVersion : task.rowVersion
						}).then(function(data) {
					return data;
				});
	};

	factory.deleteTask = function(task) {
		return http.post('d?ha=deletetask', {
			taskKey : task.key
		}).then(function(data) {
			return data;
		});
	};

	factory.recoverTask = function(task, worksheetKey) {
		return http.post('d?ha=recovertask', {
			taskKey : task.key,
			worksheetKey : worksheetKey
		}).then(function(data) {
			return data;
		});
	};

	factory.saveTaskComment = function(taskComment) {
		return http.post('d?ha=savetaskcomment', {
			key : taskComment.key,
			tcContent : taskComment.tcContent,
			taskKey : taskComment.taskKey,
			rowVersion : taskComment.rowVersion
		}).then(function(data) {
			return data;
		});
	};
	
	factory.deleteTaskComment = function(taskComment) {
		return http.post('d?ha=deletetaskcomment', {
			commentKey : taskComment.key
		}).then(function(data) {
			return data;
		});
	};

	return factory;

};

TaskService.$inject = [ 'dsHttp', '$q', '$translate' ];
