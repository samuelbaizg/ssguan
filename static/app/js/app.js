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

(function() {

	var MODULENAMEs = [];
	var ROUTEs = [];

	for ( var moduleName in conf.MODULEs) {
		registerModule(moduleName, conf.MODULEs[moduleName]);
	}

	function registerModule(moduleName, module) {
		if (module.sysMod == true) {
			MODULENAMEs.push(moduleName);
			return;
		}
		module.services = module.services || {};
		module.controlers = module.controllers || {};
		module.directives = module.directives || {};
		module.filters = module.filters || {};
		module.dependencies = module.dependencies || [];

		var modInstance = angular.module(moduleName, module.dependencies);

		for ( var serviceName in module.services) {
			modInstance.factory(serviceName, module.services[serviceName]);
		}
		for ( var directiveName in module.directives) {
			modInstance
					.directive(directiveName, module.services[directiveName]);
		}
		for ( var filterName in module.filters) {
			modInstance.filter(filterName, module.filters[filterName]);
		}
		for ( var controllerName in module.controllers) {
			var controller = module.controllers[controllerName];
			modInstance.controller(controllerName, controller[0]);
			if (controller.length > 1) {
				var tmpl = conf.TEMPLATEs[controller[1]];
				ROUTEs.push([ controller[0], controller[1],
						conf.TEMPLATEs.main + "?" + G_VERSION ]);
			}
		}
		MODULENAMEs.push(moduleName);

	}

	var browserApp = angular.module('browserApp', MODULENAMEs);

	for ( var constantName in conf.CONSTANTs) {
		browserApp.constant(constantName, conf.CONSTANTs[constantName]);
	}

	for ( var serviceName in conf.SERVICEs) {
		browserApp.factory(serviceName, conf.SERVICEs[serviceName]);
	}

	for ( var directiveName in conf.DIRECTIVEs) {
		browserApp.directive(directiveName, conf.DIRECTIVEs[directiveName]);
	}

	for ( var filterName in conf.FILTERs) {
		browserApp.filter(filterName, conf.FILTERs[filterName]);
	}

	browserApp.config([
			'$routeProvider',
			'$locationProvider',
			'$translateProvider',
			'I18N',
			function($routeProvider, $locationProvider, $translateProvider,
					I18N) {
				for (var i = 0; i < ROUTEs.length; i++) {
					var route = ROUTEs[i];
					$routeProvider.when(route[1], {
						controller : route[0],
						templateUrl : route[2]
					});
				}
				$routeProvider.otherwise({
					redirectTo : '/login'
				});
				for ( var locale in I18N.translations) {
					$translateProvider.translations(locale,
							I18N.translations[locale]);
				}
				$translateProvider.preferredLanguage(I18N.defaultLanguage);
				infobox.setDefaults("locale", I18N.defaultLanguage);
				$locationProvider.html5Mode(false);

			} ]);

	browserApp.run([ '$location', '$timeout', '$rootScope', '$filter',
			'userService',
			function($location, $timeout, $rootScope, $filter, userService) {
				$rootScope.G_VERSION = G_VERSION;
				$rootScope.EMPTY_UID = EMPTY_UID;
				$rootScope.yesNoOptions = [ {
					id : true,
					name : $filter('translate')('core_label_yes')
				}, {
					id : false,
					name : $filter('translate')('core_label_no')
				} ];
				$rootScope.loginUser = LOGIN_USER;
				$rootScope.envVar = ENV_VAR;

				if (!$rootScope.loginUser.anonymous) {
					if ($location.path() == '/login') {
						$location.path("/task");
					}
				}

				$rootScope.isCreatedBySelf = function(obj) {
					return obj.creatorKey == $rootScope.loginUser.userKey;
				}

				$rootScope.isCreatedByOther = function(obj) {
					return obj.creatorKey != $rootScope.loginUser.userKey;
				}

				$rootScope.$on("EVENT_LOGIN_REDIRECT", function(event, token) {
					LOGIN_USER = token;
					$rootScope.loginUser = token;
					$location.path("/login");
					$timeout(function() {
						$rootScope.$apply();
					}, 0);

				});
				$rootScope.$on('$routeChangeStart', function(next, current) {
					if ($location.path() == '/login') {
						if (!$rootScope.loginUser.anonymous) {
							$location.path("/task");
						}
					}
				});
			} ]);

	angular.element(document).ready(function() {
		angular.bootstrap(document, [ 'browserApp' ]);

	});

})();