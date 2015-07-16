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

var SettingsController = function($scope, $rootScope, $location, $filter,
		userService, settingsService, contactService) {
	var path = '/';

	$scope.activeGroup = null;

	var versionPendingSave = false;
	var componentPendingSave = false;
	var exceptionPendingSave = false;
	var resourcePendingSave = false;

	$scope.workdayOptions = [ {
		id : 0,
		name : $filter('translate')('cont_status_nowork')
	}, {
		id : 0.5,
		name : $filter('translate')('cont_status_workhalfday')
	}, {
		id : 1,
		name : $filter('translate')('cont_status_workallday')
	} ];

	$scope.contactLevelOptions = [];
	for (var i = 1; i <= 10; i++) {
		$scope.contactLevelOptions.push({
			id : i,
			name : i
		});
	}

	function initSettingsModule() {
		settingsService.loadGroups().then(function(data) {
			$scope.groups = data;
		});
	}

	initSettingsModule();

	$scope.$on('EVENT_CLOSE_WSRIGHTCOL',
			function() {
				if (versionPendingSave == true) {
					var message = $filter('translate')(
							'cont_error_pendingsaveversion');
					infobox.alert(message);
				} else if (componentPendingSave == true) {
					var message = $filter('translate')(
							'cont_error_pendingsavecomponent');
					infobox.alert(message);
				} else if (exceptionPendingSave == true) {
					var message = $filter('translate')(
							'cont_error_pendingsaveexception');
					infobox.alert(message);
				} else if (resourcePendingSave == true) {
					var message = $filter('translate')(
							'cont_error_pendingsaveresource');
					infobox.alert(message);
				} else {
					$rootScope.showWsRightCol(true);
				}
			});

	$scope.isActive = function(viewLocation) {
		return viewLocation === $location.path();
	};

	$scope.logout = function() {
		userService.logout().then(function(data) {
			$rootScope.$broadcast(userService.EVENT_LOGIN_REDIRECT, data);
		});
	};

	$scope.changePasswordClick = function() {
		$scope.password = {
			oldPassword : "",
			newPassword : "",
			dupPassword : ""
		};
		$rootScope.showSidebar(true);
		$scope.activeAction = {
			key : "changepassword",
			label : $filter('translate')('core_action_changepwd')
		};
	};

	$scope.groupChange = function() {
		$scope.activeGroup = null;
		for (var i = 0; i < $scope.groups.length; i++) {
			var group = $scope.groups[i];
			if (group.key == this.groupKey) {
				$scope.activeGroup = {};
				angular.copy(group, $scope.activeGroup);
				$scope.activeGroup.original = group;
				break;
			}
		}
	};

	$scope.groupCalendarClick = function() {
		if ($scope.activeGroup == null) {
			infobox.alert($filter("translate")("cont_error_choosegroup"));
		} else {
			$rootScope.showSidebar(true);
			$rootScope.showWsRightCol(true);
			$scope.activeAction = {
				key : "setcalendar",
				label : $filter("translate")("core_label_set")
						+ $filter('translate')('cont_label_groupcalendar')
			};
			$scope.fetchExceptions();
		}
	}

	$scope.groupVersionClick = function() {
		if ($scope.activeGroup == null) {
			infobox.alert($filter("translate")("cont_error_choosegroup"));
		} else {
			$rootScope.showSidebar(true);
			$rootScope.showWsRightCol(true);
			$scope.activeAction = {
				key : "setversion",
				label : $filter("translate")("core_label_set")
						+ $filter("translate")("cont_label_groupversion")
			};
			$scope.fetchVersions();
		}
	}

	$scope.groupComponentClick = function() {
		if ($scope.activeGroup == null) {
			infobox.alert($filter("translate")("cont_error_choosegroup"));
		} else {
			$rootScope.showSidebar(true);
			$rootScope.showWsRightCol(true);
			$scope.activeAction = {
				key : "setcomponent",
				label : $filter("translate")("core_label_set")
						+ $filter("translate")("cont_label_groupcomponent")
			};
			$scope.fetchComponents();
		}
	}

	$scope.groupResourceClick = function() {
		if ($scope.activeGroup == null) {
			infobox.alert($filter("translate")("cont_error_choosegroup"));
		} else {
			$rootScope.showSidebar(true);
			$rootScope.showWsRightCol(true);
			$scope.activeAction = {
				key : "setresource",
				label : $filter("translate")("core_label_set")
						+ $filter("translate")("cont_label_groupresource")
			};
			$scope.fetchResources();
		}
	}

	$scope.changePassword = function() {
		userService.changePassword($scope.password.oldPassword,
				$scope.password.newPassword, $scope.password.dupPassword).then(
				function(data) {
					var message = $filter('translate')(
							'core_status_savesuccess');
					infobox.alert(message);
				});
	};
	// ///////////////////////////////Version//////////////////////////////
	$scope.newVersion = function() {
		var version = {
			key : "",
			isReleased : false,
			groupKey : $scope.activeGroup.key
		};
		$scope.updateVersion(version, true);
	};

	$scope.editVersion = function(editable) {
		if (editable) {
			$scope.versionEditable = true;
		} else {
			$scope.versionEditable = false;
		}
	};

	$scope.updateVersion = function(version, editable) {
		if (versionPendingSave == true) {
			var message = $filter('translate')('cont_error_pendingsaveversion');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(false);
			$("#versionSaveStatusDiv").html("");
			$scope.activeVersion = {};
			angular.copy(version, $scope.activeVersion);
			$scope.activeVersion.original = version;
			if (editable == true) {
				$('#versionNameTxt').focus();
				$scope.versionEditable = true;
			} else {
				$scope.versionEditable = false;
			}
		}
	};

	$scope.saveVersion = function(auto) {
		versionPendingSave = true;
		var oldVersionKey = $scope.activeVersion.key;
		function _addVersion(version) {
			$scope.groupVersions.unshift(version);
			$scope.activeVersion.original = version;
			$scope.activeVersion.key = version.key;
			$scope.activeVersion.creatorKey = version.creatorKey;
		}
		return settingsService.saveGroupVersion($scope.activeVersion).then(
				function(version) {
					angular.copy(version, $scope.activeVersion.original);
					$scope.activeVersion.rowVersion = version.rowVersion;
					if (oldVersionKey == null || oldVersionKey == '') {
						_addVersion(version);
					}
					versionPendingSave = false;
					if (!auto) {
						$scope.versionEditable = false;
					}
					return version;
				}, function(data) {
					versionPendingSave = false;
				});
	};

	$scope.autoSaveVersion = function($event) {
		if ($scope.versionEditable) {
			versionPendingSave = true;
		}
	};

	$scope.cancelSaveVersion = function() {
		var bak = $scope.activeVersion.original;
		angular.copy($scope.activeVersion.original, $scope.activeVersion);
		$scope.activeVersion.original = bak;
		versionPendingSave = false;
		$scope.versionEditable = false;
	};

	$scope.deleteVersion = function() {
		function _deleteVersion(result) {
			if (result == true) {
				settingsService.deleteGroupVersion($scope.activeVersion).then(
						function(data) {
							$scope.activeVersion = {};
							$scope.fetchVersions().then(function(data) {
								$rootScope.showWsRightCol(true);
							});
						});
			}
		}
		var message = $filter('translate')('cont_confirm_version_delete');
		infobox.confirm(message, function(result) {
			_deleteVersion(result);
		});
	};

	$scope.fetchVersions = function() {
		return settingsService.fetchGroupVersions($scope.activeGroup.key).then(
				function(data) {
					$scope.groupVersions = data;
				});
	}

	// ////////////////////////Component////////////////////////////

	$scope.newComponent = function() {
		var component = {
			key : "",
			groupKey : $scope.activeGroup.key
		};
		$scope.updateComponent(component, true);
	};

	$scope.editComponent = function(editable) {
		if (editable) {
			$scope.componentEditable = true;
		} else {
			$scope.componentEditable = false;
		}
	};

	$scope.updateComponent = function(component, editable) {
		if (componentPendingSave == true) {
			var message = $filter('translate')(
					'cont_error_pendingsavecomponent');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(false);
			$("#componentSaveStatusDiv").html("");
			$scope.activeComponent = {};
			angular.copy(component, $scope.activeComponent);
			$scope.activeComponent.original = component;
			if (editable == true) {
				$('#componentNameTxt').focus();
				$scope.componentEditable = true;
			} else {
				$scope.componentEditable = false;
			}
		}
	};

	$scope.saveComponent = function(auto) {
		componentPendingSave = true;
		var oldComponentKey = $scope.activeComponent.key;
		function _addComponent(component) {
			$scope.groupComponents.unshift(component);
			$scope.activeComponent.original = component;
			$scope.activeComponent.key = component.key;
			$scope.activeComponent.creatorKey = component.creatorKey;
		}
		return settingsService.saveGroupComponent($scope.activeComponent).then(
				function(component) {
					angular.copy(component, $scope.activeComponent.original);
					$scope.activeComponent.rowVersion = component.rowVersion;
					if (oldComponentKey == null || oldComponentKey == '') {
						_addComponent(component);
					}
					componentPendingSave = false;
					if (!auto) {
						$scope.componentEditable = false;
					}
					return component;
				}, function(data) {
					componentPendingSave = false;
				});
	};

	$scope.autoSaveComponent = function($event) {
		if ($scope.componentEditable) {
			componentPendingSave = true;
		}
	};

	$scope.cancelSaveComponent = function() {
		var bak = $scope.activeComponent.original;
		angular.copy($scope.activeComponent.original, $scope.activeComponent);
		$scope.activeComponent.original = bak;
		componentPendingSave = false;
		$scope.componentEditable = false;
	};

	$scope.deleteComponent = function() {
		function _deleteComponent(result) {
			if (result == true) {
				settingsService.deleteGroupComponent($scope.activeComponent)
						.then(function(data) {
							$scope.activeComponent = {};
							$scope.fetchComponents().then(function(data) {
								$rootScope.showWsRightCol(true);
							});
						});
			}
		}
		var message = $filter('translate')('cont_confirm_component_delete');
		infobox.confirm(message, function(result) {
			_deleteComponent(result);
		});
	};

	$scope.fetchComponents = function() {
		return settingsService.fetchGroupComponents($scope.activeGroup.key)
				.then(function(data) {
					$scope.groupComponents = data;
				});
	}
	// ///////////////////////////////Exception//////////////////////////////
	$scope.newException = function() {
		var exception = {
			key : "",
			groupKey : $scope.activeGroup.key,
			isWork : false
		};
		$scope.updateException(exception, true);
	};

	$scope.editException = function(editable) {
		if (editable) {
			$scope.exceptionEditable = true;
		} else {
			$scope.exceptionEditable = false;
		}
	};

	$scope.updateException = function(exception, editable) {
		if (exceptionPendingSave == true) {
			var message = $filter('translate')(
					'cont_error_pendingsaveexception');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(false);
			$("#exceptionSaveStatusDiv").html("");
			$scope.activeException = {};
			angular.copy(exception, $scope.activeException);
			$scope.activeException.original = exception;
			if (editable == true) {
				$('#exceptionNameTxt').focus();
				$scope.exceptionEditable = true;
			} else {
				$scope.exceptionEditable = false;
			}
		}
	};

	$scope.saveException = function(auto) {
		exceptionPendingSave = true;
		var oldExceptionKey = $scope.activeException.key;
		function _addException(exception) {
			$scope.groupExceptions.unshift(exception);
			$scope.activeException.original = exception;
			$scope.activeException.key = exception.key;
			$scope.activeException.creatorKey = exception.creatorKey;
		}
		return settingsService.saveGroupException($scope.activeException).then(
				function(exception) {
					angular.copy(exception, $scope.activeException.original);
					$scope.activeException.rowVersion = exception.rowVersion;
					if (oldExceptionKey == null || oldExceptionKey == '') {
						_addException(exception);
					}
					exceptionPendingSave = false;
					if (!auto) {
						$scope.exceptionEditable = false;
					}
					return exception;
				}, function(data) {
					exceptionPendingSave = false;
				});
	};

	$scope.autoSaveException = function($event) {
		if ($scope.exceptionEditable) {
			exceptionPendingSave = true;
		}
	};

	$scope.cancelSaveException = function() {
		var bak = $scope.activeException.original;
		angular.copy($scope.activeException.original, $scope.activeException);
		$scope.activeException.original = bak;
		exceptionPendingSave = false;
		$scope.exceptionEditable = false;
	};

	$scope.deleteException = function() {
		function _deleteException(result) {
			if (result == true) {
				settingsService.deleteGroupException($scope.activeException)
						.then(function(data) {
							$scope.activeException = {};
							$scope.fetchExceptions().then(function(data) {
								$rootScope.showWsRightCol(true);
							});
						});
			}
		}
		var message = $filter('translate')('cont_confirm_exception_delete');
		infobox.confirm(message, function(result) {
			_deleteException(result);
		});
	};

	$scope.fetchExceptions = function() {
		return settingsService.fetchGroupExceptions($scope.activeGroup.key)
				.then(function(data) {
					$scope.groupExceptions = data;
				});
	}

	$scope.saveWorkday = function() {
		contactService.saveGroup($scope.activeGroup).then(function(data) {
			angular.copy(data, $scope.activeGroup.original);
			$scope.activeGroup.rowVersion = data.rowVersion;
			infobox.alert($filter("translate")("core_status_savesuccess"));
		});
	}

	$scope.savePeroid = function() {
		contactService.saveGroup($scope.activeGroup).then(function(data) {
			angular.copy(data, $scope.activeGroup.original);
			$scope.activeGroup.rowVersion = data.rowVersion;
			infobox.alert($filter("translate")("core_status_savesuccess"));
		});
	}

	// ///////////////////////////////Resource//////////////////////////////
	$scope.newResource = function() {
		var resource = {
			key : "",
			groupKey : $scope.activeGroup.key,
			isBillable : true,
			contactLevel : 1
		};
		$scope.updateResource(resource, true);
	};

	$scope.editResource = function(editable) {
		if (editable) {
			$scope.resourceEditable = true;
		} else {
			$scope.resourceEditable = false;
		}
	};

	$scope.updateResource = function(resource, editable) {
		if (resourcePendingSave == true) {
			var message = $filter('translate')
					('cont_error_pendingsaveresource');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(false);
			$("#resourceSaveStatusDiv").html("");
			$scope.activeResource = {};
			angular.copy(resource, $scope.activeResource);
			$scope.activeResource.original = resource;
			if (editable == true) {
				$('#resourceNameTxt').focus();
				$scope.resourceEditable = true;
			} else {
				$scope.resourceEditable = false;
			}
		}
	};

	$scope.saveResource = function(auto) {
		resourcePendingSave = true;
		var oldResourceKey = $scope.activeResource.key;
		function _addResource(resource) {
			$scope.groupResources.unshift(resource);
			$scope.activeResource.original = resource;
			$scope.activeResource.key = resource.key;
			$scope.activeResource.creatorKey = resource.creatorKey;
		}
		return settingsService.saveGroupResource($scope.activeResource).then(
				function(resource) {
					angular.copy(resource, $scope.activeResource.original);
					$scope.activeResource.rowVersion = resource.rowVersion;
					if (oldResourceKey == null || oldResourceKey == '') {
						_addResource(resource);
					}
					resourcePendingSave = false;
					if (!auto) {
						$scope.resourceEditable = false;
					}
					return resource;
				}, function(data) {
					resourcePendingSave = false;
				});
	};

	$scope.autoSaveResource = function($event) {
		if ($scope.resourceEditable) {
			resourcePendingSave = true;
		}
	};

	$scope.cancelSaveResource = function() {
		var bak = $scope.activeResource.original;
		angular.copy($scope.activeResource.original, $scope.activeResource);
		$scope.activeResource.original = bak;
		resourcePendingSave = false;
		$scope.resourceEditable = false;
	};

	$scope.deleteResource = function() {
		function _deleteResource(result) {
			if (result == true) {
				settingsService.deleteGroupResource($scope.activeResource)
						.then(function(data) {
							$scope.activeResource = {};
							$scope.fetchResources().then(function(data) {
								$rootScope.showWsRightCol(true);
							});
						});
			}
		}
		var message = $filter('translate')('cont_confirm_resource_delete');
		infobox.confirm(message, function(result) {
			_deleteResource(result);
		});
	};

	$scope.fetchResources = function() {
		return settingsService.fetchGroupResources($scope.activeGroup.key)
				.then(function(data) {
					$scope.groupResources = data.groupResources;
					$scope.contacts = data.contacts;
				});
	}

};

SettingsController.$inject = [ '$scope', '$rootScope', '$location', '$filter',
		'userService', 'settingsService', 'contactService' ];