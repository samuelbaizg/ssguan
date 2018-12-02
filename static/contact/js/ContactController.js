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

var ContactController = function($scope, $rootScope, $timeout, $filter,
		contactService) {

	$scope.TRASH_GROUP_ID = -100;
	$scope.DEFAULT_GROUP_ID = EMPTY_UID;
	$scope.groupEditable = false;
	$scope.groups = null;
	$scope.activeGroup = null;
	$scope.contactEditable = false;
	$scope.contactPager = null;
	$scope.activeContact = null;

	var contactPendingSave = false;

	$scope.$on('EVENT_SHORTCUT_GROUP', function() {
		$rootScope.showSidebar(false);
	});

	$scope.$on('EVENT_CLOSE_WSRIGHTCOL', function() {
		if (contactPendingSave == true) {
			var message = $filter('translate')('cont_error_pendingsave');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(true);
		}
	});

	function loadContactModule() {
		$scope.fetchGroups();
	}

	function updateContactCount(groupKeys, count) {

		function _updateContactCount(groupKey, count) {
			for (var i = 0; i < $scope.groups.length; i++) {
				var group = $scope.groups[i];
				if (group.key == groupKey) {
					group.contactcount += count;
					break;
				}
			}
		}
		if (groupKeys.length == 0) {
			_updateContactCount($scope.DEFAULT_GROUP_ID, count);
		} else {
			for (var i = 0; i < groupKeys.length; i++) {
				_updateContactCount(groupKeys[i], count);
			}
		}
	}

	function getContactFilterMap() {
		var contactKeywordsMap = {};
		if ($scope.groups != null) {
			$.each($scope.groups, function(i, group) {
				contactKeywordsMap["gp=" + group.groupName] = {
					gp : group.key
				};
			});
		}
		return contactKeywordsMap;
	}

	$scope.editGroup = function(editable) {
		if (editable) {
			$scope.groupEditable = true;
		} else {
			$scope.groupEditable = false;
		}
	}

	$scope.updateGroup = function(group) {
		if (group != null) {
			$scope.updatedGroup = {};
			angular.copy(group, $scope.updatedGroup);
		} else {
			$scope.updatedGroup = {
				groupName : "",
				isShared : false
			};
		}
		$("#groupDialog").modal('show');
	};

	$scope.saveGroup = function() {
		contactService.saveGroup($scope.updatedGroup).then(function(data) {
			$("#groupDialog").modal('hide');
			$("#groupDialog").on('hidden.bs.modal', function() {
				$scope.fetchGroups();
			});
		});
	};

	$scope.deleteGroup = function(group) {
		var message = $filter('translate')('cont_confirm_deletegroup');
		infobox.confirm(message, function(result) {
			if (result == true) {
				contactService.deleteGroup(group).then(function(data) {
					$scope.fetchGroups();
				});
			}
		});
	};

	$scope.emptyContactTrash = function(group) {
		var message = $filter('translate')('cont_confirm_emptytrash');
		infobox.confirm(message, function(result) {
			if (result == true) {
				contactService.emptyContactTrash().then(function(data) {
					$scope.fetchGroups();
				});
			}
		});
	};

	$scope.viewGroup = function(group) {
		if ($scope.groupEditable == false) {
			$rootScope.showSidebar(true);
			$rootScope.showWsRightCol(true);
			$scope.activeContact = null;
			$scope.activeGroup = group;
			$scope.contactSearchLabel = group.groupName;
			$scope.contactSearchKeywords = [ "gp=" + group.groupName ];
			$scope.fetchContacts();
		}
	};

	$scope.groupClick = function(group, $event) {
		if (contactPendingSave == true) {
			var message = $filter('translate')('cont_error_pendingsave');
			infobox.alert(message);
		} else {
			var srcElmt = $($event.target);
			if (srcElmt.hasClass("fa-remove")) {
				if (group.key == $scope.TRASH_GROUP_ID) {
					$scope.emptyGroupTrash(group);
				} else {
					$scope.deleteGroup(group);
				}
			} else if (srcElmt.hasClass("fa-edit")) {
				$scope.updateGroup(group);
			} else {
				$scope.viewGroup(group);
			}
		}
	};

	$scope.fetchGroups = function() {
		return contactService.fetchGroupList().then(function(data) {
			$scope.groups = data.groups;
			if (!$scope.groupEditable) {
				$scope.activeGroup = $scope.groups[0];
				$scope.viewGroup(data.groups[0]);
			}
			return data;
		});
	};

	$scope.getContactSearchKeywordHints = function() {
		var contactSearchKeywordHints = [];
		var map = getContactFilterMap();

		$.each(map, function(name, value) {
			contactSearchKeywordHints.push(name);
		});
		return contactSearchKeywordHints;
	};

	$scope.newContact = function() {
		var contact = {
			key : null,
			groupKeys : []
		};
		$scope.updateContact(contact, true);
	};

	$scope.editContact = function(editable) {
		if (editable) {
			$scope.contactEditable = true;
		} else {
			$scope.contactEditable = false;
		}
	};

	$scope.updateContact = function(contact, editable) {
		if (contactPendingSave == true) {
			var message = $filter('translate')('cont_error_pendingsave');
			infobox.alert(message);
		} else {
			$rootScope.showWsRightCol(false);
			$("#contactSaveStatusDiv").html("");
			$scope.activeContact = {};
			angular.copy(contact, $scope.activeContact);
			$scope.activeContact.original = contact;
			if (editable == true) {
				$('#contactNameTxt').focus();
				$scope.contactEditable = true;
			} else {
				$scope.contactEditable = false;
			}
		}
	};

	$scope.autoSaveContact = function($event) {
		if ($scope.contactEditable) {
			contactPendingSave = true;
		}
	};

	$scope.cancelSaveContact = function() {
		var bak = $scope.activeContact.original;
		angular.copy($scope.activeContact.original, $scope.activeContact);
		$scope.activeContact.original = bak;
		contactPendingSave = false;
		$scope.contactEditable = false;
	};

	$scope.saveContact = function(auto) {
		contactPendingSave = true;
		var oldcontactKey = $scope.activeContact.key;
		var oldContactgroupKeys = $scope.activeContact.groupKeys;
		$scope.activeContact.groupKeys = $(
				".contactedit input:checkbox:checked").map(function() {
			return $(this).val();
		}).get();

		function _addContact(contact) {
			$scope.contactPager.records.unshift(contact);
			$scope.contactPager.count += 1;
			if ($scope.contactPager.count == 1) {
				$scope.contactPager.page = 1;
				$scope.contactPager.pageNumbers = [ 1 ];
				$scope.contactPager.total = 1;
			}
			updateContactCount($scope.activeContact.groupKeys, 1);
			$scope.activeContact.original = contact;
			$scope.activeContact.key = contact.key;
			$scope.activeContact.creatorKey = contact.creatorKey;
		}
		return contactService.saveContact($scope.activeContact).then(
				function(contact) {
					angular.copy(contact, $scope.activeContact.original);
					$scope.activeContact.groupKeys = contact.groupKeys;
					$scope.activeContact.rowVersion = contact.rowVersion;
					if (oldcontactKey == null || oldcontactKey == '') {
						_addContact(contact);
					} else {
						updateContactCount(oldContactgroupKeys, -1);
						updateContactCount($scope.activeContact.groupKeys, 1);
					}
					contactPendingSave = false;
					if (!auto) {
						$scope.contactEditable = false;
					}
					return contact;
				}, function(data) {
					contactPendingSave = false;
				});
	};

	$scope.deleteContact = function() {
		function _deleteContact(result) {
			if (result == true) {
				contactService.deleteContact($scope.activeContact).then(
						function(data) {
							updateContactCount($scope.activeContact.groupKeys,
									-1);
							updateContactCount([ $scope.TRASH_GROUP_ID ], 1);
							$scope.activeContact = {};
							$scope.fetchContacts().then(function(data) {
								$rootScope.showWsRightCol(true);
							});
						});
			}
		}
		var message = $filter('translate')('cont_confirm_deletecontact');
		infobox.confirm(message, function(result) {
			_deleteContact(result);
		});
	};

	$scope.permanentDeleteContact = function() {
		function _permanentDeleteContact(result) {
			if (result == true) {
				contactService.deleteContact($scope.activeContact).then(
						function(data) {
							updateContactCount([ $scope.TRASH_GROUP_ID ], -1);
							$scope.activeContact = {};
							$scope.fetchContacts().then(function(data) {
								$rootScope.showWsRightCol(true);
							});
						});
			}
		}
		var message = $filter('translate')('cont_confirm_permanentdelete');
		infobox.confirm(message, function(result) {
			_permanentDeleteContact(result);
		});
	};

	$scope.recoverContact = function() {
		function _recoverContact(result) {
			if (result == true) {
				contactService.recoverContact($scope.activeContact).then(
						function(data) {
							updateContactCount($scope.activeContact.groupKeys,
									1);
							updateContactCount([ $scope.TRASH_GROUP_ID ], -1);
							$scope.fetchContacts();
						});
			}
		}

		var message = $filter('translate')('cont_confirm_recovercontact');
		infobox.confirm(message, function(result) {
			_recoverContact(result);
		});

	};

	$scope.searchContact = function() {
		$("#contactSearchDialog").modal('show');
	};

	$scope.submitContactSearch = function() {
		$("#contactSearchDialog").modal('hide');
		$scope.contactSearchLabel = $filter('translate')(
				'core_label_searchresult');
		$scope.fetchContacts();
	};

	$scope.fetchContacts = function(page, addMore) {

		function _getFilters() {
			var keywordsArr = $scope.contactSearchKeywords;
			var contactKeywordsMap = getContactFilterMap();
			var arr = [];
			for ( var i in keywordsArr) {
				var kw = contactKeywordsMap[keywordsArr[i]];
				arr.push(kw ? kw : {
					kw : keywordsArr[i]
				});
			}
			return arr;
		}

		page = page == undefined ? 1 : page;
		addMore = addMore == undefined ? false : addMore;
		if (addMore == false || $scope.contactPager.total >= page) {
			return contactService.fetchContactList(_getFilters(), page).then(
					function(data) {
						if (addMore == true) {
							var records = $scope.contactPager.records
									.concat(data.records);
							$scope.contactPager = data;
							$scope.contactPager.records = records;
						} else {
							$scope.contactPager = data;
						}
						$scope.activeContact = null;
						$rootScope.showWsRightCol(true);
						return data;
					});
		}
	};

	loadContactModule();

	// ///////////////////////Contact Leave ///////////////////

	$scope.newContactLeave = function() {
		var contactLeave = {
			key : "",
			contactKey : $scope.activeContact.key,
			leaveTypeCode : "cont_code_annualleave",
			contactLeaves : []

		};
		$scope.updateContactLeave(contactLeave, true);
	};

	var contactLeavePendingSave = false;

	$scope.updateContactLeave = function(contactLeave, editable) {
		$scope.activeContactLeave = {};
		angular.copy(contactLeave, $scope.activeContactLeave);
		$scope.activeContactLeave.original = contactLeave;

		$("#contactLeaveEditDialog").modal('show');
		$('#contactLeaveEditDialog').on('shown.bs.modal', function() {
			$("#contactLeaveSaveStatusDiv").html("");
		});
		$('#contactLeaveEditDialog').on('hide.bs.modal', function() {
			contactLeavePendingSave = false;
		});
	}

	$scope.saveContactLeave = function() {
		contactLeavePendingSave = true;
		var oldContactLeaveKey = $scope.activeContactLeave.key;
		function _addContactLeave(contactLeave) {
			$scope.activeContact.contactLeaves.unshift(contactLeave);
			$scope.activeContact.original.contactLeaves.unshift(contactLeave);
			$scope.activeContactLeave.original = contactLeave;
			$scope.activeContactLeave.key = contactLeave.key;
			$scope.activeContactLeave.creatorKey = contactLeave.creatorKey;
		}
		return contactService
				.saveContactLeave($scope.activeContactLeave)
				.then(
						function(contactLeave) {
							angular.copy(contactLeave,
									$scope.activeContactLeave.original);
							$scope.activeContactLeave.rowVersion = contactLeave.rowVersion;
							if (oldContactLeaveKey == null
									|| oldContactLeaveKey == '') {
								_addContactLeave(contactLeave);
							}
							$scope.activeContactLeave = contactLeave;
							contactLeavePendingSave = false;
							$("#contactLeaveEditDialog").modal('hide');
							return contactLeave;
						}, function(data) {
							contactLeavePendingSave = false;
						});
	};

	$scope.deleteContactLeave = function(contactLeave) {
		function _deleteContactLeave(result) {
			contactService.deleteContactLeave(contactLeave).then(
					function(data) {
						$.each($scope.activeContact.contactLeaves,
								function(i, cl) {
									if (contactLeave.key == cl.key) {
										$scope.activeContact.contactLeaves
												.splice(i, 1);
										return false;
									}
								});
					});
		}
		var message = $filter('translate')('cont_confirm_contactleave_delete');
		infobox.confirm(message, function(result) {
			if (result == true) {
				_deleteContactLeave();
			}
		});
	};
};

ContactController.$inject = [ '$scope', '$rootScope', '$timeout', '$filter',
		'contactService' ];