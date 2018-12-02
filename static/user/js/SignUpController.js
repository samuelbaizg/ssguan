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
		userService) {
	var path = '/';
	
	$scope.login = function() {
		userService.login($scope.loginName, $scope.loginPassword).then(
				function(data) {
					$rootScope.username = data.username;
					if (status && $routeParams && $routeParams.redirect) {
						path = path + $routeParams.redirect;
					}
					$location.path(path);
				});
	};
};

LoginController.$inject = [ '$scope', '$rootScope', '$location',
		'$routeParams', 'userService' ];