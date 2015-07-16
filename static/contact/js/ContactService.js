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

var ContactService = function(http, $q, $translate) {

	var factory = {};

	factory.fetchGroupList = function() {
		return http.post('d?ha=grouplist', {}).then(function(data) {
			return data;
		});
	};

	factory.saveGroup = function(group) {
		return http.post('d?ha=savegroup', {
			key : group.key,
			groupName : group.groupName,
			isShared : group.isShared,
			rowVersion : group.rowVersion,
			groupStartdate : group.groupStartdate,
			groupFinishdate : group.groupFinishdate,
			workdayMonday : group.workdayMonday,
			workdayTuesday : group.workdayTuesday,
			workdayWednesday : group.workdayWednesday,
			workdayThursday : group.workdayThursday,
			workdayFriday : group.workdayFriday,
			workdaySaturday : group.workdaySaturday,
			workdaySunday : group.workdaySunday
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteGroup = function(group) {
		return http.post('d?ha=deletegroup', {
			groupKey : group.key
		}).then(function(data) {
			return data;
		});
	};

	factory.emptyContactTrash = function() {
		return http.post('d?ha=emptycontacttrash', {}).then(function(data) {
			return data;
		});
	};

	factory.fetchContactList = function(filters, page, limit) {
		var postData = {
			filters : angular.toJson(filters),
			offset : page == undefined ? 1 : page,
			limit : limit ? limit : 25
		};
		return http.post('d?ha=contactlist', postData).then(function(data) {
			return data;
		});
	};

	factory.saveContact = function(contact) {
		return http.post('d?ha=savecontact', {
			key : contact.key,
			contactName : contact.contactName,
			emailWork : contact.emailWork,
			emailHome : contact.emailHome,
			birthday : contact.birthday,
			lunarBirthday : contact.lunarBirthday,
			mobileBusiness : contact.mobileBusiness,
			mobilePrivate : contact.mobilePrivate,
			phoneOffice : contact.phoneOffice,
			phoneHome : contact.phoneHome,
			faxOffice : contact.faxOffice,
			faxHome : contact.faxHome,
			company : contact.company,
			companyAddress : contact.companyAddress,
			companyWebsite : contact.companyWebsite,
			department : contact.department,
			position : contact.position,
			imQQ : contact.imQQ,
			soWeixin : contact.soWeixin,
			imSkype : contact.imSkype,
			remark : contact.remark,
			bindUserAccount : contact.bindUserAccount,
			groupKeys : contact.groupKeys.join(","),
			rowVersion : contact.rowVersion
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteContact = function(contact) {
		return http.post('d?ha=deletecontact', {
			contactKey : contact.key
		}).then(function(data) {
			return data;
		});
	};

	factory.recoverContact = function(contact) {
		return http.post('d?ha=recovercontact', {
			contactKey : contact.key
		}).then(function(data) {
			return data;
		});
	};

	factory.saveContactLeave = function(contactLeave) {
		return http.post('d?ha=savecontactleave', {
			key : contactLeave.key,
			contactKey : contactLeave.contactKey,
			leaveStartdate : contactLeave.leaveStartdate,
			leaveFinishdate : contactLeave.leaveFinishdate,
			leaveDays : contactLeave.leaveDays,
			leaveTypeCode : contactLeave.leaveTypeCode,
			leaveComment : contactLeave.leaveComment,
			rowVersion : contactLeave.rowVersion
		}).then(function(data) {
			return data;
		});
	};

	factory.deleteContactLeave = function(contactLeave) {
		return http.post('d?ha=deletecontactleave', {
			leaveKey : contactLeave.key
		}).then(function(data) {
			return data;
		});
	};

	return factory;

};

ContactService.$inject = [ 'dsHttp', '$q', '$translate' ];
