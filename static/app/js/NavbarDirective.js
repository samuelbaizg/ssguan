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

var NavbarDirective = function($location) {
	return {
		restrict : 'A',
		scope : false,
		link : function(scope, element) {
			function setActive() {
				var path = $location.path();
				var className =  'active';
				
				if (path) {
					angular.forEach(element.find('li'), function(li) {
						var anchor = li.querySelector('a');
						var href = anchor.href;
						if (href != '') {
							var trimmedHref = href.substr(
									href.indexOf('#/') + 1, href.length);
							var basePath = path.substr(0, trimmedHref.length);
							if (trimmedHref === basePath) {
								angular.element(li).addClass(className);
								scope.module = basePath.substr(1);
							} else {
								angular.element(li).removeClass(className);
							}							
							
						}
					});
				}
			}

			setActive();

			scope.$on('$locationChangeSuccess', setActive);
		}
	}
}

NavbarDirective.$inject = [ '$location' ];
