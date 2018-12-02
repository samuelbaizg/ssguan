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

var SettingsService = function(http, $q, $translate) {

	var factory = {};

	factory.loadGroups = function() {
		return http.post('d?ha=grouplist', {
			select : true
		}).then(function(data) {
			return data.groups;
		});
	};

	factory.fetchGroupVersions = function(groupKey) {
		return http.post('d?ha=groupversionlist', {
			groupKey : groupKey
		}).then(function(data) {
			return data;
		});
	};

	factory.saveGroupVersion = function(groupVersion) {
		return http.post('d?ha=savegroupversion', {
			key : groupVersion.key,
			versionName : groupVersion.versionName,
			verDescription : groupVersion.verDescription,
			groupKey : groupVersion.groupKey,
			verStartDate : groupVersion.verStartDate,
			verFinishDate : groupVersion.verFinishDate,
			isReleased : groupVersion.isReleased,
			releaseDate : groupVersion.releaseDate,
			rowVersion : groupVersion.rowVersion
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteGroupVersion = function(groupVersion) {
		return http.post('d?ha=deletegroupversion', {
			versionKey : groupVersion.key
		}).then(function(data) {
			return data;
		});
	};

	factory.fetchGroupComponents = function(groupKey) {
		return http.post('d?ha=groupcomponentlist', {
			groupKey : groupKey
		}).then(function(data) {
			return data;
		});
	};

	factory.saveGroupComponent = function(groupComponent) {
		return http.post('d?ha=savegroupcomponent', {
			key : groupComponent.key,
			groupKey : groupComponent.groupKey,
			componentName : groupComponent.componentName,
			compoDescription : groupComponent.compoDescription,
			rowVersion : groupComponent.rowVersion
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteGroupComponent = function(groupComponent) {
		return http.post('d?ha=deletegroupcomponent', {
			componentKey : groupComponent.key
		}).then(function(data) {
			return data;
		});
	};

	factory.fetchGroupExceptions = function(groupKey) {
		return http.post('d?ha=groupexceptionlist', {
			groupKey : groupKey
		}).then(function(data) {
			return data;
		});
	};

	factory.saveGroupException = function(groupExcpetion) {
		return http.post('d?ha=savegroupexception', {
			key : groupExcpetion.key,
			groupKey : groupExcpetion.groupKey,
			exceptionName : groupExcpetion.exceptionName,
			expStartDate : groupExcpetion.expStartDate,
			expFinishDate : groupExcpetion.expFinishDate,
			isWork : groupExcpetion.isWork,
			rowVersion : groupExcpetion.rowVersion
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteGroupException = function(groupExcpetion) {
		return http.post('d?ha=deletegroupexception', {
			exceptionKey : groupExcpetion.key
		}).then(function(data) {
			return data;
		});
	};

	factory.fetchGroupResources = function(groupKey) {
		return http.post('d?ha=groupresourcelist', {
			groupKey : groupKey
		}).then(function(data) {
			return data;
		});
	};

	factory.saveGroupResource = function(groupResource) {
		return http.post('d?ha=savegroupresource', {
			key : groupResource.key,
			groupKey : groupResource.groupKey,
			contactKey : groupResource.contactKey,
			joinDate : groupResource.joinDate,
			quitDate : groupResource.quitDate,
			isBillable : groupResource.isBillable,
			cgRemark : groupResource.cgRemark,
			contactLevel : groupResource.contactLevel,
			rowVersion : groupResource.rowVersion
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteGroupResource = function(groupResource) {
		return http.post('d?ha=deletegroupresource', {
			resourceKey : groupResource.key
		}).then(function(data) {
			return data;
		});
	};

	return factory;
};

SettingsService.$inject = [ 'dsHttp', '$q', '$translate' ];
