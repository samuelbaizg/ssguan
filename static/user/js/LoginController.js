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

var LoginController = function($scope, $rootScope, $location, $routeParams,
		userService, $timeout, $filter) {

	var path = '/';
	$scope.login = function() {
		userService.login(this.loginName, this.loginPassword).then(
				function(data) {
					$rootScope.loginUser = data;
					if (status && $routeParams && $routeParams.redirect) {
						path = path + $routeParams.redirect;
					}
					$location.path("/task");
				});
	};

	$scope.signupClick = function() {
		$("#signupDialog").modal('show');
	};

	$scope.signup = function() {

		if (!$('#agreeChk').is(":checked")) {
			var message = $filter('translate')('core_error_notagreeslaprivacy');
			infobox.alert(message);
		} else {
			userService.signup(this.accountName, this.password, this.userEmail,
					this.userName).then(function(data) {
				var message = $filter('translate')('core_label_signupsuccess');
				infobox.alert(message, function() {
					$("#signupDialog").modal('hide');
				});
			});
		}
	};
};

LoginController.$inject = [ '$scope', '$rootScope', '$location',
		'$routeParams', 'userService', '$timeout', '$filter' ];