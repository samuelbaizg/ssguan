'use strict';
// Copyright 2015 www.suishouguan.com
//
// Licensed under the Private License (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// https://github.com/samuelbaizg/ssguan/blob/master/LICENSE
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

var UserService = function(http, $q, $translate, $filter, $rootScope) {

	var factory = {

		EVENT_LOGIN_REDIRECT : "EVENT_LOGIN_REDIRECT",

		token : {

			anonymous : true,
			userKey : null,
			userName : null,
			accountName : null,
			preferredLanguage : null,
			dateFormat : null,
			dateMinuteFormat : null,
			dateSecondFormat : null,
			operations : null,
			taskStatusOptions : null,
			taskPriorityOptions : null
		},

		resetToken : function() {
			this.token.anonymous = true;
			this.token.userKey = null;
			this.token.userName = null;
			this.token.accountName = null;
			this.token.preferredLanguage = null;
			this.token.operations = null;
			this.token.dateFormat = null;
			this.token.dateMinuteFormat = null;
			this.token.dateSecondFormat = null;
			this.token.taskStatusOptions = null;
			this.token.taskPriorityOptions = null;
		}
	};

	factory.login = function(loginName, loginPwd) {
		var rsa = new RSAKey();
		rsa.setPublic($rootScope.loginUser.lopuKey.n,
				$rootScope.loginUser.lopuKey.e);
		var res = rsa.encrypt(loginPwd);
		loginPwd = res;
		res = rsa.encrypt(loginName);
		loginName = res;
		function login_callback(data) {
			angular.copy(data, factory.token);
			$translate.use(factory.token.preferredLanguage);
			infobox.setDefaults({
				'locale' : factory.token.preferredLanguage
			});
			return factory.token;
		}
		return http.post('d?ha=login', {
			loginName : loginName,
			loginPwd : loginPwd
		}).then(function(data) {
			return login_callback(data);
		});
	};

	factory.isOnline = function() {
		return factory.token.anonymous == false;
	};

	factory.logout = function() {
		return http.post('d?ha=logout', {}).then(function(data) {
			factory.resetToken();
			angular.copy(data, factory.token);
			return factory.token;
		});
	};

	factory.changePassword = function(oldPwd, newPwd, dupPwd) {
		return http.post('d?ha=changepwd', {
			oldPassword : oldPwd,
			newPassword : newPwd,
			dupPassword : dupPwd
		}).then(function(data) {
			return true;
		});
	};

	factory.signup = function(accountName, password, userEmail, userName) {
		return http.post('d?ha=signup', {
			accountName : accountName,
			password : password,
			userEmail : userEmail,
			userName : userName
		}).then(function(data) {
			return true;
		});
	};

	return factory;
};

UserService.$inject = [ 'dsHttp', '$q', '$translate', '$filter', '$rootScope' ];
