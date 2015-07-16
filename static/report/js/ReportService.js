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

var ReportService = function(http, $q, $translate) {

	var factory = {};

	factory.getReportBaseData = function() {
		return http.post('d?ha=rptbasedata', {
			ws : true,
			gr : true,
			as : true
		}).then(function(data) {
			return data;
		});
	};

	factory.getRptProgressData = function(groupKey, startDate, endDate,
			worksheetKeys, assigneeKeys) {
		return http.post(
				'd?ha=rptprogressdata',
				{
					groupKey : groupKey,
					worksheetKeys : worksheetKeys == null ? "" : worksheetKeys
							.join(","),
					startDate : startDate,
					endDate : endDate,
					assigneeKeys : assigneeKeys == null ? "" : assigneeKeys
							.join(",")
				}).then(function(data) {
			return data;
		});
	};

	factory.getRptAllocationData = function(groupKey, startDate, endDate,
			worksheetKeys, assigneeKeys) {
		return http.post(
				'd?ha=rptallocationdata',
				{
					groupKey : groupKey,
					worksheetKeys : worksheetKeys == null ? "" : worksheetKeys
							.join(","),
					assigneeKeys : assigneeKeys == null ? "" : assigneeKeys
							.join(","),
					startDate : startDate,
					endDate : endDate
				}).then(function(data) {
			return data;
		});
	};
	return factory;

};

ReportService.$inject = [ 'dsHttp', '$q', '$translate' ];
